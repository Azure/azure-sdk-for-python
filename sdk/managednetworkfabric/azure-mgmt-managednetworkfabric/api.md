```py
namespace azure.mgmt.managednetworkfabric

    class azure.mgmt.managednetworkfabric.ManagedNetworkFabricMgmtClient: implements ContextManager 
        access_control_lists: AccessControlListsOperations
        edge_connectors: EdgeConnectorsOperations
        external_networks: ExternalNetworksOperations
        fabrics: FabricsOperations
        internal_networks: InternalNetworksOperations
        internet_gateway_rules: InternetGatewayRulesOperations
        internet_gateways: InternetGatewaysOperations
        ip_communities: IpCommunitiesOperations
        ip_extended_communities: IpExtendedCommunitiesOperations
        ip_prefixes: IpPrefixesOperations
        l2_isolation_domains: L2IsolationDomainsOperations
        l3_isolation_domains: L3IsolationDomainsOperations
        neighbor_groups: NeighborGroupsOperations
        network_bootstrap_devices: NetworkBootstrapDevicesOperations
        network_bootstrap_interfaces: NetworkBootstrapInterfacesOperations
        network_device_skus: NetworkDeviceSkusOperations
        network_devices: NetworkDevicesOperations
        network_fabric_controllers: NetworkFabricControllersOperations
        network_fabric_skus: NetworkFabricSkusOperations
        network_fabrics: NetworkFabricsOperations
        network_interfaces: NetworkInterfacesOperations
        network_monitors: NetworkMonitorsOperations
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


namespace azure.mgmt.managednetworkfabric.aio

    class azure.mgmt.managednetworkfabric.aio.ManagedNetworkFabricMgmtClient: implements AsyncContextManager 
        access_control_lists: AccessControlListsOperations
        edge_connectors: EdgeConnectorsOperations
        external_networks: ExternalNetworksOperations
        fabrics: FabricsOperations
        internal_networks: InternalNetworksOperations
        internet_gateway_rules: InternetGatewayRulesOperations
        internet_gateways: InternetGatewaysOperations
        ip_communities: IpCommunitiesOperations
        ip_extended_communities: IpExtendedCommunitiesOperations
        ip_prefixes: IpPrefixesOperations
        l2_isolation_domains: L2IsolationDomainsOperations
        l3_isolation_domains: L3IsolationDomainsOperations
        neighbor_groups: NeighborGroupsOperations
        network_bootstrap_devices: NetworkBootstrapDevicesOperations
        network_bootstrap_interfaces: NetworkBootstrapInterfacesOperations
        network_device_skus: NetworkDeviceSkusOperations
        network_devices: NetworkDevicesOperations
        network_fabric_controllers: NetworkFabricControllersOperations
        network_fabric_skus: NetworkFabricSkusOperations
        network_fabrics: NetworkFabricsOperations
        network_interfaces: NetworkInterfacesOperations
        network_monitors: NetworkMonitorsOperations
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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessControlList]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_resync(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
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
                body: IO[bytes], 
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
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'access_control_list_name', 'accept']}, api_versions_list=['2026-01-15-preview'])
        async def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateConfigurationResponseV2]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                **kwargs: Any
            ) -> AccessControlList: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AccessControlList]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[AccessControlList]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.EdgeConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                edge_connector_name: str, 
                body: EdgeConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeConnector]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                edge_connector_name: str, 
                body: EdgeConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeConnector]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                edge_connector_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeConnector]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_connector_name']}, api_versions_list=['2026-01-15-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                edge_connector_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                edge_connector_name: str, 
                body: EdgeConnectorPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeConnector]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                edge_connector_name: str, 
                body: EdgeConnectorPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeConnector]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                edge_connector_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeConnector]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_connector_name', 'accept']}, api_versions_list=['2026-01-15-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                edge_connector_name: str, 
                **kwargs: Any
            ) -> EdgeConnector: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-01-15-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EdgeConnector]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-01-15-preview'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[EdgeConnector]: ...


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
                body: IO[bytes], 
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
                body: IO[bytes], 
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
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

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
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: ExternalNetworkUpdateBfdAdministrativeStateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExternalNetworkUpdateBfdAdministrativeStateResponse]: ...

        @overload
        async def begin_update_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: ExternalNetworkUpdateBfdAdministrativeStateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExternalNetworkUpdateBfdAdministrativeStateResponse]: ...

        @overload
        async def begin_update_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExternalNetworkUpdateBfdAdministrativeStateResponse]: ...

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
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

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
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_static_route_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                **kwargs: Any
            ) -> ExternalNetwork: ...

        @distributed_trace
        def list_by_l3_isolation_domain(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ExternalNetwork]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.FabricsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: Fabric, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Fabric]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: Fabric, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Fabric]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Fabric]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fabric_name']}, api_versions_list=['2026-01-15-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: FabricPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Fabric]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: FabricPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Fabric]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Fabric]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fabric_name', 'accept']}, api_versions_list=['2026-01-15-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> Fabric: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-01-15-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Fabric]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-01-15-preview'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Fabric]: ...


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
                body: IO[bytes], 
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
                body: IO[bytes], 
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
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

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
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: InternalNetworkUpdateBfdAdministrativeStateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InternalNetworkUpdateBfdAdministrativeStateResponse]: ...

        @overload
        async def begin_update_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: InternalNetworkUpdateBfdAdministrativeStateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InternalNetworkUpdateBfdAdministrativeStateResponse]: ...

        @overload
        async def begin_update_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InternalNetworkUpdateBfdAdministrativeStateResponse]: ...

        @overload
        async def begin_update_bgp_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: InternalNetworkUpdateBgpAdministrativeStateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InternalNetworkUpdateBgpAdministrativeStateResponse]: ...

        @overload
        async def begin_update_bgp_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: InternalNetworkUpdateBgpAdministrativeStateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InternalNetworkUpdateBgpAdministrativeStateResponse]: ...

        @overload
        async def begin_update_bgp_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InternalNetworkUpdateBgpAdministrativeStateResponse]: ...

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
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

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
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_static_route_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                **kwargs: Any
            ) -> InternalNetwork: ...

        @distributed_trace
        def list_by_l3_isolation_domain(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[InternalNetwork]: ...


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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InternetGatewayRule]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                internet_gateway_rule_name: str, 
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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InternetGatewayRule]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                internet_gateway_rule_name: str, 
                **kwargs: Any
            ) -> InternetGatewayRule: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[InternetGatewayRule]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[InternetGatewayRule]: ...


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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InternetGateway]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                internet_gateway_name: str, 
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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InternetGateway]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                internet_gateway_name: str, 
                **kwargs: Any
            ) -> InternetGateway: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[InternetGateway]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[InternetGateway]: ...


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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IpCommunity]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                ip_community_name: str, 
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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IpCommunity]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                ip_community_name: str, 
                **kwargs: Any
            ) -> IpCommunity: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[IpCommunity]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[IpCommunity]: ...


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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IpExtendedCommunity]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                ip_extended_community_name: str, 
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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IpExtendedCommunity]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                ip_extended_community_name: str, 
                **kwargs: Any
            ) -> IpExtendedCommunity: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[IpExtendedCommunity]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[IpExtendedCommunity]: ...


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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IpPrefix]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                ip_prefix_name: str, 
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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IpPrefix]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                ip_prefix_name: str, 
                **kwargs: Any
            ) -> IpPrefix: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[IpPrefix]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[IpPrefix]: ...


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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[L2IsolationDomain]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
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
                body: IO[bytes], 
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
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'l2_isolation_domain_name', 'accept']}, api_versions_list=['2026-01-15-preview'])
        async def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateConfigurationResponseV2]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                **kwargs: Any
            ) -> L2IsolationDomain: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[L2IsolationDomain]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[L2IsolationDomain]: ...


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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[L3IsolationDomain]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
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
                body: IO[bytes], 
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
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'l3_isolation_domain_name', 'accept']}, api_versions_list=['2026-01-15-preview'])
        async def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateConfigurationResponseV2]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                **kwargs: Any
            ) -> L3IsolationDomain: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[L3IsolationDomain]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[L3IsolationDomain]: ...


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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NeighborGroup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                neighbor_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'neighbor_group_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def begin_resync(
                self, 
                resource_group_name: str, 
                neighbor_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[NeighborGroupResyncResponse]: ...

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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NeighborGroup]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                neighbor_group_name: str, 
                **kwargs: Any
            ) -> NeighborGroup: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NeighborGroup]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[NeighborGroup]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.NetworkBootstrapDevicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: NetworkBootstrapDevice, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkBootstrapDevice]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: NetworkBootstrapDevice, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkBootstrapDevice]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkBootstrapDevice]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_bootstrap_device_name']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_bootstrap_device_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def begin_reboot(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkBootstrapDeviceRebootResponse]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_bootstrap_device_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def begin_refresh_configuration(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkBootstrapDeviceRefreshConfigurationResponse]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_bootstrap_device_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def begin_resync_passwords(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkBootstrapDeviceResyncPasswordsResponse]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: NetworkBootstrapDevicePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkBootstrapDevice]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: NetworkBootstrapDevicePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkBootstrapDevice]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkBootstrapDevice]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: UpdateDeviceAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkBootstrapDeviceUpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: UpdateDeviceAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkBootstrapDeviceUpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkBootstrapDeviceUpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: UpdateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkBootstrapDeviceUpgradeResponse]: ...

        @overload
        async def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: UpdateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkBootstrapDeviceUpgradeResponse]: ...

        @overload
        async def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkBootstrapDeviceUpgradeResponse]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_bootstrap_device_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                **kwargs: Any
            ) -> NetworkBootstrapDevice: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkBootstrapDevice]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[NetworkBootstrapDevice]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.NetworkBootstrapInterfacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                network_bootstrap_interface_name: str, 
                body: NetworkBootstrapInterface, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkBootstrapInterface]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                network_bootstrap_interface_name: str, 
                body: NetworkBootstrapInterface, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkBootstrapInterface]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                network_bootstrap_interface_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkBootstrapInterface]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_bootstrap_device_name', 'network_bootstrap_interface_name']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                network_bootstrap_interface_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                network_bootstrap_interface_name: str, 
                body: NetworkBootstrapInterfacePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkBootstrapInterface]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                network_bootstrap_interface_name: str, 
                body: NetworkBootstrapInterfacePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkBootstrapInterface]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                network_bootstrap_interface_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkBootstrapInterface]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                network_bootstrap_interface_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                network_bootstrap_interface_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                network_bootstrap_interface_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_bootstrap_device_name', 'network_bootstrap_interface_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                network_bootstrap_interface_name: str, 
                **kwargs: Any
            ) -> NetworkBootstrapInterface: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_bootstrap_device_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def list_by_network_bootstrap_device(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkBootstrapInterface]: ...


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
                **kwargs: Any
            ) -> NetworkDeviceSku: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[NetworkDeviceSku]: ...


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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkDevice]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
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
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_reboot(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: RebootProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_reboot(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_device_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def begin_refresh_configuration(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkDeviceRefreshConfigurationResponse]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_device_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def begin_resync_certificates(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFabricResyncCertificatesResponse]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_device_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def begin_resync_passwords(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkDeviceResyncPasswordsResponse]: ...

        @overload
        async def begin_run_ro_command(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: DeviceRoCommand, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForDeviceROCommandsOperationStatusResult]: ...

        @overload
        async def begin_run_ro_command(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: DeviceRoCommand, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForDeviceROCommandsOperationStatusResult]: ...

        @overload
        async def begin_run_ro_command(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForDeviceROCommandsOperationStatusResult]: ...

        @overload
        async def begin_run_rw_command(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: DeviceRwCommand, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkDeviceRunRwCommandResponse]: ...

        @overload
        async def begin_run_rw_command(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: DeviceRwCommand, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkDeviceRunRwCommandResponse]: ...

        @overload
        async def begin_run_rw_command(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkDeviceRunRwCommandResponse]: ...

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
                body: IO[bytes], 
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
            ) -> AsyncLROPoller[NetworkDeviceUpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: UpdateDeviceAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkDeviceUpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkDeviceUpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: NetworkDeviceUpgradeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkDeviceUpgradeResponse]: ...

        @overload
        async def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: NetworkDeviceUpgradeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkDeviceUpgradeResponse]: ...

        @overload
        async def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkDeviceUpgradeResponse]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                **kwargs: Any
            ) -> NetworkDevice: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkDevice]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[NetworkDevice]: ...


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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFabricController]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_fabric_controller_name: str, 
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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFabricController]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                network_fabric_controller_name: str, 
                **kwargs: Any
            ) -> NetworkFabricController: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkFabricController]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[NetworkFabricController]: ...


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
                **kwargs: Any
            ) -> NetworkFabricSku: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[NetworkFabricSku]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.NetworkFabricsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_fabric_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def begin_arm_configuration_diff(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ArmConfigurationDiffOperationResponse]: ...

        @overload
        async def begin_commit_batch_status(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: CommitBatchStatusRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommitBatchStatusOperationResponse]: ...

        @overload
        async def begin_commit_batch_status(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: CommitBatchStatusRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommitBatchStatusOperationResponse]: ...

        @overload
        async def begin_commit_batch_status(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommitBatchStatusOperationResponse]: ...

        @overload
        async def begin_commit_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: Optional[CommitConfigurationRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommitConfigurationResponse]: ...

        @overload
        async def begin_commit_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: Optional[CommitConfigurationRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommitConfigurationResponse]: ...

        @overload
        async def begin_commit_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommitConfigurationResponse]: ...

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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFabric]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_fabric_name']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_fabric_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def begin_deprovision(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_discard_commit_batch(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: DiscardCommitBatchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiscardCommitBatchOperationResponse]: ...

        @overload
        async def begin_discard_commit_batch(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: DiscardCommitBatchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiscardCommitBatchOperationResponse]: ...

        @overload
        async def begin_discard_commit_batch(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiscardCommitBatchOperationResponse]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_fabric_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def begin_get_topology(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[GetTopologyResponse]: ...

        @overload
        async def begin_lock_fabric(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: NetworkFabricLockRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_lock_fabric(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: NetworkFabricLockRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_lock_fabric(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_fabric_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def begin_provision(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_refresh_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: Optional[RefreshConfigurationRequestProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_refresh_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: Optional[RefreshConfigurationRequestProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_refresh_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_fabric_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def begin_resync_certificates(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFabricResyncCertificatesResponse]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_fabric_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def begin_resync_passwords(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFabricResyncPasswordsResponse]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_fabric_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def begin_rotate_certificates(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFabricRotateCertificatesResponse]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_fabric_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def begin_rotate_passwords(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFabricRotatePasswordsResponse]: ...

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
                body: IO[bytes], 
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
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_infra_management_bfd_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_infra_management_bfd_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_workload_management_bfd_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_workload_management_bfd_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_workload_management_bfd_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: UpgradeNetworkFabricProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: UpgradeNetworkFabricProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: ValidateConfigurationProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateConfigurationResponseV2]: ...

        @overload
        async def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: ValidateConfigurationProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateConfigurationResponseV2]: ...

        @overload
        async def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateConfigurationResponseV2]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_fabric_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def begin_view_device_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ViewDeviceConfigurationOperationResponse]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_fabric_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> NetworkFabric: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkFabric]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[NetworkFabric]: ...


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
                body: IO[bytes], 
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
                body: IO[bytes], 
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
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

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
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                network_interface_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                network_interface_name: str, 
                **kwargs: Any
            ) -> NetworkInterface: ...

        @distributed_trace
        def list_by_network_device(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkInterface]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.NetworkMonitorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_monitor_name: str, 
                body: NetworkMonitor, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkMonitor]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_monitor_name: str, 
                body: NetworkMonitor, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkMonitor]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                network_monitor_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkMonitor]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-06-15-preview', params_added_on={'2024-06-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'network_monitor_name']}, api_versions_list=['2024-06-15-preview', '2025-07-15', '2026-01-15-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_monitor_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_monitor_name: str, 
                body: NetworkMonitorPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkMonitor]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_monitor_name: str, 
                body: NetworkMonitorPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkMonitor]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_monitor_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkMonitor]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_monitor_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_monitor_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_monitor_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-06-15-preview', params_added_on={'2024-06-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'network_monitor_name', 'accept']}, api_versions_list=['2024-06-15-preview', '2025-07-15', '2026-01-15-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                network_monitor_name: str, 
                **kwargs: Any
            ) -> NetworkMonitor: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-06-15-preview', params_added_on={'2024-06-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2024-06-15-preview', '2025-07-15', '2026-01-15-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkMonitor]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-06-15-preview', params_added_on={'2024-06-15-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2024-06-15-preview', '2025-07-15', '2026-01-15-preview'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[NetworkMonitor]: ...


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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkPacketBroker]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_packet_broker_name: str, 
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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkPacketBroker]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                network_packet_broker_name: str, 
                **kwargs: Any
            ) -> NetworkPacketBroker: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkPacketBroker]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[NetworkPacketBroker]: ...


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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkRack]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_rack_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_rack_name: str, 
                body: NetworkRackPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkRack]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_rack_name: str, 
                body: NetworkRackPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkRack]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_rack_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkRack]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                network_rack_name: str, 
                **kwargs: Any
            ) -> NetworkRack: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkRack]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[NetworkRack]: ...


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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkTapRule]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_tap_rule_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def begin_resync(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkTapRuleResyncResponse]: ...

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
                body: IO[bytes], 
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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommonPostActionResponseForStateUpdate]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'network_tap_rule_name', 'accept']}, api_versions_list=['2026-01-15-preview'])
        async def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateConfigurationResponseV2]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                **kwargs: Any
            ) -> NetworkTapRule: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkTapRule]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[NetworkTapRule]: ...


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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkTap]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_tap_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        async def begin_resync(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkTapResyncResponse]: ...

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
                body: IO[bytes], 
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
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                **kwargs: Any
            ) -> NetworkTap: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkTap]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[NetworkTap]: ...


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
                body: IO[bytes], 
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
                body: IO[bytes], 
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
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

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
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: NniUpdateBfdAdministrativeStateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NniUpdateBfdAdministrativeStateResponse]: ...

        @overload
        async def begin_update_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: NniUpdateBfdAdministrativeStateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NniUpdateBfdAdministrativeStateResponse]: ...

        @overload
        async def begin_update_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NniUpdateBfdAdministrativeStateResponse]: ...

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
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

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
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_npb_static_route_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                **kwargs: Any
            ) -> NetworkToNetworkInterconnect: ...

        @distributed_trace
        def list_by_network_fabric(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkToNetworkInterconnect]: ...


    class azure.mgmt.managednetworkfabric.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RoutePolicy]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
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
                body: IO[bytes], 
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
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        async def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateAdministrativeStateResponse]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'route_policy_name', 'accept']}, api_versions_list=['2026-01-15-preview'])
        async def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateConfigurationResponseV2]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                **kwargs: Any
            ) -> RoutePolicy: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RoutePolicy]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[RoutePolicy]: ...


namespace azure.mgmt.managednetworkfabric.models

    class azure.mgmt.managednetworkfabric.models.AccessControlList(TrackedResource):
        id: str
        location: str
        name: str
        properties: AccessControlListProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: AccessControlListProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.AccessControlListAction(_Model):
        counter_name: Optional[str]
        police_rate_configuration: Optional[PoliceRateConfigurationProperties]
        remark_comment: Optional[str]
        type: Optional[Union[str, AclActionType]]

        @overload
        def __init__(
                self, 
                *, 
                counter_name: Optional[str] = ..., 
                police_rate_configuration: Optional[PoliceRateConfigurationProperties] = ..., 
                remark_comment: Optional[str] = ..., 
                type: Optional[Union[str, AclActionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.AccessControlListActionPatch(_Model):
        counter_name: Optional[str]
        police_rate_configuration: Optional[PoliceRateConfigurationProperties]
        remark_comment: Optional[str]
        type: Optional[Union[str, AclActionType]]

        @overload
        def __init__(
                self, 
                *, 
                counter_name: Optional[str] = ..., 
                police_rate_configuration: Optional[PoliceRateConfigurationProperties] = ..., 
                remark_comment: Optional[str] = ..., 
                type: Optional[Union[str, AclActionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.AccessControlListMatchCondition(CommonMatchConditions):
        dscp_markings: Optional[list[str]]
        ether_types: Optional[list[str]]
        fragments: Optional[list[str]]
        icmp_configuration: Optional[IcmpConfigurationProperties]
        ip_condition: IpMatchCondition
        ip_lengths: Optional[list[str]]
        port_condition: Optional[AccessControlListPortCondition]
        protocol_neighbors: Optional[list[str]]
        protocol_types: list[str]
        ttl_values: Optional[list[str]]
        vlan_match_condition: VlanMatchCondition

        @overload
        def __init__(
                self, 
                *, 
                dscp_markings: Optional[list[str]] = ..., 
                ether_types: Optional[list[str]] = ..., 
                fragments: Optional[list[str]] = ..., 
                icmp_configuration: Optional[IcmpConfigurationProperties] = ..., 
                ip_condition: Optional[IpMatchCondition] = ..., 
                ip_lengths: Optional[list[str]] = ..., 
                port_condition: Optional[AccessControlListPortCondition] = ..., 
                protocol_neighbors: Optional[list[str]] = ..., 
                protocol_types: Optional[list[str]] = ..., 
                ttl_values: Optional[list[str]] = ..., 
                vlan_match_condition: Optional[VlanMatchCondition] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.AccessControlListMatchConditionPatch(CommonMatchConditionsPatch):
        dscp_markings: Optional[list[str]]
        ether_types: Optional[list[str]]
        fragments: Optional[list[str]]
        icmp_configuration: Optional[IcmpConfigurationPatchProperties]
        ip_condition: IpMatchConditionPatch
        ip_lengths: Optional[list[str]]
        port_condition: Optional[AccessControlListPortConditionPatch]
        protocol_neighbors: Optional[list[str]]
        protocol_types: list[str]
        ttl_values: Optional[list[str]]
        vlan_match_condition: VlanMatchConditionPatch

        @overload
        def __init__(
                self, 
                *, 
                dscp_markings: Optional[list[str]] = ..., 
                ether_types: Optional[list[str]] = ..., 
                fragments: Optional[list[str]] = ..., 
                icmp_configuration: Optional[IcmpConfigurationPatchProperties] = ..., 
                ip_condition: Optional[IpMatchConditionPatch] = ..., 
                ip_lengths: Optional[list[str]] = ..., 
                port_condition: Optional[AccessControlListPortConditionPatch] = ..., 
                protocol_neighbors: Optional[list[str]] = ..., 
                protocol_types: Optional[list[str]] = ..., 
                ttl_values: Optional[list[str]] = ..., 
                vlan_match_condition: Optional[VlanMatchConditionPatch] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.AccessControlListMatchConfiguration(_Model):
        actions: Optional[list[AccessControlListAction]]
        ip_address_type: Optional[Union[str, IPAddressType]]
        match_conditions: Optional[list[AccessControlListMatchCondition]]
        match_configuration_name: Optional[str]
        sequence_number: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[list[AccessControlListAction]] = ..., 
                ip_address_type: Optional[Union[str, IPAddressType]] = ..., 
                match_conditions: Optional[list[AccessControlListMatchCondition]] = ..., 
                match_configuration_name: Optional[str] = ..., 
                sequence_number: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.AccessControlListMatchConfigurationPatch(_Model):
        actions: Optional[list[AccessControlListActionPatch]]
        ip_address_type: Optional[Union[str, IPAddressType]]
        match_conditions: Optional[list[AccessControlListMatchConditionPatch]]
        match_configuration_name: Optional[str]
        sequence_number: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[list[AccessControlListActionPatch]] = ..., 
                ip_address_type: Optional[Union[str, IPAddressType]] = ..., 
                match_conditions: Optional[list[AccessControlListMatchConditionPatch]] = ..., 
                match_configuration_name: Optional[str] = ..., 
                sequence_number: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.AccessControlListPatch(TagsUpdate):
        properties: Optional[AccessControlListPatchProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AccessControlListPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.AccessControlListPatchProperties(_Model):
        acl_type: Optional[Union[str, AclType]]
        acls_url: Optional[str]
        annotation: Optional[str]
        configuration_type: Optional[Union[str, ConfigurationType]]
        control_plane_acl_configuration: Optional[list[ControlPlaneAclPatchProperties]]
        default_action: Optional[Union[str, CommunityActionTypes]]
        device_role: Optional[Union[str, DeviceRole]]
        dynamic_match_configurations: Optional[list[CommonDynamicMatchConfigurationPatch]]
        global_access_control_list_actions: Optional[GlobalAccessControlListActionPatchProperties]
        match_configurations: Optional[list[AccessControlListMatchConfigurationPatch]]

        @overload
        def __init__(
                self, 
                *, 
                acl_type: Optional[Union[str, AclType]] = ..., 
                acls_url: Optional[str] = ..., 
                annotation: Optional[str] = ..., 
                configuration_type: Optional[Union[str, ConfigurationType]] = ..., 
                control_plane_acl_configuration: Optional[list[ControlPlaneAclPatchProperties]] = ..., 
                default_action: Optional[Union[str, CommunityActionTypes]] = ..., 
                device_role: Optional[Union[str, DeviceRole]] = ..., 
                dynamic_match_configurations: Optional[list[CommonDynamicMatchConfigurationPatch]] = ..., 
                global_access_control_list_actions: Optional[GlobalAccessControlListActionPatchProperties] = ..., 
                match_configurations: Optional[list[AccessControlListMatchConfigurationPatch]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.AccessControlListPortCondition(PortCondition):
        flags: Optional[list[str]]
        layer4_protocol: Union[str, Layer4Protocol]
        port_group_names: list[str]
        port_type: Union[str, PortType]
        ports: list[str]

        @overload
        def __init__(
                self, 
                *, 
                flags: Optional[list[str]] = ..., 
                layer4_protocol: Union[str, Layer4Protocol], 
                port_group_names: Optional[list[str]] = ..., 
                port_type: Optional[Union[str, PortType]] = ..., 
                ports: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.AccessControlListPortConditionPatch(PortConditionPatch):
        flags: Optional[list[str]]
        layer4_protocol: Union[str, Layer4Protocol]
        port_group_names: list[str]
        port_type: Union[str, PortType]
        ports: list[str]

        @overload
        def __init__(
                self, 
                *, 
                flags: Optional[list[str]] = ..., 
                layer4_protocol: Optional[Union[str, Layer4Protocol]] = ..., 
                port_group_names: Optional[list[str]] = ..., 
                port_type: Optional[Union[str, PortType]] = ..., 
                ports: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.AccessControlListProperties(_Model):
        acl_type: Optional[Union[str, AclType]]
        acls_url: Optional[str]
        administrative_state: Optional[Union[str, AdministrativeState]]
        annotation: Optional[str]
        configuration_state: Optional[Union[str, ConfigurationState]]
        configuration_type: Union[str, ConfigurationType]
        control_plane_acl_configuration: Optional[list[ControlPlaneAclProperties]]
        default_action: Optional[Union[str, CommunityActionTypes]]
        device_role: Optional[Union[str, DeviceRole]]
        dynamic_match_configurations: Optional[list[CommonDynamicMatchConfiguration]]
        global_access_control_list_actions: Optional[GlobalAccessControlListActionProperties]
        last_operation: Optional[LastOperationProperties]
        last_synced_time: Optional[datetime]
        match_configurations: Optional[list[AccessControlListMatchConfiguration]]
        network_fabric_ids: Optional[list[str]]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                acl_type: Optional[Union[str, AclType]] = ..., 
                acls_url: Optional[str] = ..., 
                annotation: Optional[str] = ..., 
                configuration_type: Union[str, ConfigurationType], 
                control_plane_acl_configuration: Optional[list[ControlPlaneAclProperties]] = ..., 
                default_action: Optional[Union[str, CommunityActionTypes]] = ..., 
                device_role: Optional[Union[str, DeviceRole]] = ..., 
                dynamic_match_configurations: Optional[list[CommonDynamicMatchConfiguration]] = ..., 
                global_access_control_list_actions: Optional[GlobalAccessControlListActionProperties] = ..., 
                match_configurations: Optional[list[AccessControlListMatchConfiguration]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.AclActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNT = "Count"
        DROP = "Drop"
        LOG = "Log"
        POLICE_RATE = "PoliceRate"
        REMARK = "Remark"


    class azure.mgmt.managednetworkfabric.models.AclType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTROL_PLANE_ACL = "ControlPlaneAcl"
        CP = "ControlPlaneTrafficPolicy"
        MANAGEMENT = "Management"
        TENANT = "Tenant"


    class azure.mgmt.managednetworkfabric.models.Action(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.managednetworkfabric.models.ActionIpCommunityPatchProperties(_Model):
        add: Optional[IpCommunityIdList]
        delete: Optional[IpCommunityIdList]
        set: Optional[IpCommunityIdList]

        @overload
        def __init__(
                self, 
                *, 
                add: Optional[IpCommunityIdList] = ..., 
                delete: Optional[IpCommunityIdList] = ..., 
                set: Optional[IpCommunityIdList] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ActionIpCommunityProperties(_Model):
        add: Optional[IpCommunityIdList]
        delete: Optional[IpCommunityIdList]
        set: Optional[IpCommunityIdList]

        @overload
        def __init__(
                self, 
                *, 
                add: Optional[IpCommunityIdList] = ..., 
                delete: Optional[IpCommunityIdList] = ..., 
                set: Optional[IpCommunityIdList] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ActionIpExtendedCommunityPatchProperties(_Model):
        add: Optional[IpExtendedCommunityIdList]
        delete: Optional[IpExtendedCommunityIdList]
        set: Optional[IpExtendedCommunityIdList]

        @overload
        def __init__(
                self, 
                *, 
                add: Optional[IpExtendedCommunityIdList] = ..., 
                delete: Optional[IpExtendedCommunityIdList] = ..., 
                set: Optional[IpExtendedCommunityIdList] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ActionIpExtendedCommunityProperties(_Model):
        add: Optional[IpExtendedCommunityIdList]
        delete: Optional[IpExtendedCommunityIdList]
        set: Optional[IpExtendedCommunityIdList]

        @overload
        def __init__(
                self, 
                *, 
                add: Optional[IpExtendedCommunityIdList] = ..., 
                delete: Optional[IpExtendedCommunityIdList] = ..., 
                set: Optional[IpExtendedCommunityIdList] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.managednetworkfabric.models.AddressFamilyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        I_PV4 = "IPv4"
        I_PV6 = "IPv6"


    class azure.mgmt.managednetworkfabric.models.AdministrativeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        ENABLED_DEGRADED = "EnabledDegraded"
        MAT = "MAT"
        RMA = "RMA"
        UNDER_MAINTENANCE = "UnderMaintenance"


    class azure.mgmt.managednetworkfabric.models.AggregateRoute(_Model):
        prefix: str

        @overload
        def __init__(
                self, 
                *, 
                prefix: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.AggregateRouteConfiguration(_Model):
        ipv4_routes: Optional[list[AggregateRoute]]
        ipv6_routes: Optional[list[AggregateRoute]]

        @overload
        def __init__(
                self, 
                *, 
                ipv4_routes: Optional[list[AggregateRoute]] = ..., 
                ipv6_routes: Optional[list[AggregateRoute]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.AggregateRoutePatchConfiguration(_Model):
        ipv4_routes: Optional[list[AggregateRoute]]
        ipv6_routes: Optional[list[AggregateRoute]]

        @overload
        def __init__(
                self, 
                *, 
                ipv4_routes: Optional[list[AggregateRoute]] = ..., 
                ipv6_routes: Optional[list[AggregateRoute]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.AllowASOverride(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"


    class azure.mgmt.managednetworkfabric.models.AnnotationResource(_Model):
        annotation: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ArmConfigurationDiffOperationResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        properties: Optional[ArmConfigurationDiffResponseProperties]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                properties: Optional[ArmConfigurationDiffResponseProperties] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ArmConfigurationDiffResponseProperties(_Model):
        configuration_diff_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                configuration_diff_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.AuthorizedTransceiverPatchProperties(_Model):
        key: Optional[str]
        vendor: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                vendor: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.AuthorizedTransceiverProperties(_Model):
        key: Optional[str]
        vendor: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                vendor: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.BfdAdministrativeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        MAT = "MAT"
        RMA = "RMA"


    class azure.mgmt.managednetworkfabric.models.BfdConfiguration(_Model):
        administrative_state: Optional[Union[str, BfdAdministrativeState]]
        interval_in_milli_seconds: Optional[int]
        multiplier: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                interval_in_milli_seconds: Optional[int] = ..., 
                multiplier: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.BfdPatchConfiguration(_Model):
        administrative_state: Optional[Union[str, BfdAdministrativeState]]
        interval_in_milli_seconds: Optional[int]
        multiplier: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                interval_in_milli_seconds: Optional[int] = ..., 
                multiplier: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.BgpAdministrativeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.managednetworkfabric.models.BgpConfiguration(AnnotationResource):
        allow_as: Optional[int]
        allow_as_override: Optional[Union[str, AllowASOverride]]
        annotation: str
        bfd_configuration: Optional[BfdConfiguration]
        bmp_configuration: Optional[InternalNetworkBmpProperties]
        default_route_originate: Optional[Union[str, BooleanEnumProperty]]
        fabric_asn: Optional[int]
        ipv4_listen_range_prefixes: Optional[list[str]]
        ipv4_neighbor_address: Optional[list[NeighborAddress]]
        ipv6_listen_range_prefixes: Optional[list[str]]
        ipv6_neighbor_address: Optional[list[NeighborAddress]]
        peer_asn: int
        v4_over_v6_bgp_session: Optional[Union[str, V4OverV6BgpSessionState]]
        v6_over_v4_bgp_session: Optional[Union[str, V6OverV4BgpSessionState]]

        @overload
        def __init__(
                self, 
                *, 
                allow_as: Optional[int] = ..., 
                allow_as_override: Optional[Union[str, AllowASOverride]] = ..., 
                annotation: Optional[str] = ..., 
                bfd_configuration: Optional[BfdConfiguration] = ..., 
                bmp_configuration: Optional[InternalNetworkBmpProperties] = ..., 
                default_route_originate: Optional[Union[str, BooleanEnumProperty]] = ..., 
                ipv4_listen_range_prefixes: Optional[list[str]] = ..., 
                ipv4_neighbor_address: Optional[list[NeighborAddress]] = ..., 
                ipv6_listen_range_prefixes: Optional[list[str]] = ..., 
                ipv6_neighbor_address: Optional[list[NeighborAddress]] = ..., 
                peer_asn: int, 
                v4_over_v6_bgp_session: Optional[Union[str, V4OverV6BgpSessionState]] = ..., 
                v6_over_v4_bgp_session: Optional[Union[str, V6OverV4BgpSessionState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.BgpPatchConfiguration(AnnotationResource):
        allow_as: Optional[int]
        allow_as_override: Optional[Union[str, AllowASOverride]]
        annotation: str
        bfd_configuration: Optional[BfdPatchConfiguration]
        bmp_configuration: Optional[InternalNetworkBmpPatchProperties]
        default_route_originate: Optional[Union[str, BooleanEnumProperty]]
        fabric_asn: Optional[int]
        ipv4_listen_range_prefixes: Optional[list[str]]
        ipv4_neighbor_address: Optional[list[NeighborAddressPatch]]
        ipv6_listen_range_prefixes: Optional[list[str]]
        ipv6_neighbor_address: Optional[list[NeighborAddressPatch]]
        peer_asn: Optional[int]
        v4_over_v6_bgp_session: Optional[Union[str, V4OverV6BgpSessionState]]
        v6_over_v4_bgp_session: Optional[Union[str, V6OverV4BgpSessionState]]

        @overload
        def __init__(
                self, 
                *, 
                allow_as: Optional[int] = ..., 
                allow_as_override: Optional[Union[str, AllowASOverride]] = ..., 
                annotation: Optional[str] = ..., 
                bfd_configuration: Optional[BfdPatchConfiguration] = ..., 
                bmp_configuration: Optional[InternalNetworkBmpPatchProperties] = ..., 
                default_route_originate: Optional[Union[str, BooleanEnumProperty]] = ..., 
                ipv4_listen_range_prefixes: Optional[list[str]] = ..., 
                ipv4_neighbor_address: Optional[list[NeighborAddressPatch]] = ..., 
                ipv6_listen_range_prefixes: Optional[list[str]] = ..., 
                ipv6_neighbor_address: Optional[list[NeighborAddressPatch]] = ..., 
                peer_asn: Optional[int] = ..., 
                v4_over_v6_bgp_session: Optional[Union[str, V4OverV6BgpSessionState]] = ..., 
                v6_over_v4_bgp_session: Optional[Union[str, V6OverV4BgpSessionState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.BitRate(_Model):
        rate: Optional[int]
        unit: Optional[Union[str, BitRateUnit]]

        @overload
        def __init__(
                self, 
                *, 
                rate: Optional[int] = ..., 
                unit: Optional[Union[str, BitRateUnit]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.BitRateUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BPS = "bps"
        GBPS = "Gbps"
        KBPS = "Kbps"
        MBPS = "Mbps"
        PPS = "Pps"


    class azure.mgmt.managednetworkfabric.models.BmpConfigurationPatchProperties(_Model):
        export_policy: Optional[Union[str, BmpExportPolicy]]
        export_policy_configuration: Optional[BmpExportPolicyPatchProperties]
        monitored_address_families: Optional[list[Union[str, BmpMonitoredAddressFamily]]]
        monitored_networks: Optional[list[str]]
        scope_resource_id: Optional[str]
        station_configuration_state: Optional[Union[str, StationConfigurationState]]
        station_connection_mode: Optional[Union[str, StationConnectionMode]]
        station_connection_properties: Optional[StationConnectionPatchProperties]
        station_ip: Optional[str]
        station_name: Optional[str]
        station_network: Optional[str]
        station_port: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                export_policy: Optional[Union[str, BmpExportPolicy]] = ..., 
                export_policy_configuration: Optional[BmpExportPolicyPatchProperties] = ..., 
                monitored_address_families: Optional[list[Union[str, BmpMonitoredAddressFamily]]] = ..., 
                monitored_networks: Optional[list[str]] = ..., 
                scope_resource_id: Optional[str] = ..., 
                station_configuration_state: Optional[Union[str, StationConfigurationState]] = ..., 
                station_connection_mode: Optional[Union[str, StationConnectionMode]] = ..., 
                station_connection_properties: Optional[StationConnectionPatchProperties] = ..., 
                station_ip: Optional[str] = ..., 
                station_name: Optional[str] = ..., 
                station_network: Optional[str] = ..., 
                station_port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.BmpConfigurationProperties(_Model):
        export_policy: Optional[Union[str, BmpExportPolicy]]
        export_policy_configuration: Optional[BmpExportPolicyProperties]
        monitored_address_families: Optional[list[Union[str, BmpMonitoredAddressFamily]]]
        monitored_networks: Optional[list[str]]
        scope_resource_id: Optional[str]
        station_configuration_state: Optional[Union[str, StationConfigurationState]]
        station_connection_mode: Optional[Union[str, StationConnectionMode]]
        station_connection_properties: Optional[StationConnectionProperties]
        station_ip: Optional[str]
        station_name: Optional[str]
        station_network: Optional[str]
        station_port: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                export_policy: Optional[Union[str, BmpExportPolicy]] = ..., 
                export_policy_configuration: Optional[BmpExportPolicyProperties] = ..., 
                monitored_address_families: Optional[list[Union[str, BmpMonitoredAddressFamily]]] = ..., 
                monitored_networks: Optional[list[str]] = ..., 
                scope_resource_id: Optional[str] = ..., 
                station_configuration_state: Optional[Union[str, StationConfigurationState]] = ..., 
                station_connection_mode: Optional[Union[str, StationConnectionMode]] = ..., 
                station_connection_properties: Optional[StationConnectionProperties] = ..., 
                station_ip: Optional[str] = ..., 
                station_name: Optional[str] = ..., 
                station_network: Optional[str] = ..., 
                station_port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.BmpConfigurationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.managednetworkfabric.models.BmpExportPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        LOCAL_RIB = "LocalRib"
        POST_POLICY = "Post-Policy"
        PRE_POLICY = "Pre-Policy"


    class azure.mgmt.managednetworkfabric.models.BmpExportPolicyPatchProperties(_Model):
        export_policies: Optional[list[Union[str, BmpExportPolicy]]]

        @overload
        def __init__(
                self, 
                *, 
                export_policies: Optional[list[Union[str, BmpExportPolicy]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.BmpExportPolicyProperties(_Model):
        export_policies: Optional[list[Union[str, BmpExportPolicy]]]

        @overload
        def __init__(
                self, 
                *, 
                export_policies: Optional[list[Union[str, BmpExportPolicy]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.BmpMonitoredAddressFamily(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        IPV4_UNICAST = "ipv4Unicast"
        IPV6_UNICAST = "ipv6Unicast"
        VPN_IPV4 = "vpnIpv4"
        VPN_IPV6 = "vpnIpv6"


    class azure.mgmt.managednetworkfabric.models.BooleanEnumProperty(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.managednetworkfabric.models.BurstSize(_Model):
        size: Optional[int]
        unit: Optional[Union[str, BurstSizeUnit]]

        @overload
        def __init__(
                self, 
                *, 
                size: Optional[int] = ..., 
                unit: Optional[Union[str, BurstSizeUnit]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.BurstSizeUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BYTES = "Bytes"
        G_BYTES = "GBytes"
        K_BYTES = "KBytes"
        M_BYTES = "MBytes"
        PACKETS = "Packets"


    class azure.mgmt.managednetworkfabric.models.CertificateArchiveReference(_Model):
        certificate_name: Optional[str]
        certificate_version: Optional[str]
        key_vault_id: Optional[str]
        key_vault_uri: Optional[str]


    class azure.mgmt.managednetworkfabric.models.CertificateRotationStatus(_Model):
        certificate_archive_reference: Optional[CertificateArchiveReference]
        certificate_type: Optional[str]
        expire_time: Optional[datetime]
        last_rotation_time: Optional[datetime]
        synchronization_status: Optional[Union[str, SynchronizationStatus]]


    class azure.mgmt.managednetworkfabric.models.CommitBatchDetails(_Model):
        failed_devices: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                failed_devices: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.CommitBatchState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        PROCESSING = "Processing"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.managednetworkfabric.models.CommitBatchStatusOperationResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        properties: Optional[CommitBatchStatusResponseProperties]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                properties: Optional[CommitBatchStatusResponseProperties] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.CommitBatchStatusRequest(_Model):
        commit_batch_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                commit_batch_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.CommitBatchStatusResponseProperties(_Model):
        commit_batch_details: Optional[CommitBatchDetails]
        commit_batch_id: Optional[str]
        commit_batch_state: Optional[Union[str, CommitBatchState]]

        @overload
        def __init__(
                self, 
                *, 
                commit_batch_details: Optional[CommitBatchDetails] = ..., 
                commit_batch_id: Optional[str] = ..., 
                commit_batch_state: Optional[Union[str, CommitBatchState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.CommitConfigurationPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STAGE_CE_CONFIGURATION = "StageCEConfiguration"


    class azure.mgmt.managednetworkfabric.models.CommitConfigurationRequest(_Model):
        commit_policy: Optional[Union[str, CommitConfigurationPolicy]]
        commit_stage: Optional[Union[str, CommitStage]]
        devices: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                commit_policy: Optional[Union[str, CommitConfigurationPolicy]] = ..., 
                commit_stage: Optional[Union[str, CommitStage]] = ..., 
                devices: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.CommitConfigurationResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.CommitStage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTINUE = "Continue"
        ROLLBACK = "Rollback"
        START = "Start"


    class azure.mgmt.managednetworkfabric.models.CommonDynamicMatchConfiguration(_Model):
        ip_groups: Optional[list[IpGroupProperties]]
        port_groups: Optional[list[PortGroupProperties]]
        vlan_groups: Optional[list[VlanGroupProperties]]

        @overload
        def __init__(
                self, 
                *, 
                ip_groups: Optional[list[IpGroupProperties]] = ..., 
                port_groups: Optional[list[PortGroupProperties]] = ..., 
                vlan_groups: Optional[list[VlanGroupProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.CommonDynamicMatchConfigurationPatch(_Model):
        ip_groups: Optional[list[IpGroupPatchProperties]]
        port_groups: Optional[list[PortGroupPatchProperties]]
        vlan_groups: Optional[list[VlanGroupPatchProperties]]

        @overload
        def __init__(
                self, 
                *, 
                ip_groups: Optional[list[IpGroupPatchProperties]] = ..., 
                port_groups: Optional[list[PortGroupPatchProperties]] = ..., 
                vlan_groups: Optional[list[VlanGroupPatchProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.CommonErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.CommonMatchConditions(_Model):
        ip_condition: Optional[IpMatchCondition]
        protocol_types: Optional[list[str]]
        vlan_match_condition: Optional[VlanMatchCondition]

        @overload
        def __init__(
                self, 
                *, 
                ip_condition: Optional[IpMatchCondition] = ..., 
                protocol_types: Optional[list[str]] = ..., 
                vlan_match_condition: Optional[VlanMatchCondition] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.CommonMatchConditionsPatch(_Model):
        ip_condition: Optional[IpMatchConditionPatch]
        protocol_types: Optional[list[str]]
        vlan_match_condition: Optional[VlanMatchConditionPatch]

        @overload
        def __init__(
                self, 
                *, 
                ip_condition: Optional[IpMatchConditionPatch] = ..., 
                protocol_types: Optional[list[str]] = ..., 
                vlan_match_condition: Optional[VlanMatchConditionPatch] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.CommonPostActionResponseForDeviceROCommands(_Model):
        configuration_state: Optional[Union[str, ConfigurationState]]
        device_configuration_preview: Optional[str]
        output_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                device_configuration_preview: Optional[str] = ..., 
                output_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.CommonPostActionResponseForDeviceROCommandsOperationStatusResult(CommonErrorResponse):
        end_time: Optional[datetime]
        error: ErrorDetail
        id: Optional[str]
        name: Optional[str]
        properties: Optional[CommonPostActionResponseForDeviceROCommands]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
                properties: Optional[CommonPostActionResponseForDeviceROCommands] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.CommonPostActionResponseForDeviceUpdate(CommonErrorResponse):
        configuration_state: Optional[Union[str, ConfigurationState]]
        error: ErrorDetail
        failed_devices: Optional[list[str]]
        successful_devices: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
                failed_devices: Optional[list[str]] = ..., 
                successful_devices: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.CommonPostActionResponseForStateUpdate(CommonErrorResponse):
        configuration_state: Optional[Union[str, ConfigurationState]]
        error: ErrorDetail

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.CommunityActionTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DENY = "Deny"
        PERMIT = "Permit"


    class azure.mgmt.managednetworkfabric.models.Condition(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUAL_TO = "EqualTo"
        GREATER_THAN_OR_EQUAL_TO = "GreaterThanOrEqualTo"
        LESSER_THAN_OR_EQUAL_TO = "LesserThanOrEqualTo"
        RANGE = "Range"


    class azure.mgmt.managednetworkfabric.models.ConditionalDefaultRouteProperties(_Model):
        ipv4_routes: Optional[list[StaticRouteProperties]]
        ipv6_routes: Optional[list[StaticRouteProperties]]

        @overload
        def __init__(
                self, 
                *, 
                ipv4_routes: Optional[list[StaticRouteProperties]] = ..., 
                ipv6_routes: Optional[list[StaticRouteProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ConfigurationRegenerationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PARTIAL = "Partial"


    class azure.mgmt.managednetworkfabric.models.ConfigurationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        COMMIT_ROLLBACK_FAILED = "CommitRollbackFailed"
        COMMIT_STAGED = "CommitStaged"
        COMMIT_STAGE_FAILED = "CommitStageFailed"
        DEFERRED_CONTROL = "DeferredControl"
        DEPROVISIONED = "Deprovisioned"
        DEPROVISIONING = "Deprovisioning"
        ERROR_DEPROVISIONING = "ErrorDeprovisioning"
        ERROR_PROVISIONING = "ErrorProvisioning"
        FAILED = "Failed"
        PENDING_ADMINISTRATIVE_UPDATE = "PendingAdministrativeUpdate"
        PENDING_COMMIT = "PendingCommit"
        PROVISIONED = "Provisioned"
        PROVISIONING = "Provisioning"
        REJECTED = "Rejected"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.managednetworkfabric.models.ConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FILE = "File"
        INLINE = "Inline"


    class azure.mgmt.managednetworkfabric.models.ConnectedSubnet(AnnotationResource):
        annotation: str
        prefix: str

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                prefix: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ConnectedSubnetPatch(AnnotationResource):
        annotation: str
        prefix: str

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                prefix: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ConnectedSubnetRoutePolicy(_Model):
        export_route_policy: Optional[L3ExportRoutePolicy]

        @overload
        def __init__(
                self, 
                *, 
                export_route_policy: Optional[L3ExportRoutePolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ConnectedSubnetRoutePolicyPatch(_Model):
        export_route_policy: Optional[L3ExportRoutePolicyPatch]

        @overload
        def __init__(
                self, 
                *, 
                export_route_policy: Optional[L3ExportRoutePolicyPatch] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ConnectivityModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARC_PROXY = "arcProxy"
        DIRECT = "direct"
        EXPRESS_ROUTE = "expressRoute"
        NONE = "none"


    class azure.mgmt.managednetworkfabric.models.ControlPlanAclIpMatchCondition(_Model):
        destination_ip_prefix: Optional[str]
        source_ip_prefix: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                destination_ip_prefix: Optional[str] = ..., 
                source_ip_prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ControlPlaneAclAction(_Model):
        remark_comment: Optional[str]
        type: Optional[Union[str, ControlPlaneAclActionType]]

        @overload
        def __init__(
                self, 
                *, 
                remark_comment: Optional[str] = ..., 
                type: Optional[Union[str, ControlPlaneAclActionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ControlPlaneAclActionPatch(_Model):
        remark_comment: Optional[str]
        type: Optional[Union[str, ControlPlaneAclActionType]]

        @overload
        def __init__(
                self, 
                *, 
                remark_comment: Optional[str] = ..., 
                type: Optional[Union[str, ControlPlaneAclActionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ControlPlaneAclActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DENY = "Deny"
        PERMIT = "Permit"
        REMARK = "Remark"


    class azure.mgmt.managednetworkfabric.models.ControlPlaneAclIpMatchConditionPatch(_Model):
        destination_ip_prefix: Optional[str]
        source_ip_prefix: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                destination_ip_prefix: Optional[str] = ..., 
                source_ip_prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ControlPlaneAclMatchCondition(_Model):
        flags: Optional[list[str]]
        icmp_configuration: Optional[IcmpConfigurationProperties]
        ip_condition: Optional[ControlPlanAclIpMatchCondition]
        port_condition: Optional[ControlPlaneAclPortMatchCondition]
        protocol_types: Optional[str]
        ttl_match_condition: Optional[ControlPlaneAclTtlMatchCondition]

        @overload
        def __init__(
                self, 
                *, 
                flags: Optional[list[str]] = ..., 
                icmp_configuration: Optional[IcmpConfigurationProperties] = ..., 
                ip_condition: Optional[ControlPlanAclIpMatchCondition] = ..., 
                port_condition: Optional[ControlPlaneAclPortMatchCondition] = ..., 
                protocol_types: Optional[str] = ..., 
                ttl_match_condition: Optional[ControlPlaneAclTtlMatchCondition] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ControlPlaneAclMatchConditionPatch(_Model):
        flags: Optional[list[str]]
        icmp_configuration: Optional[IcmpConfigurationPatchProperties]
        ip_condition: Optional[ControlPlaneAclIpMatchConditionPatch]
        port_condition: Optional[ControlPlaneAclPortMatchConditionPatch]
        protocol_types: Optional[str]
        ttl_match_condition: Optional[ControlPlaneAclTtlMatchConditionPatch]

        @overload
        def __init__(
                self, 
                *, 
                flags: Optional[list[str]] = ..., 
                icmp_configuration: Optional[IcmpConfigurationPatchProperties] = ..., 
                ip_condition: Optional[ControlPlaneAclIpMatchConditionPatch] = ..., 
                port_condition: Optional[ControlPlaneAclPortMatchConditionPatch] = ..., 
                protocol_types: Optional[str] = ..., 
                ttl_match_condition: Optional[ControlPlaneAclTtlMatchConditionPatch] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ControlPlaneAclMatchConfigurationPatchProperties(_Model):
        action: Optional[ControlPlaneAclActionPatch]
        match_condition: Optional[ControlPlaneAclMatchConditionPatch]
        match_configuration_name: Optional[str]
        sequence_number: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[ControlPlaneAclActionPatch] = ..., 
                match_condition: Optional[ControlPlaneAclMatchConditionPatch] = ..., 
                match_configuration_name: Optional[str] = ..., 
                sequence_number: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ControlPlaneAclMatchConfigurationProperties(_Model):
        action: Optional[ControlPlaneAclAction]
        match_condition: Optional[ControlPlaneAclMatchCondition]
        match_configuration_name: Optional[str]
        sequence_number: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[ControlPlaneAclAction] = ..., 
                match_condition: Optional[ControlPlaneAclMatchCondition] = ..., 
                match_configuration_name: Optional[str] = ..., 
                sequence_number: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ControlPlaneAclPatchProperties(_Model):
        ip_address_type: Optional[Union[str, IPAddressType]]
        match_configurations: Optional[list[ControlPlaneAclMatchConfigurationPatchProperties]]

        @overload
        def __init__(
                self, 
                *, 
                ip_address_type: Optional[Union[str, IPAddressType]] = ..., 
                match_configurations: Optional[list[ControlPlaneAclMatchConfigurationPatchProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ControlPlaneAclPortCondition(_Model):
        port_match_type: Optional[Union[str, ControlPlaneAclPortMatchType]]
        ports: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                port_match_type: Optional[Union[str, ControlPlaneAclPortMatchType]] = ..., 
                ports: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ControlPlaneAclPortMatchCondition(_Model):
        destination_ports: Optional[ControlPlaneAclPortCondition]
        source_ports: Optional[ControlPlaneAclPortCondition]

        @overload
        def __init__(
                self, 
                *, 
                destination_ports: Optional[ControlPlaneAclPortCondition] = ..., 
                source_ports: Optional[ControlPlaneAclPortCondition] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ControlPlaneAclPortMatchConditionPatch(_Model):
        destination_ports: Optional[ControlPlaneAclPortCondition]
        source_ports: Optional[ControlPlaneAclPortCondition]

        @overload
        def __init__(
                self, 
                *, 
                destination_ports: Optional[ControlPlaneAclPortCondition] = ..., 
                source_ports: Optional[ControlPlaneAclPortCondition] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ControlPlaneAclPortMatchType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUALS = "eq"
        GREATER_THAN = "gt"
        LESSER_THAN = "lt"
        NOT_EQUALS = "neq"
        RANGE = "range"


    class azure.mgmt.managednetworkfabric.models.ControlPlaneAclProperties(_Model):
        ip_address_type: Optional[Union[str, IPAddressType]]
        match_configurations: Optional[list[ControlPlaneAclMatchConfigurationProperties]]

        @overload
        def __init__(
                self, 
                *, 
                ip_address_type: Optional[Union[str, IPAddressType]] = ..., 
                match_configurations: Optional[list[ControlPlaneAclMatchConfigurationProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ControlPlaneAclTtlMatchCondition(_Model):
        ttl_match_type: Optional[Union[str, ControlPlaneAclTtlMatchType]]
        ttl_value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ttl_match_type: Optional[Union[str, ControlPlaneAclTtlMatchType]] = ..., 
                ttl_value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ControlPlaneAclTtlMatchConditionPatch(_Model):
        ttl_match_type: Optional[Union[str, ControlPlaneAclTtlMatchType]]
        ttl_value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ttl_match_type: Optional[Union[str, ControlPlaneAclTtlMatchType]] = ..., 
                ttl_value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ControlPlaneAclTtlMatchType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUALS = "eq"
        GREATER_THAN = "gt"
        LESSER_THAN = "lt"
        NOT_EQUALS = "neq"


    class azure.mgmt.managednetworkfabric.models.ControllerServices(_Model):
        ipv4_address_spaces: Optional[list[str]]
        ipv6_address_spaces: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                ipv4_address_spaces: Optional[list[str]] = ..., 
                ipv6_address_spaces: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ControllerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARISTA_CLOUD_VISION = "aristaCloudVision"
        CISCO_ACI = "ciscoAci"
        DIRECT = "direct"


    class azure.mgmt.managednetworkfabric.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.managednetworkfabric.models.DestinationPatchProperties(_Model):
        destination_id: Optional[str]
        destination_tap_rule_id: Optional[str]
        destination_type: Optional[Union[str, DestinationType]]
        isolation_domain_properties: Optional[IsolationDomainPatchProperties]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                destination_id: Optional[str] = ..., 
                destination_tap_rule_id: Optional[str] = ..., 
                destination_type: Optional[Union[str, DestinationType]] = ..., 
                isolation_domain_properties: Optional[IsolationDomainPatchProperties] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.DestinationProperties(_Model):
        destination_id: str
        destination_tap_rule_id: Optional[str]
        destination_type: Union[str, DestinationType]
        isolation_domain_properties: Optional[IsolationDomainProperties]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                destination_id: str, 
                destination_tap_rule_id: Optional[str] = ..., 
                destination_type: Union[str, DestinationType], 
                isolation_domain_properties: Optional[IsolationDomainProperties] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.DestinationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIRECT = "Direct"
        ISOLATION_DOMAIN = "IsolationDomain"


    class azure.mgmt.managednetworkfabric.models.DeviceAdministrativeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"
        GRACEFUL_QUARANTINE = "GracefulQuarantine"
        QUARANTINE = "Quarantine"
        RESYNC = "Resync"
        RMA = "RMA"
        UNDER_MAINTENANCE = "UnderMaintenance"
        UNGRACEFUL_QUARANTINE = "UngracefulQuarantine"
        UNGRACEFUL_RMA = "UngracefulRMA"


    class azure.mgmt.managednetworkfabric.models.DeviceInterfaceProperties(_Model):
        identifier: Optional[str]
        interface_type: Optional[str]
        supported_connector_types: Optional[list[SupportedConnectorProperties]]

        @overload
        def __init__(
                self, 
                *, 
                identifier: Optional[str] = ..., 
                interface_type: Optional[str] = ..., 
                supported_connector_types: Optional[list[SupportedConnectorProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.DeviceRoCommand(_Model):
        command: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                command: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.DeviceRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CE = "CE"
        MANAGEMENT_SWITCH = "ManagementSwitch"
        NPB = "NPB"
        TERMINAL_SERVER = "TerminalServer"
        TO_R = "ToR"


    class azure.mgmt.managednetworkfabric.models.DeviceRwCommand(_Model):
        command: Optional[str]
        command_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                command: Optional[str] = ..., 
                command_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.DiscardCommitBatchOperationResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        properties: Optional[DiscardCommitBatchResponseProperties]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                properties: Optional[DiscardCommitBatchResponseProperties] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.DiscardCommitBatchRequest(_Model):
        commit_batch_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                commit_batch_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.DiscardCommitBatchResponseProperties(_Model):
        commit_batch_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                commit_batch_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.EdgeConnector(TrackedResource):
        id: str
        location: str
        name: str
        properties: EdgeConnectorProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: EdgeConnectorProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.EdgeConnectorPatch(_Model):
        properties: Optional[EdgeConnectorPatchableProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EdgeConnectorPatchableProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.EdgeConnectorPatchableProperties(_Model):
        connectivity_model: Optional[Union[str, ConnectivityModel]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                connectivity_model: Optional[Union[str, ConnectivityModel]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.EdgeConnectorProperties(_Model):
        connectivity_model: Optional[Union[str, ConnectivityModel]]
        managed_fabric_ids: Optional[list[str]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                connectivity_model: Optional[Union[str, ConnectivityModel]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.EnableDisableOnResources(_Model):
        resource_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                resource_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.EnableDisableState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"
        UNDER_MAINTENANCE = "UnderMaintenance"


    class azure.mgmt.managednetworkfabric.models.Encapsulation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GRE = "GRE"
        NONE = "None"


    class azure.mgmt.managednetworkfabric.models.EncapsulationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GT_PV1 = "GTPv1"
        NONE = "None"


    class azure.mgmt.managednetworkfabric.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.managednetworkfabric.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.managednetworkfabric.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ExportRoutePolicy(_Model):
        export_ipv4_route_policy_id: Optional[str]
        export_ipv6_route_policy_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                export_ipv4_route_policy_id: Optional[str] = ..., 
                export_ipv6_route_policy_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ExportRoutePolicyInformation(_Model):
        export_ipv4_route_policy_id: Optional[str]
        export_ipv6_route_policy_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                export_ipv4_route_policy_id: Optional[str] = ..., 
                export_ipv6_route_policy_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ExportRoutePolicyInformationPatch(_Model):
        export_ipv4_route_policy_id: Optional[str]
        export_ipv6_route_policy_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                export_ipv4_route_policy_id: Optional[str] = ..., 
                export_ipv6_route_policy_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ExportRoutePolicyPatch(_Model):
        export_ipv4_route_policy_id: Optional[str]
        export_ipv6_route_policy_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                export_ipv4_route_policy_id: Optional[str] = ..., 
                export_ipv6_route_policy_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ExpressRouteConnectionInformation(_Model):
        express_route_authorization_key: str
        express_route_circuit_id: str

        @overload
        def __init__(
                self, 
                *, 
                express_route_authorization_key: str, 
                express_route_circuit_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ExtendedVlan(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.managednetworkfabric.models.Extension(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_EXTENSION = "NoExtension"
        NPB = "NPB"


    class azure.mgmt.managednetworkfabric.models.ExternalNetwork(ProxyResource):
        id: str
        name: str
        properties: ExternalNetworkProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: ExternalNetworkProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ExternalNetworkBmpPatchProperties(_Model):
        configuration_state: Optional[Union[str, BmpConfigurationState]]

        @overload
        def __init__(
                self, 
                *, 
                configuration_state: Optional[Union[str, BmpConfigurationState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ExternalNetworkBmpProperties(_Model):
        configuration_state: Optional[Union[str, BmpConfigurationState]]

        @overload
        def __init__(
                self, 
                *, 
                configuration_state: Optional[Union[str, BmpConfigurationState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ExternalNetworkPatch(_Model):
        properties: Optional[ExternalNetworkPatchProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ExternalNetworkPatchProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ExternalNetworkPatchProperties(_Model):
        annotation: Optional[str]
        export_route_policy: Optional[ExportRoutePolicyPatch]
        import_route_policy: Optional[ImportRoutePolicyPatch]
        network_to_network_interconnect_id: Optional[str]
        option_a_properties: Optional[ExternalNetworkPatchPropertiesOptionAProperties]
        option_b_properties: Optional[L3OptionBPatchProperties]
        peering_option: Optional[Union[str, PeeringOption]]
        static_route_configuration: Optional[ExternalNetworkStaticRoutePatchConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                export_route_policy: Optional[ExportRoutePolicyPatch] = ..., 
                import_route_policy: Optional[ImportRoutePolicyPatch] = ..., 
                network_to_network_interconnect_id: Optional[str] = ..., 
                option_a_properties: Optional[ExternalNetworkPatchPropertiesOptionAProperties] = ..., 
                option_b_properties: Optional[L3OptionBPatchProperties] = ..., 
                peering_option: Optional[Union[str, PeeringOption]] = ..., 
                static_route_configuration: Optional[ExternalNetworkStaticRoutePatchConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ExternalNetworkPatchPropertiesOptionAProperties(_Model):
        bfd_configuration: Optional[BfdPatchConfiguration]
        bmp_configuration: Optional[ExternalNetworkBmpPatchProperties]
        egress_acl_id: Optional[str]
        fabric_asn: Optional[int]
        ingress_acl_id: Optional[str]
        mtu: Optional[int]
        native_ipv4_prefix_limit: Optional[NativeIpv4PrefixLimitPatchProperties]
        native_ipv6_prefix_limit: Optional[NativeIpv6PrefixLimitPatchProperties]
        peer_asn: Optional[int]
        primary_ipv4_prefix: Optional[str]
        primary_ipv6_prefix: Optional[str]
        secondary_ipv4_prefix: Optional[str]
        secondary_ipv6_prefix: Optional[str]
        v4_over_v6_bgp_session: Optional[Union[str, V4OverV6BgpSessionState]]
        v6_over_v4_bgp_session: Optional[Union[str, V6OverV4BgpSessionState]]
        vlan_id: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                bfd_configuration: Optional[BfdPatchConfiguration] = ..., 
                bmp_configuration: Optional[ExternalNetworkBmpPatchProperties] = ..., 
                egress_acl_id: Optional[str] = ..., 
                ingress_acl_id: Optional[str] = ..., 
                mtu: Optional[int] = ..., 
                native_ipv4_prefix_limit: Optional[NativeIpv4PrefixLimitPatchProperties] = ..., 
                native_ipv6_prefix_limit: Optional[NativeIpv6PrefixLimitPatchProperties] = ..., 
                peer_asn: Optional[int] = ..., 
                primary_ipv4_prefix: Optional[str] = ..., 
                primary_ipv6_prefix: Optional[str] = ..., 
                secondary_ipv4_prefix: Optional[str] = ..., 
                secondary_ipv6_prefix: Optional[str] = ..., 
                v4_over_v6_bgp_session: Optional[Union[str, V4OverV6BgpSessionState]] = ..., 
                v6_over_v4_bgp_session: Optional[Union[str, V6OverV4BgpSessionState]] = ..., 
                vlan_id: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ExternalNetworkProperties(_Model):
        administrative_state: Optional[Union[str, AdministrativeState]]
        annotation: Optional[str]
        configuration_state: Optional[Union[str, ConfigurationState]]
        export_route_policy: Optional[ExportRoutePolicy]
        import_route_policy: Optional[ImportRoutePolicy]
        last_operation: Optional[LastOperationProperties]
        network_fabric_id: Optional[str]
        network_to_network_interconnect_id: Optional[str]
        option_a_properties: Optional[ExternalNetworkPropertiesOptionAProperties]
        option_b_properties: Optional[L3OptionBProperties]
        peering_option: Union[str, PeeringOption]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        static_route_configuration: Optional[ExternalNetworkStaticRouteConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                export_route_policy: Optional[ExportRoutePolicy] = ..., 
                import_route_policy: Optional[ImportRoutePolicy] = ..., 
                network_to_network_interconnect_id: Optional[str] = ..., 
                option_a_properties: Optional[ExternalNetworkPropertiesOptionAProperties] = ..., 
                option_b_properties: Optional[L3OptionBProperties] = ..., 
                peering_option: Union[str, PeeringOption], 
                static_route_configuration: Optional[ExternalNetworkStaticRouteConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ExternalNetworkPropertiesOptionAProperties(_Model):
        bfd_configuration: Optional[BfdConfiguration]
        bmp_configuration: Optional[ExternalNetworkBmpProperties]
        egress_acl_id: Optional[str]
        fabric_asn: Optional[int]
        ingress_acl_id: Optional[str]
        mtu: Optional[int]
        native_ipv4_prefix_limit: Optional[NativeIpv4PrefixLimitProperties]
        native_ipv6_prefix_limit: Optional[NativeIpv6PrefixLimitProperties]
        peer_asn: int
        primary_ipv4_prefix: Optional[str]
        primary_ipv6_prefix: Optional[str]
        secondary_ipv4_prefix: Optional[str]
        secondary_ipv6_prefix: Optional[str]
        v4_over_v6_bgp_session: Optional[Union[str, V4OverV6BgpSessionState]]
        v6_over_v4_bgp_session: Optional[Union[str, V6OverV4BgpSessionState]]
        vlan_id: int

        @overload
        def __init__(
                self, 
                *, 
                bfd_configuration: Optional[BfdConfiguration] = ..., 
                bmp_configuration: Optional[ExternalNetworkBmpProperties] = ..., 
                egress_acl_id: Optional[str] = ..., 
                ingress_acl_id: Optional[str] = ..., 
                mtu: Optional[int] = ..., 
                native_ipv4_prefix_limit: Optional[NativeIpv4PrefixLimitProperties] = ..., 
                native_ipv6_prefix_limit: Optional[NativeIpv6PrefixLimitProperties] = ..., 
                peer_asn: int, 
                primary_ipv4_prefix: Optional[str] = ..., 
                primary_ipv6_prefix: Optional[str] = ..., 
                secondary_ipv4_prefix: Optional[str] = ..., 
                secondary_ipv6_prefix: Optional[str] = ..., 
                v4_over_v6_bgp_session: Optional[Union[str, V4OverV6BgpSessionState]] = ..., 
                v6_over_v4_bgp_session: Optional[Union[str, V6OverV4BgpSessionState]] = ..., 
                vlan_id: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ExternalNetworkRouteType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OPTION_A = "OptionA"
        STATIC = "Static"


    class azure.mgmt.managednetworkfabric.models.ExternalNetworkStaticRouteConfiguration(_Model):
        bfd_configuration: Optional[BfdConfiguration]
        ipv4_routes: Optional[list[StaticRouteProperties]]
        ipv6_routes: Optional[list[StaticRouteProperties]]

        @overload
        def __init__(
                self, 
                *, 
                bfd_configuration: Optional[BfdConfiguration] = ..., 
                ipv4_routes: Optional[list[StaticRouteProperties]] = ..., 
                ipv6_routes: Optional[list[StaticRouteProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ExternalNetworkStaticRoutePatchConfiguration(_Model):
        bfd_configuration: Optional[BfdPatchConfiguration]
        ipv4_routes: Optional[list[StaticRoutePatchProperties]]
        ipv6_routes: Optional[list[StaticRoutePatchProperties]]

        @overload
        def __init__(
                self, 
                *, 
                bfd_configuration: Optional[BfdPatchConfiguration] = ..., 
                ipv4_routes: Optional[list[StaticRoutePatchProperties]] = ..., 
                ipv6_routes: Optional[list[StaticRoutePatchProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ExternalNetworkUpdateBfdAdministrativeStateRequest(_Model):
        administrative_state: Optional[Union[str, BfdAdministrativeState]]
        route_type: Optional[Union[str, ExternalNetworkRouteType]]

        @overload
        def __init__(
                self, 
                *, 
                administrative_state: Optional[Union[str, BfdAdministrativeState]] = ..., 
                route_type: Optional[Union[str, ExternalNetworkRouteType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ExternalNetworkUpdateBfdAdministrativeStateResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        properties: Optional[ExternalNetworkUpdateBfdAdministrativeStateResponseProperties]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                properties: Optional[ExternalNetworkUpdateBfdAdministrativeStateResponseProperties] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ExternalNetworkUpdateBfdAdministrativeStateResponseProperties(_Model):
        administrative_state: Optional[Union[str, BfdAdministrativeState]]
        route_type: Optional[Union[str, ExternalNetworkRouteType]]

        @overload
        def __init__(
                self, 
                *, 
                administrative_state: Optional[Union[str, BfdAdministrativeState]] = ..., 
                route_type: Optional[Union[str, ExternalNetworkRouteType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.Fabric(TrackedResource):
        id: str
        location: str
        name: str
        properties: FabricProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: FabricProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.FabricLockProperties(_Model):
        lock_state: Optional[Union[str, LockConfigurationState]]
        lock_type: Optional[Union[str, NetworkFabricLockType]]

        @overload
        def __init__(
                self, 
                *, 
                lock_state: Optional[Union[str, LockConfigurationState]] = ..., 
                lock_type: Optional[Union[str, NetworkFabricLockType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.FabricPatch(_Model):
        properties: Optional[FabricPatchableProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FabricPatchableProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.FabricPatchableProperties(_Model):
        controller_credential_ref: Optional[str]
        controller_endpoint: Optional[str]
        infrastructure_networks: Optional[PatchInfrastructureNetworks]
        infrastructure_services: Optional[PatchInfrastructureServices]
        operation_policy: Optional[Union[str, OperationPolicy]]

        @overload
        def __init__(
                self, 
                *, 
                controller_credential_ref: Optional[str] = ..., 
                controller_endpoint: Optional[str] = ..., 
                infrastructure_networks: Optional[PatchInfrastructureNetworks] = ..., 
                infrastructure_services: Optional[PatchInfrastructureServices] = ..., 
                operation_policy: Optional[Union[str, OperationPolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.FabricProperties(_Model):
        controller_credential_ref: Optional[str]
        controller_endpoint: Optional[str]
        controller_type: Optional[Union[str, ControllerType]]
        customer_subnet_id: Optional[str]
        customer_vnet_id: Optional[str]
        edge_connector_id: Optional[str]
        fabric_sku: Optional[str]
        infrastructure_networks: Optional[InfrastructureNetworks]
        infrastructure_services: Optional[InfrastructureServices]
        management_mode: Union[str, ManagementMode]
        operation_policy: Optional[Union[str, OperationPolicy]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        rack_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                controller_credential_ref: Optional[str] = ..., 
                controller_endpoint: Optional[str] = ..., 
                controller_type: Optional[Union[str, ControllerType]] = ..., 
                customer_subnet_id: Optional[str] = ..., 
                customer_vnet_id: Optional[str] = ..., 
                edge_connector_id: Optional[str] = ..., 
                fabric_sku: Optional[str] = ..., 
                infrastructure_networks: Optional[InfrastructureNetworks] = ..., 
                infrastructure_services: Optional[InfrastructureServices] = ..., 
                management_mode: Union[str, ManagementMode], 
                operation_policy: Optional[Union[str, OperationPolicy]] = ..., 
                rack_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.FabricSkuType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MULTI_RACK = "MultiRack"
        SINGLE_RACK = "SingleRack"


    class azure.mgmt.managednetworkfabric.models.FeatureFlagProperties(_Model):
        feature_flag_name: Optional[str]
        feature_flag_value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                feature_flag_name: Optional[str] = ..., 
                feature_flag_value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.GatewayType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INFRASTRUCTURE = "Infrastructure"
        WORKLOAD = "Workload"


    class azure.mgmt.managednetworkfabric.models.GenerateBaseConfiguration(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.managednetworkfabric.models.GetTopologyResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        properties: Optional[GetTopologyResponseProperties]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                properties: Optional[GetTopologyResponseProperties] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.GetTopologyResponseProperties(_Model):
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.GlobalAccessControlListActionPatchProperties(_Model):
        enable_count: Optional[Union[str, BooleanEnumProperty]]

        @overload
        def __init__(
                self, 
                *, 
                enable_count: Optional[Union[str, BooleanEnumProperty]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.GlobalAccessControlListActionProperties(_Model):
        enable_count: Optional[Union[str, BooleanEnumProperty]]

        @overload
        def __init__(
                self, 
                *, 
                enable_count: Optional[Union[str, BooleanEnumProperty]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.GlobalNetworkTapRuleActionPatchProperties(_Model):
        enable_count: Optional[Union[str, BooleanEnumProperty]]
        truncate: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enable_count: Optional[Union[str, BooleanEnumProperty]] = ..., 
                truncate: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.GlobalNetworkTapRuleActionProperties(_Model):
        enable_count: Optional[Union[str, BooleanEnumProperty]]
        truncate: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enable_count: Optional[Union[str, BooleanEnumProperty]] = ..., 
                truncate: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.HeaderAddressProperties(_Model):
        address_list: Optional[list[str]]
        header_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                address_list: Optional[list[str]] = ..., 
                header_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IPAddressType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        I_PV4 = "IPv4"
        I_PV6 = "IPv6"


    class azure.mgmt.managednetworkfabric.models.IcmpConfigurationPatchProperties(_Model):
        icmp_types: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                icmp_types: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IcmpConfigurationProperties(_Model):
        icmp_types: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                icmp_types: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IdentitySelector(_Model):
        identity_type: Union[str, ManagedServiceIdentitySelectorType]
        user_assigned_identity_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity_type: Union[str, ManagedServiceIdentitySelectorType], 
                user_assigned_identity_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IdentitySelectorPatch(_Model):
        identity_type: Optional[Union[str, ManagedServiceIdentitySelectorType]]
        user_assigned_identity_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity_type: Optional[Union[str, ManagedServiceIdentitySelectorType]] = ..., 
                user_assigned_identity_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ImportRoutePolicy(_Model):
        import_ipv4_route_policy_id: Optional[str]
        import_ipv6_route_policy_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                import_ipv4_route_policy_id: Optional[str] = ..., 
                import_ipv6_route_policy_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ImportRoutePolicyInformation(_Model):
        import_ipv4_route_policy_id: Optional[str]
        import_ipv6_route_policy_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                import_ipv4_route_policy_id: Optional[str] = ..., 
                import_ipv6_route_policy_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ImportRoutePolicyInformationPatch(_Model):
        import_ipv4_route_policy_id: Optional[str]
        import_ipv6_route_policy_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                import_ipv4_route_policy_id: Optional[str] = ..., 
                import_ipv6_route_policy_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ImportRoutePolicyPatch(_Model):
        import_ipv4_route_policy_id: Optional[str]
        import_ipv6_route_policy_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                import_ipv4_route_policy_id: Optional[str] = ..., 
                import_ipv6_route_policy_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.InfraNetwork(_Model):
        ipv4_end_addr: str
        ipv4_gateway: str
        ipv4_start_addr: str
        ipv4_subnet: str
        mtu: Optional[int]
        vlan_id: int

        @overload
        def __init__(
                self, 
                *, 
                ipv4_end_addr: str, 
                ipv4_gateway: str, 
                ipv4_start_addr: str, 
                ipv4_subnet: str, 
                mtu: Optional[int] = ..., 
                vlan_id: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.InfraNetworkOptionalIp(_Model):
        ipv4_end_addr: Optional[str]
        ipv4_gateway: Optional[str]
        ipv4_start_addr: Optional[str]
        ipv4_subnet: Optional[str]
        mtu: Optional[int]
        vlan_id: int

        @overload
        def __init__(
                self, 
                *, 
                ipv4_end_addr: Optional[str] = ..., 
                ipv4_gateway: Optional[str] = ..., 
                ipv4_start_addr: Optional[str] = ..., 
                ipv4_subnet: Optional[str] = ..., 
                mtu: Optional[int] = ..., 
                vlan_id: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.InfrastructureNetworks(_Model):
        bmc: InfraNetwork
        management: InfraNetwork
        pdu: Optional[InfraNetwork]
        pxe: InfraNetwork
        storage: InfraNetwork
        storage_mgmt: Optional[InfraNetworkOptionalIp]

        @overload
        def __init__(
                self, 
                *, 
                bmc: InfraNetwork, 
                management: InfraNetwork, 
                pdu: Optional[InfraNetwork] = ..., 
                pxe: InfraNetwork, 
                storage: InfraNetwork, 
                storage_mgmt: Optional[InfraNetworkOptionalIp] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.InfrastructureServices(_Model):
        dns_servers: list[str]
        ntp_servers: list[str]
        platform_proxy: PlatformProxy

        @overload
        def __init__(
                self, 
                *, 
                dns_servers: list[str], 
                ntp_servers: list[str], 
                platform_proxy: PlatformProxy
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.InterfaceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA = "Data"
        MANAGEMENT = "Management"


    class azure.mgmt.managednetworkfabric.models.InternalNetwork(ProxyResource):
        id: str
        name: str
        properties: InternalNetworkProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: InternalNetworkProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.InternalNetworkBmpPatchProperties(_Model):
        bmp_configuration_state: Optional[Union[str, BmpConfigurationState]]
        neighbor_ip_exclusions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                bmp_configuration_state: Optional[Union[str, BmpConfigurationState]] = ..., 
                neighbor_ip_exclusions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.InternalNetworkBmpProperties(_Model):
        bmp_configuration_state: Optional[Union[str, BmpConfigurationState]]
        export_policy_configuration: Optional[BmpExportPolicyProperties]
        neighbor_ip_exclusions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                bmp_configuration_state: Optional[Union[str, BmpConfigurationState]] = ..., 
                export_policy_configuration: Optional[BmpExportPolicyProperties] = ..., 
                neighbor_ip_exclusions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.InternalNetworkPatch(_Model):
        properties: Optional[InternalNetworkPatchProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[InternalNetworkPatchProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.InternalNetworkPatchProperties(_Model):
        annotation: Optional[str]
        bgp_configuration: Optional[BgpPatchConfiguration]
        connected_i_pv4_subnets: Optional[list[ConnectedSubnetPatch]]
        connected_i_pv6_subnets: Optional[list[ConnectedSubnetPatch]]
        egress_acl_id: Optional[str]
        export_route_policy: Optional[ExportRoutePolicy]
        import_route_policy: Optional[ImportRoutePolicy]
        ingress_acl_id: Optional[str]
        is_monitoring_enabled: Optional[Union[str, IsMonitoringEnabled]]
        mtu: Optional[int]
        native_ipv4_prefix_limit: Optional[NativeIpv4PrefixLimitPatchProperties]
        native_ipv6_prefix_limit: Optional[NativeIpv6PrefixLimitPatchProperties]
        static_route_configuration: Optional[StaticRoutePatchConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                bgp_configuration: Optional[BgpPatchConfiguration] = ..., 
                connected_i_pv4_subnets: Optional[list[ConnectedSubnetPatch]] = ..., 
                connected_i_pv6_subnets: Optional[list[ConnectedSubnetPatch]] = ..., 
                egress_acl_id: Optional[str] = ..., 
                export_route_policy: Optional[ExportRoutePolicy] = ..., 
                import_route_policy: Optional[ImportRoutePolicy] = ..., 
                ingress_acl_id: Optional[str] = ..., 
                is_monitoring_enabled: Optional[Union[str, IsMonitoringEnabled]] = ..., 
                mtu: Optional[int] = ..., 
                native_ipv4_prefix_limit: Optional[NativeIpv4PrefixLimitPatchProperties] = ..., 
                native_ipv6_prefix_limit: Optional[NativeIpv6PrefixLimitPatchProperties] = ..., 
                static_route_configuration: Optional[StaticRoutePatchConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.InternalNetworkProperties(_Model):
        administrative_state: Optional[Union[str, AdministrativeState]]
        annotation: Optional[str]
        bgp_configuration: Optional[BgpConfiguration]
        configuration_state: Optional[Union[str, ConfigurationState]]
        connected_i_pv4_subnets: Optional[list[ConnectedSubnet]]
        connected_i_pv6_subnets: Optional[list[ConnectedSubnet]]
        egress_acl_id: Optional[str]
        export_route_policy: Optional[ExportRoutePolicy]
        extension: Optional[Union[str, Extension]]
        import_route_policy: Optional[ImportRoutePolicy]
        ingress_acl_id: Optional[str]
        is_monitoring_enabled: Optional[Union[str, IsMonitoringEnabled]]
        last_operation: Optional[LastOperationProperties]
        mtu: Optional[int]
        native_ipv4_prefix_limit: Optional[NativeIpv4PrefixLimitProperties]
        native_ipv6_prefix_limit: Optional[NativeIpv6PrefixLimitProperties]
        network_fabric_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        static_route_configuration: Optional[StaticRouteConfiguration]
        vlan_id: int

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                bgp_configuration: Optional[BgpConfiguration] = ..., 
                connected_i_pv4_subnets: Optional[list[ConnectedSubnet]] = ..., 
                connected_i_pv6_subnets: Optional[list[ConnectedSubnet]] = ..., 
                egress_acl_id: Optional[str] = ..., 
                export_route_policy: Optional[ExportRoutePolicy] = ..., 
                extension: Optional[Union[str, Extension]] = ..., 
                import_route_policy: Optional[ImportRoutePolicy] = ..., 
                ingress_acl_id: Optional[str] = ..., 
                is_monitoring_enabled: Optional[Union[str, IsMonitoringEnabled]] = ..., 
                mtu: Optional[int] = ..., 
                native_ipv4_prefix_limit: Optional[NativeIpv4PrefixLimitProperties] = ..., 
                native_ipv6_prefix_limit: Optional[NativeIpv6PrefixLimitProperties] = ..., 
                static_route_configuration: Optional[StaticRouteConfiguration] = ..., 
                vlan_id: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.InternalNetworkRouteType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BGP = "Bgp"
        STATIC = "Static"


    class azure.mgmt.managednetworkfabric.models.InternalNetworkUpdateBfdAdministrativeStateRequest(_Model):
        administrative_state: Optional[Union[str, BfdAdministrativeState]]
        neighbor_address: Optional[str]
        route_type: Optional[Union[str, InternalNetworkRouteType]]

        @overload
        def __init__(
                self, 
                *, 
                administrative_state: Optional[Union[str, BfdAdministrativeState]] = ..., 
                neighbor_address: Optional[str] = ..., 
                route_type: Optional[Union[str, InternalNetworkRouteType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.InternalNetworkUpdateBfdAdministrativeStateResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        properties: Optional[InternalNetworkUpdateBfdAdministrativeStateResponseProperties]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                properties: Optional[InternalNetworkUpdateBfdAdministrativeStateResponseProperties] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.InternalNetworkUpdateBfdAdministrativeStateResponseProperties(_Model):
        neighbor_address_administrative_status: Optional[list[NeighborAddressBfdAdministrativeStatus]]

        @overload
        def __init__(
                self, 
                *, 
                neighbor_address_administrative_status: Optional[list[NeighborAddressBfdAdministrativeStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.InternalNetworkUpdateBgpAdministrativeStateRequest(_Model):
        administrative_state: Optional[Union[str, BgpAdministrativeState]]
        neighbor_address: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                administrative_state: Optional[Union[str, BgpAdministrativeState]] = ..., 
                neighbor_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.InternalNetworkUpdateBgpAdministrativeStateResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        properties: Optional[InternalNetworkUpdateBgpAdministrativeStateResponseProperties]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                properties: Optional[InternalNetworkUpdateBgpAdministrativeStateResponseProperties] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.InternalNetworkUpdateBgpAdministrativeStateResponseProperties(_Model):
        neighbor_address_administrative_status: Optional[list[NeighborAddressBgpAdministrativeStatus]]

        @overload
        def __init__(
                self, 
                *, 
                neighbor_address_administrative_status: Optional[list[NeighborAddressBgpAdministrativeStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.InternetGateway(TrackedResource):
        id: str
        location: str
        name: str
        properties: InternetGatewayProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: InternetGatewayProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.InternetGatewayPatch(TagsUpdate):
        properties: Optional[InternetGatewayPatchProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[InternetGatewayPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.InternetGatewayPatchProperties(_Model):
        internet_gateway_rule_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                internet_gateway_rule_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.InternetGatewayProperties(_Model):
        annotation: Optional[str]
        internet_gateway_rule_id: Optional[str]
        internet_gateway_type: Optional[Union[str, GatewayType]]
        ipv4_address: Optional[str]
        last_operation: Optional[LastOperationProperties]
        network_fabric_controller_id: str
        port: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        type: Optional[Union[str, GatewayType]]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                internet_gateway_rule_id: Optional[str] = ..., 
                internet_gateway_type: Optional[Union[str, GatewayType]] = ..., 
                network_fabric_controller_id: str, 
                type: Optional[Union[str, GatewayType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.InternetGatewayRule(TrackedResource):
        id: str
        location: str
        name: str
        properties: InternetGatewayRuleProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: InternetGatewayRuleProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.InternetGatewayRulePatch(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.InternetGatewayRuleProperties(AnnotationResource):
        annotation: str
        internet_gateway_ids: Optional[list[str]]
        last_operation: Optional[LastOperationProperties]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        rule_properties: RuleProperties

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                rule_properties: RuleProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IpCommunity(TrackedResource):
        id: str
        location: str
        name: str
        properties: IpCommunityProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: IpCommunityProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IpCommunityIdList(_Model):
        ip_community_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                ip_community_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IpCommunityPatch(TagsUpdate):
        properties: Optional[IpCommunityPatchableProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[IpCommunityPatchableProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IpCommunityPatchableProperties(_Model):
        ip_community_rules: Optional[list[IpCommunityRule]]

        @overload
        def __init__(
                self, 
                *, 
                ip_community_rules: Optional[list[IpCommunityRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IpCommunityProperties(_Model):
        administrative_state: Optional[Union[str, AdministrativeState]]
        annotation: Optional[str]
        configuration_state: Optional[Union[str, ConfigurationState]]
        ip_community_rules: list[IpCommunityRule]
        last_operation: Optional[LastOperationProperties]
        network_fabric_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                ip_community_rules: list[IpCommunityRule]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IpCommunityRule(_Model):
        action: Union[str, CommunityActionTypes]
        community_members: list[str]
        sequence_number: int
        well_known_communities: Optional[list[Union[str, WellKnownCommunities]]]

        @overload
        def __init__(
                self, 
                *, 
                action: Union[str, CommunityActionTypes], 
                community_members: list[str], 
                sequence_number: int, 
                well_known_communities: Optional[list[Union[str, WellKnownCommunities]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IpExtendedCommunity(TrackedResource):
        id: str
        location: str
        name: str
        properties: IpExtendedCommunityProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: IpExtendedCommunityProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IpExtendedCommunityIdList(_Model):
        ip_extended_community_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                ip_extended_community_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IpExtendedCommunityPatch(TagsUpdate):
        properties: Optional[IpExtendedCommunityPatchProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[IpExtendedCommunityPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IpExtendedCommunityPatchProperties(_Model):
        annotation: Optional[str]
        ip_extended_community_rules: Optional[list[IpExtendedCommunityRule]]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                ip_extended_community_rules: Optional[list[IpExtendedCommunityRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IpExtendedCommunityProperties(_Model):
        administrative_state: Optional[Union[str, AdministrativeState]]
        annotation: Optional[str]
        configuration_state: Optional[Union[str, ConfigurationState]]
        ip_extended_community_rules: list[IpExtendedCommunityRule]
        last_operation: Optional[LastOperationProperties]
        network_fabric_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                ip_extended_community_rules: list[IpExtendedCommunityRule]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IpExtendedCommunityRule(_Model):
        action: Union[str, CommunityActionTypes]
        route_targets: list[str]
        sequence_number: int

        @overload
        def __init__(
                self, 
                *, 
                action: Union[str, CommunityActionTypes], 
                route_targets: list[str], 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IpGroupPatchProperties(_Model):
        ip_address_type: Optional[Union[str, IPAddressType]]
        ip_prefixes: Optional[list[str]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ip_address_type: Optional[Union[str, IPAddressType]] = ..., 
                ip_prefixes: Optional[list[str]] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IpGroupProperties(_Model):
        ip_address_type: Optional[Union[str, IPAddressType]]
        ip_prefixes: Optional[list[str]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ip_address_type: Optional[Union[str, IPAddressType]] = ..., 
                ip_prefixes: Optional[list[str]] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IpMatchCondition(_Model):
        ip_group_names: Optional[list[str]]
        ip_prefix_values: Optional[list[str]]
        prefix_type: Optional[Union[str, PrefixType]]
        type: Optional[Union[str, SourceDestinationType]]

        @overload
        def __init__(
                self, 
                *, 
                ip_group_names: Optional[list[str]] = ..., 
                ip_prefix_values: Optional[list[str]] = ..., 
                prefix_type: Optional[Union[str, PrefixType]] = ..., 
                type: Optional[Union[str, SourceDestinationType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IpMatchConditionPatch(_Model):
        ip_group_names: Optional[list[str]]
        ip_prefix_values: Optional[list[str]]
        prefix_type: Optional[Union[str, PrefixType]]
        type: Optional[Union[str, SourceDestinationType]]

        @overload
        def __init__(
                self, 
                *, 
                ip_group_names: Optional[list[str]] = ..., 
                ip_prefix_values: Optional[list[str]] = ..., 
                prefix_type: Optional[Union[str, PrefixType]] = ..., 
                type: Optional[Union[str, SourceDestinationType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IpPrefix(TrackedResource):
        id: str
        location: str
        name: str
        properties: IpPrefixProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: IpPrefixProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IpPrefixPatch(TagsUpdate):
        properties: Optional[IpPrefixPatchProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[IpPrefixPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IpPrefixPatchProperties(_Model):
        annotation: Optional[str]
        ip_prefix_rules: Optional[list[IpPrefixRule]]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                ip_prefix_rules: Optional[list[IpPrefixRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IpPrefixProperties(_Model):
        administrative_state: Optional[Union[str, AdministrativeState]]
        annotation: Optional[str]
        configuration_state: Optional[Union[str, ConfigurationState]]
        ip_prefix_rules: list[IpPrefixRule]
        last_operation: Optional[LastOperationProperties]
        network_fabric_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                ip_prefix_rules: list[IpPrefixRule]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IpPrefixRule(_Model):
        action: Union[str, CommunityActionTypes]
        condition: Optional[Union[str, Condition]]
        network_prefix: str
        sequence_number: int
        subnet_mask_length: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action: Union[str, CommunityActionTypes], 
                condition: Optional[Union[str, Condition]] = ..., 
                network_prefix: str, 
                sequence_number: int, 
                subnet_mask_length: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IsManagementType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.managednetworkfabric.models.IsMonitoringEnabled(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.managednetworkfabric.models.IsWorkloadManagementNetworkEnabled(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.managednetworkfabric.models.IsolationDomainPatchProperties(_Model):
        encapsulation: Optional[Union[str, Encapsulation]]
        neighbor_group_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                encapsulation: Optional[Union[str, Encapsulation]] = ..., 
                neighbor_group_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.IsolationDomainProperties(_Model):
        encapsulation: Optional[Union[str, Encapsulation]]
        neighbor_group_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                encapsulation: Optional[Union[str, Encapsulation]] = ..., 
                neighbor_group_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.L2IsolationDomain(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: L2IsolationDomainProperties
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
                properties: L2IsolationDomainProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.L2IsolationDomainPatch(TagsUpdate):
        identity: Optional[ManagedServiceIdentityPatch]
        properties: Optional[L2IsolationDomainPatchProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentityPatch] = ..., 
                properties: Optional[L2IsolationDomainPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.L2IsolationDomainPatchProperties(AnnotationResource):
        annotation: str
        extended_vlan: Optional[Union[str, ExtendedVlan]]
        mtu: Optional[int]
        network_to_network_interconnect_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                extended_vlan: Optional[Union[str, ExtendedVlan]] = ..., 
                mtu: Optional[int] = ..., 
                network_to_network_interconnect_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.L2IsolationDomainProperties(AnnotationResource):
        administrative_state: Optional[Union[str, AdministrativeState]]
        annotation: str
        configuration_state: Optional[Union[str, ConfigurationState]]
        extended_vlan: Optional[Union[str, ExtendedVlan]]
        last_operation: Optional[LastOperationProperties]
        mtu: Optional[int]
        network_fabric_id: str
        network_to_network_interconnect_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        vlan_id: int

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                extended_vlan: Optional[Union[str, ExtendedVlan]] = ..., 
                mtu: Optional[int] = ..., 
                network_fabric_id: str, 
                network_to_network_interconnect_id: Optional[str] = ..., 
                vlan_id: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.L3ExportRoutePolicy(_Model):
        export_ipv4_route_policy_id: Optional[str]
        export_ipv6_route_policy_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                export_ipv4_route_policy_id: Optional[str] = ..., 
                export_ipv6_route_policy_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.L3ExportRoutePolicyPatch(_Model):
        export_ipv4_route_policy_id: Optional[str]
        export_ipv6_route_policy_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                export_ipv4_route_policy_id: Optional[str] = ..., 
                export_ipv6_route_policy_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.L3IsolationDomain(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: L3IsolationDomainProperties
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
                properties: L3IsolationDomainProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.L3IsolationDomainPatch(TagsUpdate):
        identity: Optional[ManagedServiceIdentityPatch]
        properties: Optional[L3IsolationDomainPatchProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentityPatch] = ..., 
                properties: Optional[L3IsolationDomainPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.L3IsolationDomainPatchProperties(_Model):
        aggregate_route_configuration: Optional[AggregateRoutePatchConfiguration]
        annotation: Optional[str]
        connected_subnet_route_policy: Optional[ConnectedSubnetRoutePolicyPatch]
        export_policy_configuration: Optional[BmpExportPolicyPatchProperties]
        redistribute_connected_subnets: Optional[Union[str, RedistributeConnectedSubnets]]
        redistribute_static_routes: Optional[Union[str, RedistributeStaticRoutes]]
        static_route_policy: Optional[StaticRoutePolicyPatch]
        v4_route_prefix_limit: Optional[RoutePrefixLimitPatchProperties]
        v6_route_prefix_limit: Optional[RoutePrefixLimitPatchProperties]

        @overload
        def __init__(
                self, 
                *, 
                aggregate_route_configuration: Optional[AggregateRoutePatchConfiguration] = ..., 
                annotation: Optional[str] = ..., 
                connected_subnet_route_policy: Optional[ConnectedSubnetRoutePolicyPatch] = ..., 
                export_policy_configuration: Optional[BmpExportPolicyPatchProperties] = ..., 
                redistribute_connected_subnets: Optional[Union[str, RedistributeConnectedSubnets]] = ..., 
                redistribute_static_routes: Optional[Union[str, RedistributeStaticRoutes]] = ..., 
                static_route_policy: Optional[StaticRoutePolicyPatch] = ..., 
                v4_route_prefix_limit: Optional[RoutePrefixLimitPatchProperties] = ..., 
                v6_route_prefix_limit: Optional[RoutePrefixLimitPatchProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.L3IsolationDomainProperties(_Model):
        administrative_state: Optional[Union[str, AdministrativeState]]
        aggregate_route_configuration: Optional[AggregateRouteConfiguration]
        annotation: Optional[str]
        configuration_state: Optional[Union[str, ConfigurationState]]
        connected_subnet_route_policy: Optional[ConnectedSubnetRoutePolicy]
        export_policy_configuration: Optional[BmpExportPolicyProperties]
        last_operation: Optional[LastOperationProperties]
        network_fabric_id: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        redistribute_connected_subnets: Optional[Union[str, RedistributeConnectedSubnets]]
        redistribute_static_routes: Optional[Union[str, RedistributeStaticRoutes]]
        static_route_policy: Optional[StaticRoutePolicy]
        unique_rd_configuration: Optional[L3UniqueRouteDistinguisherProperties]
        v4_route_prefix_limit: Optional[RoutePrefixLimitProperties]
        v6_route_prefix_limit: Optional[RoutePrefixLimitProperties]

        @overload
        def __init__(
                self, 
                *, 
                aggregate_route_configuration: Optional[AggregateRouteConfiguration] = ..., 
                annotation: Optional[str] = ..., 
                connected_subnet_route_policy: Optional[ConnectedSubnetRoutePolicy] = ..., 
                export_policy_configuration: Optional[BmpExportPolicyProperties] = ..., 
                network_fabric_id: str, 
                redistribute_connected_subnets: Optional[Union[str, RedistributeConnectedSubnets]] = ..., 
                redistribute_static_routes: Optional[Union[str, RedistributeStaticRoutes]] = ..., 
                static_route_policy: Optional[StaticRoutePolicy] = ..., 
                unique_rd_configuration: Optional[L3UniqueRouteDistinguisherProperties] = ..., 
                v4_route_prefix_limit: Optional[RoutePrefixLimitProperties] = ..., 
                v6_route_prefix_limit: Optional[RoutePrefixLimitProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.L3OptionBPatchProperties(_Model):
        export_route_targets: Optional[list[str]]
        import_route_targets: Optional[list[str]]
        route_targets: Optional[RouteTargetPatchInformation]

        @overload
        def __init__(
                self, 
                *, 
                export_route_targets: Optional[list[str]] = ..., 
                import_route_targets: Optional[list[str]] = ..., 
                route_targets: Optional[RouteTargetPatchInformation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.L3OptionBProperties(_Model):
        export_route_targets: Optional[list[str]]
        import_route_targets: Optional[list[str]]
        route_targets: Optional[RouteTargetInformation]

        @overload
        def __init__(
                self, 
                *, 
                export_route_targets: Optional[list[str]] = ..., 
                import_route_targets: Optional[list[str]] = ..., 
                route_targets: Optional[RouteTargetInformation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.L3UniqueRouteDistinguisherProperties(_Model):
        unique_rds: Optional[list[str]]


    class azure.mgmt.managednetworkfabric.models.LastOperationProperties(_Model):
        details: Optional[str]


    class azure.mgmt.managednetworkfabric.models.Layer2Configuration(_Model):
        interfaces: Optional[list[str]]
        mtu: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                interfaces: Optional[list[str]] = ..., 
                mtu: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.Layer2ConfigurationPatch(_Model):
        interfaces: Optional[list[str]]
        mtu: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                interfaces: Optional[list[str]] = ..., 
                mtu: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.Layer3IpPrefixPatchProperties(_Model):
        primary_ipv4_prefix: Optional[str]
        primary_ipv6_prefix: Optional[str]
        secondary_ipv4_prefix: Optional[str]
        secondary_ipv6_prefix: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                primary_ipv4_prefix: Optional[str] = ..., 
                primary_ipv6_prefix: Optional[str] = ..., 
                secondary_ipv4_prefix: Optional[str] = ..., 
                secondary_ipv6_prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.Layer3IpPrefixProperties(_Model):
        primary_ipv4_prefix: Optional[str]
        primary_ipv6_prefix: Optional[str]
        secondary_ipv4_prefix: Optional[str]
        secondary_ipv6_prefix: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                primary_ipv4_prefix: Optional[str] = ..., 
                primary_ipv6_prefix: Optional[str] = ..., 
                secondary_ipv4_prefix: Optional[str] = ..., 
                secondary_ipv6_prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.Layer4Protocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SCTP = "SCTP"
        TCP = "TCP"
        UDP = "UDP"


    class azure.mgmt.managednetworkfabric.models.LockConfigurationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.managednetworkfabric.models.ManagedResourceGroupConfiguration(_Model):
        location: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.managednetworkfabric.models.ManagedServiceIdentityPatch(_Model):
        type: Optional[Union[str, ManagedServiceIdentityType]]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ManagedServiceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ManagedServiceIdentitySelectorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED_IDENTITY = "SystemAssignedIdentity"
        USER_ASSIGNED_IDENTITY = "UserAssignedIdentity"


    class azure.mgmt.managednetworkfabric.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.managednetworkfabric.models.ManagementMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED = "managed"
        UNMANAGED = "unmanaged"


    class azure.mgmt.managednetworkfabric.models.ManagementNetworkConfigurationProperties(_Model):
        infrastructure_vpn_configuration: VpnConfigurationProperties
        workload_vpn_configuration: VpnConfigurationProperties

        @overload
        def __init__(
                self, 
                *, 
                infrastructure_vpn_configuration: VpnConfigurationProperties, 
                workload_vpn_configuration: VpnConfigurationProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ManagementNetworkPatchConfiguration(_Model):
        infrastructure_vpn_configuration: Optional[VpnConfigurationPatchableProperties]
        workload_vpn_configuration: Optional[VpnConfigurationPatchableProperties]

        @overload
        def __init__(
                self, 
                *, 
                infrastructure_vpn_configuration: Optional[VpnConfigurationPatchableProperties] = ..., 
                workload_vpn_configuration: Optional[VpnConfigurationPatchableProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.MicroBfdState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.managednetworkfabric.models.NNIDerivedUniqueRouteDistinguisherConfigurationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.managednetworkfabric.models.NativeIpv4PrefixLimitPatchProperties(_Model):
        prefix_limits: Optional[list[PrefixLimitPatchProperties]]

        @overload
        def __init__(
                self, 
                *, 
                prefix_limits: Optional[list[PrefixLimitPatchProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NativeIpv4PrefixLimitProperties(_Model):
        prefix_limits: Optional[list[PrefixLimitProperties]]

        @overload
        def __init__(
                self, 
                *, 
                prefix_limits: Optional[list[PrefixLimitProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NativeIpv6PrefixLimitPatchProperties(_Model):
        prefix_limits: Optional[list[PrefixLimitPatchProperties]]

        @overload
        def __init__(
                self, 
                *, 
                prefix_limits: Optional[list[PrefixLimitPatchProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NativeIpv6PrefixLimitProperties(_Model):
        prefix_limits: Optional[list[PrefixLimitProperties]]

        @overload
        def __init__(
                self, 
                *, 
                prefix_limits: Optional[list[PrefixLimitProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NeighborAddress(_Model):
        address: Optional[str]
        bfd_administrative_state: Optional[Union[str, BfdAdministrativeState]]
        bgp_administrative_state: Optional[Union[str, BgpAdministrativeState]]
        configuration_state: Optional[Union[str, ConfigurationState]]

        @overload
        def __init__(
                self, 
                *, 
                address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NeighborAddressBfdAdministrativeStatus(_Model):
        administrative_state: Optional[Union[str, BfdAdministrativeState]]
        error: Optional[str]
        neighbor_address: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                administrative_state: Optional[Union[str, BfdAdministrativeState]] = ..., 
                error: Optional[str] = ..., 
                neighbor_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NeighborAddressBgpAdministrativeStatus(_Model):
        administrative_state: Optional[Union[str, BgpAdministrativeState]]
        error: Optional[str]
        neighbor_address: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                administrative_state: Optional[Union[str, BgpAdministrativeState]] = ..., 
                error: Optional[str] = ..., 
                neighbor_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NeighborAddressPatch(_Model):
        address: Optional[str]
        bfd_administrative_state: Optional[Union[str, BfdAdministrativeState]]
        bgp_administrative_state: Optional[Union[str, BgpAdministrativeState]]
        configuration_state: Optional[Union[str, ConfigurationState]]

        @overload
        def __init__(
                self, 
                *, 
                address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NeighborGroup(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: NeighborGroupProperties
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
                properties: NeighborGroupProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NeighborGroupDestination(_Model):
        ipv4_addresses: Optional[list[str]]
        ipv6_addresses: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                ipv4_addresses: Optional[list[str]] = ..., 
                ipv6_addresses: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NeighborGroupDestinationPatch(_Model):
        ipv4_addresses: Optional[list[str]]
        ipv6_addresses: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                ipv4_addresses: Optional[list[str]] = ..., 
                ipv6_addresses: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NeighborGroupPatch(TagsUpdate):
        identity: Optional[ManagedServiceIdentityPatch]
        properties: Optional[NeighborGroupPatchProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentityPatch] = ..., 
                properties: Optional[NeighborGroupPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NeighborGroupPatchProperties(_Model):
        annotation: Optional[str]
        destination: Optional[NeighborGroupDestinationPatch]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                destination: Optional[NeighborGroupDestinationPatch] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NeighborGroupProperties(_Model):
        administrative_state: Optional[Union[str, AdministrativeState]]
        annotation: Optional[str]
        configuration_state: Optional[Union[str, ConfigurationState]]
        destination: NeighborGroupDestination
        last_operation: Optional[LastOperationProperties]
        network_fabric_ids: Optional[list[str]]
        network_tap_ids: Optional[list[str]]
        network_tap_rule_ids: Optional[list[str]]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                destination: NeighborGroupDestination
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NeighborGroupResyncResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkBootstrapDevice(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: NetworkBootstrapDeviceProperties
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
                properties: NetworkBootstrapDeviceProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkBootstrapDevicePatch(TagsUpdate):
        identity: Optional[ManagedServiceIdentityPatch]
        properties: Optional[NetworkBootstrapDevicePatchProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentityPatch] = ..., 
                properties: Optional[NetworkBootstrapDevicePatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkBootstrapDevicePatchProperties(_Model):
        annotation: Optional[str]
        control_plane_acls: Optional[list[str]]
        host_name: Optional[str]
        serial_number: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                control_plane_acls: Optional[list[str]] = ..., 
                host_name: Optional[str] = ..., 
                serial_number: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkBootstrapDeviceProperties(_Model):
        administrative_state: Optional[Union[str, AdministrativeState]]
        annotation: Optional[str]
        configuration_state: Optional[Union[str, ConfigurationState]]
        control_plane_acls: Optional[list[str]]
        dhcp_v4_server_ip_address: Optional[str]
        host_name: Optional[str]
        network_device_sku: Optional[str]
        network_fabric_id: Optional[str]
        operational_state: Optional[Union[str, OperationalState]]
        primary_management_ipv4_address: Optional[str]
        primary_management_ipv6_address: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        secondary_management_ipv4_address: Optional[str]
        secondary_management_ipv6_address: Optional[str]
        secret_rotation_status: Optional[list[SecretRotationStatus]]
        serial_number: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                control_plane_acls: Optional[list[str]] = ..., 
                host_name: Optional[str] = ..., 
                network_device_sku: Optional[str] = ..., 
                serial_number: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkBootstrapDeviceRebootResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkBootstrapDeviceRefreshConfigurationResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkBootstrapDeviceResyncPasswordsResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkBootstrapDeviceUpdateAdministrativeStateResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkBootstrapDeviceUpgradeResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkBootstrapInterface(ProxyResource):
        id: str
        name: str
        properties: NetworkBootstrapInterfaceProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: NetworkBootstrapInterfaceProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkBootstrapInterfacePatch(_Model):
        properties: Optional[NetworkBootstrapInterfacePatchProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NetworkBootstrapInterfacePatchProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkBootstrapInterfacePatchProperties(AnnotationResource):
        additional_description: Optional[str]
        annotation: str
        serial_number: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_description: Optional[str] = ..., 
                annotation: Optional[str] = ..., 
                serial_number: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkBootstrapInterfaceProperties(AnnotationResource):
        additional_description: Optional[str]
        administrative_state: Optional[Union[str, AdministrativeState]]
        annotation: str
        configuration_state: Optional[Union[str, ConfigurationState]]
        connected_to: Optional[str]
        description: Optional[str]
        interface_type: Optional[Union[str, InterfaceType]]
        ipv4_address: Optional[str]
        ipv6_address: Optional[str]
        operational_state: Optional[Union[str, OperationalState]]
        physical_identifier: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        serial_number: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_description: Optional[str] = ..., 
                annotation: Optional[str] = ..., 
                serial_number: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkDevice(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: NetworkDeviceProperties
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
                properties: NetworkDeviceProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkDevicePatchParameters(TagsUpdate):
        identity: Optional[ManagedServiceIdentityPatch]
        properties: Optional[NetworkDevicePatchParametersProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentityPatch] = ..., 
                properties: Optional[NetworkDevicePatchParametersProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkDevicePatchParametersProperties(_Model):
        annotation: Optional[str]
        host_name: Optional[str]
        identity_selector: Optional[IdentitySelectorPatch]
        serial_number: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                host_name: Optional[str] = ..., 
                identity_selector: Optional[IdentitySelectorPatch] = ..., 
                serial_number: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkDeviceProperties(_Model):
        administrative_state: Optional[Union[str, AdministrativeState]]
        annotation: Optional[str]
        certificate_rotation_status: Optional[list[CertificateRotationStatus]]
        configuration_state: Optional[Union[str, ConfigurationState]]
        host_name: Optional[str]
        identity_selector: Optional[IdentitySelector]
        last_operation: Optional[LastOperationProperties]
        management_ipv4_address: Optional[str]
        management_ipv6_address: Optional[str]
        network_device_role: Optional[Union[str, NetworkDeviceRole]]
        network_device_sku: Optional[str]
        network_fabric_id: Optional[str]
        network_rack_id: Optional[str]
        operational_state: Optional[Union[str, OperationalState]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        rw_device_config: Optional[str]
        secret_rotation_status: Optional[list[SecretRotationStatus]]
        serial_number: str
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                host_name: Optional[str] = ..., 
                identity_selector: Optional[IdentitySelector] = ..., 
                network_device_sku: Optional[str] = ..., 
                serial_number: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkDeviceRefreshConfigurationResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkDeviceResyncPasswordsResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.managednetworkfabric.models.NetworkDeviceRunRwCommandResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        properties: Optional[NetworkDeviceRwCommandResponseProperties]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                properties: Optional[NetworkDeviceRwCommandResponseProperties] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkDeviceRwCommandResponseProperties(_Model):
        configuration_state: Optional[Union[str, ConfigurationState]]
        output_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                output_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkDeviceSku(ProxyResource):
        id: str
        name: str
        properties: NetworkDeviceSkuProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: NetworkDeviceSkuProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkDeviceSkuProperties(_Model):
        interfaces: Optional[list[DeviceInterfaceProperties]]
        manufacturer: Optional[str]
        model: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        supported_role_types: Optional[list[Union[str, NetworkDeviceRoleName]]]
        supported_versions: Optional[list[SupportedVersionProperties]]

        @overload
        def __init__(
                self, 
                *, 
                interfaces: Optional[list[DeviceInterfaceProperties]] = ..., 
                manufacturer: Optional[str] = ..., 
                model: str, 
                supported_role_types: Optional[list[Union[str, NetworkDeviceRoleName]]] = ..., 
                supported_versions: Optional[list[SupportedVersionProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkDeviceUpdateAdministrativeStateResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkDeviceUpgradeRequest(_Model):
        rw_device_config_url: Optional[str]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                rw_device_config_url: Optional[str] = ..., 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkDeviceUpgradeResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkFabric(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: NetworkFabricProperties
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
                properties: NetworkFabricProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkFabricController(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: NetworkFabricControllerProperties
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
                properties: NetworkFabricControllerProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkFabricControllerPatch(TagsUpdate):
        identity: Optional[ManagedServiceIdentityPatch]
        properties: Optional[NetworkFabricControllerPatchProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentityPatch] = ..., 
                properties: Optional[NetworkFabricControllerPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkFabricControllerPatchProperties(_Model):
        infrastructure_express_route_connections: Optional[list[ExpressRouteConnectionInformation]]
        workload_express_route_connections: Optional[list[ExpressRouteConnectionInformation]]

        @overload
        def __init__(
                self, 
                *, 
                infrastructure_express_route_connections: Optional[list[ExpressRouteConnectionInformation]] = ..., 
                workload_express_route_connections: Optional[list[ExpressRouteConnectionInformation]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkFabricControllerProperties(_Model):
        annotation: Optional[str]
        infrastructure_express_route_connections: Optional[list[ExpressRouteConnectionInformation]]
        infrastructure_services: Optional[ControllerServices]
        ipv4_address_space: Optional[str]
        ipv6_address_space: Optional[str]
        is_workload_management_network_enabled: Optional[Union[str, IsWorkloadManagementNetworkEnabled]]
        last_operation: Optional[LastOperationProperties]
        managed_resource_group_configuration: Optional[ManagedResourceGroupConfiguration]
        network_fabric_ids: Optional[list[str]]
        nfc_sku: Optional[Union[str, NfcSku]]
        operational_state: Optional[Union[str, OperationalState]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        tenant_internet_gateway_ids: Optional[list[str]]
        vm_profile: Optional[VmProfile]
        workload_express_route_connections: Optional[list[ExpressRouteConnectionInformation]]
        workload_services: Optional[ControllerServices]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                infrastructure_express_route_connections: Optional[list[ExpressRouteConnectionInformation]] = ..., 
                ipv4_address_space: Optional[str] = ..., 
                ipv6_address_space: Optional[str] = ..., 
                is_workload_management_network_enabled: Optional[Union[str, IsWorkloadManagementNetworkEnabled]] = ..., 
                managed_resource_group_configuration: Optional[ManagedResourceGroupConfiguration] = ..., 
                nfc_sku: Optional[Union[str, NfcSku]] = ..., 
                vm_profile: Optional[VmProfile] = ..., 
                workload_express_route_connections: Optional[list[ExpressRouteConnectionInformation]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkFabricLockAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCK = "Lock"
        UNLOCK = "Unlock"


    class azure.mgmt.managednetworkfabric.models.NetworkFabricLockRequest(_Model):
        action: Optional[Union[str, NetworkFabricLockAction]]
        lock_type: Optional[Union[str, NetworkFabricLockType]]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, NetworkFabricLockAction]] = ..., 
                lock_type: Optional[Union[str, NetworkFabricLockType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkFabricLockType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADMINISTRATIVE = "Administrative"
        CONFIGURATION = "Configuration"


    class azure.mgmt.managednetworkfabric.models.NetworkFabricPatch(TagsUpdate):
        identity: Optional[ManagedServiceIdentityPatch]
        properties: Optional[NetworkFabricPatchProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentityPatch] = ..., 
                properties: Optional[NetworkFabricPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkFabricPatchProperties(_Model):
        annotation: Optional[str]
        authorized_transceiver: Optional[AuthorizedTransceiverPatchProperties]
        control_plane_acls: Optional[list[str]]
        fabric_asn: Optional[int]
        feature_flags: Optional[list[FeatureFlagProperties]]
        hardware_alert_threshold: Optional[int]
        ipv4_prefix: Optional[str]
        ipv6_prefix: Optional[str]
        management_network_configuration: Optional[ManagementNetworkPatchConfiguration]
        qos_configuration: Optional[QosPatchProperties]
        rack_count: Optional[int]
        secret_archive_settings: Optional[SecretArchivePatchSettings]
        server_count_per_rack: Optional[int]
        storage_account_configuration: Optional[StorageAccountPatchConfiguration]
        terminal_server_configuration: Optional[TerminalServerPatchConfiguration]
        trusted_ip_prefixes: Optional[list[str]]
        unique_rd_configuration: Optional[UniqueRouteDistinguisherPatchProperties]
        upgrade_profile: Optional[list[UpgradeProfilePropertiesPatchProperties]]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                authorized_transceiver: Optional[AuthorizedTransceiverPatchProperties] = ..., 
                control_plane_acls: Optional[list[str]] = ..., 
                fabric_asn: Optional[int] = ..., 
                feature_flags: Optional[list[FeatureFlagProperties]] = ..., 
                hardware_alert_threshold: Optional[int] = ..., 
                ipv4_prefix: Optional[str] = ..., 
                ipv6_prefix: Optional[str] = ..., 
                management_network_configuration: Optional[ManagementNetworkPatchConfiguration] = ..., 
                qos_configuration: Optional[QosPatchProperties] = ..., 
                rack_count: Optional[int] = ..., 
                secret_archive_settings: Optional[SecretArchivePatchSettings] = ..., 
                server_count_per_rack: Optional[int] = ..., 
                storage_account_configuration: Optional[StorageAccountPatchConfiguration] = ..., 
                terminal_server_configuration: Optional[TerminalServerPatchConfiguration] = ..., 
                trusted_ip_prefixes: Optional[list[str]] = ..., 
                unique_rd_configuration: Optional[UniqueRouteDistinguisherPatchProperties] = ..., 
                upgrade_profile: Optional[list[UpgradeProfilePropertiesPatchProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkFabricProperties(AnnotationResource):
        active_commit_batches: Optional[list[str]]
        administrative_state: Optional[Union[str, AdministrativeState]]
        annotation: str
        authorized_transceiver: Optional[AuthorizedTransceiverProperties]
        configuration_state: Optional[Union[str, ConfigurationState]]
        control_plane_acls: Optional[list[str]]
        fabric_asn: int
        fabric_locks: Optional[list[FabricLockProperties]]
        fabric_version: Optional[str]
        feature_flags: Optional[list[FeatureFlagProperties]]
        hardware_alert_threshold: Optional[int]
        ipv4_prefix: str
        ipv6_prefix: Optional[str]
        l2_isolation_domains: Optional[list[str]]
        l3_isolation_domains: Optional[list[str]]
        last_operation: Optional[LastOperationProperties]
        management_network_configuration: ManagementNetworkConfigurationProperties
        network_bootstrap_device_id: Optional[str]
        network_fabric_controller_id: str
        network_fabric_sku: str
        operational_state: Optional[Union[str, OperationalState]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        qos_configuration: Optional[QosProperties]
        rack_count: Optional[int]
        racks: Optional[list[str]]
        router_ids: Optional[list[str]]
        secret_archive_settings: Optional[SecretArchiveSettings]
        secret_rotation_summary: Optional[SecretRotationSummary]
        server_count_per_rack: int
        storage_account_configuration: Optional[StorageAccountConfiguration]
        storage_array_count: Optional[int]
        terminal_server_configuration: TerminalServerConfiguration
        trusted_ip_prefixes: Optional[list[str]]
        unique_rd_configuration: Optional[UniqueRouteDistinguisherProperties]
        upgrade_profile: Optional[list[UpgradeProfileProperties]]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                authorized_transceiver: Optional[AuthorizedTransceiverProperties] = ..., 
                control_plane_acls: Optional[list[str]] = ..., 
                fabric_asn: int, 
                fabric_version: Optional[str] = ..., 
                feature_flags: Optional[list[FeatureFlagProperties]] = ..., 
                hardware_alert_threshold: Optional[int] = ..., 
                ipv4_prefix: str, 
                ipv6_prefix: Optional[str] = ..., 
                management_network_configuration: ManagementNetworkConfigurationProperties, 
                network_fabric_controller_id: str, 
                network_fabric_sku: str, 
                qos_configuration: Optional[QosProperties] = ..., 
                rack_count: Optional[int] = ..., 
                secret_archive_settings: Optional[SecretArchiveSettings] = ..., 
                server_count_per_rack: int, 
                storage_account_configuration: Optional[StorageAccountConfiguration] = ..., 
                storage_array_count: Optional[int] = ..., 
                terminal_server_configuration: TerminalServerConfiguration, 
                trusted_ip_prefixes: Optional[list[str]] = ..., 
                unique_rd_configuration: Optional[UniqueRouteDistinguisherProperties] = ..., 
                upgrade_profile: Optional[list[UpgradeProfileProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkFabricRefreshDeviceTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CE = "CE"
        MANAGEMENT_SWITCH = "ManagementSwitch"
        NPB = "NPB"
        TO_R = "ToR"


    class azure.mgmt.managednetworkfabric.models.NetworkFabricResyncCertificatesResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkFabricResyncPasswordsResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkFabricRotateCertificatesResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkFabricRotatePasswordsResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkFabricSku(ProxyResource):
        id: str
        name: str
        properties: NetworkFabricSkuProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: NetworkFabricSkuProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkFabricSkuProperties(_Model):
        details: Optional[str]
        max_compute_racks: Optional[int]
        maximum_server_count: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        supported_versions: Optional[list[str]]
        type: Optional[Union[str, FabricSkuType]]

        @overload
        def __init__(
                self, 
                *, 
                max_compute_racks: Optional[int] = ..., 
                maximum_server_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkFabricUpgradeAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE = "Complete"
        START = "Start"


    class azure.mgmt.managednetworkfabric.models.NetworkInterface(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        name: str
        properties: NetworkInterfaceProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: NetworkInterfaceProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkInterfacePatch(_Model):
        identity: Optional[ManagedServiceIdentityPatch]
        properties: Optional[NetworkInterfacePatchProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentityPatch] = ..., 
                properties: Optional[NetworkInterfacePatchProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkInterfacePatchProperties(AnnotationResource):
        additional_description: Optional[str]
        annotation: str

        @overload
        def __init__(
                self, 
                *, 
                additional_description: Optional[str] = ..., 
                annotation: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkInterfaceProperties(AnnotationResource):
        additional_description: Optional[str]
        administrative_state: Optional[Union[str, AdministrativeState]]
        annotation: str
        configuration_state: Optional[Union[str, ConfigurationState]]
        connected_to: Optional[str]
        description: Optional[str]
        interface_type: Optional[Union[str, InterfaceType]]
        ipv4_address: Optional[str]
        ipv6_address: Optional[str]
        last_operation: Optional[LastOperationProperties]
        network_fabric_id: Optional[str]
        operational_state: Optional[Union[str, OperationalState]]
        physical_identifier: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                additional_description: Optional[str] = ..., 
                annotation: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkMonitor(TrackedResource):
        id: str
        location: str
        name: str
        properties: NetworkMonitorProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: NetworkMonitorProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkMonitorPatch(TagsUpdate):
        properties: Optional[NetworkMonitorPatchProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NetworkMonitorPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkMonitorPatchProperties(_Model):
        bmp_configuration: Optional[BmpConfigurationPatchProperties]

        @overload
        def __init__(
                self, 
                *, 
                bmp_configuration: Optional[BmpConfigurationPatchProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkMonitorProperties(AnnotationResource):
        administrative_state: Optional[Union[str, AdministrativeState]]
        annotation: str
        bmp_configuration: Optional[BmpConfigurationProperties]
        configuration_state: Optional[Union[str, ConfigurationState]]
        last_operation: Optional[LastOperationProperties]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                bmp_configuration: Optional[BmpConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkPacketBroker(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: NetworkPacketBrokerProperties
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
                properties: NetworkPacketBrokerProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkPacketBrokerPatch(TagsUpdate):
        identity: Optional[ManagedServiceIdentityPatch]
        properties: Optional[NetworkPacketBrokerPatchProperties]
        tags: dict[str, str]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentityPatch] = ..., 
                properties: Optional[NetworkPacketBrokerPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkPacketBrokerPatchProperties(_Model):
        source_network_tap_rule_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                source_network_tap_rule_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkPacketBrokerProperties(_Model):
        configuration_state: Optional[Union[str, ConfigurationState]]
        last_operation: Optional[LastOperationProperties]
        neighbor_group_ids: Optional[list[str]]
        network_device_ids: Optional[list[str]]
        network_fabric_id: str
        network_tap_ids: Optional[list[str]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        source_interface_ids: Optional[list[str]]
        source_network_tap_rule_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                network_fabric_id: str, 
                source_network_tap_rule_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkRack(TrackedResource):
        id: str
        location: str
        name: str
        properties: NetworkRackProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: NetworkRackProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkRackPatch(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkRackProperties(AnnotationResource):
        annotation: str
        configuration_state: Optional[Union[str, ConfigurationState]]
        last_operation: Optional[LastOperationProperties]
        network_devices: Optional[list[str]]
        network_fabric_id: str
        network_rack_type: Optional[Union[str, NetworkRackType]]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                network_fabric_id: str, 
                network_rack_type: Optional[Union[str, NetworkRackType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkRackType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGGREGATE = "Aggregate"
        COMBINED = "Combined"
        COMPUTE = "Compute"


    class azure.mgmt.managednetworkfabric.models.NetworkTap(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: NetworkTapProperties
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
                properties: NetworkTapProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkTapPatch(TagsUpdate):
        identity: Optional[ManagedServiceIdentityPatch]
        properties: Optional[NetworkTapPatchProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentityPatch] = ..., 
                properties: Optional[NetworkTapPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkTapPatchProperties(AnnotationResource):
        annotation: str
        destinations: Optional[list[DestinationPatchProperties]]
        polling_type: Optional[Union[str, PollingType]]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                destinations: Optional[list[DestinationPatchProperties]] = ..., 
                polling_type: Optional[Union[str, PollingType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkTapProperties(AnnotationResource):
        administrative_state: Optional[Union[str, AdministrativeState]]
        annotation: str
        configuration_state: Optional[Union[str, ConfigurationState]]
        destinations: list[DestinationProperties]
        last_operation: Optional[LastOperationProperties]
        network_fabric_ids: Optional[list[str]]
        network_packet_broker_id: str
        polling_type: Optional[Union[str, PollingType]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        source_tap_rule_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                destinations: list[DestinationProperties], 
                network_packet_broker_id: str, 
                polling_type: Optional[Union[str, PollingType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkTapResyncResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkTapRule(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: NetworkTapRuleProperties
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
                properties: NetworkTapRuleProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkTapRuleAction(_Model):
        destination_id: Optional[str]
        is_timestamp_enabled: Optional[Union[str, BooleanEnumProperty]]
        match_configuration_name: Optional[str]
        truncate: Optional[str]
        type: Optional[Union[str, TapRuleActionType]]

        @overload
        def __init__(
                self, 
                *, 
                destination_id: Optional[str] = ..., 
                is_timestamp_enabled: Optional[Union[str, BooleanEnumProperty]] = ..., 
                match_configuration_name: Optional[str] = ..., 
                truncate: Optional[str] = ..., 
                type: Optional[Union[str, TapRuleActionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkTapRuleActionPatch(_Model):
        destination_id: Optional[str]
        is_timestamp_enabled: Optional[Union[str, BooleanEnumProperty]]
        match_configuration_name: Optional[str]
        truncate: Optional[str]
        type: Optional[Union[str, TapRuleActionType]]

        @overload
        def __init__(
                self, 
                *, 
                destination_id: Optional[str] = ..., 
                is_timestamp_enabled: Optional[Union[str, BooleanEnumProperty]] = ..., 
                match_configuration_name: Optional[str] = ..., 
                truncate: Optional[str] = ..., 
                type: Optional[Union[str, TapRuleActionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkTapRuleMatchCondition(CommonMatchConditions):
        encapsulation_type: Optional[Union[str, EncapsulationType]]
        ip_condition: IpMatchCondition
        port_condition: Optional[PortCondition]
        protocol_types: list[str]
        vlan_match_condition: VlanMatchCondition

        @overload
        def __init__(
                self, 
                *, 
                encapsulation_type: Optional[Union[str, EncapsulationType]] = ..., 
                ip_condition: Optional[IpMatchCondition] = ..., 
                port_condition: Optional[PortCondition] = ..., 
                protocol_types: Optional[list[str]] = ..., 
                vlan_match_condition: Optional[VlanMatchCondition] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkTapRuleMatchConditionPatch(CommonMatchConditionsPatch):
        encapsulation_type: Optional[Union[str, EncapsulationType]]
        ip_condition: IpMatchConditionPatch
        port_condition: Optional[PortConditionPatch]
        protocol_types: list[str]
        vlan_match_condition: VlanMatchConditionPatch

        @overload
        def __init__(
                self, 
                *, 
                encapsulation_type: Optional[Union[str, EncapsulationType]] = ..., 
                ip_condition: Optional[IpMatchConditionPatch] = ..., 
                port_condition: Optional[PortConditionPatch] = ..., 
                protocol_types: Optional[list[str]] = ..., 
                vlan_match_condition: Optional[VlanMatchConditionPatch] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkTapRuleMatchConfiguration(_Model):
        actions: Optional[list[NetworkTapRuleAction]]
        ip_address_type: Optional[Union[str, IPAddressType]]
        match_conditions: Optional[list[NetworkTapRuleMatchCondition]]
        match_configuration_name: Optional[str]
        sequence_number: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[list[NetworkTapRuleAction]] = ..., 
                ip_address_type: Optional[Union[str, IPAddressType]] = ..., 
                match_conditions: Optional[list[NetworkTapRuleMatchCondition]] = ..., 
                match_configuration_name: Optional[str] = ..., 
                sequence_number: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkTapRuleMatchConfigurationPatch(_Model):
        actions: Optional[list[NetworkTapRuleActionPatch]]
        ip_address_type: Optional[Union[str, IPAddressType]]
        match_conditions: Optional[list[NetworkTapRuleMatchConditionPatch]]
        match_configuration_name: Optional[str]
        sequence_number: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[list[NetworkTapRuleActionPatch]] = ..., 
                ip_address_type: Optional[Union[str, IPAddressType]] = ..., 
                match_conditions: Optional[list[NetworkTapRuleMatchConditionPatch]] = ..., 
                match_configuration_name: Optional[str] = ..., 
                sequence_number: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkTapRulePatch(TagsUpdate):
        identity: Optional[ManagedServiceIdentityPatch]
        properties: Optional[NetworkTapRulePatchProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentityPatch] = ..., 
                properties: Optional[NetworkTapRulePatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkTapRulePatchProperties(_Model):
        annotation: Optional[str]
        configuration_type: Optional[Union[str, ConfigurationType]]
        dynamic_match_configurations: Optional[list[CommonDynamicMatchConfigurationPatch]]
        global_network_tap_rule_actions: Optional[GlobalNetworkTapRuleActionPatchProperties]
        identity_selector: Optional[IdentitySelectorPatch]
        match_configurations: Optional[list[NetworkTapRuleMatchConfigurationPatch]]
        tap_rules_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                configuration_type: Optional[Union[str, ConfigurationType]] = ..., 
                dynamic_match_configurations: Optional[list[CommonDynamicMatchConfigurationPatch]] = ..., 
                global_network_tap_rule_actions: Optional[GlobalNetworkTapRuleActionPatchProperties] = ..., 
                identity_selector: Optional[IdentitySelectorPatch] = ..., 
                match_configurations: Optional[list[NetworkTapRuleMatchConfigurationPatch]] = ..., 
                tap_rules_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkTapRuleProperties(_Model):
        administrative_state: Optional[Union[str, AdministrativeState]]
        annotation: Optional[str]
        configuration_state: Optional[Union[str, ConfigurationState]]
        configuration_type: Union[str, ConfigurationType]
        dynamic_match_configurations: Optional[list[CommonDynamicMatchConfiguration]]
        global_network_tap_rule_actions: Optional[GlobalNetworkTapRuleActionProperties]
        identity_selector: Optional[IdentitySelector]
        last_operation: Optional[LastOperationProperties]
        last_synced_time: Optional[datetime]
        match_configurations: Optional[list[NetworkTapRuleMatchConfiguration]]
        network_fabric_ids: Optional[list[str]]
        network_tap_id: Optional[str]
        network_tap_ids: Optional[list[str]]
        polling_interval_in_seconds: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        tap_rules_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Optional[str] = ..., 
                configuration_type: Union[str, ConfigurationType], 
                dynamic_match_configurations: Optional[list[CommonDynamicMatchConfiguration]] = ..., 
                global_network_tap_rule_actions: Optional[GlobalNetworkTapRuleActionProperties] = ..., 
                identity_selector: Optional[IdentitySelector] = ..., 
                match_configurations: Optional[list[NetworkTapRuleMatchConfiguration]] = ..., 
                polling_interval_in_seconds: Optional[int] = ..., 
                tap_rules_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkTapRuleResyncResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkToNetworkInterconnect(ProxyResource):
        id: str
        name: str
        properties: NetworkToNetworkInterconnectProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: NetworkToNetworkInterconnectProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkToNetworkInterconnectPatch(ProxyResourceBase):
        id: str
        properties: Optional[NetworkToNetworkInterconnectPatchProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NetworkToNetworkInterconnectPatchProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkToNetworkInterconnectPatchProperties(_Model):
        egress_acl_id: Optional[str]
        export_route_policy: Optional[ExportRoutePolicyInformationPatch]
        import_route_policy: Optional[ImportRoutePolicyInformationPatch]
        ingress_acl_id: Optional[str]
        layer2_configuration: Optional[Layer2ConfigurationPatch]
        micro_bfd_state: Optional[Union[str, MicroBfdState]]
        npb_static_route_configuration: Optional[NpbStaticRouteConfigurationPatch]
        option_b_layer3_configuration: Optional[OptionBLayer3ConfigurationPatchProperties]
        static_route_configuration: Optional[NniStaticRoutePatchConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                egress_acl_id: Optional[str] = ..., 
                export_route_policy: Optional[ExportRoutePolicyInformationPatch] = ..., 
                import_route_policy: Optional[ImportRoutePolicyInformationPatch] = ..., 
                ingress_acl_id: Optional[str] = ..., 
                layer2_configuration: Optional[Layer2ConfigurationPatch] = ..., 
                micro_bfd_state: Optional[Union[str, MicroBfdState]] = ..., 
                npb_static_route_configuration: Optional[NpbStaticRouteConfigurationPatch] = ..., 
                option_b_layer3_configuration: Optional[OptionBLayer3ConfigurationPatchProperties] = ..., 
                static_route_configuration: Optional[NniStaticRoutePatchConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NetworkToNetworkInterconnectProperties(_Model):
        administrative_state: Optional[Union[str, AdministrativeState]]
        conditional_default_route_configuration: Optional[ConditionalDefaultRouteProperties]
        configuration_state: Optional[Union[str, ConfigurationState]]
        egress_acl_id: Optional[str]
        export_route_policy: Optional[ExportRoutePolicyInformation]
        import_route_policy: Optional[ImportRoutePolicyInformation]
        ingress_acl_id: Optional[str]
        is_management_type: Optional[Union[str, IsManagementType]]
        last_operation: Optional[LastOperationProperties]
        layer2_configuration: Optional[Layer2Configuration]
        micro_bfd_state: Optional[Union[str, MicroBfdState]]
        nni_type: Optional[Union[str, NniType]]
        npb_static_route_configuration: Optional[NpbStaticRouteConfiguration]
        option_b_layer3_configuration: Optional[OptionBLayer3Configuration]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        static_route_configuration: Optional[NniStaticRouteConfiguration]
        use_option_b: Union[str, BooleanEnumProperty]

        @overload
        def __init__(
                self, 
                *, 
                conditional_default_route_configuration: Optional[ConditionalDefaultRouteProperties] = ..., 
                egress_acl_id: Optional[str] = ..., 
                export_route_policy: Optional[ExportRoutePolicyInformation] = ..., 
                import_route_policy: Optional[ImportRoutePolicyInformation] = ..., 
                ingress_acl_id: Optional[str] = ..., 
                is_management_type: Optional[Union[str, IsManagementType]] = ..., 
                layer2_configuration: Optional[Layer2Configuration] = ..., 
                micro_bfd_state: Optional[Union[str, MicroBfdState]] = ..., 
                nni_type: Optional[Union[str, NniType]] = ..., 
                npb_static_route_configuration: Optional[NpbStaticRouteConfiguration] = ..., 
                option_b_layer3_configuration: Optional[OptionBLayer3Configuration] = ..., 
                static_route_configuration: Optional[NniStaticRouteConfiguration] = ..., 
                use_option_b: Union[str, BooleanEnumProperty]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NfcSku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        HIGH_PERFORMANCE = "HighPerformance"
        STANDARD = "Standard"


    class azure.mgmt.managednetworkfabric.models.NniBmpPatchProperties(_Model):
        configuration_state: Optional[Union[str, BmpConfigurationState]]

        @overload
        def __init__(
                self, 
                *, 
                configuration_state: Optional[Union[str, BmpConfigurationState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NniBmpProperties(_Model):
        configuration_state: Union[str, BmpConfigurationState]

        @overload
        def __init__(
                self, 
                *, 
                configuration_state: Union[str, BmpConfigurationState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NniStaticRouteConfiguration(_Model):
        bfd_configuration: Optional[BfdConfiguration]
        ipv4_routes: Optional[list[StaticRouteProperties]]
        ipv6_routes: Optional[list[StaticRouteProperties]]

        @overload
        def __init__(
                self, 
                *, 
                bfd_configuration: Optional[BfdConfiguration] = ..., 
                ipv4_routes: Optional[list[StaticRouteProperties]] = ..., 
                ipv6_routes: Optional[list[StaticRouteProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NniStaticRoutePatchConfiguration(_Model):
        bfd_configuration: Optional[BfdPatchConfiguration]
        ipv4_routes: Optional[list[StaticRoutePatchProperties]]
        ipv6_routes: Optional[list[StaticRoutePatchProperties]]

        @overload
        def __init__(
                self, 
                *, 
                bfd_configuration: Optional[BfdPatchConfiguration] = ..., 
                ipv4_routes: Optional[list[StaticRoutePatchProperties]] = ..., 
                ipv6_routes: Optional[list[StaticRoutePatchProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NniType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CE = "CE"
        NPB = "NPB"


    class azure.mgmt.managednetworkfabric.models.NniUpdateBfdAdministrativeStateRequest(_Model):
        administrative_state: Optional[Union[str, BfdAdministrativeState]]
        route_type: Optional[Union[str, RouteType]]

        @overload
        def __init__(
                self, 
                *, 
                administrative_state: Optional[Union[str, BfdAdministrativeState]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NniUpdateBfdAdministrativeStateResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        properties: Optional[NniUpdateBfdAdministrativeStateResponseProperties]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                properties: Optional[NniUpdateBfdAdministrativeStateResponseProperties] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NniUpdateBfdAdministrativeStateResponseProperties(_Model):
        administrative_state: Optional[Union[str, BfdAdministrativeState]]
        route_type: Optional[Union[str, RouteType]]

        @overload
        def __init__(
                self, 
                *, 
                administrative_state: Optional[Union[str, BfdAdministrativeState]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NpbStaticRouteConfiguration(_Model):
        bfd_configuration: Optional[BfdConfiguration]
        ipv4_routes: Optional[list[StaticRouteProperties]]
        ipv6_routes: Optional[list[StaticRouteProperties]]

        @overload
        def __init__(
                self, 
                *, 
                bfd_configuration: Optional[BfdConfiguration] = ..., 
                ipv4_routes: Optional[list[StaticRouteProperties]] = ..., 
                ipv6_routes: Optional[list[StaticRouteProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.NpbStaticRouteConfigurationPatch(_Model):
        bfd_configuration: Optional[BfdPatchConfiguration]
        ipv4_routes: Optional[list[StaticRoutePatchProperties]]
        ipv6_routes: Optional[list[StaticRoutePatchProperties]]

        @overload
        def __init__(
                self, 
                *, 
                bfd_configuration: Optional[BfdPatchConfiguration] = ..., 
                ipv4_routes: Optional[list[StaticRoutePatchProperties]] = ..., 
                ipv6_routes: Optional[list[StaticRoutePatchProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.Operation(_Model):
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


    class azure.mgmt.managednetworkfabric.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.managednetworkfabric.models.OperationPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL_CONTROL = "fullControl"
        VALIDATE_ONLY = "validateOnly"


    class azure.mgmt.managednetworkfabric.models.OperationStatusResult(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.OperationalState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEGRADED = "Degraded"
        DOWN = "Down"
        UNKNOWN = "Unknown"
        UP = "Up"


    class azure.mgmt.managednetworkfabric.models.OptionBLayer3Configuration(Layer3IpPrefixProperties):
        bmp_configuration: Optional[NniBmpProperties]
        fabric_asn: Optional[int]
        pe_loopback_ip_address: Optional[list[str]]
        peer_asn: int
        prefix_limits: Optional[list[OptionBLayer3PrefixLimitProperties]]
        primary_ipv4_prefix: str
        primary_ipv6_prefix: str
        secondary_ipv4_prefix: str
        secondary_ipv6_prefix: str
        vlan_id: int

        @overload
        def __init__(
                self, 
                *, 
                bmp_configuration: Optional[NniBmpProperties] = ..., 
                pe_loopback_ip_address: Optional[list[str]] = ..., 
                peer_asn: int, 
                prefix_limits: Optional[list[OptionBLayer3PrefixLimitProperties]] = ..., 
                primary_ipv4_prefix: Optional[str] = ..., 
                primary_ipv6_prefix: Optional[str] = ..., 
                secondary_ipv4_prefix: Optional[str] = ..., 
                secondary_ipv6_prefix: Optional[str] = ..., 
                vlan_id: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.OptionBLayer3ConfigurationPatchProperties(Layer3IpPrefixPatchProperties):
        bmp_configuration: Optional[NniBmpPatchProperties]
        fabric_asn: Optional[int]
        pe_loopback_ip_address: Optional[list[str]]
        peer_asn: Optional[int]
        prefix_limits: Optional[list[OptionBLayer3PrefixLimitPatchProperties]]
        primary_ipv4_prefix: str
        primary_ipv6_prefix: str
        secondary_ipv4_prefix: str
        secondary_ipv6_prefix: str
        vlan_id: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                bmp_configuration: Optional[NniBmpPatchProperties] = ..., 
                pe_loopback_ip_address: Optional[list[str]] = ..., 
                peer_asn: Optional[int] = ..., 
                prefix_limits: Optional[list[OptionBLayer3PrefixLimitPatchProperties]] = ..., 
                primary_ipv4_prefix: Optional[str] = ..., 
                primary_ipv6_prefix: Optional[str] = ..., 
                secondary_ipv4_prefix: Optional[str] = ..., 
                secondary_ipv6_prefix: Optional[str] = ..., 
                vlan_id: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.OptionBLayer3PrefixLimitPatchProperties(_Model):
        maximum_routes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                maximum_routes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.OptionBLayer3PrefixLimitProperties(_Model):
        maximum_routes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                maximum_routes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.managednetworkfabric.models.PatchInfraNetwork(_Model):
        ipv4_end_addr: Optional[str]
        ipv4_gateway: Optional[str]
        ipv4_start_addr: Optional[str]
        ipv4_subnet: Optional[str]
        mtu: Optional[int]
        vlan_id: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                ipv4_end_addr: Optional[str] = ..., 
                ipv4_gateway: Optional[str] = ..., 
                ipv4_start_addr: Optional[str] = ..., 
                ipv4_subnet: Optional[str] = ..., 
                mtu: Optional[int] = ..., 
                vlan_id: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.PatchInfrastructureNetworks(_Model):
        bmc: Optional[PatchInfraNetwork]
        management: Optional[PatchInfraNetwork]
        pdu: Optional[PatchInfraNetwork]
        pxe: Optional[PatchInfraNetwork]
        storage: Optional[PatchInfraNetwork]
        storage_mgmt: Optional[PatchInfraNetwork]

        @overload
        def __init__(
                self, 
                *, 
                bmc: Optional[PatchInfraNetwork] = ..., 
                management: Optional[PatchInfraNetwork] = ..., 
                pdu: Optional[PatchInfraNetwork] = ..., 
                pxe: Optional[PatchInfraNetwork] = ..., 
                storage: Optional[PatchInfraNetwork] = ..., 
                storage_mgmt: Optional[PatchInfraNetwork] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.PatchInfrastructureServices(_Model):
        dns_servers: Optional[list[str]]
        ntp_servers: Optional[list[str]]
        platform_proxy: Optional[PatchPlatformProxy]

        @overload
        def __init__(
                self, 
                *, 
                dns_servers: Optional[list[str]] = ..., 
                ntp_servers: Optional[list[str]] = ..., 
                platform_proxy: Optional[PatchPlatformProxy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.PatchPlatformProxy(_Model):
        http_proxy: Optional[str]
        https_proxy: Optional[str]
        no_proxy: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                http_proxy: Optional[str] = ..., 
                https_proxy: Optional[str] = ..., 
                no_proxy: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.PeeringOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OPTION_A = "OptionA"
        OPTION_B = "OptionB"


    class azure.mgmt.managednetworkfabric.models.PlatformProxy(_Model):
        http_proxy: str
        https_proxy: str
        no_proxy: list[str]

        @overload
        def __init__(
                self, 
                *, 
                http_proxy: str, 
                https_proxy: str, 
                no_proxy: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.PoliceRateConfigurationProperties(_Model):
        bit_rate: Optional[BitRate]
        burst_size: Optional[BurstSize]

        @overload
        def __init__(
                self, 
                *, 
                bit_rate: Optional[BitRate] = ..., 
                burst_size: Optional[BurstSize] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.PollingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PULL = "Pull"
        PUSH = "Push"


    class azure.mgmt.managednetworkfabric.models.PortCondition(_Model):
        layer4_protocol: Union[str, Layer4Protocol]
        port_group_names: Optional[list[str]]
        port_type: Optional[Union[str, PortType]]
        ports: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                layer4_protocol: Union[str, Layer4Protocol], 
                port_group_names: Optional[list[str]] = ..., 
                port_type: Optional[Union[str, PortType]] = ..., 
                ports: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.PortConditionPatch(_Model):
        layer4_protocol: Optional[Union[str, Layer4Protocol]]
        port_group_names: Optional[list[str]]
        port_type: Optional[Union[str, PortType]]
        ports: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                layer4_protocol: Optional[Union[str, Layer4Protocol]] = ..., 
                port_group_names: Optional[list[str]] = ..., 
                port_type: Optional[Union[str, PortType]] = ..., 
                ports: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.PortGroupPatchProperties(_Model):
        name: Optional[str]
        ports: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                ports: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.PortGroupProperties(_Model):
        name: Optional[str]
        ports: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                ports: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.PortType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BIDIRECTIONAL = "Bidirectional"
        DESTINATION_PORT = "DestinationPort"
        SOURCE_PORT = "SourcePort"


    class azure.mgmt.managednetworkfabric.models.PostUpgradeProfilePatchProperties(_Model):
        max_exiting_maintenance_timeout_in_seconds: Optional[int]
        mlag_reload_delay_timeout_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                max_exiting_maintenance_timeout_in_seconds: Optional[int] = ..., 
                mlag_reload_delay_timeout_in_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.PostUpgradeProfileProperties(_Model):
        max_exiting_maintenance_timeout_in_seconds: Optional[int]
        mlag_reload_delay_timeout_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                max_exiting_maintenance_timeout_in_seconds: Optional[int] = ..., 
                mlag_reload_delay_timeout_in_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.PreUpgradeProfilePatchProperties(_Model):
        max_entering_maintenance_timeout_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                max_entering_maintenance_timeout_in_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.PreUpgradeProfileProperties(_Model):
        max_entering_maintenance_timeout_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                max_entering_maintenance_timeout_in_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.PrefixLimitPatchProperties(_Model):
        idle_time_expiry: Optional[int]
        maximum_routes: Optional[int]
        threshold: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                idle_time_expiry: Optional[int] = ..., 
                maximum_routes: Optional[int] = ..., 
                threshold: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.PrefixLimitProperties(_Model):
        idle_time_expiry: Optional[int]
        maximum_routes: Optional[int]
        threshold: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                idle_time_expiry: Optional[int] = ..., 
                maximum_routes: Optional[int] = ..., 
                threshold: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.managednetworkfabric.models.ProxyResourceBase(_Model):
        id: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.managednetworkfabric.models.QosConfigurationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.managednetworkfabric.models.QosPatchProperties(_Model):
        qos_configuration_state: Optional[Union[str, QosConfigurationState]]

        @overload
        def __init__(
                self, 
                *, 
                qos_configuration_state: Optional[Union[str, QosConfigurationState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.QosProperties(_Model):
        qos_configuration_state: Optional[Union[str, QosConfigurationState]]

        @overload
        def __init__(
                self, 
                *, 
                qos_configuration_state: Optional[Union[str, QosConfigurationState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.RebootProperties(_Model):
        reboot_type: Optional[Union[str, RebootType]]

        @overload
        def __init__(
                self, 
                *, 
                reboot_type: Optional[Union[str, RebootType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.managednetworkfabric.models.RefreshConfigurationRequestProperties(_Model):
        configuration_regeneration_type: Union[str, ConfigurationRegenerationType]
        device_types: Optional[list[Union[str, NetworkFabricRefreshDeviceTypes]]]
        generate_base_configuration: Union[str, GenerateBaseConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                configuration_regeneration_type: Union[str, ConfigurationRegenerationType], 
                device_types: Optional[list[Union[str, NetworkFabricRefreshDeviceTypes]]] = ..., 
                generate_base_configuration: Union[str, GenerateBaseConfiguration]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.managednetworkfabric.models.RoutePolicy(TrackedResource):
        id: str
        location: str
        name: str
        properties: RoutePolicyProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: RoutePolicyProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.RoutePolicyActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTINUE = "Continue"
        DENY = "Deny"
        PERMIT = "Permit"


    class azure.mgmt.managednetworkfabric.models.RoutePolicyConditionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AND = "And"
        OR = "Or"


    class azure.mgmt.managednetworkfabric.models.RoutePolicyPatch(TagsUpdate):
        properties: Optional[RoutePolicyPatchableProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RoutePolicyPatchableProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managednetworkfabric.models.RoutePolicyPatchableProperties(_Model):
        default_action: Optional[Union[str, CommunityActionTypes]]
        statements: Optional[list[RoutePolicyStatementPatchProperties]]

        @overload
        def __init__(
                self, 
                *, 
                default_action: Optional[Union[str, CommunityActionTypes]] = ..., 
                statements: Optional[list[RoutePolicyStatementPatchProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.RoutePolicyProperties(_Model):
        address_family_type: Optional[Union[str, AddressFamilyType]]
        administrative_state: Optional[Union[str, AdministrativeState]]
        annotation: Optional[str]
        configuration_state: Optional[Union[str, ConfigurationState]]
        default_action: Optional[Union[str, CommunityActionTypes]]
        last_operation: Optional[LastOperationProperties]
        network_fabric_id: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        statements: list[RoutePolicyStatementProperties]

        @overload
        def __init__(
                self, 
                *, 
                address_family_type: Optional[Union[str, AddressFamilyType]] = ..., 
                annotation: Optional[str] = ..., 
                default_action: Optional[Union[str, CommunityActionTypes]] = ..., 
                network_fabric_id: str, 
                statements: list[RoutePolicyStatementProperties]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.RoutePolicyStatementPatchProperties(AnnotationResource):
        action: StatementActionPatchProperties
        annotation: str
        condition: StatementConditionPatchProperties
        sequence_number: int

        @overload
        def __init__(
                self, 
                *, 
                action: StatementActionPatchProperties, 
                annotation: Optional[str] = ..., 
                condition: StatementConditionPatchProperties, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.RoutePolicyStatementProperties(AnnotationResource):
        action: StatementActionProperties
        annotation: str
        condition: StatementConditionProperties
        sequence_number: int

        @overload
        def __init__(
                self, 
                *, 
                action: StatementActionProperties, 
                annotation: Optional[str] = ..., 
                condition: StatementConditionProperties, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.RoutePrefixLimitPatchProperties(_Model):
        hard_limit: Optional[int]
        threshold: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                hard_limit: Optional[int] = ..., 
                threshold: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.RoutePrefixLimitProperties(_Model):
        hard_limit: Optional[int]
        threshold: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                hard_limit: Optional[int] = ..., 
                threshold: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.RouteTargetInformation(_Model):
        export_ipv4_route_targets: Optional[list[str]]
        export_ipv6_route_targets: Optional[list[str]]
        import_ipv4_route_targets: Optional[list[str]]
        import_ipv6_route_targets: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                export_ipv4_route_targets: Optional[list[str]] = ..., 
                export_ipv6_route_targets: Optional[list[str]] = ..., 
                import_ipv4_route_targets: Optional[list[str]] = ..., 
                import_ipv6_route_targets: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.RouteTargetPatchInformation(_Model):
        export_ipv4_route_targets: Optional[list[str]]
        export_ipv6_route_targets: Optional[list[str]]
        import_ipv4_route_targets: Optional[list[str]]
        import_ipv6_route_targets: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                export_ipv4_route_targets: Optional[list[str]] = ..., 
                export_ipv6_route_targets: Optional[list[str]] = ..., 
                import_ipv4_route_targets: Optional[list[str]] = ..., 
                import_ipv6_route_targets: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.RouteType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OPTION_A = "OptionA"
        STATIC = "Static"


    class azure.mgmt.managednetworkfabric.models.RuleCondition(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AND = "And"
        OR = "Or"


    class azure.mgmt.managednetworkfabric.models.RuleProperties(_Model):
        action: Union[str, Action]
        address_list: Optional[list[str]]
        condition: Optional[Union[str, RuleCondition]]
        destination_address_list: Optional[list[str]]
        header_address_list: Optional[list[HeaderAddressProperties]]
        source_address_list: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                action: Union[str, Action], 
                address_list: Optional[list[str]] = ..., 
                condition: Optional[Union[str, RuleCondition]] = ..., 
                destination_address_list: Optional[list[str]] = ..., 
                header_address_list: Optional[list[HeaderAddressProperties]] = ..., 
                source_address_list: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.SecretArchivePatchSettings(_Model):
        associated_identity: Optional[IdentitySelectorPatch]
        vault_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                associated_identity: Optional[IdentitySelectorPatch] = ..., 
                vault_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.SecretArchiveReference(_Model):
        key_vault_id: Optional[str]
        key_vault_uri: Optional[str]
        secret_name: Optional[str]
        secret_version: Optional[str]


    class azure.mgmt.managednetworkfabric.models.SecretArchiveSettings(_Model):
        associated_identity: IdentitySelector
        vault_uri: str

        @overload
        def __init__(
                self, 
                *, 
                associated_identity: IdentitySelector, 
                vault_uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.SecretRotationStatus(_Model):
        last_rotation_time: Optional[datetime]
        secret_archive_reference: Optional[SecretArchiveReference]
        secret_type: Optional[str]
        synchronization_status: Optional[Union[str, SynchronizationStatus]]


    class azure.mgmt.managednetworkfabric.models.SecretRotationSummary(_Model):
        active_password_set_count: Optional[int]


    class azure.mgmt.managednetworkfabric.models.SourceDestinationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BIDIRECTIONAL = "Bidirectional"
        DESTINATION_IP = "DestinationIP"
        SOURCE_IP = "SourceIP"


    class azure.mgmt.managednetworkfabric.models.StatementActionPatchProperties(_Model):
        action_type: Union[str, RoutePolicyActionType]
        ip_community_properties: Optional[ActionIpCommunityPatchProperties]
        ip_extended_community_properties: Optional[ActionIpExtendedCommunityPatchProperties]
        local_preference: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                action_type: Union[str, RoutePolicyActionType], 
                ip_community_properties: Optional[ActionIpCommunityPatchProperties] = ..., 
                ip_extended_community_properties: Optional[ActionIpExtendedCommunityPatchProperties] = ..., 
                local_preference: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.StatementActionProperties(_Model):
        action_type: Union[str, RoutePolicyActionType]
        ip_community_properties: Optional[ActionIpCommunityProperties]
        ip_extended_community_properties: Optional[ActionIpExtendedCommunityProperties]
        local_preference: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                action_type: Union[str, RoutePolicyActionType], 
                ip_community_properties: Optional[ActionIpCommunityProperties] = ..., 
                ip_extended_community_properties: Optional[ActionIpExtendedCommunityProperties] = ..., 
                local_preference: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.StatementConditionPatchProperties(_Model):
        ip_community_ids: Optional[list[str]]
        ip_extended_community_ids: Optional[list[str]]
        ip_prefix_id: Optional[str]
        type: Optional[Union[str, RoutePolicyConditionType]]

        @overload
        def __init__(
                self, 
                *, 
                ip_community_ids: Optional[list[str]] = ..., 
                ip_extended_community_ids: Optional[list[str]] = ..., 
                ip_prefix_id: Optional[str] = ..., 
                type: Optional[Union[str, RoutePolicyConditionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.StatementConditionProperties(_Model):
        ip_community_ids: Optional[list[str]]
        ip_extended_community_ids: Optional[list[str]]
        ip_prefix_id: Optional[str]
        type: Optional[Union[str, RoutePolicyConditionType]]

        @overload
        def __init__(
                self, 
                *, 
                ip_community_ids: Optional[list[str]] = ..., 
                ip_extended_community_ids: Optional[list[str]] = ..., 
                ip_prefix_id: Optional[str] = ..., 
                type: Optional[Union[str, RoutePolicyConditionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.StaticRouteConfiguration(_Model):
        bfd_configuration: Optional[BfdConfiguration]
        extension: Optional[Union[str, Extension]]
        ipv4_routes: Optional[list[StaticRouteProperties]]
        ipv6_routes: Optional[list[StaticRouteProperties]]

        @overload
        def __init__(
                self, 
                *, 
                bfd_configuration: Optional[BfdConfiguration] = ..., 
                extension: Optional[Union[str, Extension]] = ..., 
                ipv4_routes: Optional[list[StaticRouteProperties]] = ..., 
                ipv6_routes: Optional[list[StaticRouteProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.StaticRoutePatchConfiguration(_Model):
        bfd_configuration: Optional[BfdPatchConfiguration]
        ipv4_routes: Optional[list[StaticRoutePatchProperties]]
        ipv6_routes: Optional[list[StaticRoutePatchProperties]]

        @overload
        def __init__(
                self, 
                *, 
                bfd_configuration: Optional[BfdPatchConfiguration] = ..., 
                ipv4_routes: Optional[list[StaticRoutePatchProperties]] = ..., 
                ipv6_routes: Optional[list[StaticRoutePatchProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.StaticRoutePatchProperties(_Model):
        next_hop: list[str]
        prefix: str

        @overload
        def __init__(
                self, 
                *, 
                next_hop: list[str], 
                prefix: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.StaticRoutePolicy(_Model):
        export_route_policy: Optional[L3ExportRoutePolicy]

        @overload
        def __init__(
                self, 
                *, 
                export_route_policy: Optional[L3ExportRoutePolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.StaticRoutePolicyPatch(_Model):
        export_route_policy: Optional[L3ExportRoutePolicyPatch]

        @overload
        def __init__(
                self, 
                *, 
                export_route_policy: Optional[L3ExportRoutePolicyPatch] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.StaticRouteProperties(_Model):
        next_hop: list[str]
        prefix: str

        @overload
        def __init__(
                self, 
                *, 
                next_hop: list[str], 
                prefix: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.StationConfigurationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.managednetworkfabric.models.StationConnectionMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        PASSIVE = "Passive"


    class azure.mgmt.managednetworkfabric.models.StationConnectionPatchProperties(_Model):
        keepalive_idle_time: Optional[int]
        probe_count: Optional[int]
        probe_interval: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                keepalive_idle_time: Optional[int] = ..., 
                probe_count: Optional[int] = ..., 
                probe_interval: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.StationConnectionProperties(_Model):
        keepalive_idle_time: Optional[int]
        probe_count: Optional[int]
        probe_interval: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                keepalive_idle_time: Optional[int] = ..., 
                probe_count: Optional[int] = ..., 
                probe_interval: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.StorageAccountConfiguration(_Model):
        storage_account_id: Optional[str]
        storage_account_identity: Optional[IdentitySelector]

        @overload
        def __init__(
                self, 
                *, 
                storage_account_id: Optional[str] = ..., 
                storage_account_identity: Optional[IdentitySelector] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.StorageAccountPatchConfiguration(_Model):
        storage_account_id: Optional[str]
        storage_account_identity: Optional[IdentitySelectorPatch]

        @overload
        def __init__(
                self, 
                *, 
                storage_account_id: Optional[str] = ..., 
                storage_account_identity: Optional[IdentitySelectorPatch] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.SupportedConnectorProperties(_Model):
        connector_type: Optional[str]
        max_speed_in_mbps: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                connector_type: Optional[str] = ..., 
                max_speed_in_mbps: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.SupportedVersionProperties(_Model):
        is_default: Optional[Union[str, BooleanEnumProperty]]
        vendor_firmware_version: Optional[str]
        vendor_os_version: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_default: Optional[Union[str, BooleanEnumProperty]] = ..., 
                vendor_firmware_version: Optional[str] = ..., 
                vendor_os_version: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.SynchronizationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IN_SYNC = "InSync"
        OUT_OF_SYNC = "OutOfSync"
        SYNCHRONIZING = "Synchronizing"


    class azure.mgmt.managednetworkfabric.models.SystemData(_Model):
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


    class azure.mgmt.managednetworkfabric.models.TagsUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.TapRuleActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNT = "Count"
        DROP = "Drop"
        GOTO = "Goto"
        LOG = "Log"
        MIRROR = "Mirror"
        REDIRECT = "Redirect"
        REPLICATE = "Replicate"


    class azure.mgmt.managednetworkfabric.models.TerminalServerConfiguration(_Model):
        network_device_id: Optional[str]
        password: str
        primary_ipv4_prefix: str
        primary_ipv6_prefix: Optional[str]
        secondary_ipv4_prefix: str
        secondary_ipv6_prefix: Optional[str]
        secret_rotation_status: Optional[list[SecretRotationStatus]]
        serial_number: Optional[str]
        username: str

        @overload
        def __init__(
                self, 
                *, 
                password: str, 
                primary_ipv4_prefix: str, 
                primary_ipv6_prefix: Optional[str] = ..., 
                secondary_ipv4_prefix: str, 
                secondary_ipv6_prefix: Optional[str] = ..., 
                serial_number: Optional[str] = ..., 
                username: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.TerminalServerPatchConfiguration(_Model):
        password: Optional[str]
        primary_ipv4_prefix: Optional[str]
        primary_ipv6_prefix: Optional[str]
        secondary_ipv4_prefix: Optional[str]
        secondary_ipv6_prefix: Optional[str]
        serial_number: Optional[str]
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                password: Optional[str] = ..., 
                primary_ipv4_prefix: Optional[str] = ..., 
                primary_ipv6_prefix: Optional[str] = ..., 
                secondary_ipv4_prefix: Optional[str] = ..., 
                secondary_ipv6_prefix: Optional[str] = ..., 
                serial_number: Optional[str] = ..., 
                username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.TrackedResource(Resource):
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


    class azure.mgmt.managednetworkfabric.models.UniqueRouteDistinguisherConfigurationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.managednetworkfabric.models.UniqueRouteDistinguisherPatchProperties(_Model):
        nni_derived_unique_rd_configuration_state: Optional[Union[str, NNIDerivedUniqueRouteDistinguisherConfigurationState]]
        unique_rd_configuration_state: Optional[Union[str, UniqueRouteDistinguisherConfigurationState]]

        @overload
        def __init__(
                self, 
                *, 
                nni_derived_unique_rd_configuration_state: Optional[Union[str, NNIDerivedUniqueRouteDistinguisherConfigurationState]] = ..., 
                unique_rd_configuration_state: Optional[Union[str, UniqueRouteDistinguisherConfigurationState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.UniqueRouteDistinguisherProperties(_Model):
        nni_derived_unique_rd_configuration_state: Optional[Union[str, NNIDerivedUniqueRouteDistinguisherConfigurationState]]
        unique_rd_configuration_state: Optional[Union[str, UniqueRouteDistinguisherConfigurationState]]
        unique_rds: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                nni_derived_unique_rd_configuration_state: Optional[Union[str, NNIDerivedUniqueRouteDistinguisherConfigurationState]] = ..., 
                unique_rd_configuration_state: Optional[Union[str, UniqueRouteDistinguisherConfigurationState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.UpdateAdministrativeState(EnableDisableOnResources):
        resource_ids: list[str]
        state: Optional[Union[str, EnableDisableState]]

        @overload
        def __init__(
                self, 
                *, 
                resource_ids: Optional[list[str]] = ..., 
                state: Optional[Union[str, EnableDisableState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.UpdateAdministrativeStateResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        properties: Optional[UpdateAdministrativeStateResponseProperties]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                properties: Optional[UpdateAdministrativeStateResponseProperties] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.UpdateAdministrativeStateResponseProperties(_Model):
        failed_resources: Optional[list[str]]
        successful_resources: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                failed_resources: Optional[list[str]] = ..., 
                successful_resources: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.UpdateDeviceAdministrativeState(EnableDisableOnResources):
        resource_ids: list[str]
        state: Optional[Union[str, DeviceAdministrativeState]]

        @overload
        def __init__(
                self, 
                *, 
                resource_ids: Optional[list[str]] = ..., 
                state: Optional[Union[str, DeviceAdministrativeState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.UpdateVersion(_Model):
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.UpgradeNetworkFabricProperties(UpdateVersion):
        action: Optional[Union[str, NetworkFabricUpgradeAction]]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, NetworkFabricUpgradeAction]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.UpgradeProfileProperties(_Model):
        post_upgrade_profile: Optional[PostUpgradeProfileProperties]
        pre_upgrade_profile: Optional[PreUpgradeProfileProperties]

        @overload
        def __init__(
                self, 
                *, 
                post_upgrade_profile: Optional[PostUpgradeProfileProperties] = ..., 
                pre_upgrade_profile: Optional[PreUpgradeProfileProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.UpgradeProfilePropertiesPatchProperties(_Model):
        post_upgrade_profile: Optional[PostUpgradeProfilePatchProperties]
        pre_upgrade_profile: Optional[PreUpgradeProfilePatchProperties]

        @overload
        def __init__(
                self, 
                *, 
                post_upgrade_profile: Optional[PostUpgradeProfilePatchProperties] = ..., 
                pre_upgrade_profile: Optional[PreUpgradeProfilePatchProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.managednetworkfabric.models.V4OverV6BgpSessionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.managednetworkfabric.models.V6OverV4BgpSessionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.managednetworkfabric.models.ValidateAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CABLING = "Cabling"
        CONFIGURATION = "Configuration"
        CONNECTIVITY = "Connectivity"


    class azure.mgmt.managednetworkfabric.models.ValidateConfigurationProperties(_Model):
        validate_action: Optional[Union[str, ValidateAction]]

        @overload
        def __init__(
                self, 
                *, 
                validate_action: Optional[Union[str, ValidateAction]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ValidateConfigurationResponseProperties(_Model):
        configuration_state: Optional[Union[str, ConfigurationState]]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ValidateConfigurationResponseV2(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        properties: Optional[ValidateConfigurationResponseProperties]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                properties: Optional[ValidateConfigurationResponseProperties] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ViewDeviceConfigurationOperationResponse(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        properties: Optional[ViewDeviceConfigurationResponseProperties]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                properties: Optional[ViewDeviceConfigurationResponseProperties] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.ViewDeviceConfigurationResponseProperties(_Model):
        device_configuration_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                device_configuration_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.VlanGroupPatchProperties(_Model):
        name: Optional[str]
        vlans: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                vlans: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.VlanGroupProperties(_Model):
        name: Optional[str]
        vlans: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                vlans: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.VlanMatchCondition(_Model):
        inner_vlans: Optional[list[str]]
        vlan_group_names: Optional[list[str]]
        vlans: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                inner_vlans: Optional[list[str]] = ..., 
                vlan_group_names: Optional[list[str]] = ..., 
                vlans: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.VlanMatchConditionPatch(_Model):
        inner_vlans: Optional[list[str]]
        vlan_group_names: Optional[list[str]]
        vlans: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                inner_vlans: Optional[list[str]] = ..., 
                vlan_group_names: Optional[list[str]] = ..., 
                vlans: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.VmProfile(_Model):
        vm_sku_name: str

        @overload
        def __init__(
                self, 
                *, 
                vm_sku_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.VpnConfigurationPatchableProperties(_Model):
        network_to_network_interconnect_id: Optional[str]
        option_a_properties: Optional[VpnOptionAPatchProperties]
        option_b_properties: Optional[VpnOptionBPatchProperties]
        peering_option: Optional[Union[str, PeeringOption]]

        @overload
        def __init__(
                self, 
                *, 
                network_to_network_interconnect_id: Optional[str] = ..., 
                option_a_properties: Optional[VpnOptionAPatchProperties] = ..., 
                option_b_properties: Optional[VpnOptionBPatchProperties] = ..., 
                peering_option: Optional[Union[str, PeeringOption]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.VpnConfigurationProperties(_Model):
        administrative_state: Optional[Union[str, AdministrativeState]]
        network_to_network_interconnect_id: Optional[str]
        option_a_properties: Optional[VpnOptionAProperties]
        option_b_properties: Optional[VpnOptionBProperties]
        peering_option: Union[str, PeeringOption]

        @overload
        def __init__(
                self, 
                *, 
                network_to_network_interconnect_id: Optional[str] = ..., 
                option_a_properties: Optional[VpnOptionAProperties] = ..., 
                option_b_properties: Optional[VpnOptionBProperties] = ..., 
                peering_option: Union[str, PeeringOption]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.VpnOptionAPatchProperties(Layer3IpPrefixPatchProperties):
        bfd_configuration: Optional[BfdPatchConfiguration]
        mtu: Optional[int]
        peer_asn: Optional[int]
        primary_ipv4_prefix: str
        primary_ipv6_prefix: str
        secondary_ipv4_prefix: str
        secondary_ipv6_prefix: str
        vlan_id: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                bfd_configuration: Optional[BfdPatchConfiguration] = ..., 
                mtu: Optional[int] = ..., 
                peer_asn: Optional[int] = ..., 
                primary_ipv4_prefix: Optional[str] = ..., 
                primary_ipv6_prefix: Optional[str] = ..., 
                secondary_ipv4_prefix: Optional[str] = ..., 
                secondary_ipv6_prefix: Optional[str] = ..., 
                vlan_id: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.VpnOptionAProperties(Layer3IpPrefixProperties):
        bfd_configuration: Optional[BfdConfiguration]
        mtu: Optional[int]
        peer_asn: int
        primary_ipv4_prefix: str
        primary_ipv6_prefix: str
        secondary_ipv4_prefix: str
        secondary_ipv6_prefix: str
        vlan_id: int

        @overload
        def __init__(
                self, 
                *, 
                bfd_configuration: Optional[BfdConfiguration] = ..., 
                mtu: Optional[int] = ..., 
                peer_asn: int, 
                primary_ipv4_prefix: Optional[str] = ..., 
                primary_ipv6_prefix: Optional[str] = ..., 
                secondary_ipv4_prefix: Optional[str] = ..., 
                secondary_ipv6_prefix: Optional[str] = ..., 
                vlan_id: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.VpnOptionBPatchProperties(_Model):
        export_route_targets: Optional[list[str]]
        import_route_targets: Optional[list[str]]
        route_targets: Optional[RouteTargetPatchInformation]

        @overload
        def __init__(
                self, 
                *, 
                export_route_targets: Optional[list[str]] = ..., 
                import_route_targets: Optional[list[str]] = ..., 
                route_targets: Optional[RouteTargetPatchInformation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managednetworkfabric.models.VpnOptionBProperties(_Model):
        export_route_targets: Optional[list[str]]
        import_route_targets: Optional[list[str]]
        route_targets: Optional[RouteTargetInformation]

        @overload
        def __init__(
                self, 
                *, 
                export_route_targets: Optional[list[str]] = ..., 
                import_route_targets: Optional[list[str]] = ..., 
                route_targets: Optional[RouteTargetInformation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
            ) -> None: ...

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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessControlList]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_resync(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
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
                body: IO[bytes], 
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
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'access_control_list_name', 'accept']}, api_versions_list=['2026-01-15-preview'])
        def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                **kwargs: Any
            ) -> LROPoller[ValidateConfigurationResponseV2]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                access_control_list_name: str, 
                **kwargs: Any
            ) -> AccessControlList: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AccessControlList]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[AccessControlList]: ...


    class azure.mgmt.managednetworkfabric.operations.EdgeConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                edge_connector_name: str, 
                body: EdgeConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeConnector]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                edge_connector_name: str, 
                body: EdgeConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeConnector]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                edge_connector_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeConnector]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_connector_name']}, api_versions_list=['2026-01-15-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                edge_connector_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                edge_connector_name: str, 
                body: EdgeConnectorPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeConnector]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                edge_connector_name: str, 
                body: EdgeConnectorPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeConnector]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                edge_connector_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeConnector]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_connector_name', 'accept']}, api_versions_list=['2026-01-15-preview'])
        def get(
                self, 
                resource_group_name: str, 
                edge_connector_name: str, 
                **kwargs: Any
            ) -> EdgeConnector: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-01-15-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EdgeConnector]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-01-15-preview'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[EdgeConnector]: ...


    class azure.mgmt.managednetworkfabric.operations.ExternalNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                body: IO[bytes], 
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
                body: IO[bytes], 
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
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

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
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: ExternalNetworkUpdateBfdAdministrativeStateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExternalNetworkUpdateBfdAdministrativeStateResponse]: ...

        @overload
        def begin_update_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: ExternalNetworkUpdateBfdAdministrativeStateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExternalNetworkUpdateBfdAdministrativeStateResponse]: ...

        @overload
        def begin_update_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExternalNetworkUpdateBfdAdministrativeStateResponse]: ...

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
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

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
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_static_route_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                external_network_name: str, 
                **kwargs: Any
            ) -> ExternalNetwork: ...

        @distributed_trace
        def list_by_l3_isolation_domain(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ExternalNetwork]: ...


    class azure.mgmt.managednetworkfabric.operations.FabricsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: Fabric, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Fabric]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: Fabric, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Fabric]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Fabric]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fabric_name']}, api_versions_list=['2026-01-15-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: FabricPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Fabric]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: FabricPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Fabric]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Fabric]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fabric_name', 'accept']}, api_versions_list=['2026-01-15-preview'])
        def get(
                self, 
                resource_group_name: str, 
                fabric_name: str, 
                **kwargs: Any
            ) -> Fabric: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-01-15-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Fabric]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-01-15-preview'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Fabric]: ...


    class azure.mgmt.managednetworkfabric.operations.InternalNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                body: IO[bytes], 
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
                body: IO[bytes], 
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
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

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
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: InternalNetworkUpdateBfdAdministrativeStateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InternalNetworkUpdateBfdAdministrativeStateResponse]: ...

        @overload
        def begin_update_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: InternalNetworkUpdateBfdAdministrativeStateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InternalNetworkUpdateBfdAdministrativeStateResponse]: ...

        @overload
        def begin_update_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InternalNetworkUpdateBfdAdministrativeStateResponse]: ...

        @overload
        def begin_update_bgp_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: InternalNetworkUpdateBgpAdministrativeStateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InternalNetworkUpdateBgpAdministrativeStateResponse]: ...

        @overload
        def begin_update_bgp_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: InternalNetworkUpdateBgpAdministrativeStateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InternalNetworkUpdateBgpAdministrativeStateResponse]: ...

        @overload
        def begin_update_bgp_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InternalNetworkUpdateBgpAdministrativeStateResponse]: ...

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
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

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
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_static_route_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                internal_network_name: str, 
                **kwargs: Any
            ) -> InternalNetwork: ...

        @distributed_trace
        def list_by_l3_isolation_domain(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                **kwargs: Any
            ) -> ItemPaged[InternalNetwork]: ...


    class azure.mgmt.managednetworkfabric.operations.InternetGatewayRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InternetGatewayRule]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                internet_gateway_rule_name: str, 
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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InternetGatewayRule]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                internet_gateway_rule_name: str, 
                **kwargs: Any
            ) -> InternetGatewayRule: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[InternetGatewayRule]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[InternetGatewayRule]: ...


    class azure.mgmt.managednetworkfabric.operations.InternetGatewaysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InternetGateway]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                internet_gateway_name: str, 
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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InternetGateway]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                internet_gateway_name: str, 
                **kwargs: Any
            ) -> InternetGateway: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[InternetGateway]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[InternetGateway]: ...


    class azure.mgmt.managednetworkfabric.operations.IpCommunitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IpCommunity]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                ip_community_name: str, 
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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IpCommunity]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                ip_community_name: str, 
                **kwargs: Any
            ) -> IpCommunity: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[IpCommunity]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[IpCommunity]: ...


    class azure.mgmt.managednetworkfabric.operations.IpExtendedCommunitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IpExtendedCommunity]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                ip_extended_community_name: str, 
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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IpExtendedCommunity]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                ip_extended_community_name: str, 
                **kwargs: Any
            ) -> IpExtendedCommunity: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[IpExtendedCommunity]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[IpExtendedCommunity]: ...


    class azure.mgmt.managednetworkfabric.operations.IpPrefixesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IpPrefix]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                ip_prefix_name: str, 
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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IpPrefix]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                ip_prefix_name: str, 
                **kwargs: Any
            ) -> IpPrefix: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[IpPrefix]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[IpPrefix]: ...


    class azure.mgmt.managednetworkfabric.operations.L2IsolationDomainsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_commit_configuration(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[L2IsolationDomain]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
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
                body: IO[bytes], 
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
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'l2_isolation_domain_name', 'accept']}, api_versions_list=['2026-01-15-preview'])
        def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                **kwargs: Any
            ) -> LROPoller[ValidateConfigurationResponseV2]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                l2_isolation_domain_name: str, 
                **kwargs: Any
            ) -> L2IsolationDomain: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[L2IsolationDomain]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[L2IsolationDomain]: ...


    class azure.mgmt.managednetworkfabric.operations.L3IsolationDomainsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_commit_configuration(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[L3IsolationDomain]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
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
                body: IO[bytes], 
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
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'l3_isolation_domain_name', 'accept']}, api_versions_list=['2026-01-15-preview'])
        def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                **kwargs: Any
            ) -> LROPoller[ValidateConfigurationResponseV2]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                l3_isolation_domain_name: str, 
                **kwargs: Any
            ) -> L3IsolationDomain: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[L3IsolationDomain]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[L3IsolationDomain]: ...


    class azure.mgmt.managednetworkfabric.operations.NeighborGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NeighborGroup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                neighbor_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'neighbor_group_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def begin_resync(
                self, 
                resource_group_name: str, 
                neighbor_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[NeighborGroupResyncResponse]: ...

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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NeighborGroup]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                neighbor_group_name: str, 
                **kwargs: Any
            ) -> NeighborGroup: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NeighborGroup]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[NeighborGroup]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkBootstrapDevicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: NetworkBootstrapDevice, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkBootstrapDevice]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: NetworkBootstrapDevice, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkBootstrapDevice]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkBootstrapDevice]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_bootstrap_device_name']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_bootstrap_device_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def begin_reboot(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                **kwargs: Any
            ) -> LROPoller[NetworkBootstrapDeviceRebootResponse]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_bootstrap_device_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def begin_refresh_configuration(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                **kwargs: Any
            ) -> LROPoller[NetworkBootstrapDeviceRefreshConfigurationResponse]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_bootstrap_device_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def begin_resync_passwords(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                **kwargs: Any
            ) -> LROPoller[NetworkBootstrapDeviceResyncPasswordsResponse]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: NetworkBootstrapDevicePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkBootstrapDevice]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: NetworkBootstrapDevicePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkBootstrapDevice]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkBootstrapDevice]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: UpdateDeviceAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkBootstrapDeviceUpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: UpdateDeviceAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkBootstrapDeviceUpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkBootstrapDeviceUpdateAdministrativeStateResponse]: ...

        @overload
        def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: UpdateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkBootstrapDeviceUpgradeResponse]: ...

        @overload
        def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: UpdateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkBootstrapDeviceUpgradeResponse]: ...

        @overload
        def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkBootstrapDeviceUpgradeResponse]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_bootstrap_device_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def get(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                **kwargs: Any
            ) -> NetworkBootstrapDevice: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkBootstrapDevice]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[NetworkBootstrapDevice]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkBootstrapInterfacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                network_bootstrap_interface_name: str, 
                body: NetworkBootstrapInterface, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkBootstrapInterface]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                network_bootstrap_interface_name: str, 
                body: NetworkBootstrapInterface, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkBootstrapInterface]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                network_bootstrap_interface_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkBootstrapInterface]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_bootstrap_device_name', 'network_bootstrap_interface_name']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                network_bootstrap_interface_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                network_bootstrap_interface_name: str, 
                body: NetworkBootstrapInterfacePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkBootstrapInterface]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                network_bootstrap_interface_name: str, 
                body: NetworkBootstrapInterfacePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkBootstrapInterface]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                network_bootstrap_interface_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkBootstrapInterface]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                network_bootstrap_interface_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                network_bootstrap_interface_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                network_bootstrap_interface_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_bootstrap_device_name', 'network_bootstrap_interface_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def get(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                network_bootstrap_interface_name: str, 
                **kwargs: Any
            ) -> NetworkBootstrapInterface: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_bootstrap_device_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def list_by_network_bootstrap_device(
                self, 
                resource_group_name: str, 
                network_bootstrap_device_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkBootstrapInterface]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkDeviceSkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                network_device_sku_name: str, 
                **kwargs: Any
            ) -> NetworkDeviceSku: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[NetworkDeviceSku]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkDevicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkDevice]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
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
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_reboot(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: RebootProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_reboot(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_device_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def begin_refresh_configuration(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                **kwargs: Any
            ) -> LROPoller[NetworkDeviceRefreshConfigurationResponse]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_device_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def begin_resync_certificates(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                **kwargs: Any
            ) -> LROPoller[NetworkFabricResyncCertificatesResponse]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_device_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def begin_resync_passwords(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                **kwargs: Any
            ) -> LROPoller[NetworkDeviceResyncPasswordsResponse]: ...

        @overload
        def begin_run_ro_command(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: DeviceRoCommand, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForDeviceROCommandsOperationStatusResult]: ...

        @overload
        def begin_run_ro_command(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: DeviceRoCommand, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForDeviceROCommandsOperationStatusResult]: ...

        @overload
        def begin_run_ro_command(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForDeviceROCommandsOperationStatusResult]: ...

        @overload
        def begin_run_rw_command(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: DeviceRwCommand, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkDeviceRunRwCommandResponse]: ...

        @overload
        def begin_run_rw_command(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: DeviceRwCommand, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkDeviceRunRwCommandResponse]: ...

        @overload
        def begin_run_rw_command(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkDeviceRunRwCommandResponse]: ...

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
                body: IO[bytes], 
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
            ) -> LROPoller[NetworkDeviceUpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: UpdateDeviceAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkDeviceUpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkDeviceUpdateAdministrativeStateResponse]: ...

        @overload
        def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: NetworkDeviceUpgradeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkDeviceUpgradeResponse]: ...

        @overload
        def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: NetworkDeviceUpgradeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkDeviceUpgradeResponse]: ...

        @overload
        def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkDeviceUpgradeResponse]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                **kwargs: Any
            ) -> NetworkDevice: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkDevice]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[NetworkDevice]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkFabricControllersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkFabricController]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_fabric_controller_name: str, 
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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkFabricController]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                network_fabric_controller_name: str, 
                **kwargs: Any
            ) -> NetworkFabricController: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkFabricController]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[NetworkFabricController]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkFabricSkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                network_fabric_sku_name: str, 
                **kwargs: Any
            ) -> NetworkFabricSku: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[NetworkFabricSku]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkFabricsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_fabric_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def begin_arm_configuration_diff(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> LROPoller[ArmConfigurationDiffOperationResponse]: ...

        @overload
        def begin_commit_batch_status(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: CommitBatchStatusRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommitBatchStatusOperationResponse]: ...

        @overload
        def begin_commit_batch_status(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: CommitBatchStatusRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommitBatchStatusOperationResponse]: ...

        @overload
        def begin_commit_batch_status(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommitBatchStatusOperationResponse]: ...

        @overload
        def begin_commit_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: Optional[CommitConfigurationRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommitConfigurationResponse]: ...

        @overload
        def begin_commit_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: Optional[CommitConfigurationRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommitConfigurationResponse]: ...

        @overload
        def begin_commit_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommitConfigurationResponse]: ...

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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkFabric]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_fabric_name']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_fabric_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def begin_deprovision(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_discard_commit_batch(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: DiscardCommitBatchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiscardCommitBatchOperationResponse]: ...

        @overload
        def begin_discard_commit_batch(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: DiscardCommitBatchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiscardCommitBatchOperationResponse]: ...

        @overload
        def begin_discard_commit_batch(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiscardCommitBatchOperationResponse]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_fabric_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def begin_get_topology(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> LROPoller[GetTopologyResponse]: ...

        @overload
        def begin_lock_fabric(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: NetworkFabricLockRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_lock_fabric(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: NetworkFabricLockRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_lock_fabric(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_fabric_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def begin_provision(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_refresh_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: Optional[RefreshConfigurationRequestProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_refresh_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: Optional[RefreshConfigurationRequestProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_refresh_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_fabric_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def begin_resync_certificates(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> LROPoller[NetworkFabricResyncCertificatesResponse]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_fabric_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def begin_resync_passwords(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> LROPoller[NetworkFabricResyncPasswordsResponse]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_fabric_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def begin_rotate_certificates(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> LROPoller[NetworkFabricRotateCertificatesResponse]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_fabric_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def begin_rotate_passwords(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> LROPoller[NetworkFabricRotatePasswordsResponse]: ...

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
                body: IO[bytes], 
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
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_infra_management_bfd_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_infra_management_bfd_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_workload_management_bfd_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_workload_management_bfd_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_workload_management_bfd_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: UpgradeNetworkFabricProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: UpgradeNetworkFabricProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_upgrade(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: ValidateConfigurationProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ValidateConfigurationResponseV2]: ...

        @overload
        def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: ValidateConfigurationProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ValidateConfigurationResponseV2]: ...

        @overload
        def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ValidateConfigurationResponseV2]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_fabric_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def begin_view_device_configuration(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> LROPoller[ViewDeviceConfigurationOperationResponse]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_fabric_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def get(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> NetworkFabric: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkFabric]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[NetworkFabric]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkInterfacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                body: IO[bytes], 
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
                body: IO[bytes], 
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
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

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
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                network_interface_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                network_interface_name: str, 
                **kwargs: Any
            ) -> NetworkInterface: ...

        @distributed_trace
        def list_by_network_device(
                self, 
                resource_group_name: str, 
                network_device_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkInterface]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkMonitorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_monitor_name: str, 
                body: NetworkMonitor, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkMonitor]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_monitor_name: str, 
                body: NetworkMonitor, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkMonitor]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                network_monitor_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkMonitor]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-06-15-preview', params_added_on={'2024-06-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'network_monitor_name']}, api_versions_list=['2024-06-15-preview', '2025-07-15', '2026-01-15-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_monitor_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_monitor_name: str, 
                body: NetworkMonitorPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkMonitor]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_monitor_name: str, 
                body: NetworkMonitorPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkMonitor]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_monitor_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkMonitor]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_monitor_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_monitor_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_monitor_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForDeviceUpdate]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-06-15-preview', params_added_on={'2024-06-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'network_monitor_name', 'accept']}, api_versions_list=['2024-06-15-preview', '2025-07-15', '2026-01-15-preview'])
        def get(
                self, 
                resource_group_name: str, 
                network_monitor_name: str, 
                **kwargs: Any
            ) -> NetworkMonitor: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-06-15-preview', params_added_on={'2024-06-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2024-06-15-preview', '2025-07-15', '2026-01-15-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkMonitor]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-06-15-preview', params_added_on={'2024-06-15-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2024-06-15-preview', '2025-07-15', '2026-01-15-preview'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[NetworkMonitor]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkPacketBrokersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkPacketBroker]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_packet_broker_name: str, 
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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkPacketBroker]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                network_packet_broker_name: str, 
                **kwargs: Any
            ) -> NetworkPacketBroker: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkPacketBroker]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[NetworkPacketBroker]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkRacksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkRack]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_rack_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_rack_name: str, 
                body: NetworkRackPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkRack]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_rack_name: str, 
                body: NetworkRackPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkRack]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_rack_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkRack]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                network_rack_name: str, 
                **kwargs: Any
            ) -> NetworkRack: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkRack]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[NetworkRack]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkTapRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkTapRule]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_tap_rule_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def begin_resync(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                **kwargs: Any
            ) -> LROPoller[NetworkTapRuleResyncResponse]: ...

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
                body: IO[bytes], 
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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommonPostActionResponseForStateUpdate]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'network_tap_rule_name', 'accept']}, api_versions_list=['2026-01-15-preview'])
        def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                **kwargs: Any
            ) -> LROPoller[ValidateConfigurationResponseV2]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                network_tap_rule_name: str, 
                **kwargs: Any
            ) -> NetworkTapRule: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkTapRule]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[NetworkTapRule]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkTapsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkTap]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-15', params_added_on={'2025-07-15': ['api_version', 'subscription_id', 'resource_group_name', 'network_tap_name', 'accept']}, api_versions_list=['2025-07-15', '2026-01-15-preview'])
        def begin_resync(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                **kwargs: Any
            ) -> LROPoller[NetworkTapResyncResponse]: ...

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
                body: IO[bytes], 
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
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                network_tap_name: str, 
                **kwargs: Any
            ) -> NetworkTap: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkTap]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[NetworkTap]: ...


    class azure.mgmt.managednetworkfabric.operations.NetworkToNetworkInterconnectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                body: IO[bytes], 
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
                body: IO[bytes], 
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
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

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
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: NniUpdateBfdAdministrativeStateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NniUpdateBfdAdministrativeStateResponse]: ...

        @overload
        def begin_update_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: NniUpdateBfdAdministrativeStateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NniUpdateBfdAdministrativeStateResponse]: ...

        @overload
        def begin_update_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NniUpdateBfdAdministrativeStateResponse]: ...

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
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

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
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_npb_static_route_bfd_administrative_state(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                network_to_network_interconnect_name: str, 
                **kwargs: Any
            ) -> NetworkToNetworkInterconnect: ...

        @distributed_trace
        def list_by_network_fabric(
                self, 
                resource_group_name: str, 
                network_fabric_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkToNetworkInterconnect]: ...


    class azure.mgmt.managednetworkfabric.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.managednetworkfabric.operations.RoutePoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_commit_configuration(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
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
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RoutePolicy]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
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
                body: IO[bytes], 
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
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                body: UpdateAdministrativeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @overload
        def begin_update_administrative_state(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UpdateAdministrativeStateResponse]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'route_policy_name', 'accept']}, api_versions_list=['2026-01-15-preview'])
        def begin_validate_configuration(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                **kwargs: Any
            ) -> LROPoller[ValidateConfigurationResponseV2]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                route_policy_name: str, 
                **kwargs: Any
            ) -> RoutePolicy: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RoutePolicy]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[RoutePolicy]: ...


namespace azure.mgmt.managednetworkfabric.types

    class azure.mgmt.managednetworkfabric.types.AccessControlList(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[AccessControlListProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: AccessControlListProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managednetworkfabric.types.AccessControlListAction(TypedDict, total=False):
        key "counterName": str
        key "policeRateConfiguration": ForwardRef('PoliceRateConfigurationProperties', module='types')
        key "remarkComment": str
        key "type": Union[str, AclActionType]
        counterName: str
        policeRateConfiguration: PoliceRateConfigurationProperties
        remarkComment: str
        type: Union[str, AclActionType]


    class azure.mgmt.managednetworkfabric.types.AccessControlListActionPatch(TypedDict, total=False):
        key "counterName": str
        key "policeRateConfiguration": ForwardRef('PoliceRateConfigurationProperties', module='types')
        key "remarkComment": str
        key "type": Union[str, AclActionType]
        counterName: str
        policeRateConfiguration: PoliceRateConfigurationProperties
        remarkComment: str
        type: Union[str, AclActionType]


    class azure.mgmt.managednetworkfabric.types.AccessControlListMatchCondition(CommonMatchConditions):
        key "icmpConfiguration": ForwardRef('IcmpConfigurationProperties', module='types')
        key "ipCondition": ForwardRef('IpMatchCondition', module='types')
        key "portCondition": ForwardRef('AccessControlListPortCondition', module='types')
        key "vlanMatchCondition": ForwardRef('VlanMatchCondition', module='types')
        dscpMarkings: list[str]
        etherTypes: list[str]
        fragments: list[str]
        icmpConfiguration: IcmpConfigurationProperties
        ipCondition: IpMatchCondition
        ipLengths: list[str]
        portCondition: AccessControlListPortCondition
        protocolNeighbors: list[str]
        protocolTypes: list[str]
        ttlValues: list[str]
        vlanMatchCondition: VlanMatchCondition


    class azure.mgmt.managednetworkfabric.types.AccessControlListMatchConditionPatch(CommonMatchConditionsPatch):
        key "icmpConfiguration": ForwardRef('IcmpConfigurationPatchProperties', module='types')
        key "ipCondition": ForwardRef('IpMatchConditionPatch', module='types')
        key "portCondition": ForwardRef('AccessControlListPortConditionPatch', module='types')
        key "vlanMatchCondition": ForwardRef('VlanMatchConditionPatch', module='types')
        dscpMarkings: list[str]
        etherTypes: list[str]
        fragments: list[str]
        icmpConfiguration: IcmpConfigurationPatchProperties
        ipCondition: IpMatchConditionPatch
        ipLengths: list[str]
        portCondition: AccessControlListPortConditionPatch
        protocolNeighbors: list[str]
        protocolTypes: list[str]
        ttlValues: list[str]
        vlanMatchCondition: VlanMatchConditionPatch


    class azure.mgmt.managednetworkfabric.types.AccessControlListMatchConfiguration(TypedDict, total=False):
        key "ipAddressType": Union[str, IPAddressType]
        key "matchConfigurationName": str
        key "sequenceNumber": int
        actions: list[AccessControlListAction]
        ipAddressType: Union[str, IPAddressType]
        matchConditions: list[AccessControlListMatchCondition]
        matchConfigurationName: str
        sequenceNumber: int


    class azure.mgmt.managednetworkfabric.types.AccessControlListMatchConfigurationPatch(TypedDict, total=False):
        key "ipAddressType": Union[str, IPAddressType]
        key "matchConfigurationName": str
        key "sequenceNumber": int
        actions: list[AccessControlListActionPatch]
        ipAddressType: Union[str, IPAddressType]
        matchConditions: list[AccessControlListMatchConditionPatch]
        matchConfigurationName: str
        sequenceNumber: int


    class azure.mgmt.managednetworkfabric.types.AccessControlListPatch(TagsUpdate):
        key "properties": ForwardRef('AccessControlListPatchProperties', module='types')
        properties: AccessControlListPatchProperties
        tags: dict[str, str]


    class azure.mgmt.managednetworkfabric.types.AccessControlListPatchProperties(TypedDict, total=False):
        key "aclType": Union[str, AclType]
        key "aclsUrl": str
        key "annotation": str
        key "configurationType": Union[str, ConfigurationType]
        key "defaultAction": Union[str, CommunityActionTypes]
        key "deviceRole": Union[str, DeviceRole]
        key "globalAccessControlListActions": ForwardRef('GlobalAccessControlListActionPatchProperties', module='types')
        aclType: Union[str, AclType]
        aclsUrl: str
        annotation: str
        configurationType: Union[str, ConfigurationType]
        controlPlaneAclConfiguration: list[ControlPlaneAclPatchProperties]
        defaultAction: Union[str, CommunityActionTypes]
        deviceRole: Union[str, DeviceRole]
        dynamicMatchConfigurations: list[CommonDynamicMatchConfigurationPatch]
        globalAccessControlListActions: GlobalAccessControlListActionPatchProperties
        matchConfigurations: list[AccessControlListMatchConfigurationPatch]


    class azure.mgmt.managednetworkfabric.types.AccessControlListPortCondition(PortCondition):
        key "layer4Protocol": Required[Union[str, Layer4Protocol]]
        key "portType": Union[str, PortType]
        flags: list[str]
        layer4Protocol: Union[str, Layer4Protocol]
        portGroupNames: list[str]
        portType: Union[str, PortType]
        ports: list[str]


    class azure.mgmt.managednetworkfabric.types.AccessControlListPortConditionPatch(PortConditionPatch):
        key "layer4Protocol": Union[str, Layer4Protocol]
        key "portType": Union[str, PortType]
        flags: list[str]
        layer4Protocol: Union[str, Layer4Protocol]
        portGroupNames: list[str]
        portType: Union[str, PortType]
        ports: list[str]


    class azure.mgmt.managednetworkfabric.types.AccessControlListProperties(TypedDict, total=False):
        key "aclType": Union[str, AclType]
        key "aclsUrl": str
        key "administrativeState": Union[str, AdministrativeState]
        key "annotation": str
        key "configurationState": Union[str, ConfigurationState]
        key "configurationType": Required[Union[str, ConfigurationType]]
        key "defaultAction": Union[str, CommunityActionTypes]
        key "deviceRole": Union[str, DeviceRole]
        key "globalAccessControlListActions": ForwardRef('GlobalAccessControlListActionProperties', module='types')
        key "lastOperation": ForwardRef('LastOperationProperties', module='types')
        key "lastSyncedTime": str
        key "provisioningState": Union[str, ProvisioningState]
        aclType: Union[str, AclType]
        aclsUrl: str
        administrativeState: Union[str, AdministrativeState]
        annotation: str
        configurationState: Union[str, ConfigurationState]
        configurationType: Union[str, ConfigurationType]
        controlPlaneAclConfiguration: list[ControlPlaneAclProperties]
        defaultAction: Union[str, CommunityActionTypes]
        deviceRole: Union[str, DeviceRole]
        dynamicMatchConfigurations: list[CommonDynamicMatchConfiguration]
        globalAccessControlListActions: GlobalAccessControlListActionProperties
        lastOperation: LastOperationProperties
        lastSyncedTime: str
        matchConfigurations: list[AccessControlListMatchConfiguration]
        networkFabricIds: list[str]
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.managednetworkfabric.types.ActionIpCommunityPatchProperties(TypedDict, total=False):
        key "add": ForwardRef('IpCommunityIdList', module='types')
        key "delete": ForwardRef('IpCommunityIdList', module='types')
        key "set": ForwardRef('IpCommunityIdList', module='types')
        add: IpCommunityIdList
        delete: IpCommunityIdList
        set: IpCommunityIdList


    class azure.mgmt.managednetworkfabric.types.ActionIpCommunityProperties(TypedDict, total=False):
        key "add": ForwardRef('IpCommunityIdList', module='types')
        key "delete": ForwardRef('IpCommunityIdList', module='types')
        key "set": ForwardRef('IpCommunityIdList', module='types')
        add: IpCommunityIdList
        delete: IpCommunityIdList
        set: IpCommunityIdList


    class azure.mgmt.managednetworkfabric.types.ActionIpExtendedCommunityPatchProperties(TypedDict, total=False):
        key "add": ForwardRef('IpExtendedCommunityIdList', module='types')
        key "delete": ForwardRef('IpExtendedCommunityIdList', module='types')
        key "set": ForwardRef('IpExtendedCommunityIdList', module='types')
        add: IpExtendedCommunityIdList
        delete: IpExtendedCommunityIdList
        set: IpExtendedCommunityIdList


    class azure.mgmt.managednetworkfabric.types.ActionIpExtendedCommunityProperties(TypedDict, total=False):
        key "add": ForwardRef('IpExtendedCommunityIdList', module='types')
        key "delete": ForwardRef('IpExtendedCommunityIdList', module='types')
        key "set": ForwardRef('IpExtendedCommunityIdList', module='types')
        add: IpExtendedCommunityIdList
        delete: IpExtendedCommunityIdList
        set: IpExtendedCommunityIdList


    class azure.mgmt.managednetworkfabric.types.AggregateRoute(TypedDict, total=False):
        key "prefix": Required[str]
        prefix: str


    class azure.mgmt.managednetworkfabric.types.AggregateRouteConfiguration(TypedDict, total=False):
        ipv4Routes: list[AggregateRoute]
        ipv6Routes: list[AggregateRoute]


    class azure.mgmt.managednetworkfabric.types.AggregateRoutePatchConfiguration(TypedDict, total=False):
        ipv4Routes: list[AggregateRoute]
        ipv6Routes: list[AggregateRoute]


    class azure.mgmt.managednetworkfabric.types.AnnotationResource(TypedDict, total=False):
        key "annotation": str
        annotation: str


    class azure.mgmt.managednetworkfabric.types.AuthorizedTransceiverPatchProperties(TypedDict, total=False):
        key "key": str
        key "vendor": str
        key: str
        vendor: str


    class azure.mgmt.managednetworkfabric.types.AuthorizedTransceiverProperties(TypedDict, total=False):
        key "key": str
        key "vendor": str
        key: str
        vendor: str


    class azure.mgmt.managednetworkfabric.types.BfdConfiguration(TypedDict, total=False):
        key "administrativeState": Union[str, BfdAdministrativeState]
        key "intervalInMilliSeconds": int
        key "multiplier": int
        administrativeState: Union[str, BfdAdministrativeState]
        intervalInMilliSeconds: int
        multiplier: int


    class azure.mgmt.managednetworkfabric.types.BfdPatchConfiguration(TypedDict, total=False):
        key "administrativeState": Union[str, BfdAdministrativeState]
        key "intervalInMilliSeconds": int
        key "multiplier": int
        administrativeState: Union[str, BfdAdministrativeState]
        intervalInMilliSeconds: int
        multiplier: int


    class azure.mgmt.managednetworkfabric.types.BgpConfiguration(AnnotationResource):
        key "allowAS": int
        key "allowASOverride": Union[str, AllowASOverride]
        key "annotation": str
        key "bfdConfiguration": ForwardRef('BfdConfiguration', module='types')
        key "bmpConfiguration": ForwardRef('InternalNetworkBmpProperties', module='types')
        key "defaultRouteOriginate": Union[str, BooleanEnumProperty]
        key "fabricASN": int
        key "peerASN": Required[int]
        key "v4OverV6BgpSession": Union[str, V4OverV6BgpSessionState]
        key "v6OverV4BgpSession": Union[str, V6OverV4BgpSessionState]
        allowAS: int
        allowASOverride: Union[str, AllowASOverride]
        annotation: str
        bfdConfiguration: BfdConfiguration
        bmpConfiguration: InternalNetworkBmpProperties
        defaultRouteOriginate: Union[str, BooleanEnumProperty]
        fabricASN: int
        ipv4ListenRangePrefixes: list[str]
        ipv4NeighborAddress: list[NeighborAddress]
        ipv6ListenRangePrefixes: list[str]
        ipv6NeighborAddress: list[NeighborAddress]
        peerASN: int
        v4OverV6BgpSession: Union[str, V4OverV6BgpSessionState]
        v6OverV4BgpSession: Union[str, V6OverV4BgpSessionState]


    class azure.mgmt.managednetworkfabric.types.BgpPatchConfiguration(AnnotationResource):
        key "allowAS": int
        key "allowASOverride": Union[str, AllowASOverride]
        key "annotation": str
        key "bfdConfiguration": ForwardRef('BfdPatchConfiguration', module='types')
        key "bmpConfiguration": ForwardRef('InternalNetworkBmpPatchProperties', module='types')
        key "defaultRouteOriginate": Union[str, BooleanEnumProperty]
        key "fabricASN": int
        key "peerASN": int
        key "v4OverV6BgpSession": Union[str, V4OverV6BgpSessionState]
        key "v6OverV4BgpSession": Union[str, V6OverV4BgpSessionState]
        allowAS: int
        allowASOverride: Union[str, AllowASOverride]
        annotation: str
        bfdConfiguration: BfdPatchConfiguration
        bmpConfiguration: InternalNetworkBmpPatchProperties
        defaultRouteOriginate: Union[str, BooleanEnumProperty]
        fabricASN: int
        ipv4ListenRangePrefixes: list[str]
        ipv4NeighborAddress: list[NeighborAddressPatch]
        ipv6ListenRangePrefixes: list[str]
        ipv6NeighborAddress: list[NeighborAddressPatch]
        peerASN: int
        v4OverV6BgpSession: Union[str, V4OverV6BgpSessionState]
        v6OverV4BgpSession: Union[str, V6OverV4BgpSessionState]


    class azure.mgmt.managednetworkfabric.types.BitRate(TypedDict, total=False):
        key "rate": int
        key "unit": Union[str, BitRateUnit]
        rate: int
        unit: Union[str, BitRateUnit]


    class azure.mgmt.managednetworkfabric.types.BmpConfigurationPatchProperties(TypedDict, total=False):
        key "exportPolicy": Union[str, BmpExportPolicy]
        key "exportPolicyConfiguration": ForwardRef('BmpExportPolicyPatchProperties', module='types')
        key "scopeResourceId": str
        key "stationConfigurationState": Union[str, StationConfigurationState]
        key "stationConnectionMode": Union[str, StationConnectionMode]
        key "stationConnectionProperties": ForwardRef('StationConnectionPatchProperties', module='types')
        key "stationIp": str
        key "stationName": str
        key "stationNetwork": str
        key "stationPort": int
        exportPolicy: Union[str, BmpExportPolicy]
        exportPolicyConfiguration: BmpExportPolicyPatchProperties
        monitoredAddressFamilies: list[Union[str, BmpMonitoredAddressFamily]]
        monitoredNetworks: list[str]
        scopeResourceId: str
        stationConfigurationState: Union[str, StationConfigurationState]
        stationConnectionMode: Union[str, StationConnectionMode]
        stationConnectionProperties: StationConnectionPatchProperties
        stationIp: str
        stationName: str
        stationNetwork: str
        stationPort: int


    class azure.mgmt.managednetworkfabric.types.BmpConfigurationProperties(TypedDict, total=False):
        key "exportPolicy": Union[str, BmpExportPolicy]
        key "exportPolicyConfiguration": ForwardRef('BmpExportPolicyProperties', module='types')
        key "scopeResourceId": str
        key "stationConfigurationState": Union[str, StationConfigurationState]
        key "stationConnectionMode": Union[str, StationConnectionMode]
        key "stationConnectionProperties": ForwardRef('StationConnectionProperties', module='types')
        key "stationIp": str
        key "stationName": str
        key "stationNetwork": str
        key "stationPort": int
        exportPolicy: Union[str, BmpExportPolicy]
        exportPolicyConfiguration: BmpExportPolicyProperties
        monitoredAddressFamilies: list[Union[str, BmpMonitoredAddressFamily]]
        monitoredNetworks: list[str]
        scopeResourceId: str
        stationConfigurationState: Union[str, StationConfigurationState]
        stationConnectionMode: Union[str, StationConnectionMode]
        stationConnectionProperties: StationConnectionProperties
        stationIp: str
        stationName: str
        stationNetwork: str
        stationPort: int


    class azure.mgmt.managednetworkfabric.types.BmpExportPolicyPatchProperties(TypedDict, total=False):
        exportPolicies: list[Union[str, BmpExportPolicy]]


    class azure.mgmt.managednetworkfabric.types.BmpExportPolicyProperties(TypedDict, total=False):
        exportPolicies: list[Union[str, BmpExportPolicy]]


    class azure.mgmt.managednetworkfabric.types.BurstSize(TypedDict, total=False):
        key "size": int
        key "unit": Union[str, BurstSizeUnit]
        size: int
        unit: Union[str, BurstSizeUnit]


    class azure.mgmt.managednetworkfabric.types.CertificateArchiveReference(TypedDict, total=False):
        key "certificateName": str
        key "certificateVersion": str
        key "keyVaultId": str
        key "keyVaultUri": str
        certificateName: str
        certificateVersion: str
        keyVaultId: str
        keyVaultUri: str


    class azure.mgmt.managednetworkfabric.types.CertificateRotationStatus(TypedDict, total=False):
        key "certificateArchiveReference": ForwardRef('CertificateArchiveReference', module='types')
        key "certificateType": str
        key "expireTime": str
        key "lastRotationTime": str
        key "synchronizationStatus": Union[str, SynchronizationStatus]
        certificateArchiveReference: CertificateArchiveReference
        certificateType: str
        expireTime: str
        lastRotationTime: str
        synchronizationStatus: Union[str, SynchronizationStatus]


    class azure.mgmt.managednetworkfabric.types.CommitBatchStatusRequest(TypedDict, total=False):
        key "commitBatchId": str
        commitBatchId: str


    class azure.mgmt.managednetworkfabric.types.CommitConfigurationRequest(TypedDict, total=False):
        key "commitPolicy": Union[str, CommitConfigurationPolicy]
        key "commitStage": Union[str, CommitStage]
        commitPolicy: Union[str, CommitConfigurationPolicy]
        commitStage: Union[str, CommitStage]
        devices: list[str]


    class azure.mgmt.managednetworkfabric.types.CommonDynamicMatchConfiguration(TypedDict, total=False):
        ipGroups: list[IpGroupProperties]
        portGroups: list[PortGroupProperties]
        vlanGroups: list[VlanGroupProperties]


    class azure.mgmt.managednetworkfabric.types.CommonDynamicMatchConfigurationPatch(TypedDict, total=False):
        ipGroups: list[IpGroupPatchProperties]
        portGroups: list[PortGroupPatchProperties]
        vlanGroups: list[VlanGroupPatchProperties]


    class azure.mgmt.managednetworkfabric.types.CommonMatchConditions(TypedDict, total=False):
        key "ipCondition": ForwardRef('IpMatchCondition', module='types')
        key "vlanMatchCondition": ForwardRef('VlanMatchCondition', module='types')
        ipCondition: IpMatchCondition
        protocolTypes: list[str]
        vlanMatchCondition: VlanMatchCondition


    class azure.mgmt.managednetworkfabric.types.CommonMatchConditionsPatch(TypedDict, total=False):
        key "ipCondition": ForwardRef('IpMatchConditionPatch', module='types')
        key "vlanMatchCondition": ForwardRef('VlanMatchConditionPatch', module='types')
        ipCondition: IpMatchConditionPatch
        protocolTypes: list[str]
        vlanMatchCondition: VlanMatchConditionPatch


    class azure.mgmt.managednetworkfabric.types.ConditionalDefaultRouteProperties(TypedDict, total=False):
        ipv4Routes: list[StaticRouteProperties]
        ipv6Routes: list[StaticRouteProperties]


    class azure.mgmt.managednetworkfabric.types.ConnectedSubnet(AnnotationResource):
        key "annotation": str
        key "prefix": Required[str]
        annotation: str
        prefix: str


    class azure.mgmt.managednetworkfabric.types.ConnectedSubnetPatch(AnnotationResource):
        key "annotation": str
        key "prefix": Required[str]
        annotation: str
        prefix: str


    class azure.mgmt.managednetworkfabric.types.ConnectedSubnetRoutePolicy(TypedDict, total=False):
        key "exportRoutePolicy": ForwardRef('L3ExportRoutePolicy', module='types')
        exportRoutePolicy: L3ExportRoutePolicy


    class azure.mgmt.managednetworkfabric.types.ConnectedSubnetRoutePolicyPatch(TypedDict, total=False):
        key "exportRoutePolicy": ForwardRef('L3ExportRoutePolicyPatch', module='types')
        exportRoutePolicy: L3ExportRoutePolicyPatch


    class azure.mgmt.managednetworkfabric.types.ControlPlanAclIpMatchCondition(TypedDict, total=False):
        key "destinationIpPrefix": str
        key "sourceIpPrefix": str
        destinationIpPrefix: str
        sourceIpPrefix: str


    class azure.mgmt.managednetworkfabric.types.ControlPlaneAclAction(TypedDict, total=False):
        key "remarkComment": str
        key "type": Union[str, ControlPlaneAclActionType]
        remarkComment: str
        type: Union[str, ControlPlaneAclActionType]


    class azure.mgmt.managednetworkfabric.types.ControlPlaneAclActionPatch(TypedDict, total=False):
        key "remarkComment": str
        key "type": Union[str, ControlPlaneAclActionType]
        remarkComment: str
        type: Union[str, ControlPlaneAclActionType]


    class azure.mgmt.managednetworkfabric.types.ControlPlaneAclIpMatchConditionPatch(TypedDict, total=False):
        key "destinationIpPrefix": str
        key "sourceIpPrefix": str
        destinationIpPrefix: str
        sourceIpPrefix: str


    class azure.mgmt.managednetworkfabric.types.ControlPlaneAclMatchCondition(TypedDict, total=False):
        key "icmpConfiguration": ForwardRef('IcmpConfigurationProperties', module='types')
        key "ipCondition": ForwardRef('ControlPlanAclIpMatchCondition', module='types')
        key "portCondition": ForwardRef('ControlPlaneAclPortMatchCondition', module='types')
        key "protocolTypes": str
        key "ttlMatchCondition": ForwardRef('ControlPlaneAclTtlMatchCondition', module='types')
        flags: list[str]
        icmpConfiguration: IcmpConfigurationProperties
        ipCondition: ControlPlanAclIpMatchCondition
        portCondition: ControlPlaneAclPortMatchCondition
        protocolTypes: str
        ttlMatchCondition: ControlPlaneAclTtlMatchCondition


    class azure.mgmt.managednetworkfabric.types.ControlPlaneAclMatchConditionPatch(TypedDict, total=False):
        key "icmpConfiguration": ForwardRef('IcmpConfigurationPatchProperties', module='types')
        key "ipCondition": ForwardRef('ControlPlaneAclIpMatchConditionPatch', module='types')
        key "portCondition": ForwardRef('ControlPlaneAclPortMatchConditionPatch', module='types')
        key "protocolTypes": str
        key "ttlMatchCondition": ForwardRef('ControlPlaneAclTtlMatchConditionPatch', module='types')
        flags: list[str]
        icmpConfiguration: IcmpConfigurationPatchProperties
        ipCondition: ControlPlaneAclIpMatchConditionPatch
        portCondition: ControlPlaneAclPortMatchConditionPatch
        protocolTypes: str
        ttlMatchCondition: ControlPlaneAclTtlMatchConditionPatch


    class azure.mgmt.managednetworkfabric.types.ControlPlaneAclMatchConfigurationPatchProperties(TypedDict, total=False):
        key "action": ForwardRef('ControlPlaneAclActionPatch', module='types')
        key "matchCondition": ForwardRef('ControlPlaneAclMatchConditionPatch', module='types')
        key "matchConfigurationName": str
        key "sequenceNumber": int
        action: ControlPlaneAclActionPatch
        matchCondition: ControlPlaneAclMatchConditionPatch
        matchConfigurationName: str
        sequenceNumber: int


    class azure.mgmt.managednetworkfabric.types.ControlPlaneAclMatchConfigurationProperties(TypedDict, total=False):
        key "action": ForwardRef('ControlPlaneAclAction', module='types')
        key "matchCondition": ForwardRef('ControlPlaneAclMatchCondition', module='types')
        key "matchConfigurationName": str
        key "sequenceNumber": int
        action: ControlPlaneAclAction
        matchCondition: ControlPlaneAclMatchCondition
        matchConfigurationName: str
        sequenceNumber: int


    class azure.mgmt.managednetworkfabric.types.ControlPlaneAclPatchProperties(TypedDict, total=False):
        key "ipAddressType": Union[str, IPAddressType]
        ipAddressType: Union[str, IPAddressType]
        matchConfigurations: list[ControlPlaneAclMatchConfigurationPatchProperties]


    class azure.mgmt.managednetworkfabric.types.ControlPlaneAclPortCondition(TypedDict, total=False):
        key "portMatchType": Union[str, ControlPlaneAclPortMatchType]
        portMatchType: Union[str, ControlPlaneAclPortMatchType]
        ports: list[str]


    class azure.mgmt.managednetworkfabric.types.ControlPlaneAclPortMatchCondition(TypedDict, total=False):
        key "destinationPorts": ForwardRef('ControlPlaneAclPortCondition', module='types')
        key "sourcePorts": ForwardRef('ControlPlaneAclPortCondition', module='types')
        destinationPorts: ControlPlaneAclPortCondition
        sourcePorts: ControlPlaneAclPortCondition


    class azure.mgmt.managednetworkfabric.types.ControlPlaneAclPortMatchConditionPatch(TypedDict, total=False):
        key "destinationPorts": ForwardRef('ControlPlaneAclPortCondition', module='types')
        key "sourcePorts": ForwardRef('ControlPlaneAclPortCondition', module='types')
        destinationPorts: ControlPlaneAclPortCondition
        sourcePorts: ControlPlaneAclPortCondition


    class azure.mgmt.managednetworkfabric.types.ControlPlaneAclProperties(TypedDict, total=False):
        key "ipAddressType": Union[str, IPAddressType]
        ipAddressType: Union[str, IPAddressType]
        matchConfigurations: list[ControlPlaneAclMatchConfigurationProperties]


    class azure.mgmt.managednetworkfabric.types.ControlPlaneAclTtlMatchCondition(TypedDict, total=False):
        key "ttlMatchType": Union[str, ControlPlaneAclTtlMatchType]
        key "ttlValue": str
        ttlMatchType: Union[str, ControlPlaneAclTtlMatchType]
        ttlValue: str


    class azure.mgmt.managednetworkfabric.types.ControlPlaneAclTtlMatchConditionPatch(TypedDict, total=False):
        key "ttlMatchType": Union[str, ControlPlaneAclTtlMatchType]
        key "ttlValue": str
        ttlMatchType: Union[str, ControlPlaneAclTtlMatchType]
        ttlValue: str


    class azure.mgmt.managednetworkfabric.types.ControllerServices(TypedDict, total=False):
        ipv4AddressSpaces: list[str]
        ipv6AddressSpaces: list[str]


    class azure.mgmt.managednetworkfabric.types.DestinationPatchProperties(TypedDict, total=False):
        key "destinationId": str
        key "destinationTapRuleId": str
        key "destinationType": Union[str, DestinationType]
        key "isolationDomainProperties": ForwardRef('IsolationDomainPatchProperties', module='types')
        key "name": str
        destinationId: str
        destinationTapRuleId: str
        destinationType: Union[str, DestinationType]
        isolationDomainProperties: IsolationDomainPatchProperties
        name: str


    class azure.mgmt.managednetworkfabric.types.DestinationProperties(TypedDict, total=False):
        key "destinationId": Required[str]
        key "destinationTapRuleId": str
        key "destinationType": Required[Union[str, DestinationType]]
        key "isolationDomainProperties": ForwardRef('IsolationDomainProperties', module='types')
        key "name": Required[str]
        destinationId: str
        destinationTapRuleId: str
        destinationType: Union[str, DestinationType]
        isolationDomainProperties: IsolationDomainProperties
        name: str


    class azure.mgmt.managednetworkfabric.types.DeviceRoCommand(TypedDict, total=False):
        key "command": str
        command: str


    class azure.mgmt.managednetworkfabric.types.DeviceRwCommand(TypedDict, total=False):
        key "command": str
        key "commandUrl": str
        command: str
        commandUrl: str


    class azure.mgmt.managednetworkfabric.types.DiscardCommitBatchRequest(TypedDict, total=False):
        key "commitBatchId": str
        commitBatchId: str


    class azure.mgmt.managednetworkfabric.types.EdgeConnector(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[EdgeConnectorProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: EdgeConnectorProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managednetworkfabric.types.EdgeConnectorPatch(TypedDict, total=False):
        key "properties": ForwardRef('EdgeConnectorPatchableProperties', module='types')
        properties: EdgeConnectorPatchableProperties
        tags: dict[str, str]


    class azure.mgmt.managednetworkfabric.types.EdgeConnectorPatchableProperties(TypedDict, total=False):
        key "connectivityModel": Union[str, ConnectivityModel]
        key "version": str
        connectivityModel: Union[str, ConnectivityModel]
        version: str


    class azure.mgmt.managednetworkfabric.types.EdgeConnectorProperties(TypedDict, total=False):
        key "connectivityModel": Union[str, ConnectivityModel]
        key "provisioningState": Union[str, ProvisioningState]
        key "version": str
        connectivityModel: Union[str, ConnectivityModel]
        managedFabricIds: list[str]
        provisioningState: Union[str, ProvisioningState]
        version: str


    class azure.mgmt.managednetworkfabric.types.EnableDisableOnResources(TypedDict, total=False):
        resourceIds: list[str]


    class azure.mgmt.managednetworkfabric.types.ExportRoutePolicy(TypedDict, total=False):
        key "exportIpv4RoutePolicyId": str
        key "exportIpv6RoutePolicyId": str
        exportIpv4RoutePolicyId: str
        exportIpv6RoutePolicyId: str


    class azure.mgmt.managednetworkfabric.types.ExportRoutePolicyInformation(TypedDict, total=False):
        key "exportIpv4RoutePolicyId": str
        key "exportIpv6RoutePolicyId": str
        exportIpv4RoutePolicyId: str
        exportIpv6RoutePolicyId: str


    class azure.mgmt.managednetworkfabric.types.ExportRoutePolicyInformationPatch(TypedDict, total=False):
        key "exportIpv4RoutePolicyId": str
        key "exportIpv6RoutePolicyId": str
        exportIpv4RoutePolicyId: str
        exportIpv6RoutePolicyId: str


    class azure.mgmt.managednetworkfabric.types.ExportRoutePolicyPatch(TypedDict, total=False):
        key "exportIpv4RoutePolicyId": str
        key "exportIpv6RoutePolicyId": str
        exportIpv4RoutePolicyId: str
        exportIpv6RoutePolicyId: str


    class azure.mgmt.managednetworkfabric.types.ExpressRouteConnectionInformation(TypedDict, total=False):
        key "expressRouteAuthorizationKey": Required[str]
        key "expressRouteCircuitId": Required[str]
        expressRouteAuthorizationKey: str
        expressRouteCircuitId: str


    class azure.mgmt.managednetworkfabric.types.ExternalNetwork(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[ExternalNetworkProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ExternalNetworkProperties
        systemData: SystemData
        type: str


    class azure.mgmt.managednetworkfabric.types.ExternalNetworkBmpPatchProperties(TypedDict, total=False):
        key "configurationState": Union[str, BmpConfigurationState]
        configurationState: Union[str, BmpConfigurationState]


    class azure.mgmt.managednetworkfabric.types.ExternalNetworkBmpProperties(TypedDict, total=False):
        key "configurationState": Union[str, BmpConfigurationState]
        configurationState: Union[str, BmpConfigurationState]


    class azure.mgmt.managednetworkfabric.types.ExternalNetworkPatch(TypedDict, total=False):
        key "properties": ForwardRef('ExternalNetworkPatchProperties', module='types')
        properties: ExternalNetworkPatchProperties


    class azure.mgmt.managednetworkfabric.types.ExternalNetworkPatchProperties(TypedDict, total=False):
        key "annotation": str
        key "exportRoutePolicy": ForwardRef('ExportRoutePolicyPatch', module='types')
        key "importRoutePolicy": ForwardRef('ImportRoutePolicyPatch', module='types')
        key "networkToNetworkInterconnectId": str
        key "optionAProperties": ForwardRef('ExternalNetworkPatchPropertiesOptionAProperties', module='types')
        key "optionBProperties": ForwardRef('L3OptionBPatchProperties', module='types')
        key "peeringOption": Union[str, PeeringOption]
        key "staticRouteConfiguration": ForwardRef('ExternalNetworkStaticRoutePatchConfiguration', module='types')
        annotation: str
        exportRoutePolicy: ExportRoutePolicyPatch
        importRoutePolicy: ImportRoutePolicyPatch
        networkToNetworkInterconnectId: str
        optionAProperties: ExternalNetworkPatchPropertiesOptionAProperties
        optionBProperties: L3OptionBPatchProperties
        peeringOption: Union[str, PeeringOption]
        staticRouteConfiguration: ExternalNetworkStaticRoutePatchConfiguration


    class azure.mgmt.managednetworkfabric.types.ExternalNetworkPatchPropertiesOptionAProperties(TypedDict, total=False):
        key "bfdConfiguration": ForwardRef('BfdPatchConfiguration', module='types')
        key "bmpConfiguration": ForwardRef('ExternalNetworkBmpPatchProperties', module='types')
        key "egressAclId": str
        key "fabricASN": int
        key "ingressAclId": str
        key "mtu": int
        key "nativeIpv4PrefixLimit": ForwardRef('NativeIpv4PrefixLimitPatchProperties', module='types')
        key "nativeIpv6PrefixLimit": ForwardRef('NativeIpv6PrefixLimitPatchProperties', module='types')
        key "peerASN": int
        key "primaryIpv4Prefix": str
        key "primaryIpv6Prefix": str
        key "secondaryIpv4Prefix": str
        key "secondaryIpv6Prefix": str
        key "v4OverV6BgpSession": Union[str, V4OverV6BgpSessionState]
        key "v6OverV4BgpSession": Union[str, V6OverV4BgpSessionState]
        key "vlanId": int
        bfdConfiguration: BfdPatchConfiguration
        bmpConfiguration: ExternalNetworkBmpPatchProperties
        egressAclId: str
        fabricASN: int
        ingressAclId: str
        mtu: int
        nativeIpv4PrefixLimit: NativeIpv4PrefixLimitPatchProperties
        nativeIpv6PrefixLimit: NativeIpv6PrefixLimitPatchProperties
        peerASN: int
        primaryIpv4Prefix: str
        primaryIpv6Prefix: str
        secondaryIpv4Prefix: str
        secondaryIpv6Prefix: str
        v4OverV6BgpSession: Union[str, V4OverV6BgpSessionState]
        v6OverV4BgpSession: Union[str, V6OverV4BgpSessionState]
        vlanId: int


    class azure.mgmt.managednetworkfabric.types.ExternalNetworkProperties(TypedDict, total=False):
        key "administrativeState": Union[str, AdministrativeState]
        key "annotation": str
        key "configurationState": Union[str, ConfigurationState]
        key "exportRoutePolicy": ForwardRef('ExportRoutePolicy', module='types')
        key "importRoutePolicy": ForwardRef('ImportRoutePolicy', module='types')
        key "lastOperation": ForwardRef('LastOperationProperties', module='types')
        key "networkFabricId": str
        key "networkToNetworkInterconnectId": str
        key "optionAProperties": ForwardRef('ExternalNetworkPropertiesOptionAProperties', module='types')
        key "optionBProperties": ForwardRef('L3OptionBProperties', module='types')
        key "peeringOption": Required[Union[str, PeeringOption]]
        key "provisioningState": Union[str, ProvisioningState]
        key "staticRouteConfiguration": ForwardRef('ExternalNetworkStaticRouteConfiguration', module='types')
        administrativeState: Union[str, AdministrativeState]
        annotation: str
        configurationState: Union[str, ConfigurationState]
        exportRoutePolicy: ExportRoutePolicy
        importRoutePolicy: ImportRoutePolicy
        lastOperation: LastOperationProperties
        networkFabricId: str
        networkToNetworkInterconnectId: str
        optionAProperties: ExternalNetworkPropertiesOptionAProperties
        optionBProperties: L3OptionBProperties
        peeringOption: Union[str, PeeringOption]
        provisioningState: Union[str, ProvisioningState]
        staticRouteConfiguration: ExternalNetworkStaticRouteConfiguration


    class azure.mgmt.managednetworkfabric.types.ExternalNetworkPropertiesOptionAProperties(TypedDict, total=False):
        key "bfdConfiguration": ForwardRef('BfdConfiguration', module='types')
        key "bmpConfiguration": ForwardRef('ExternalNetworkBmpProperties', module='types')
        key "egressAclId": str
        key "fabricASN": int
        key "ingressAclId": str
        key "mtu": int
        key "nativeIpv4PrefixLimit": ForwardRef('NativeIpv4PrefixLimitProperties', module='types')
        key "nativeIpv6PrefixLimit": ForwardRef('NativeIpv6PrefixLimitProperties', module='types')
        key "peerASN": Required[int]
        key "primaryIpv4Prefix": str
        key "primaryIpv6Prefix": str
        key "secondaryIpv4Prefix": str
        key "secondaryIpv6Prefix": str
        key "v4OverV6BgpSession": Union[str, V4OverV6BgpSessionState]
        key "v6OverV4BgpSession": Union[str, V6OverV4BgpSessionState]
        key "vlanId": Required[int]
        bfdConfiguration: BfdConfiguration
        bmpConfiguration: ExternalNetworkBmpProperties
        egressAclId: str
        fabricASN: int
        ingressAclId: str
        mtu: int
        nativeIpv4PrefixLimit: NativeIpv4PrefixLimitProperties
        nativeIpv6PrefixLimit: NativeIpv6PrefixLimitProperties
        peerASN: int
        primaryIpv4Prefix: str
        primaryIpv6Prefix: str
        secondaryIpv4Prefix: str
        secondaryIpv6Prefix: str
        v4OverV6BgpSession: Union[str, V4OverV6BgpSessionState]
        v6OverV4BgpSession: Union[str, V6OverV4BgpSessionState]
        vlanId: int


    class azure.mgmt.managednetworkfabric.types.ExternalNetworkStaticRouteConfiguration(TypedDict, total=False):
        key "bfdConfiguration": ForwardRef('BfdConfiguration', module='types')
        bfdConfiguration: BfdConfiguration
        ipv4Routes: list[StaticRouteProperties]
        ipv6Routes: list[StaticRouteProperties]


    class azure.mgmt.managednetworkfabric.types.ExternalNetworkStaticRoutePatchConfiguration(TypedDict, total=False):
        key "bfdConfiguration": ForwardRef('BfdPatchConfiguration', module='types')
        bfdConfiguration: BfdPatchConfiguration
        ipv4Routes: list[StaticRoutePatchProperties]
        ipv6Routes: list[StaticRoutePatchProperties]


    class azure.mgmt.managednetworkfabric.types.ExternalNetworkUpdateBfdAdministrativeStateRequest(TypedDict, total=False):
        key "administrativeState": Union[str, BfdAdministrativeState]
        key "routeType": Union[str, ExternalNetworkRouteType]
        administrativeState: Union[str, BfdAdministrativeState]
        routeType: Union[str, ExternalNetworkRouteType]


    class azure.mgmt.managednetworkfabric.types.Fabric(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[FabricProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: FabricProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managednetworkfabric.types.FabricLockProperties(TypedDict, total=False):
        key "lockState": Union[str, LockConfigurationState]
        key "lockType": Union[str, NetworkFabricLockType]
        lockState: Union[str, LockConfigurationState]
        lockType: Union[str, NetworkFabricLockType]


    class azure.mgmt.managednetworkfabric.types.FabricPatch(TypedDict, total=False):
        key "properties": ForwardRef('FabricPatchableProperties', module='types')
        properties: FabricPatchableProperties
        tags: dict[str, str]


    class azure.mgmt.managednetworkfabric.types.FabricPatchableProperties(TypedDict, total=False):
        key "controllerCredentialRef": str
        key "controllerEndpoint": str
        key "infrastructureNetworks": ForwardRef('PatchInfrastructureNetworks', module='types')
        key "infrastructureServices": ForwardRef('PatchInfrastructureServices', module='types')
        key "operationPolicy": Union[str, OperationPolicy]
        controllerCredentialRef: str
        controllerEndpoint: str
        infrastructureNetworks: PatchInfrastructureNetworks
        infrastructureServices: PatchInfrastructureServices
        operationPolicy: Union[str, OperationPolicy]


    class azure.mgmt.managednetworkfabric.types.FabricProperties(TypedDict, total=False):
        key "controllerCredentialRef": str
        key "controllerEndpoint": str
        key "controllerType": Union[str, ControllerType]
        key "customerSubnetId": str
        key "customerVnetId": str
        key "edgeConnectorId": str
        key "fabricSku": str
        key "infrastructureNetworks": ForwardRef('InfrastructureNetworks', module='types')
        key "infrastructureServices": ForwardRef('InfrastructureServices', module='types')
        key "managementMode": Required[Union[str, ManagementMode]]
        key "operationPolicy": Union[str, OperationPolicy]
        key "provisioningState": Union[str, ProvisioningState]
        key "rackCount": int
        controllerCredentialRef: str
        controllerEndpoint: str
        controllerType: Union[str, ControllerType]
        customerSubnetId: str
        customerVnetId: str
        edgeConnectorId: str
        fabricSku: str
        infrastructureNetworks: InfrastructureNetworks
        infrastructureServices: InfrastructureServices
        managementMode: Union[str, ManagementMode]
        operationPolicy: Union[str, OperationPolicy]
        provisioningState: Union[str, ProvisioningState]
        rackCount: int


    class azure.mgmt.managednetworkfabric.types.FeatureFlagProperties(TypedDict, total=False):
        key "featureFlagName": str
        key "featureFlagValue": str
        featureFlagName: str
        featureFlagValue: str


    class azure.mgmt.managednetworkfabric.types.GlobalAccessControlListActionPatchProperties(TypedDict, total=False):
        key "enableCount": Union[str, BooleanEnumProperty]
        enableCount: Union[str, BooleanEnumProperty]


    class azure.mgmt.managednetworkfabric.types.GlobalAccessControlListActionProperties(TypedDict, total=False):
        key "enableCount": Union[str, BooleanEnumProperty]
        enableCount: Union[str, BooleanEnumProperty]


    class azure.mgmt.managednetworkfabric.types.GlobalNetworkTapRuleActionPatchProperties(TypedDict, total=False):
        key "enableCount": Union[str, BooleanEnumProperty]
        key "truncate": str
        enableCount: Union[str, BooleanEnumProperty]
        truncate: str


    class azure.mgmt.managednetworkfabric.types.GlobalNetworkTapRuleActionProperties(TypedDict, total=False):
        key "enableCount": Union[str, BooleanEnumProperty]
        key "truncate": str
        enableCount: Union[str, BooleanEnumProperty]
        truncate: str


    class azure.mgmt.managednetworkfabric.types.HeaderAddressProperties(TypedDict, total=False):
        key "headerName": str
        addressList: list[str]
        headerName: str


    class azure.mgmt.managednetworkfabric.types.IcmpConfigurationPatchProperties(TypedDict, total=False):
        icmpTypes: list[str]


    class azure.mgmt.managednetworkfabric.types.IcmpConfigurationProperties(TypedDict, total=False):
        icmpTypes: list[str]


    class azure.mgmt.managednetworkfabric.types.IdentitySelector(TypedDict, total=False):
        key "identityType": Required[Union[str, ManagedServiceIdentitySelectorType]]
        key "userAssignedIdentityResourceId": str
        identityType: Union[str, ManagedServiceIdentitySelectorType]
        userAssignedIdentityResourceId: str


    class azure.mgmt.managednetworkfabric.types.IdentitySelectorPatch(TypedDict, total=False):
        key "identityType": Union[str, ManagedServiceIdentitySelectorType]
        key "userAssignedIdentityResourceId": str
        identityType: Union[str, ManagedServiceIdentitySelectorType]
        userAssignedIdentityResourceId: str


    class azure.mgmt.managednetworkfabric.types.ImportRoutePolicy(TypedDict, total=False):
        key "importIpv4RoutePolicyId": str
        key "importIpv6RoutePolicyId": str
        importIpv4RoutePolicyId: str
        importIpv6RoutePolicyId: str


    class azure.mgmt.managednetworkfabric.types.ImportRoutePolicyInformation(TypedDict, total=False):
        key "importIpv4RoutePolicyId": str
        key "importIpv6RoutePolicyId": str
        importIpv4RoutePolicyId: str
        importIpv6RoutePolicyId: str


    class azure.mgmt.managednetworkfabric.types.ImportRoutePolicyInformationPatch(TypedDict, total=False):
        key "importIpv4RoutePolicyId": str
        key "importIpv6RoutePolicyId": str
        importIpv4RoutePolicyId: str
        importIpv6RoutePolicyId: str


    class azure.mgmt.managednetworkfabric.types.ImportRoutePolicyPatch(TypedDict, total=False):
        key "importIpv4RoutePolicyId": str
        key "importIpv6RoutePolicyId": str
        importIpv4RoutePolicyId: str
        importIpv6RoutePolicyId: str


    class azure.mgmt.managednetworkfabric.types.InfraNetwork(TypedDict, total=False):
        key "ipv4EndAddr": Required[str]
        key "ipv4Gateway": Required[str]
        key "ipv4StartAddr": Required[str]
        key "ipv4Subnet": Required[str]
        key "mtu": int
        key "vlanId": Required[int]
        ipv4EndAddr: str
        ipv4Gateway: str
        ipv4StartAddr: str
        ipv4Subnet: str
        mtu: int
        vlanId: int


    class azure.mgmt.managednetworkfabric.types.InfraNetworkOptionalIp(TypedDict, total=False):
        key "ipv4EndAddr": str
        key "ipv4Gateway": str
        key "ipv4StartAddr": str
        key "ipv4Subnet": str
        key "mtu": int
        key "vlanId": Required[int]
        ipv4EndAddr: str
        ipv4Gateway: str
        ipv4StartAddr: str
        ipv4Subnet: str
        mtu: int
        vlanId: int


    class azure.mgmt.managednetworkfabric.types.InfrastructureNetworks(TypedDict, total=False):
        key "bmc": Required[InfraNetwork]
        key "management": Required[InfraNetwork]
        key "pdu": ForwardRef('InfraNetwork', module='types')
        key "pxe": Required[InfraNetwork]
        key "storage": Required[InfraNetwork]
        key "storageMgmt": ForwardRef('InfraNetworkOptionalIp', module='types')
        bmc: InfraNetwork
        management: InfraNetwork
        pdu: InfraNetwork
        pxe: InfraNetwork
        storage: InfraNetwork
        storageMgmt: InfraNetworkOptionalIp


    class azure.mgmt.managednetworkfabric.types.InfrastructureServices(TypedDict, total=False):
        key "dnsServers": Required[list[str]]
        key "ntpServers": Required[list[str]]
        key "platformProxy": Required[PlatformProxy]
        dnsServers: list[str]
        ntpServers: list[str]
        platformProxy: PlatformProxy


    class azure.mgmt.managednetworkfabric.types.InternalNetwork(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[InternalNetworkProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: InternalNetworkProperties
        systemData: SystemData
        type: str


    class azure.mgmt.managednetworkfabric.types.InternalNetworkBmpPatchProperties(TypedDict, total=False):
        key "bmpConfigurationState": Union[str, BmpConfigurationState]
        bmpConfigurationState: Union[str, BmpConfigurationState]
        neighborIpExclusions: list[str]


    class azure.mgmt.managednetworkfabric.types.InternalNetworkBmpProperties(TypedDict, total=False):
        key "bmpConfigurationState": Union[str, BmpConfigurationState]
        key "exportPolicyConfiguration": ForwardRef('BmpExportPolicyProperties', module='types')
        bmpConfigurationState: Union[str, BmpConfigurationState]
        exportPolicyConfiguration: BmpExportPolicyProperties
        neighborIpExclusions: list[str]


    class azure.mgmt.managednetworkfabric.types.InternalNetworkPatch(TypedDict, total=False):
        key "properties": ForwardRef('InternalNetworkPatchProperties', module='types')
        properties: InternalNetworkPatchProperties


    class azure.mgmt.managednetworkfabric.types.InternalNetworkPatchProperties(TypedDict, total=False):
        key "annotation": str
        key "bgpConfiguration": ForwardRef('BgpPatchConfiguration', module='types')
        key "egressAclId": str
        key "exportRoutePolicy": ForwardRef('ExportRoutePolicy', module='types')
        key "importRoutePolicy": ForwardRef('ImportRoutePolicy', module='types')
        key "ingressAclId": str
        key "isMonitoringEnabled": Union[str, IsMonitoringEnabled]
        key "mtu": int
        key "nativeIpv4PrefixLimit": ForwardRef('NativeIpv4PrefixLimitPatchProperties', module='types')
        key "nativeIpv6PrefixLimit": ForwardRef('NativeIpv6PrefixLimitPatchProperties', module='types')
        key "staticRouteConfiguration": ForwardRef('StaticRoutePatchConfiguration', module='types')
        annotation: str
        bgpConfiguration: BgpPatchConfiguration
        connectedIPv4Subnets: list[ConnectedSubnetPatch]
        connectedIPv6Subnets: list[ConnectedSubnetPatch]
        egressAclId: str
        exportRoutePolicy: ExportRoutePolicy
        importRoutePolicy: ImportRoutePolicy
        ingressAclId: str
        isMonitoringEnabled: Union[str, IsMonitoringEnabled]
        mtu: int
        nativeIpv4PrefixLimit: NativeIpv4PrefixLimitPatchProperties
        nativeIpv6PrefixLimit: NativeIpv6PrefixLimitPatchProperties
        staticRouteConfiguration: StaticRoutePatchConfiguration


    class azure.mgmt.managednetworkfabric.types.InternalNetworkProperties(TypedDict, total=False):
        key "administrativeState": Union[str, AdministrativeState]
        key "annotation": str
        key "bgpConfiguration": ForwardRef('BgpConfiguration', module='types')
        key "configurationState": Union[str, ConfigurationState]
        key "egressAclId": str
        key "exportRoutePolicy": ForwardRef('ExportRoutePolicy', module='types')
        key "extension": Union[str, Extension]
        key "importRoutePolicy": ForwardRef('ImportRoutePolicy', module='types')
        key "ingressAclId": str
        key "isMonitoringEnabled": Union[str, IsMonitoringEnabled]
        key "lastOperation": ForwardRef('LastOperationProperties', module='types')
        key "mtu": int
        key "nativeIpv4PrefixLimit": ForwardRef('NativeIpv4PrefixLimitProperties', module='types')
        key "nativeIpv6PrefixLimit": ForwardRef('NativeIpv6PrefixLimitProperties', module='types')
        key "networkFabricId": str
        key "provisioningState": Union[str, ProvisioningState]
        key "staticRouteConfiguration": ForwardRef('StaticRouteConfiguration', module='types')
        key "vlanId": Required[int]
        administrativeState: Union[str, AdministrativeState]
        annotation: str
        bgpConfiguration: BgpConfiguration
        configurationState: Union[str, ConfigurationState]
        connectedIPv4Subnets: list[ConnectedSubnet]
        connectedIPv6Subnets: list[ConnectedSubnet]
        egressAclId: str
        exportRoutePolicy: ExportRoutePolicy
        extension: Union[str, Extension]
        importRoutePolicy: ImportRoutePolicy
        ingressAclId: str
        isMonitoringEnabled: Union[str, IsMonitoringEnabled]
        lastOperation: LastOperationProperties
        mtu: int
        nativeIpv4PrefixLimit: NativeIpv4PrefixLimitProperties
        nativeIpv6PrefixLimit: NativeIpv6PrefixLimitProperties
        networkFabricId: str
        provisioningState: Union[str, ProvisioningState]
        staticRouteConfiguration: StaticRouteConfiguration
        vlanId: int


    class azure.mgmt.managednetworkfabric.types.InternalNetworkUpdateBfdAdministrativeStateRequest(TypedDict, total=False):
        key "administrativeState": Union[str, BfdAdministrativeState]
        key "neighborAddress": str
        key "routeType": Union[str, InternalNetworkRouteType]
        administrativeState: Union[str, BfdAdministrativeState]
        neighborAddress: str
        routeType: Union[str, InternalNetworkRouteType]


    class azure.mgmt.managednetworkfabric.types.InternalNetworkUpdateBgpAdministrativeStateRequest(TypedDict, total=False):
        key "administrativeState": Union[str, BgpAdministrativeState]
        key "neighborAddress": str
        administrativeState: Union[str, BgpAdministrativeState]
        neighborAddress: str


    class azure.mgmt.managednetworkfabric.types.InternetGateway(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[InternetGatewayProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: InternetGatewayProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managednetworkfabric.types.InternetGatewayPatch(TagsUpdate):
        key "properties": ForwardRef('InternetGatewayPatchProperties', module='types')
        properties: InternetGatewayPatchProperties
        tags: dict[str, str]


    class azure.mgmt.managednetworkfabric.types.InternetGatewayPatchProperties(TypedDict, total=False):
        key "internetGatewayRuleId": str
        internetGatewayRuleId: str


    class azure.mgmt.managednetworkfabric.types.InternetGatewayProperties(TypedDict, total=False):
        key "annotation": str
        key "internetGatewayRuleId": str
        key "internetGatewayType": Union[str, GatewayType]
        key "ipv4Address": str
        key "lastOperation": ForwardRef('LastOperationProperties', module='types')
        key "networkFabricControllerId": Required[str]
        key "port": int
        key "provisioningState": Union[str, ProvisioningState]
        key "type": Union[str, GatewayType]
        annotation: str
        internetGatewayRuleId: str
        internetGatewayType: Union[str, GatewayType]
        ipv4Address: str
        lastOperation: LastOperationProperties
        networkFabricControllerId: str
        port: int
        provisioningState: Union[str, ProvisioningState]
        type: Union[str, GatewayType]


    class azure.mgmt.managednetworkfabric.types.InternetGatewayRule(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[InternetGatewayRuleProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: InternetGatewayRuleProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managednetworkfabric.types.InternetGatewayRulePatch(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.managednetworkfabric.types.InternetGatewayRuleProperties(AnnotationResource):
        key "annotation": str
        key "lastOperation": ForwardRef('LastOperationProperties', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "ruleProperties": Required[RuleProperties]
        annotation: str
        internetGatewayIds: list[str]
        lastOperation: LastOperationProperties
        provisioningState: Union[str, ProvisioningState]
        ruleProperties: RuleProperties


    class azure.mgmt.managednetworkfabric.types.IpCommunity(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[IpCommunityProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: IpCommunityProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managednetworkfabric.types.IpCommunityIdList(TypedDict, total=False):
        ipCommunityIds: list[str]


    class azure.mgmt.managednetworkfabric.types.IpCommunityPatch(TagsUpdate):
        key "properties": ForwardRef('IpCommunityPatchableProperties', module='types')
        properties: IpCommunityPatchableProperties
        tags: dict[str, str]


    class azure.mgmt.managednetworkfabric.types.IpCommunityPatchableProperties(TypedDict, total=False):
        ipCommunityRules: list[IpCommunityRule]


    class azure.mgmt.managednetworkfabric.types.IpCommunityProperties(TypedDict, total=False):
        key "administrativeState": Union[str, AdministrativeState]
        key "annotation": str
        key "configurationState": Union[str, ConfigurationState]
        key "ipCommunityRules": Required[list[IpCommunityRule]]
        key "lastOperation": ForwardRef('LastOperationProperties', module='types')
        key "networkFabricId": str
        key "provisioningState": Union[str, ProvisioningState]
        administrativeState: Union[str, AdministrativeState]
        annotation: str
        configurationState: Union[str, ConfigurationState]
        ipCommunityRules: list[IpCommunityRule]
        lastOperation: LastOperationProperties
        networkFabricId: str
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.managednetworkfabric.types.IpCommunityRule(TypedDict, total=False):
        key "action": Required[Union[str, CommunityActionTypes]]
        key "communityMembers": Required[list[str]]
        key "sequenceNumber": Required[int]
        action: Union[str, CommunityActionTypes]
        communityMembers: list[str]
        sequenceNumber: int
        wellKnownCommunities: list[Union[str, WellKnownCommunities]]


    class azure.mgmt.managednetworkfabric.types.IpExtendedCommunity(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[IpExtendedCommunityProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: IpExtendedCommunityProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managednetworkfabric.types.IpExtendedCommunityIdList(TypedDict, total=False):
        ipExtendedCommunityIds: list[str]


    class azure.mgmt.managednetworkfabric.types.IpExtendedCommunityPatch(TagsUpdate):
        key "properties": ForwardRef('IpExtendedCommunityPatchProperties', module='types')
        properties: IpExtendedCommunityPatchProperties
        tags: dict[str, str]


    class azure.mgmt.managednetworkfabric.types.IpExtendedCommunityPatchProperties(TypedDict, total=False):
        key "annotation": str
        annotation: str
        ipExtendedCommunityRules: list[IpExtendedCommunityRule]


    class azure.mgmt.managednetworkfabric.types.IpExtendedCommunityProperties(TypedDict, total=False):
        key "administrativeState": Union[str, AdministrativeState]
        key "annotation": str
        key "configurationState": Union[str, ConfigurationState]
        key "ipExtendedCommunityRules": Required[list[IpExtendedCommunityRule]]
        key "lastOperation": ForwardRef('LastOperationProperties', module='types')
        key "networkFabricId": str
        key "provisioningState": Union[str, ProvisioningState]
        administrativeState: Union[str, AdministrativeState]
        annotation: str
        configurationState: Union[str, ConfigurationState]
        ipExtendedCommunityRules: list[IpExtendedCommunityRule]
        lastOperation: LastOperationProperties
        networkFabricId: str
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.managednetworkfabric.types.IpExtendedCommunityRule(TypedDict, total=False):
        key "action": Required[Union[str, CommunityActionTypes]]
        key "routeTargets": Required[list[str]]
        key "sequenceNumber": Required[int]
        action: Union[str, CommunityActionTypes]
        routeTargets: list[str]
        sequenceNumber: int


    class azure.mgmt.managednetworkfabric.types.IpGroupPatchProperties(TypedDict, total=False):
        key "ipAddressType": Union[str, IPAddressType]
        key "name": str
        ipAddressType: Union[str, IPAddressType]
        ipPrefixes: list[str]
        name: str


    class azure.mgmt.managednetworkfabric.types.IpGroupProperties(TypedDict, total=False):
        key "ipAddressType": Union[str, IPAddressType]
        key "name": str
        ipAddressType: Union[str, IPAddressType]
        ipPrefixes: list[str]
        name: str


    class azure.mgmt.managednetworkfabric.types.IpMatchCondition(TypedDict, total=False):
        key "prefixType": Union[str, PrefixType]
        key "type": Union[str, SourceDestinationType]
        ipGroupNames: list[str]
        ipPrefixValues: list[str]
        prefixType: Union[str, PrefixType]
        type: Union[str, SourceDestinationType]


    class azure.mgmt.managednetworkfabric.types.IpMatchConditionPatch(TypedDict, total=False):
        key "prefixType": Union[str, PrefixType]
        key "type": Union[str, SourceDestinationType]
        ipGroupNames: list[str]
        ipPrefixValues: list[str]
        prefixType: Union[str, PrefixType]
        type: Union[str, SourceDestinationType]


    class azure.mgmt.managednetworkfabric.types.IpPrefix(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[IpPrefixProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: IpPrefixProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managednetworkfabric.types.IpPrefixPatch(TagsUpdate):
        key "properties": ForwardRef('IpPrefixPatchProperties', module='types')
        properties: IpPrefixPatchProperties
        tags: dict[str, str]


    class azure.mgmt.managednetworkfabric.types.IpPrefixPatchProperties(TypedDict, total=False):
        key "annotation": str
        annotation: str
        ipPrefixRules: list[IpPrefixRule]


    class azure.mgmt.managednetworkfabric.types.IpPrefixProperties(TypedDict, total=False):
        key "administrativeState": Union[str, AdministrativeState]
        key "annotation": str
        key "configurationState": Union[str, ConfigurationState]
        key "ipPrefixRules": Required[list[IpPrefixRule]]
        key "lastOperation": ForwardRef('LastOperationProperties', module='types')
        key "networkFabricId": str
        key "provisioningState": Union[str, ProvisioningState]
        administrativeState: Union[str, AdministrativeState]
        annotation: str
        configurationState: Union[str, ConfigurationState]
        ipPrefixRules: list[IpPrefixRule]
        lastOperation: LastOperationProperties
        networkFabricId: str
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.managednetworkfabric.types.IpPrefixRule(TypedDict, total=False):
        key "action": Required[Union[str, CommunityActionTypes]]
        key "condition": Union[str, Condition]
        key "networkPrefix": Required[str]
        key "sequenceNumber": Required[int]
        key "subnetMaskLength": str
        action: Union[str, CommunityActionTypes]
        condition: Union[str, Condition]
        networkPrefix: str
        sequenceNumber: int
        subnetMaskLength: str


    class azure.mgmt.managednetworkfabric.types.IsolationDomainPatchProperties(TypedDict, total=False):
        key "encapsulation": Union[str, Encapsulation]
        encapsulation: Union[str, Encapsulation]
        neighborGroupIds: list[str]


    class azure.mgmt.managednetworkfabric.types.IsolationDomainProperties(TypedDict, total=False):
        key "encapsulation": Union[str, Encapsulation]
        encapsulation: Union[str, Encapsulation]
        neighborGroupIds: list[str]


    class azure.mgmt.managednetworkfabric.types.L2IsolationDomain(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[L2IsolationDomainProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: L2IsolationDomainProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managednetworkfabric.types.L2IsolationDomainPatch(TagsUpdate):
        key "identity": ForwardRef('ManagedServiceIdentityPatch', module='types')
        key "properties": ForwardRef('L2IsolationDomainPatchProperties', module='types')
        identity: ManagedServiceIdentityPatch
        properties: L2IsolationDomainPatchProperties
        tags: dict[str, str]


    class azure.mgmt.managednetworkfabric.types.L2IsolationDomainPatchProperties(AnnotationResource):
        key "annotation": str
        key "extendedVlan": Union[str, ExtendedVlan]
        key "mtu": int
        key "networkToNetworkInterconnectId": str
        annotation: str
        extendedVlan: Union[str, ExtendedVlan]
        mtu: int
        networkToNetworkInterconnectId: str


    class azure.mgmt.managednetworkfabric.types.L2IsolationDomainProperties(AnnotationResource):
        key "administrativeState": Union[str, AdministrativeState]
        key "annotation": str
        key "configurationState": Union[str, ConfigurationState]
        key "extendedVlan": Union[str, ExtendedVlan]
        key "lastOperation": ForwardRef('LastOperationProperties', module='types')
        key "mtu": int
        key "networkFabricId": Required[str]
        key "networkToNetworkInterconnectId": str
        key "provisioningState": Union[str, ProvisioningState]
        key "vlanId": Required[int]
        administrativeState: Union[str, AdministrativeState]
        annotation: str
        configurationState: Union[str, ConfigurationState]
        extendedVlan: Union[str, ExtendedVlan]
        lastOperation: LastOperationProperties
        mtu: int
        networkFabricId: str
        networkToNetworkInterconnectId: str
        provisioningState: Union[str, ProvisioningState]
        vlanId: int


    class azure.mgmt.managednetworkfabric.types.L3ExportRoutePolicy(TypedDict, total=False):
        key "exportIpv4RoutePolicyId": str
        key "exportIpv6RoutePolicyId": str
        exportIpv4RoutePolicyId: str
        exportIpv6RoutePolicyId: str


    class azure.mgmt.managednetworkfabric.types.L3ExportRoutePolicyPatch(TypedDict, total=False):
        key "exportIpv4RoutePolicyId": str
        key "exportIpv6RoutePolicyId": str
        exportIpv4RoutePolicyId: str
        exportIpv6RoutePolicyId: str


    class azure.mgmt.managednetworkfabric.types.L3IsolationDomain(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[L3IsolationDomainProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: L3IsolationDomainProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managednetworkfabric.types.L3IsolationDomainPatch(TagsUpdate):
        key "identity": ForwardRef('ManagedServiceIdentityPatch', module='types')
        key "properties": ForwardRef('L3IsolationDomainPatchProperties', module='types')
        identity: ManagedServiceIdentityPatch
        properties: L3IsolationDomainPatchProperties
        tags: dict[str, str]


    class azure.mgmt.managednetworkfabric.types.L3IsolationDomainPatchProperties(TypedDict, total=False):
        key "aggregateRouteConfiguration": ForwardRef('AggregateRoutePatchConfiguration', module='types')
        key "annotation": str
        key "connectedSubnetRoutePolicy": ForwardRef('ConnectedSubnetRoutePolicyPatch', module='types')
        key "exportPolicyConfiguration": ForwardRef('BmpExportPolicyPatchProperties', module='types')
        key "redistributeConnectedSubnets": Union[str, RedistributeConnectedSubnets]
        key "redistributeStaticRoutes": Union[str, RedistributeStaticRoutes]
        key "staticRouteRoutePolicy": ForwardRef('StaticRoutePolicyPatch', module='types')
        key "v4routePrefixLimit": ForwardRef('RoutePrefixLimitPatchProperties', module='types')
        key "v6routePrefixLimit": ForwardRef('RoutePrefixLimitPatchProperties', module='types')
        aggregateRouteConfiguration: AggregateRoutePatchConfiguration
        annotation: str
        connectedSubnetRoutePolicy: ConnectedSubnetRoutePolicyPatch
        exportPolicyConfiguration: BmpExportPolicyPatchProperties
        redistributeConnectedSubnets: Union[str, RedistributeConnectedSubnets]
        redistributeStaticRoutes: Union[str, RedistributeStaticRoutes]
        staticRouteRoutePolicy: StaticRoutePolicyPatch
        v4routePrefixLimit: RoutePrefixLimitPatchProperties
        v6routePrefixLimit: RoutePrefixLimitPatchProperties


    class azure.mgmt.managednetworkfabric.types.L3IsolationDomainProperties(TypedDict, total=False):
        key "administrativeState": Union[str, AdministrativeState]
        key "aggregateRouteConfiguration": ForwardRef('AggregateRouteConfiguration', module='types')
        key "annotation": str
        key "configurationState": Union[str, ConfigurationState]
        key "connectedSubnetRoutePolicy": ForwardRef('ConnectedSubnetRoutePolicy', module='types')
        key "exportPolicyConfiguration": ForwardRef('BmpExportPolicyProperties', module='types')
        key "lastOperation": ForwardRef('LastOperationProperties', module='types')
        key "networkFabricId": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        key "redistributeConnectedSubnets": Union[str, RedistributeConnectedSubnets]
        key "redistributeStaticRoutes": Union[str, RedistributeStaticRoutes]
        key "staticRouteRoutePolicy": ForwardRef('StaticRoutePolicy', module='types')
        key "uniqueRdConfiguration": ForwardRef('L3UniqueRouteDistinguisherProperties', module='types')
        key "v4routePrefixLimit": ForwardRef('RoutePrefixLimitProperties', module='types')
        key "v6routePrefixLimit": ForwardRef('RoutePrefixLimitProperties', module='types')
        administrativeState: Union[str, AdministrativeState]
        aggregateRouteConfiguration: AggregateRouteConfiguration
        annotation: str
        configurationState: Union[str, ConfigurationState]
        connectedSubnetRoutePolicy: ConnectedSubnetRoutePolicy
        exportPolicyConfiguration: BmpExportPolicyProperties
        lastOperation: LastOperationProperties
        networkFabricId: str
        provisioningState: Union[str, ProvisioningState]
        redistributeConnectedSubnets: Union[str, RedistributeConnectedSubnets]
        redistributeStaticRoutes: Union[str, RedistributeStaticRoutes]
        staticRouteRoutePolicy: StaticRoutePolicy
        uniqueRdConfiguration: L3UniqueRouteDistinguisherProperties
        v4routePrefixLimit: RoutePrefixLimitProperties
        v6routePrefixLimit: RoutePrefixLimitProperties


    class azure.mgmt.managednetworkfabric.types.L3OptionBPatchProperties(TypedDict, total=False):
        key "routeTargets": ForwardRef('RouteTargetPatchInformation', module='types')
        exportRouteTargets: list[str]
        importRouteTargets: list[str]
        routeTargets: RouteTargetPatchInformation


    class azure.mgmt.managednetworkfabric.types.L3OptionBProperties(TypedDict, total=False):
        key "routeTargets": ForwardRef('RouteTargetInformation', module='types')
        exportRouteTargets: list[str]
        importRouteTargets: list[str]
        routeTargets: RouteTargetInformation


    class azure.mgmt.managednetworkfabric.types.L3UniqueRouteDistinguisherProperties(TypedDict, total=False):
        uniqueRds: list[str]


    class azure.mgmt.managednetworkfabric.types.LastOperationProperties(TypedDict, total=False):
        key "details": str
        details: str


    class azure.mgmt.managednetworkfabric.types.Layer2Configuration(TypedDict, total=False):
        key "mtu": int
        interfaces: list[str]
        mtu: int


    class azure.mgmt.managednetworkfabric.types.Layer2ConfigurationPatch(TypedDict, total=False):
        key "mtu": int
        interfaces: list[str]
        mtu: int


    class azure.mgmt.managednetworkfabric.types.Layer3IpPrefixPatchProperties(TypedDict, total=False):
        key "primaryIpv4Prefix": str
        key "primaryIpv6Prefix": str
        key "secondaryIpv4Prefix": str
        key "secondaryIpv6Prefix": str
        primaryIpv4Prefix: str
        primaryIpv6Prefix: str
        secondaryIpv4Prefix: str
        secondaryIpv6Prefix: str


    class azure.mgmt.managednetworkfabric.types.Layer3IpPrefixProperties(TypedDict, total=False):
        key "primaryIpv4Prefix": str
        key "primaryIpv6Prefix": str
        key "secondaryIpv4Prefix": str
        key "secondaryIpv6Prefix": str
        primaryIpv4Prefix: str
        primaryIpv6Prefix: str
        secondaryIpv4Prefix: str
        secondaryIpv6Prefix: str


    class azure.mgmt.managednetworkfabric.types.ManagedResourceGroupConfiguration(TypedDict, total=False):
        key "location": str
        key "name": str
        location: str
        name: str


    class azure.mgmt.managednetworkfabric.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.managednetworkfabric.types.ManagedServiceIdentityPatch(TypedDict, total=False):
        key "type": Union[str, ManagedServiceIdentityType]
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.managednetworkfabric.types.ManagementNetworkConfigurationProperties(TypedDict, total=False):
        key "infrastructureVpnConfiguration": Required[VpnConfigurationProperties]
        key "workloadVpnConfiguration": Required[VpnConfigurationProperties]
        infrastructureVpnConfiguration: VpnConfigurationProperties
        workloadVpnConfiguration: VpnConfigurationProperties


    class azure.mgmt.managednetworkfabric.types.ManagementNetworkPatchConfiguration(TypedDict, total=False):
        key "infrastructureVpnConfiguration": ForwardRef('VpnConfigurationPatchableProperties', module='types')
        key "workloadVpnConfiguration": ForwardRef('VpnConfigurationPatchableProperties', module='types')
        infrastructureVpnConfiguration: VpnConfigurationPatchableProperties
        workloadVpnConfiguration: VpnConfigurationPatchableProperties


    class azure.mgmt.managednetworkfabric.types.NativeIpv4PrefixLimitPatchProperties(TypedDict, total=False):
        prefixLimits: list[PrefixLimitPatchProperties]


    class azure.mgmt.managednetworkfabric.types.NativeIpv4PrefixLimitProperties(TypedDict, total=False):
        prefixLimits: list[PrefixLimitProperties]


    class azure.mgmt.managednetworkfabric.types.NativeIpv6PrefixLimitPatchProperties(TypedDict, total=False):
        prefixLimits: list[PrefixLimitPatchProperties]


    class azure.mgmt.managednetworkfabric.types.NativeIpv6PrefixLimitProperties(TypedDict, total=False):
        prefixLimits: list[PrefixLimitProperties]


    class azure.mgmt.managednetworkfabric.types.NeighborAddress(TypedDict, total=False):
        key "address": str
        key "bfdAdministrativeState": Union[str, BfdAdministrativeState]
        key "bgpAdministrativeState": Union[str, BgpAdministrativeState]
        key "configurationState": Union[str, ConfigurationState]
        address: str
        bfdAdministrativeState: Union[str, BfdAdministrativeState]
        bgpAdministrativeState: Union[str, BgpAdministrativeState]
        configurationState: Union[str, ConfigurationState]


    class azure.mgmt.managednetworkfabric.types.NeighborAddressPatch(TypedDict, total=False):
        key "address": str
        key "bfdAdministrativeState": Union[str, BfdAdministrativeState]
        key "bgpAdministrativeState": Union[str, BgpAdministrativeState]
        key "configurationState": Union[str, ConfigurationState]
        address: str
        bfdAdministrativeState: Union[str, BfdAdministrativeState]
        bgpAdministrativeState: Union[str, BgpAdministrativeState]
        configurationState: Union[str, ConfigurationState]


    class azure.mgmt.managednetworkfabric.types.NeighborGroup(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[NeighborGroupProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: NeighborGroupProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managednetworkfabric.types.NeighborGroupDestination(TypedDict, total=False):
        ipv4Addresses: list[str]
        ipv6Addresses: list[str]


    class azure.mgmt.managednetworkfabric.types.NeighborGroupDestinationPatch(TypedDict, total=False):
        ipv4Addresses: list[str]
        ipv6Addresses: list[str]


    class azure.mgmt.managednetworkfabric.types.NeighborGroupPatch(TagsUpdate):
        key "identity": ForwardRef('ManagedServiceIdentityPatch', module='types')
        key "properties": ForwardRef('NeighborGroupPatchProperties', module='types')
        identity: ManagedServiceIdentityPatch
        properties: NeighborGroupPatchProperties
        tags: dict[str, str]


    class azure.mgmt.managednetworkfabric.types.NeighborGroupPatchProperties(TypedDict, total=False):
        key "annotation": str
        key "destination": ForwardRef('NeighborGroupDestinationPatch', module='types')
        annotation: str
        destination: NeighborGroupDestinationPatch


    class azure.mgmt.managednetworkfabric.types.NeighborGroupProperties(TypedDict, total=False):
        key "administrativeState": Union[str, AdministrativeState]
        key "annotation": str
        key "configurationState": Union[str, ConfigurationState]
        key "destination": Required[NeighborGroupDestination]
        key "lastOperation": ForwardRef('LastOperationProperties', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        administrativeState: Union[str, AdministrativeState]
        annotation: str
        configurationState: Union[str, ConfigurationState]
        destination: NeighborGroupDestination
        lastOperation: LastOperationProperties
        networkFabricIds: list[str]
        networkTapIds: list[str]
        networkTapRuleIds: list[str]
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.managednetworkfabric.types.NetworkBootstrapDevice(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[NetworkBootstrapDeviceProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: NetworkBootstrapDeviceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managednetworkfabric.types.NetworkBootstrapDevicePatch(TagsUpdate):
        key "identity": ForwardRef('ManagedServiceIdentityPatch', module='types')
        key "properties": ForwardRef('NetworkBootstrapDevicePatchProperties', module='types')
        identity: ManagedServiceIdentityPatch
        properties: NetworkBootstrapDevicePatchProperties
        tags: dict[str, str]


    class azure.mgmt.managednetworkfabric.types.NetworkBootstrapDevicePatchProperties(TypedDict, total=False):
        key "annotation": str
        key "hostName": str
        key "serialNumber": str
        annotation: str
        controlPlaneAcls: list[str]
        hostName: str
        serialNumber: str


    class azure.mgmt.managednetworkfabric.types.NetworkBootstrapDeviceProperties(TypedDict, total=False):
        key "administrativeState": Union[str, AdministrativeState]
        key "annotation": str
        key "configurationState": Union[str, ConfigurationState]
        key "dhcpV4ServerIpAddress": str
        key "hostName": str
        key "networkDeviceSku": str
        key "networkFabricId": str
        key "operationalState": Union[str, OperationalState]
        key "primaryManagementIpv4Address": str
        key "primaryManagementIpv6Address": str
        key "provisioningState": Union[str, ProvisioningState]
        key "secondaryManagementIpv4Address": str
        key "secondaryManagementIpv6Address": str
        key "serialNumber": str
        key "version": str
        administrativeState: Union[str, AdministrativeState]
        annotation: str
        configurationState: Union[str, ConfigurationState]
        controlPlaneAcls: list[str]
        dhcpV4ServerIpAddress: str
        hostName: str
        networkDeviceSku: str
        networkFabricId: str
        operationalState: Union[str, OperationalState]
        primaryManagementIpv4Address: str
        primaryManagementIpv6Address: str
        provisioningState: Union[str, ProvisioningState]
        secondaryManagementIpv4Address: str
        secondaryManagementIpv6Address: str
        secretRotationStatus: list[SecretRotationStatus]
        serialNumber: str
        version: str


    class azure.mgmt.managednetworkfabric.types.NetworkBootstrapInterface(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[NetworkBootstrapInterfaceProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: NetworkBootstrapInterfaceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.managednetworkfabric.types.NetworkBootstrapInterfacePatch(TypedDict, total=False):
        key "properties": ForwardRef('NetworkBootstrapInterfacePatchProperties', module='types')
        properties: NetworkBootstrapInterfacePatchProperties


    class azure.mgmt.managednetworkfabric.types.NetworkBootstrapInterfacePatchProperties(AnnotationResource):
        key "additionalDescription": str
        key "annotation": str
        key "serialNumber": str
        additionalDescription: str
        annotation: str
        serialNumber: str


    class azure.mgmt.managednetworkfabric.types.NetworkBootstrapInterfaceProperties(AnnotationResource):
        key "additionalDescription": str
        key "administrativeState": Union[str, AdministrativeState]
        key "annotation": str
        key "configurationState": Union[str, ConfigurationState]
        key "connectedTo": str
        key "description": str
        key "interfaceType": Union[str, InterfaceType]
        key "ipv4Address": str
        key "ipv6Address": str
        key "operationalState": Union[str, OperationalState]
        key "physicalIdentifier": str
        key "provisioningState": Union[str, ProvisioningState]
        key "serialNumber": str
        additionalDescription: str
        administrativeState: Union[str, AdministrativeState]
        annotation: str
        configurationState: Union[str, ConfigurationState]
        connectedTo: str
        description: str
        interfaceType: Union[str, InterfaceType]
        ipv4Address: str
        ipv6Address: str
        operationalState: Union[str, OperationalState]
        physicalIdentifier: str
        provisioningState: Union[str, ProvisioningState]
        serialNumber: str


    class azure.mgmt.managednetworkfabric.types.NetworkDevice(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[NetworkDeviceProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: NetworkDeviceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managednetworkfabric.types.NetworkDevicePatchParameters(TagsUpdate):
        key "identity": ForwardRef('ManagedServiceIdentityPatch', module='types')
        key "properties": ForwardRef('NetworkDevicePatchParametersProperties', module='types')
        identity: ManagedServiceIdentityPatch
        properties: NetworkDevicePatchParametersProperties
        tags: dict[str, str]


    class azure.mgmt.managednetworkfabric.types.NetworkDevicePatchParametersProperties(TypedDict, total=False):
        key "annotation": str
        key "hostName": str
        key "identitySelector": ForwardRef('IdentitySelectorPatch', module='types')
        key "serialNumber": str
        annotation: str
        hostName: str
        identitySelector: IdentitySelectorPatch
        serialNumber: str


    class azure.mgmt.managednetworkfabric.types.NetworkDeviceProperties(TypedDict, total=False):
        key "administrativeState": Union[str, AdministrativeState]
        key "annotation": str
        key "configurationState": Union[str, ConfigurationState]
        key "hostName": str
        key "identitySelector": ForwardRef('IdentitySelector', module='types')
        key "lastOperation": ForwardRef('LastOperationProperties', module='types')
        key "managementIpv4Address": str
        key "managementIpv6Address": str
        key "networkDeviceRole": Union[str, NetworkDeviceRole]
        key "networkDeviceSku": str
        key "networkFabricId": str
        key "networkRackId": str
        key "operationalState": Union[str, OperationalState]
        key "provisioningState": Union[str, ProvisioningState]
        key "rwDeviceConfig": str
        key "serialNumber": Required[str]
        key "version": str
        administrativeState: Union[str, AdministrativeState]
        annotation: str
        certificateRotationStatus: list[CertificateRotationStatus]
        configurationState: Union[str, ConfigurationState]
        hostName: str
        identitySelector: IdentitySelector
        lastOperation: LastOperationProperties
        managementIpv4Address: str
        managementIpv6Address: str
        networkDeviceRole: Union[str, NetworkDeviceRole]
        networkDeviceSku: str
        networkFabricId: str
        networkRackId: str
        operationalState: Union[str, OperationalState]
        provisioningState: Union[str, ProvisioningState]
        rwDeviceConfig: str
        secretRotationStatus: list[SecretRotationStatus]
        serialNumber: str
        version: str


    class azure.mgmt.managednetworkfabric.types.NetworkDeviceUpgradeRequest(TypedDict, total=False):
        key "rwDeviceConfigUrl": str
        key "version": Required[str]
        rwDeviceConfigUrl: str
        version: str


    class azure.mgmt.managednetworkfabric.types.NetworkFabric(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[NetworkFabricProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: NetworkFabricProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managednetworkfabric.types.NetworkFabricController(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[NetworkFabricControllerProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: NetworkFabricControllerProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managednetworkfabric.types.NetworkFabricControllerPatch(TagsUpdate):
        key "identity": ForwardRef('ManagedServiceIdentityPatch', module='types')
        key "properties": ForwardRef('NetworkFabricControllerPatchProperties', module='types')
        identity: ManagedServiceIdentityPatch
        properties: NetworkFabricControllerPatchProperties
        tags: dict[str, str]


    class azure.mgmt.managednetworkfabric.types.NetworkFabricControllerPatchProperties(TypedDict, total=False):
        infrastructureExpressRouteConnections: list[ExpressRouteConnectionInformation]
        workloadExpressRouteConnections: list[ExpressRouteConnectionInformation]


    class azure.mgmt.managednetworkfabric.types.NetworkFabricControllerProperties(TypedDict, total=False):
        key "annotation": str
        key "infrastructureServices": ForwardRef('ControllerServices', module='types')
        key "ipv4AddressSpace": str
        key "ipv6AddressSpace": str
        key "isWorkloadManagementNetworkEnabled": Union[str, IsWorkloadManagementNetworkEnabled]
        key "lastOperation": ForwardRef('LastOperationProperties', module='types')
        key "managedResourceGroupConfiguration": ForwardRef('ManagedResourceGroupConfiguration', module='types')
        key "nfcSku": Union[str, NfcSku]
        key "operationalState": Union[str, OperationalState]
        key "provisioningState": Union[str, ProvisioningState]
        key "vmProfile": ForwardRef('VmProfile', module='types')
        key "workloadServices": ForwardRef('ControllerServices', module='types')
        annotation: str
        infrastructureExpressRouteConnections: list[ExpressRouteConnectionInformation]
        infrastructureServices: ControllerServices
        ipv4AddressSpace: str
        ipv6AddressSpace: str
        isWorkloadManagementNetworkEnabled: Union[str, IsWorkloadManagementNetworkEnabled]
        lastOperation: LastOperationProperties
        managedResourceGroupConfiguration: ManagedResourceGroupConfiguration
        networkFabricIds: list[str]
        nfcSku: Union[str, NfcSku]
        operationalState: Union[str, OperationalState]
        provisioningState: Union[str, ProvisioningState]
        tenantInternetGatewayIds: list[str]
        vmProfile: VmProfile
        workloadExpressRouteConnections: list[ExpressRouteConnectionInformation]
        workloadServices: ControllerServices


    class azure.mgmt.managednetworkfabric.types.NetworkFabricLockRequest(TypedDict, total=False):
        key "action": Union[str, NetworkFabricLockAction]
        key "lockType": Union[str, NetworkFabricLockType]
        action: Union[str, NetworkFabricLockAction]
        lockType: Union[str, NetworkFabricLockType]


    class azure.mgmt.managednetworkfabric.types.NetworkFabricPatch(TagsUpdate):
        key "identity": ForwardRef('ManagedServiceIdentityPatch', module='types')
        key "properties": ForwardRef('NetworkFabricPatchProperties', module='types')
        identity: ManagedServiceIdentityPatch
        properties: NetworkFabricPatchProperties
        tags: dict[str, str]


    class azure.mgmt.managednetworkfabric.types.NetworkFabricPatchProperties(TypedDict, total=False):
        key "annotation": str
        key "authorizedTransceiver": ForwardRef('AuthorizedTransceiverPatchProperties', module='types')
        key "fabricASN": int
        key "hardwareAlertThreshold": int
        key "ipv4Prefix": str
        key "ipv6Prefix": str
        key "managementNetworkConfiguration": ForwardRef('ManagementNetworkPatchConfiguration', module='types')
        key "qosConfiguration": ForwardRef('QosPatchProperties', module='types')
        key "rackCount": int
        key "secretArchiveSettings": Optional[SecretArchivePatchSettings]
        key "serverCountPerRack": int
        key "storageAccountConfiguration": ForwardRef('StorageAccountPatchConfiguration', module='types')
        key "terminalServerConfiguration": ForwardRef('TerminalServerPatchConfiguration', module='types')
        key "uniqueRdConfiguration": ForwardRef('UniqueRouteDistinguisherPatchProperties', module='types')
        annotation: str
        authorizedTransceiver: AuthorizedTransceiverPatchProperties
        controlPlaneAcls: list[str]
        fabricASN: int
        featureFlags: list[FeatureFlagProperties]
        hardwareAlertThreshold: int
        ipv4Prefix: str
        ipv6Prefix: str
        managementNetworkConfiguration: ManagementNetworkPatchConfiguration
        qosConfiguration: QosPatchProperties
        rackCount: int
        secretArchiveSettings: SecretArchivePatchSettings
        serverCountPerRack: int
        storageAccountConfiguration: StorageAccountPatchConfiguration
        terminalServerConfiguration: TerminalServerPatchConfiguration
        trustedIpPrefixes: list[str]
        uniqueRdConfiguration: UniqueRouteDistinguisherPatchProperties
        upgradeProfile: list[UpgradeProfilePropertiesPatchProperties]


    class azure.mgmt.managednetworkfabric.types.NetworkFabricProperties(AnnotationResource):
        key "administrativeState": Union[str, AdministrativeState]
        key "annotation": str
        key "authorizedTransceiver": ForwardRef('AuthorizedTransceiverProperties', module='types')
        key "configurationState": Union[str, ConfigurationState]
        key "fabricASN": Required[int]
        key "fabricVersion": str
        key "hardwareAlertThreshold": int
        key "ipv4Prefix": Required[str]
        key "ipv6Prefix": str
        key "lastOperation": ForwardRef('LastOperationProperties', module='types')
        key "managementNetworkConfiguration": Required[ManagementNetworkConfigurationProperties]
        key "networkBootstrapDeviceId": str
        key "networkFabricControllerId": Required[str]
        key "networkFabricSku": Required[str]
        key "operationalState": Union[str, OperationalState]
        key "provisioningState": Union[str, ProvisioningState]
        key "qosConfiguration": ForwardRef('QosProperties', module='types')
        key "rackCount": int
        key "secretArchiveSettings": ForwardRef('SecretArchiveSettings', module='types')
        key "secretRotationSummary": ForwardRef('SecretRotationSummary', module='types')
        key "serverCountPerRack": Required[int]
        key "storageAccountConfiguration": ForwardRef('StorageAccountConfiguration', module='types')
        key "storageArrayCount": int
        key "terminalServerConfiguration": Required[TerminalServerConfiguration]
        key "uniqueRdConfiguration": ForwardRef('UniqueRouteDistinguisherProperties', module='types')
        activeCommitBatches: list[str]
        administrativeState: Union[str, AdministrativeState]
        annotation: str
        authorizedTransceiver: AuthorizedTransceiverProperties
        configurationState: Union[str, ConfigurationState]
        controlPlaneAcls: list[str]
        fabricASN: int
        fabricLocks: list[FabricLockProperties]
        fabricVersion: str
        featureFlags: list[FeatureFlagProperties]
        hardwareAlertThreshold: int
        ipv4Prefix: str
        ipv6Prefix: str
        l2IsolationDomains: list[str]
        l3IsolationDomains: list[str]
        lastOperation: LastOperationProperties
        managementNetworkConfiguration: ManagementNetworkConfigurationProperties
        networkBootstrapDeviceId: str
        networkFabricControllerId: str
        networkFabricSku: str
        operationalState: Union[str, OperationalState]
        provisioningState: Union[str, ProvisioningState]
        qosConfiguration: QosProperties
        rackCount: int
        racks: list[str]
        routerIds: list[str]
        secretArchiveSettings: SecretArchiveSettings
        secretRotationSummary: SecretRotationSummary
        serverCountPerRack: int
        storageAccountConfiguration: StorageAccountConfiguration
        storageArrayCount: int
        terminalServerConfiguration: TerminalServerConfiguration
        trustedIpPrefixes: list[str]
        uniqueRdConfiguration: UniqueRouteDistinguisherProperties
        upgradeProfile: list[UpgradeProfileProperties]


    class azure.mgmt.managednetworkfabric.types.NetworkInterface(ProxyResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "name": str
        key "properties": Required[NetworkInterfaceProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        name: str
        properties: NetworkInterfaceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.managednetworkfabric.types.NetworkInterfacePatch(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentityPatch', module='types')
        key "properties": ForwardRef('NetworkInterfacePatchProperties', module='types')
        identity: ManagedServiceIdentityPatch
        properties: NetworkInterfacePatchProperties


    class azure.mgmt.managednetworkfabric.types.NetworkInterfacePatchProperties(AnnotationResource):
        key "additionalDescription": str
        key "annotation": str
        additionalDescription: str
        annotation: str


    class azure.mgmt.managednetworkfabric.types.NetworkInterfaceProperties(AnnotationResource):
        key "additionalDescription": str
        key "administrativeState": Union[str, AdministrativeState]
        key "annotation": str
        key "configurationState": Union[str, ConfigurationState]
        key "connectedTo": str
        key "description": str
        key "interfaceType": Union[str, InterfaceType]
        key "ipv4Address": str
        key "ipv6Address": str
        key "lastOperation": ForwardRef('LastOperationProperties', module='types')
        key "networkFabricId": str
        key "operationalState": Union[str, OperationalState]
        key "physicalIdentifier": str
        key "provisioningState": Union[str, ProvisioningState]
        additionalDescription: str
        administrativeState: Union[str, AdministrativeState]
        annotation: str
        configurationState: Union[str, ConfigurationState]
        connectedTo: str
        description: str
        interfaceType: Union[str, InterfaceType]
        ipv4Address: str
        ipv6Address: str
        lastOperation: LastOperationProperties
        networkFabricId: str
        operationalState: Union[str, OperationalState]
        physicalIdentifier: str
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.managednetworkfabric.types.NetworkMonitor(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[NetworkMonitorProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: NetworkMonitorProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managednetworkfabric.types.NetworkMonitorPatch(TagsUpdate):
        key "properties": ForwardRef('NetworkMonitorPatchProperties', module='types')
        properties: NetworkMonitorPatchProperties
        tags: dict[str, str]


    class azure.mgmt.managednetworkfabric.types.NetworkMonitorPatchProperties(TypedDict, total=False):
        key "bmpConfiguration": ForwardRef('BmpConfigurationPatchProperties', module='types')
        bmpConfiguration: BmpConfigurationPatchProperties


    class azure.mgmt.managednetworkfabric.types.NetworkMonitorProperties(AnnotationResource):
        key "administrativeState": Union[str, AdministrativeState]
        key "annotation": str
        key "bmpConfiguration": ForwardRef('BmpConfigurationProperties', module='types')
        key "configurationState": Union[str, ConfigurationState]
        key "lastOperation": ForwardRef('LastOperationProperties', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        administrativeState: Union[str, AdministrativeState]
        annotation: str
        bmpConfiguration: BmpConfigurationProperties
        configurationState: Union[str, ConfigurationState]
        lastOperation: LastOperationProperties
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.managednetworkfabric.types.NetworkPacketBroker(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[NetworkPacketBrokerProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: NetworkPacketBrokerProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managednetworkfabric.types.NetworkPacketBrokerPatch(TagsUpdate):
        key "identity": ForwardRef('ManagedServiceIdentityPatch', module='types')
        key "properties": ForwardRef('NetworkPacketBrokerPatchProperties', module='types')
        identity: ManagedServiceIdentityPatch
        properties: NetworkPacketBrokerPatchProperties
        tags: dict[str, str]


    class azure.mgmt.managednetworkfabric.types.NetworkPacketBrokerPatchProperties(TypedDict, total=False):
        key "sourceNetworkTapRuleId": str
        sourceNetworkTapRuleId: str


    class azure.mgmt.managednetworkfabric.types.NetworkPacketBrokerProperties(TypedDict, total=False):
        key "configurationState": Union[str, ConfigurationState]
        key "lastOperation": ForwardRef('LastOperationProperties', module='types')
        key "networkFabricId": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        key "sourceNetworkTapRuleId": str
        configurationState: Union[str, ConfigurationState]
        lastOperation: LastOperationProperties
        neighborGroupIds: list[str]
        networkDeviceIds: list[str]
        networkFabricId: str
        networkTapIds: list[str]
        provisioningState: Union[str, ProvisioningState]
        sourceInterfaceIds: list[str]
        sourceNetworkTapRuleId: str


    class azure.mgmt.managednetworkfabric.types.NetworkRack(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[NetworkRackProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: NetworkRackProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managednetworkfabric.types.NetworkRackPatch(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.managednetworkfabric.types.NetworkRackProperties(AnnotationResource):
        key "annotation": str
        key "configurationState": Union[str, ConfigurationState]
        key "lastOperation": ForwardRef('LastOperationProperties', module='types')
        key "networkFabricId": Required[str]
        key "networkRackType": Union[str, NetworkRackType]
        key "provisioningState": Union[str, ProvisioningState]
        annotation: str
        configurationState: Union[str, ConfigurationState]
        lastOperation: LastOperationProperties
        networkDevices: list[str]
        networkFabricId: str
        networkRackType: Union[str, NetworkRackType]
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.managednetworkfabric.types.NetworkTap(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[NetworkTapProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: NetworkTapProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managednetworkfabric.types.NetworkTapPatch(TagsUpdate):
        key "identity": ForwardRef('ManagedServiceIdentityPatch', module='types')
        key "properties": ForwardRef('NetworkTapPatchProperties', module='types')
        identity: ManagedServiceIdentityPatch
        properties: NetworkTapPatchProperties
        tags: dict[str, str]


    class azure.mgmt.managednetworkfabric.types.NetworkTapPatchProperties(AnnotationResource):
        key "annotation": str
        key "pollingType": Union[str, PollingType]
        annotation: str
        destinations: list[DestinationPatchProperties]
        pollingType: Union[str, PollingType]


    class azure.mgmt.managednetworkfabric.types.NetworkTapProperties(AnnotationResource):
        key "administrativeState": Union[str, AdministrativeState]
        key "annotation": str
        key "configurationState": Union[str, ConfigurationState]
        key "destinations": Required[list[DestinationProperties]]
        key "lastOperation": ForwardRef('LastOperationProperties', module='types')
        key "networkPacketBrokerId": Required[str]
        key "pollingType": Union[str, PollingType]
        key "provisioningState": Union[str, ProvisioningState]
        key "sourceTapRuleId": str
        administrativeState: Union[str, AdministrativeState]
        annotation: str
        configurationState: Union[str, ConfigurationState]
        destinations: list[DestinationProperties]
        lastOperation: LastOperationProperties
        networkFabricIds: list[str]
        networkPacketBrokerId: str
        pollingType: Union[str, PollingType]
        provisioningState: Union[str, ProvisioningState]
        sourceTapRuleId: str


    class azure.mgmt.managednetworkfabric.types.NetworkTapRule(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[NetworkTapRuleProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: NetworkTapRuleProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managednetworkfabric.types.NetworkTapRuleAction(TypedDict, total=False):
        key "destinationId": str
        key "isTimestampEnabled": Union[str, BooleanEnumProperty]
        key "matchConfigurationName": str
        key "truncate": str
        key "type": Union[str, TapRuleActionType]
        destinationId: str
        isTimestampEnabled: Union[str, BooleanEnumProperty]
        matchConfigurationName: str
        truncate: str
        type: Union[str, TapRuleActionType]


    class azure.mgmt.managednetworkfabric.types.NetworkTapRuleActionPatch(TypedDict, total=False):
        key "destinationId": str
        key "isTimestampEnabled": Union[str, BooleanEnumProperty]
        key "matchConfigurationName": str
        key "truncate": str
        key "type": Union[str, TapRuleActionType]
        destinationId: str
        isTimestampEnabled: Union[str, BooleanEnumProperty]
        matchConfigurationName: str
        truncate: str
        type: Union[str, TapRuleActionType]


    class azure.mgmt.managednetworkfabric.types.NetworkTapRuleMatchCondition(CommonMatchConditions):
        key "encapsulationType": Union[str, EncapsulationType]
        key "ipCondition": ForwardRef('IpMatchCondition', module='types')
        key "portCondition": ForwardRef('PortCondition', module='types')
        key "vlanMatchCondition": ForwardRef('VlanMatchCondition', module='types')
        encapsulationType: Union[str, EncapsulationType]
        ipCondition: IpMatchCondition
        portCondition: PortCondition
        protocolTypes: list[str]
        vlanMatchCondition: VlanMatchCondition


    class azure.mgmt.managednetworkfabric.types.NetworkTapRuleMatchConditionPatch(CommonMatchConditionsPatch):
        key "encapsulationType": Union[str, EncapsulationType]
        key "ipCondition": ForwardRef('IpMatchConditionPatch', module='types')
        key "portCondition": ForwardRef('PortConditionPatch', module='types')
        key "vlanMatchCondition": ForwardRef('VlanMatchConditionPatch', module='types')
        encapsulationType: Union[str, EncapsulationType]
        ipCondition: IpMatchConditionPatch
        portCondition: PortConditionPatch
        protocolTypes: list[str]
        vlanMatchCondition: VlanMatchConditionPatch


    class azure.mgmt.managednetworkfabric.types.NetworkTapRuleMatchConfiguration(TypedDict, total=False):
        key "ipAddressType": Union[str, IPAddressType]
        key "matchConfigurationName": str
        key "sequenceNumber": int
        actions: list[NetworkTapRuleAction]
        ipAddressType: Union[str, IPAddressType]
        matchConditions: list[NetworkTapRuleMatchCondition]
        matchConfigurationName: str
        sequenceNumber: int


    class azure.mgmt.managednetworkfabric.types.NetworkTapRuleMatchConfigurationPatch(TypedDict, total=False):
        key "ipAddressType": Union[str, IPAddressType]
        key "matchConfigurationName": str
        key "sequenceNumber": int
        actions: list[NetworkTapRuleActionPatch]
        ipAddressType: Union[str, IPAddressType]
        matchConditions: list[NetworkTapRuleMatchConditionPatch]
        matchConfigurationName: str
        sequenceNumber: int


    class azure.mgmt.managednetworkfabric.types.NetworkTapRulePatch(TagsUpdate):
        key "identity": ForwardRef('ManagedServiceIdentityPatch', module='types')
        key "properties": ForwardRef('NetworkTapRulePatchProperties', module='types')
        identity: ManagedServiceIdentityPatch
        properties: NetworkTapRulePatchProperties
        tags: dict[str, str]


    class azure.mgmt.managednetworkfabric.types.NetworkTapRulePatchProperties(TypedDict, total=False):
        key "annotation": str
        key "configurationType": Union[str, ConfigurationType]
        key "globalNetworkTapRuleActions": ForwardRef('GlobalNetworkTapRuleActionPatchProperties', module='types')
        key "identitySelector": ForwardRef('IdentitySelectorPatch', module='types')
        key "tapRulesUrl": str
        annotation: str
        configurationType: Union[str, ConfigurationType]
        dynamicMatchConfigurations: list[CommonDynamicMatchConfigurationPatch]
        globalNetworkTapRuleActions: GlobalNetworkTapRuleActionPatchProperties
        identitySelector: IdentitySelectorPatch
        matchConfigurations: list[NetworkTapRuleMatchConfigurationPatch]
        tapRulesUrl: str


    class azure.mgmt.managednetworkfabric.types.NetworkTapRuleProperties(TypedDict, total=False):
        key "administrativeState": Union[str, AdministrativeState]
        key "annotation": str
        key "configurationState": Union[str, ConfigurationState]
        key "configurationType": Required[Union[str, ConfigurationType]]
        key "globalNetworkTapRuleActions": ForwardRef('GlobalNetworkTapRuleActionProperties', module='types')
        key "identitySelector": ForwardRef('IdentitySelector', module='types')
        key "lastOperation": ForwardRef('LastOperationProperties', module='types')
        key "lastSyncedTime": str
        key "networkTapId": str
        key "pollingIntervalInSeconds": int
        key "provisioningState": Union[str, ProvisioningState]
        key "tapRulesUrl": str
        administrativeState: Union[str, AdministrativeState]
        annotation: str
        configurationState: Union[str, ConfigurationState]
        configurationType: Union[str, ConfigurationType]
        dynamicMatchConfigurations: list[CommonDynamicMatchConfiguration]
        globalNetworkTapRuleActions: GlobalNetworkTapRuleActionProperties
        identitySelector: IdentitySelector
        lastOperation: LastOperationProperties
        lastSyncedTime: str
        matchConfigurations: list[NetworkTapRuleMatchConfiguration]
        networkFabricIds: list[str]
        networkTapId: str
        networkTapIds: list[str]
        pollingIntervalInSeconds: int
        provisioningState: Union[str, ProvisioningState]
        tapRulesUrl: str


    class azure.mgmt.managednetworkfabric.types.NetworkToNetworkInterconnect(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[NetworkToNetworkInterconnectProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: NetworkToNetworkInterconnectProperties
        systemData: SystemData
        type: str


    class azure.mgmt.managednetworkfabric.types.NetworkToNetworkInterconnectPatch(ProxyResourceBase):
        key "id": str
        key "properties": ForwardRef('NetworkToNetworkInterconnectPatchProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        properties: NetworkToNetworkInterconnectPatchProperties
        systemData: SystemData
        type: str


    class azure.mgmt.managednetworkfabric.types.NetworkToNetworkInterconnectPatchProperties(TypedDict, total=False):
        key "egressAclId": str
        key "exportRoutePolicy": ForwardRef('ExportRoutePolicyInformationPatch', module='types')
        key "importRoutePolicy": ForwardRef('ImportRoutePolicyInformationPatch', module='types')
        key "ingressAclId": str
        key "layer2Configuration": ForwardRef('Layer2ConfigurationPatch', module='types')
        key "microBfdState": Union[str, MicroBfdState]
        key "npbStaticRouteConfiguration": ForwardRef('NpbStaticRouteConfigurationPatch', module='types')
        key "optionBLayer3Configuration": ForwardRef('OptionBLayer3ConfigurationPatchProperties', module='types')
        key "staticRouteConfiguration": ForwardRef('NniStaticRoutePatchConfiguration', module='types')
        egressAclId: str
        exportRoutePolicy: ExportRoutePolicyInformationPatch
        importRoutePolicy: ImportRoutePolicyInformationPatch
        ingressAclId: str
        layer2Configuration: Layer2ConfigurationPatch
        microBfdState: Union[str, MicroBfdState]
        npbStaticRouteConfiguration: NpbStaticRouteConfigurationPatch
        optionBLayer3Configuration: OptionBLayer3ConfigurationPatchProperties
        staticRouteConfiguration: NniStaticRoutePatchConfiguration


    class azure.mgmt.managednetworkfabric.types.NetworkToNetworkInterconnectProperties(TypedDict, total=False):
        key "administrativeState": Union[str, AdministrativeState]
        key "conditionalDefaultRouteConfiguration": ForwardRef('ConditionalDefaultRouteProperties', module='types')
        key "configurationState": Union[str, ConfigurationState]
        key "egressAclId": str
        key "exportRoutePolicy": ForwardRef('ExportRoutePolicyInformation', module='types')
        key "importRoutePolicy": ForwardRef('ImportRoutePolicyInformation', module='types')
        key "ingressAclId": str
        key "isManagementType": Union[str, IsManagementType]
        key "lastOperation": ForwardRef('LastOperationProperties', module='types')
        key "layer2Configuration": ForwardRef('Layer2Configuration', module='types')
        key "microBfdState": Union[str, MicroBfdState]
        key "nniType": Union[str, NniType]
        key "npbStaticRouteConfiguration": ForwardRef('NpbStaticRouteConfiguration', module='types')
        key "optionBLayer3Configuration": ForwardRef('OptionBLayer3Configuration', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "staticRouteConfiguration": ForwardRef('NniStaticRouteConfiguration', module='types')
        key "useOptionB": Required[Union[str, BooleanEnumProperty]]
        administrativeState: Union[str, AdministrativeState]
        conditionalDefaultRouteConfiguration: ConditionalDefaultRouteProperties
        configurationState: Union[str, ConfigurationState]
        egressAclId: str
        exportRoutePolicy: ExportRoutePolicyInformation
        importRoutePolicy: ImportRoutePolicyInformation
        ingressAclId: str
        isManagementType: Union[str, IsManagementType]
        lastOperation: LastOperationProperties
        layer2Configuration: Layer2Configuration
        microBfdState: Union[str, MicroBfdState]
        nniType: Union[str, NniType]
        npbStaticRouteConfiguration: NpbStaticRouteConfiguration
        optionBLayer3Configuration: OptionBLayer3Configuration
        provisioningState: Union[str, ProvisioningState]
        staticRouteConfiguration: NniStaticRouteConfiguration
        useOptionB: Union[str, BooleanEnumProperty]


    class azure.mgmt.managednetworkfabric.types.NniBmpPatchProperties(TypedDict, total=False):
        key "configurationState": Union[str, BmpConfigurationState]
        configurationState: Union[str, BmpConfigurationState]


    class azure.mgmt.managednetworkfabric.types.NniBmpProperties(TypedDict, total=False):
        key "configurationState": Required[Union[str, BmpConfigurationState]]
        configurationState: Union[str, BmpConfigurationState]


    class azure.mgmt.managednetworkfabric.types.NniStaticRouteConfiguration(TypedDict, total=False):
        key "bfdConfiguration": ForwardRef('BfdConfiguration', module='types')
        bfdConfiguration: BfdConfiguration
        ipv4Routes: list[StaticRouteProperties]
        ipv6Routes: list[StaticRouteProperties]


    class azure.mgmt.managednetworkfabric.types.NniStaticRoutePatchConfiguration(TypedDict, total=False):
        key "bfdConfiguration": ForwardRef('BfdPatchConfiguration', module='types')
        bfdConfiguration: BfdPatchConfiguration
        ipv4Routes: list[StaticRoutePatchProperties]
        ipv6Routes: list[StaticRoutePatchProperties]


    class azure.mgmt.managednetworkfabric.types.NniUpdateBfdAdministrativeStateRequest(TypedDict, total=False):
        key "administrativeState": Union[str, BfdAdministrativeState]
        key "routeType": Union[str, RouteType]
        administrativeState: Union[str, BfdAdministrativeState]
        routeType: Union[str, RouteType]


    class azure.mgmt.managednetworkfabric.types.NpbStaticRouteConfiguration(TypedDict, total=False):
        key "bfdConfiguration": ForwardRef('BfdConfiguration', module='types')
        bfdConfiguration: BfdConfiguration
        ipv4Routes: list[StaticRouteProperties]
        ipv6Routes: list[StaticRouteProperties]


    class azure.mgmt.managednetworkfabric.types.NpbStaticRouteConfigurationPatch(TypedDict, total=False):
        key "bfdConfiguration": ForwardRef('BfdPatchConfiguration', module='types')
        bfdConfiguration: BfdPatchConfiguration
        ipv4Routes: list[StaticRoutePatchProperties]
        ipv6Routes: list[StaticRoutePatchProperties]


    class azure.mgmt.managednetworkfabric.types.OptionBLayer3Configuration(Layer3IpPrefixProperties):
        key "bmpConfiguration": ForwardRef('NniBmpProperties', module='types')
        key "fabricASN": int
        key "peerASN": Required[int]
        key "primaryIpv4Prefix": str
        key "primaryIpv6Prefix": str
        key "secondaryIpv4Prefix": str
        key "secondaryIpv6Prefix": str
        key "vlanId": Required[int]
        bmpConfiguration: NniBmpProperties
        fabricASN: int
        peLoopbackIpAddress: list[str]
        peerASN: int
        prefixLimits: list[OptionBLayer3PrefixLimitProperties]
        primaryIpv4Prefix: str
        primaryIpv6Prefix: str
        secondaryIpv4Prefix: str
        secondaryIpv6Prefix: str
        vlanId: int


    class azure.mgmt.managednetworkfabric.types.OptionBLayer3ConfigurationPatchProperties(Layer3IpPrefixPatchProperties):
        key "bmpConfiguration": ForwardRef('NniBmpPatchProperties', module='types')
        key "fabricASN": int
        key "peerASN": int
        key "primaryIpv4Prefix": str
        key "primaryIpv6Prefix": str
        key "secondaryIpv4Prefix": str
        key "secondaryIpv6Prefix": str
        key "vlanId": int
        bmpConfiguration: NniBmpPatchProperties
        fabricASN: int
        peLoopbackIpAddress: list[str]
        peerASN: int
        prefixLimits: list[OptionBLayer3PrefixLimitPatchProperties]
        primaryIpv4Prefix: str
        primaryIpv6Prefix: str
        secondaryIpv4Prefix: str
        secondaryIpv6Prefix: str
        vlanId: int


    class azure.mgmt.managednetworkfabric.types.OptionBLayer3PrefixLimitPatchProperties(TypedDict, total=False):
        key "maximumRoutes": int
        maximumRoutes: int


    class azure.mgmt.managednetworkfabric.types.OptionBLayer3PrefixLimitProperties(TypedDict, total=False):
        key "maximumRoutes": int
        maximumRoutes: int


    class azure.mgmt.managednetworkfabric.types.PatchInfraNetwork(TypedDict, total=False):
        key "ipv4EndAddr": str
        key "ipv4Gateway": str
        key "ipv4StartAddr": str
        key "ipv4Subnet": str
        key "mtu": int
        key "vlanId": int
        ipv4EndAddr: str
        ipv4Gateway: str
        ipv4StartAddr: str
        ipv4Subnet: str
        mtu: int
        vlanId: int


    class azure.mgmt.managednetworkfabric.types.PatchInfrastructureNetworks(TypedDict, total=False):
        key "bmc": ForwardRef('PatchInfraNetwork', module='types')
        key "management": ForwardRef('PatchInfraNetwork', module='types')
        key "pdu": ForwardRef('PatchInfraNetwork', module='types')
        key "pxe": ForwardRef('PatchInfraNetwork', module='types')
        key "storage": ForwardRef('PatchInfraNetwork', module='types')
        key "storageMgmt": ForwardRef('PatchInfraNetwork', module='types')
        bmc: PatchInfraNetwork
        management: PatchInfraNetwork
        pdu: PatchInfraNetwork
        pxe: PatchInfraNetwork
        storage: PatchInfraNetwork
        storageMgmt: PatchInfraNetwork


    class azure.mgmt.managednetworkfabric.types.PatchInfrastructureServices(TypedDict, total=False):
        key "platformProxy": ForwardRef('PatchPlatformProxy', module='types')
        dnsServers: list[str]
        ntpServers: list[str]
        platformProxy: PatchPlatformProxy


    class azure.mgmt.managednetworkfabric.types.PatchPlatformProxy(TypedDict, total=False):
        key "httpProxy": str
        key "httpsProxy": str
        httpProxy: str
        httpsProxy: str
        noProxy: list[str]


    class azure.mgmt.managednetworkfabric.types.PlatformProxy(TypedDict, total=False):
        key "httpProxy": Required[str]
        key "httpsProxy": Required[str]
        key "noProxy": Required[list[str]]
        httpProxy: str
        httpsProxy: str
        noProxy: list[str]


    class azure.mgmt.managednetworkfabric.types.PoliceRateConfigurationProperties(TypedDict, total=False):
        key "bitRate": ForwardRef('BitRate', module='types')
        key "burstSize": ForwardRef('BurstSize', module='types')
        bitRate: BitRate
        burstSize: BurstSize


    class azure.mgmt.managednetworkfabric.types.PortCondition(TypedDict, total=False):
        key "layer4Protocol": Required[Union[str, Layer4Protocol]]
        key "portType": Union[str, PortType]
        layer4Protocol: Union[str, Layer4Protocol]
        portGroupNames: list[str]
        portType: Union[str, PortType]
        ports: list[str]


    class azure.mgmt.managednetworkfabric.types.PortConditionPatch(TypedDict, total=False):
        key "layer4Protocol": Union[str, Layer4Protocol]
        key "portType": Union[str, PortType]
        layer4Protocol: Union[str, Layer4Protocol]
        portGroupNames: list[str]
        portType: Union[str, PortType]
        ports: list[str]


    class azure.mgmt.managednetworkfabric.types.PortGroupPatchProperties(TypedDict, total=False):
        key "name": str
        name: str
        ports: list[str]


    class azure.mgmt.managednetworkfabric.types.PortGroupProperties(TypedDict, total=False):
        key "name": str
        name: str
        ports: list[str]


    class azure.mgmt.managednetworkfabric.types.PostUpgradeProfilePatchProperties(TypedDict, total=False):
        key "maxExitingMaintenanceTimeoutInSeconds": int
        key "mlagReloadDelayTimeoutInSeconds": int
        maxExitingMaintenanceTimeoutInSeconds: int
        mlagReloadDelayTimeoutInSeconds: int


    class azure.mgmt.managednetworkfabric.types.PostUpgradeProfileProperties(TypedDict, total=False):
        key "maxExitingMaintenanceTimeoutInSeconds": int
        key "mlagReloadDelayTimeoutInSeconds": int
        maxExitingMaintenanceTimeoutInSeconds: int
        mlagReloadDelayTimeoutInSeconds: int


    class azure.mgmt.managednetworkfabric.types.PreUpgradeProfilePatchProperties(TypedDict, total=False):
        key "maxEnteringMaintenanceTimeoutInSeconds": int
        maxEnteringMaintenanceTimeoutInSeconds: int


    class azure.mgmt.managednetworkfabric.types.PreUpgradeProfileProperties(TypedDict, total=False):
        key "maxEnteringMaintenanceTimeoutInSeconds": int
        maxEnteringMaintenanceTimeoutInSeconds: int


    class azure.mgmt.managednetworkfabric.types.PrefixLimitPatchProperties(TypedDict, total=False):
        key "idleTimeExpiry": int
        key "maximumRoutes": int
        key "threshold": int
        idleTimeExpiry: int
        maximumRoutes: int
        threshold: int


    class azure.mgmt.managednetworkfabric.types.PrefixLimitProperties(TypedDict, total=False):
        key "idleTimeExpiry": int
        key "maximumRoutes": int
        key "threshold": int
        idleTimeExpiry: int
        maximumRoutes: int
        threshold: int


    class azure.mgmt.managednetworkfabric.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.managednetworkfabric.types.ProxyResourceBase(TypedDict, total=False):
        key "id": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        systemData: SystemData
        type: str


    class azure.mgmt.managednetworkfabric.types.QosPatchProperties(TypedDict, total=False):
        key "qosConfigurationState": Union[str, QosConfigurationState]
        qosConfigurationState: Union[str, QosConfigurationState]


    class azure.mgmt.managednetworkfabric.types.QosProperties(TypedDict, total=False):
        key "qosConfigurationState": Union[str, QosConfigurationState]
        qosConfigurationState: Union[str, QosConfigurationState]


    class azure.mgmt.managednetworkfabric.types.RebootProperties(TypedDict, total=False):
        key "rebootType": Union[str, RebootType]
        rebootType: Union[str, RebootType]


    class azure.mgmt.managednetworkfabric.types.RefreshConfigurationRequestProperties(TypedDict, total=False):
        key "configurationRegenerationType": Required[Union[str, ConfigurationRegenerationType]]
        key "generateBaseConfiguration": Required[Union[str, GenerateBaseConfiguration]]
        configurationRegenerationType: Union[str, ConfigurationRegenerationType]
        deviceTypes: list[Union[str, NetworkFabricRefreshDeviceTypes]]
        generateBaseConfiguration: Union[str, GenerateBaseConfiguration]


    class azure.mgmt.managednetworkfabric.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.managednetworkfabric.types.RoutePolicy(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[RoutePolicyProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: RoutePolicyProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.managednetworkfabric.types.RoutePolicyPatch(TagsUpdate):
        key "properties": ForwardRef('RoutePolicyPatchableProperties', module='types')
        properties: RoutePolicyPatchableProperties
        tags: dict[str, str]


    class azure.mgmt.managednetworkfabric.types.RoutePolicyPatchableProperties(TypedDict, total=False):
        key "defaultAction": Union[str, CommunityActionTypes]
        defaultAction: Union[str, CommunityActionTypes]
        statements: list[RoutePolicyStatementPatchProperties]


    class azure.mgmt.managednetworkfabric.types.RoutePolicyProperties(TypedDict, total=False):
        key "addressFamilyType": Union[str, AddressFamilyType]
        key "administrativeState": Union[str, AdministrativeState]
        key "annotation": str
        key "configurationState": Union[str, ConfigurationState]
        key "defaultAction": Union[str, CommunityActionTypes]
        key "lastOperation": ForwardRef('LastOperationProperties', module='types')
        key "networkFabricId": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        key "statements": Required[list[RoutePolicyStatementProperties]]
        addressFamilyType: Union[str, AddressFamilyType]
        administrativeState: Union[str, AdministrativeState]
        annotation: str
        configurationState: Union[str, ConfigurationState]
        defaultAction: Union[str, CommunityActionTypes]
        lastOperation: LastOperationProperties
        networkFabricId: str
        provisioningState: Union[str, ProvisioningState]
        statements: list[RoutePolicyStatementProperties]


    class azure.mgmt.managednetworkfabric.types.RoutePolicyStatementPatchProperties(AnnotationResource):
        key "action": Required[StatementActionPatchProperties]
        key "annotation": str
        key "condition": Required[StatementConditionPatchProperties]
        key "sequenceNumber": Required[int]
        action: StatementActionPatchProperties
        annotation: str
        condition: StatementConditionPatchProperties
        sequenceNumber: int


    class azure.mgmt.managednetworkfabric.types.RoutePolicyStatementProperties(AnnotationResource):
        key "action": Required[StatementActionProperties]
        key "annotation": str
        key "condition": Required[StatementConditionProperties]
        key "sequenceNumber": Required[int]
        action: StatementActionProperties
        annotation: str
        condition: StatementConditionProperties
        sequenceNumber: int


    class azure.mgmt.managednetworkfabric.types.RoutePrefixLimitPatchProperties(TypedDict, total=False):
        key "hardLimit": int
        key "threshold": int
        hardLimit: int
        threshold: int


    class azure.mgmt.managednetworkfabric.types.RoutePrefixLimitProperties(TypedDict, total=False):
        key "hardLimit": int
        key "threshold": int
        hardLimit: int
        threshold: int


    class azure.mgmt.managednetworkfabric.types.RouteTargetInformation(TypedDict, total=False):
        exportIpv4RouteTargets: list[str]
        exportIpv6RouteTargets: list[str]
        importIpv4RouteTargets: list[str]
        importIpv6RouteTargets: list[str]


    class azure.mgmt.managednetworkfabric.types.RouteTargetPatchInformation(TypedDict, total=False):
        exportIpv4RouteTargets: list[str]
        exportIpv6RouteTargets: list[str]
        importIpv4RouteTargets: list[str]
        importIpv6RouteTargets: list[str]


    class azure.mgmt.managednetworkfabric.types.RuleProperties(TypedDict, total=False):
        key "action": Required[Union[str, Action]]
        key "condition": Union[str, RuleCondition]
        action: Union[str, Action]
        addressList: list[str]
        condition: Union[str, RuleCondition]
        destinationAddressList: list[str]
        headerAddressList: list[HeaderAddressProperties]
        sourceAddressList: list[str]


    class azure.mgmt.managednetworkfabric.types.SecretArchivePatchSettings(TypedDict, total=False):
        key "associatedIdentity": ForwardRef('IdentitySelectorPatch', module='types')
        key "vaultUri": str
        associatedIdentity: IdentitySelectorPatch
        vaultUri: str


    class azure.mgmt.managednetworkfabric.types.SecretArchiveReference(TypedDict, total=False):
        key "keyVaultId": str
        key "keyVaultUri": str
        key "secretName": str
        key "secretVersion": str
        keyVaultId: str
        keyVaultUri: str
        secretName: str
        secretVersion: str


    class azure.mgmt.managednetworkfabric.types.SecretArchiveSettings(TypedDict, total=False):
        key "associatedIdentity": Required[IdentitySelector]
        key "vaultUri": Required[str]
        associatedIdentity: IdentitySelector
        vaultUri: str


    class azure.mgmt.managednetworkfabric.types.SecretRotationStatus(TypedDict, total=False):
        key "lastRotationTime": str
        key "secretArchiveReference": ForwardRef('SecretArchiveReference', module='types')
        key "secretType": str
        key "synchronizationStatus": Union[str, SynchronizationStatus]
        lastRotationTime: str
        secretArchiveReference: SecretArchiveReference
        secretType: str
        synchronizationStatus: Union[str, SynchronizationStatus]


    class azure.mgmt.managednetworkfabric.types.SecretRotationSummary(TypedDict, total=False):
        key "activePasswordSetCount": int
        activePasswordSetCount: int


    class azure.mgmt.managednetworkfabric.types.StatementActionPatchProperties(TypedDict, total=False):
        key "actionType": Required[Union[str, RoutePolicyActionType]]
        key "ipCommunityProperties": ForwardRef('ActionIpCommunityPatchProperties', module='types')
        key "ipExtendedCommunityProperties": ForwardRef('ActionIpExtendedCommunityPatchProperties', module='types')
        key "localPreference": int
        actionType: Union[str, RoutePolicyActionType]
        ipCommunityProperties: ActionIpCommunityPatchProperties
        ipExtendedCommunityProperties: ActionIpExtendedCommunityPatchProperties
        localPreference: int


    class azure.mgmt.managednetworkfabric.types.StatementActionProperties(TypedDict, total=False):
        key "actionType": Required[Union[str, RoutePolicyActionType]]
        key "ipCommunityProperties": ForwardRef('ActionIpCommunityProperties', module='types')
        key "ipExtendedCommunityProperties": ForwardRef('ActionIpExtendedCommunityProperties', module='types')
        key "localPreference": int
        actionType: Union[str, RoutePolicyActionType]
        ipCommunityProperties: ActionIpCommunityProperties
        ipExtendedCommunityProperties: ActionIpExtendedCommunityProperties
        localPreference: int


    class azure.mgmt.managednetworkfabric.types.StatementConditionPatchProperties(TypedDict, total=False):
        key "ipPrefixId": str
        key "type": Union[str, RoutePolicyConditionType]
        ipCommunityIds: list[str]
        ipExtendedCommunityIds: list[str]
        ipPrefixId: str
        type: Union[str, RoutePolicyConditionType]


    class azure.mgmt.managednetworkfabric.types.StatementConditionProperties(TypedDict, total=False):
        key "ipPrefixId": str
        key "type": Union[str, RoutePolicyConditionType]
        ipCommunityIds: list[str]
        ipExtendedCommunityIds: list[str]
        ipPrefixId: str
        type: Union[str, RoutePolicyConditionType]


    class azure.mgmt.managednetworkfabric.types.StaticRouteConfiguration(TypedDict, total=False):
        key "bfdConfiguration": ForwardRef('BfdConfiguration', module='types')
        key "extension": Union[str, Extension]
        bfdConfiguration: BfdConfiguration
        extension: Union[str, Extension]
        ipv4Routes: list[StaticRouteProperties]
        ipv6Routes: list[StaticRouteProperties]


    class azure.mgmt.managednetworkfabric.types.StaticRoutePatchConfiguration(TypedDict, total=False):
        key "bfdConfiguration": ForwardRef('BfdPatchConfiguration', module='types')
        bfdConfiguration: BfdPatchConfiguration
        ipv4Routes: list[StaticRoutePatchProperties]
        ipv6Routes: list[StaticRoutePatchProperties]


    class azure.mgmt.managednetworkfabric.types.StaticRoutePatchProperties(TypedDict, total=False):
        key "nextHop": Required[list[str]]
        key "prefix": Required[str]
        nextHop: list[str]
        prefix: str


    class azure.mgmt.managednetworkfabric.types.StaticRoutePolicy(TypedDict, total=False):
        key "exportRoutePolicy": ForwardRef('L3ExportRoutePolicy', module='types')
        exportRoutePolicy: L3ExportRoutePolicy


    class azure.mgmt.managednetworkfabric.types.StaticRoutePolicyPatch(TypedDict, total=False):
        key "exportRoutePolicy": ForwardRef('L3ExportRoutePolicyPatch', module='types')
        exportRoutePolicy: L3ExportRoutePolicyPatch


    class azure.mgmt.managednetworkfabric.types.StaticRouteProperties(TypedDict, total=False):
        key "nextHop": Required[list[str]]
        key "prefix": Required[str]
        nextHop: list[str]
        prefix: str


    class azure.mgmt.managednetworkfabric.types.StationConnectionPatchProperties(TypedDict, total=False):
        key "keepaliveIdleTime": int
        key "probeCount": int
        key "probeInterval": int
        keepaliveIdleTime: int
        probeCount: int
        probeInterval: int


    class azure.mgmt.managednetworkfabric.types.StationConnectionProperties(TypedDict, total=False):
        key "keepaliveIdleTime": int
        key "probeCount": int
        key "probeInterval": int
        keepaliveIdleTime: int
        probeCount: int
        probeInterval: int


    class azure.mgmt.managednetworkfabric.types.StorageAccountConfiguration(TypedDict, total=False):
        key "storageAccountId": str
        key "storageAccountIdentity": ForwardRef('IdentitySelector', module='types')
        storageAccountId: str
        storageAccountIdentity: IdentitySelector


    class azure.mgmt.managednetworkfabric.types.StorageAccountPatchConfiguration(TypedDict, total=False):
        key "storageAccountId": str
        key "storageAccountIdentity": ForwardRef('IdentitySelectorPatch', module='types')
        storageAccountId: str
        storageAccountIdentity: IdentitySelectorPatch


    class azure.mgmt.managednetworkfabric.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.managednetworkfabric.types.TagsUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.managednetworkfabric.types.TerminalServerConfiguration(TypedDict, total=False):
        key "networkDeviceId": str
        key "password": Required[str]
        key "primaryIpv4Prefix": Required[str]
        key "primaryIpv6Prefix": str
        key "secondaryIpv4Prefix": Required[str]
        key "secondaryIpv6Prefix": str
        key "serialNumber": str
        key "username": Required[str]
        networkDeviceId: str
        password: str
        primaryIpv4Prefix: str
        primaryIpv6Prefix: str
        secondaryIpv4Prefix: str
        secondaryIpv6Prefix: str
        secretRotationStatus: list[SecretRotationStatus]
        serialNumber: str
        username: str


    class azure.mgmt.managednetworkfabric.types.TerminalServerPatchConfiguration(TypedDict, total=False):
        key "password": str
        key "primaryIpv4Prefix": str
        key "primaryIpv6Prefix": str
        key "secondaryIpv4Prefix": str
        key "secondaryIpv6Prefix": str
        key "serialNumber": str
        key "username": str
        password: str
        primaryIpv4Prefix: str
        primaryIpv6Prefix: str
        secondaryIpv4Prefix: str
        secondaryIpv6Prefix: str
        serialNumber: str
        username: str


    class azure.mgmt.managednetworkfabric.types.TrackedResource(Resource):
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


    class azure.mgmt.managednetworkfabric.types.UniqueRouteDistinguisherPatchProperties(TypedDict, total=False):
        key "nniDerivedUniqueRdConfigurationState": Union[str, NNIDerivedUniqueRouteDistinguisherConfigurationState]
        key "uniqueRdConfigurationState": Union[str, UniqueRouteDistinguisherConfigurationState]
        nniDerivedUniqueRdConfigurationState: Union[str, NNIDerivedUniqueRouteDistinguisherConfigurationState]
        uniqueRdConfigurationState: Union[str, UniqueRouteDistinguisherConfigurationState]


    class azure.mgmt.managednetworkfabric.types.UniqueRouteDistinguisherProperties(TypedDict, total=False):
        key "nniDerivedUniqueRdConfigurationState": Union[str, NNIDerivedUniqueRouteDistinguisherConfigurationState]
        key "uniqueRdConfigurationState": Union[str, UniqueRouteDistinguisherConfigurationState]
        nniDerivedUniqueRdConfigurationState: Union[str, NNIDerivedUniqueRouteDistinguisherConfigurationState]
        uniqueRdConfigurationState: Union[str, UniqueRouteDistinguisherConfigurationState]
        uniqueRds: list[str]


    class azure.mgmt.managednetworkfabric.types.UpdateAdministrativeState(EnableDisableOnResources):
        key "state": Union[str, EnableDisableState]
        resourceIds: list[str]
        state: Union[str, EnableDisableState]


    class azure.mgmt.managednetworkfabric.types.UpdateDeviceAdministrativeState(EnableDisableOnResources):
        key "state": Union[str, DeviceAdministrativeState]
        resourceIds: list[str]
        state: Union[str, DeviceAdministrativeState]


    class azure.mgmt.managednetworkfabric.types.UpdateVersion(TypedDict, total=False):
        key "version": str
        version: str


    class azure.mgmt.managednetworkfabric.types.UpgradeNetworkFabricProperties(UpdateVersion):
        key "action": Union[str, NetworkFabricUpgradeAction]
        key "version": str
        action: Union[str, NetworkFabricUpgradeAction]
        version: str


    class azure.mgmt.managednetworkfabric.types.UpgradeProfileProperties(TypedDict, total=False):
        key "postUpgradeProfile": ForwardRef('PostUpgradeProfileProperties', module='types')
        key "preUpgradeProfile": ForwardRef('PreUpgradeProfileProperties', module='types')
        postUpgradeProfile: PostUpgradeProfileProperties
        preUpgradeProfile: PreUpgradeProfileProperties


    class azure.mgmt.managednetworkfabric.types.UpgradeProfilePropertiesPatchProperties(TypedDict, total=False):
        key "postUpgradeProfile": ForwardRef('PostUpgradeProfilePatchProperties', module='types')
        key "preUpgradeProfile": ForwardRef('PreUpgradeProfilePatchProperties', module='types')
        postUpgradeProfile: PostUpgradeProfilePatchProperties
        preUpgradeProfile: PreUpgradeProfilePatchProperties


    class azure.mgmt.managednetworkfabric.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.managednetworkfabric.types.ValidateConfigurationProperties(TypedDict, total=False):
        key "validateAction": Union[str, ValidateAction]
        validateAction: Union[str, ValidateAction]


    class azure.mgmt.managednetworkfabric.types.VlanGroupPatchProperties(TypedDict, total=False):
        key "name": str
        name: str
        vlans: list[str]


    class azure.mgmt.managednetworkfabric.types.VlanGroupProperties(TypedDict, total=False):
        key "name": str
        name: str
        vlans: list[str]


    class azure.mgmt.managednetworkfabric.types.VlanMatchCondition(TypedDict, total=False):
        innerVlans: list[str]
        vlanGroupNames: list[str]
        vlans: list[str]


    class azure.mgmt.managednetworkfabric.types.VlanMatchConditionPatch(TypedDict, total=False):
        innerVlans: list[str]
        vlanGroupNames: list[str]
        vlans: list[str]


    class azure.mgmt.managednetworkfabric.types.VmProfile(TypedDict, total=False):
        key "vmSkuName": Required[str]
        vmSkuName: str


    class azure.mgmt.managednetworkfabric.types.VpnConfigurationPatchableProperties(TypedDict, total=False):
        key "networkToNetworkInterconnectId": str
        key "optionAProperties": ForwardRef('VpnOptionAPatchProperties', module='types')
        key "optionBProperties": ForwardRef('VpnOptionBPatchProperties', module='types')
        key "peeringOption": Union[str, PeeringOption]
        networkToNetworkInterconnectId: str
        optionAProperties: VpnOptionAPatchProperties
        optionBProperties: VpnOptionBPatchProperties
        peeringOption: Union[str, PeeringOption]


    class azure.mgmt.managednetworkfabric.types.VpnConfigurationProperties(TypedDict, total=False):
        key "administrativeState": Union[str, AdministrativeState]
        key "networkToNetworkInterconnectId": str
        key "optionAProperties": ForwardRef('VpnOptionAProperties', module='types')
        key "optionBProperties": ForwardRef('VpnOptionBProperties', module='types')
        key "peeringOption": Required[Union[str, PeeringOption]]
        administrativeState: Union[str, AdministrativeState]
        networkToNetworkInterconnectId: str
        optionAProperties: VpnOptionAProperties
        optionBProperties: VpnOptionBProperties
        peeringOption: Union[str, PeeringOption]


    class azure.mgmt.managednetworkfabric.types.VpnOptionAPatchProperties(Layer3IpPrefixPatchProperties):
        key "bfdConfiguration": ForwardRef('BfdPatchConfiguration', module='types')
        key "mtu": int
        key "peerASN": int
        key "primaryIpv4Prefix": str
        key "primaryIpv6Prefix": str
        key "secondaryIpv4Prefix": str
        key "secondaryIpv6Prefix": str
        key "vlanId": int
        bfdConfiguration: BfdPatchConfiguration
        mtu: int
        peerASN: int
        primaryIpv4Prefix: str
        primaryIpv6Prefix: str
        secondaryIpv4Prefix: str
        secondaryIpv6Prefix: str
        vlanId: int


    class azure.mgmt.managednetworkfabric.types.VpnOptionAProperties(Layer3IpPrefixProperties):
        key "bfdConfiguration": ForwardRef('BfdConfiguration', module='types')
        key "mtu": int
        key "peerASN": Required[int]
        key "primaryIpv4Prefix": str
        key "primaryIpv6Prefix": str
        key "secondaryIpv4Prefix": str
        key "secondaryIpv6Prefix": str
        key "vlanId": Required[int]
        bfdConfiguration: BfdConfiguration
        mtu: int
        peerASN: int
        primaryIpv4Prefix: str
        primaryIpv6Prefix: str
        secondaryIpv4Prefix: str
        secondaryIpv6Prefix: str
        vlanId: int


    class azure.mgmt.managednetworkfabric.types.VpnOptionBPatchProperties(TypedDict, total=False):
        key "routeTargets": ForwardRef('RouteTargetPatchInformation', module='types')
        exportRouteTargets: list[str]
        importRouteTargets: list[str]
        routeTargets: RouteTargetPatchInformation


    class azure.mgmt.managednetworkfabric.types.VpnOptionBProperties(TypedDict, total=False):
        key "routeTargets": ForwardRef('RouteTargetInformation', module='types')
        exportRouteTargets: list[str]
        importRouteTargets: list[str]
        routeTargets: RouteTargetInformation


```