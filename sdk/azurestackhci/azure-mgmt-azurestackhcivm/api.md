```py
namespace azure.mgmt.azurestackhcivm

    class azure.mgmt.azurestackhcivm.AzureStackHCIVmClient: implements ContextManager 
        attestation_statuses: AttestationStatusesOperations
        gallery_images: GalleryImagesOperations
        guest_agents: GuestAgentsOperations
        hybrid_identity_metadata: HybridIdentityMetadataOperations
        inbound_rules: InboundRulesOperations
        load_balancers: LoadBalancersOperations
        logical_networks: LogicalNetworksOperations
        marketplace_gallery_images: MarketplaceGalleryImagesOperations
        nat_gateways: NatGatewaysOperations
        network_interfaces: NetworkInterfacesOperations
        network_security_groups: NetworkSecurityGroupsOperations
        operations: Operations
        public_ip_addresses: PublicIPAddressesOperations
        security_rules: SecurityRulesOperations
        snapshots: SnapshotsOperations
        storage_containers: StorageContainersOperations
        virtual_hard_disks: VirtualHardDisksOperations
        virtual_machine_instances: VirtualMachineInstancesOperations
        virtual_network_subnets: VirtualNetworkSubnetsOperations
        virtual_networks: VirtualNetworksOperations

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


namespace azure.mgmt.azurestackhcivm.aio

    class azure.mgmt.azurestackhcivm.aio.AzureStackHCIVmClient: implements AsyncContextManager 
        attestation_statuses: AttestationStatusesOperations
        gallery_images: GalleryImagesOperations
        guest_agents: GuestAgentsOperations
        hybrid_identity_metadata: HybridIdentityMetadataOperations
        inbound_rules: InboundRulesOperations
        load_balancers: LoadBalancersOperations
        logical_networks: LogicalNetworksOperations
        marketplace_gallery_images: MarketplaceGalleryImagesOperations
        nat_gateways: NatGatewaysOperations
        network_interfaces: NetworkInterfacesOperations
        network_security_groups: NetworkSecurityGroupsOperations
        operations: Operations
        public_ip_addresses: PublicIPAddressesOperations
        security_rules: SecurityRulesOperations
        snapshots: SnapshotsOperations
        storage_containers: StorageContainersOperations
        virtual_hard_disks: VirtualHardDisksOperations
        virtual_machine_instances: VirtualMachineInstancesOperations
        virtual_network_subnets: VirtualNetworkSubnetsOperations
        virtual_networks: VirtualNetworksOperations

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


namespace azure.mgmt.azurestackhcivm.aio.operations

    class azure.mgmt.azurestackhcivm.aio.operations.AttestationStatusesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AttestationStatus: ...


    class azure.mgmt.azurestackhcivm.aio.operations.GalleryImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_image_name: str, 
                resource: GalleryImage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryImage]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_image_name: str, 
                resource: GalleryImage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryImage]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_image_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryImage]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                gallery_image_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_image_name: str, 
                properties: GalleryImageTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryImage]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_image_name: str, 
                properties: GalleryImageTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryImage]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_image_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryImage]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                gallery_image_name: str, 
                **kwargs: Any
            ) -> GalleryImage: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> AsyncItemPaged[GalleryImage]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GalleryImage]: ...


    class azure.mgmt.azurestackhcivm.aio.operations.GuestAgentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_uri: str, 
                resource: GuestAgent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GuestAgent]: ...

        @overload
        async def begin_create(
                self, 
                resource_uri: str, 
                resource: GuestAgent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GuestAgent]: ...

        @overload
        async def begin_create(
                self, 
                resource_uri: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GuestAgent]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> GuestAgent: ...

        @distributed_trace
        def list_by_virtual_machine_instance(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GuestAgent]: ...


    class azure.mgmt.azurestackhcivm.aio.operations.HybridIdentityMetadataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> HybridIdentityMetadata: ...

        @distributed_trace
        def list_by_virtual_machine_instance(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[HybridIdentityMetadata]: ...


    class azure.mgmt.azurestackhcivm.aio.operations.InboundRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                inbound_rule_name: str, 
                resource: InboundRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InboundRule]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                inbound_rule_name: str, 
                resource: InboundRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InboundRule]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                inbound_rule_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InboundRule]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'nat_gateway_name', 'inbound_rule_name']}, api_versions_list=['2026-04-01-preview', '2026-07-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                inbound_rule_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'nat_gateway_name', 'inbound_rule_name', 'accept']}, api_versions_list=['2026-04-01-preview', '2026-07-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                inbound_rule_name: str, 
                **kwargs: Any
            ) -> InboundRule: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'nat_gateway_name', 'accept']}, api_versions_list=['2026-04-01-preview', '2026-07-01-preview'])
        def list_by_nat_gateway(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[InboundRule]: ...


    class azure.mgmt.azurestackhcivm.aio.operations.LoadBalancersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                load_balancer_name: str, 
                resource: LoadBalancer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LoadBalancer]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                load_balancer_name: str, 
                resource: LoadBalancer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LoadBalancer]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                load_balancer_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LoadBalancer]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'load_balancer_name']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                load_balancer_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_tags(
                self, 
                resource_group_name: str, 
                load_balancer_name: str, 
                properties: LoadBalancerTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LoadBalancer]: ...

        @overload
        async def begin_update_tags(
                self, 
                resource_group_name: str, 
                load_balancer_name: str, 
                properties: LoadBalancerTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LoadBalancer]: ...

        @overload
        async def begin_update_tags(
                self, 
                resource_group_name: str, 
                load_balancer_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LoadBalancer]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'load_balancer_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                load_balancer_name: str, 
                **kwargs: Any
            ) -> LoadBalancer: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def list_all(self, **kwargs: Any) -> AsyncItemPaged[LoadBalancer]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[LoadBalancer]: ...


    class azure.mgmt.azurestackhcivm.aio.operations.LogicalNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                logical_network_name: str, 
                resource: LogicalNetwork, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LogicalNetwork]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                logical_network_name: str, 
                resource: LogicalNetwork, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LogicalNetwork]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                logical_network_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LogicalNetwork]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                logical_network_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                logical_network_name: str, 
                properties: LogicalNetworksUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LogicalNetwork]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                logical_network_name: str, 
                properties: LogicalNetworksUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LogicalNetwork]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                logical_network_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LogicalNetwork]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                logical_network_name: str, 
                **kwargs: Any
            ) -> LogicalNetwork: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> AsyncItemPaged[LogicalNetwork]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[LogicalNetwork]: ...


    class azure.mgmt.azurestackhcivm.aio.operations.MarketplaceGalleryImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                marketplace_gallery_image_name: str, 
                resource: MarketplaceGalleryImage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MarketplaceGalleryImage]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                marketplace_gallery_image_name: str, 
                resource: MarketplaceGalleryImage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MarketplaceGalleryImage]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                marketplace_gallery_image_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MarketplaceGalleryImage]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                marketplace_gallery_image_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                marketplace_gallery_image_name: str, 
                properties: MarketplaceGalleryImageTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MarketplaceGalleryImage]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                marketplace_gallery_image_name: str, 
                properties: MarketplaceGalleryImageTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MarketplaceGalleryImage]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                marketplace_gallery_image_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MarketplaceGalleryImage]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                marketplace_gallery_image_name: str, 
                **kwargs: Any
            ) -> MarketplaceGalleryImage: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> AsyncItemPaged[MarketplaceGalleryImage]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MarketplaceGalleryImage]: ...


    class azure.mgmt.azurestackhcivm.aio.operations.NatGatewaysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                resource: NatGateway, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NatGateway]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                resource: NatGateway, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NatGateway]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NatGateway]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'nat_gateway_name']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_tags(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                properties: NatGatewayTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NatGateway]: ...

        @overload
        async def begin_update_tags(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                properties: NatGatewayTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NatGateway]: ...

        @overload
        async def begin_update_tags(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NatGateway]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'nat_gateway_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                **kwargs: Any
            ) -> NatGateway: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def list_all(self, **kwargs: Any) -> AsyncItemPaged[NatGateway]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NatGateway]: ...


    class azure.mgmt.azurestackhcivm.aio.operations.NetworkInterfacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_interface_name: str, 
                resource: NetworkInterface, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkInterface]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_interface_name: str, 
                resource: NetworkInterface, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkInterface]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_interface_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkInterface]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_interface_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_interface_name: str, 
                properties: NetworkInterfacesUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkInterface]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_interface_name: str, 
                properties: NetworkInterfacesUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkInterface]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_interface_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkInterface]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                network_interface_name: str, 
                **kwargs: Any
            ) -> NetworkInterface: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> AsyncItemPaged[NetworkInterface]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkInterface]: ...


    class azure.mgmt.azurestackhcivm.aio.operations.NetworkSecurityGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                resource: NetworkSecurityGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkSecurityGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                resource: NetworkSecurityGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkSecurityGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkSecurityGroup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_tags(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                properties: NetworkSecurityGroupTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkSecurityGroup]: ...

        @overload
        async def begin_update_tags(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                properties: NetworkSecurityGroupTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkSecurityGroup]: ...

        @overload
        async def begin_update_tags(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkSecurityGroup]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityGroup: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> AsyncItemPaged[NetworkSecurityGroup]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkSecurityGroup]: ...


    class azure.mgmt.azurestackhcivm.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.azurestackhcivm.aio.operations.PublicIPAddressesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                public_ip_address_name: str, 
                resource: PublicIPAddress, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PublicIPAddress]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                public_ip_address_name: str, 
                resource: PublicIPAddress, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PublicIPAddress]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                public_ip_address_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PublicIPAddress]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'public_ip_address_name']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                public_ip_address_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_tags(
                self, 
                resource_group_name: str, 
                public_ip_address_name: str, 
                properties: PublicIPAddressTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PublicIPAddress]: ...

        @overload
        async def begin_update_tags(
                self, 
                resource_group_name: str, 
                public_ip_address_name: str, 
                properties: PublicIPAddressTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PublicIPAddress]: ...

        @overload
        async def begin_update_tags(
                self, 
                resource_group_name: str, 
                public_ip_address_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PublicIPAddress]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'public_ip_address_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                public_ip_address_name: str, 
                **kwargs: Any
            ) -> PublicIPAddress: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def list_all(self, **kwargs: Any) -> AsyncItemPaged[PublicIPAddress]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PublicIPAddress]: ...


    class azure.mgmt.azurestackhcivm.aio.operations.SecurityRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                security_rule_name: str, 
                resource: SecurityRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SecurityRule]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                security_rule_name: str, 
                resource: SecurityRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SecurityRule]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                security_rule_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SecurityRule]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                security_rule_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                security_rule_name: str, 
                **kwargs: Any
            ) -> SecurityRule: ...

        @distributed_trace
        def list_by_network_security_group(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SecurityRule]: ...


    class azure.mgmt.azurestackhcivm.aio.operations.SnapshotsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                resource: Snapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Snapshot]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                resource: Snapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Snapshot]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Snapshot]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-02-01-preview', params_added_on={'2026-02-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'snapshot_name']}, api_versions_list=['2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                properties: SnapshotTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Snapshot]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                properties: SnapshotTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Snapshot]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Snapshot]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-02-01-preview', params_added_on={'2026-02-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'snapshot_name', 'accept']}, api_versions_list=['2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                **kwargs: Any
            ) -> Snapshot: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-02-01-preview', params_added_on={'2026-02-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def list_all(self, **kwargs: Any) -> AsyncItemPaged[Snapshot]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-02-01-preview', params_added_on={'2026-02-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Snapshot]: ...


    class azure.mgmt.azurestackhcivm.aio.operations.StorageContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                resource: StorageContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageContainer]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                resource: StorageContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageContainer]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageContainer]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                properties: StorageContainerTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageContainer]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                properties: StorageContainerTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageContainer]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageContainer]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                **kwargs: Any
            ) -> StorageContainer: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> AsyncItemPaged[StorageContainer]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StorageContainer]: ...


    class azure.mgmt.azurestackhcivm.aio.operations.VirtualHardDisksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_hard_disk_name: str, 
                resource: VirtualHardDisk, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualHardDisk]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_hard_disk_name: str, 
                resource: VirtualHardDisk, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualHardDisk]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_hard_disk_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualHardDisk]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_hard_disk_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_hard_disk_name: str, 
                properties: VirtualHardDisksUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualHardDisk]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_hard_disk_name: str, 
                properties: VirtualHardDisksUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualHardDisk]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_hard_disk_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualHardDisk]: ...

        @overload
        async def begin_upload(
                self, 
                resource_group_name: str, 
                virtual_hard_disk_name: str, 
                body: VirtualHardDiskUploadRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualHardDiskUploadResponse]: ...

        @overload
        async def begin_upload(
                self, 
                resource_group_name: str, 
                virtual_hard_disk_name: str, 
                body: VirtualHardDiskUploadRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualHardDiskUploadResponse]: ...

        @overload
        async def begin_upload(
                self, 
                resource_group_name: str, 
                virtual_hard_disk_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualHardDiskUploadResponse]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                virtual_hard_disk_name: str, 
                **kwargs: Any
            ) -> VirtualHardDisk: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> AsyncItemPaged[VirtualHardDisk]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualHardDisk]: ...


    class azure.mgmt.azurestackhcivm.aio.operations.VirtualMachineInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                resource: VirtualMachineInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineInstance]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                resource: VirtualMachineInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineInstance]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineInstance]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_pause(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_power_off(
                self, 
                resource_uri: str, 
                body: PowerOffVirtualMachineOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_power_off(
                self, 
                resource_uri: str, 
                body: PowerOffVirtualMachineOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_power_off(
                self, 
                resource_uri: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def begin_restart(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_save(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_stop(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_uri: str, 
                properties: VirtualMachineInstanceUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineInstance]: ...

        @overload
        async def begin_update(
                self, 
                resource_uri: str, 
                properties: VirtualMachineInstanceUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineInstance]: ...

        @overload
        async def begin_update(
                self, 
                resource_uri: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineInstance]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> VirtualMachineInstance: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualMachineInstance]: ...


    class azure.mgmt.azurestackhcivm.aio.operations.VirtualNetworkSubnetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                subnet_name: str, 
                resource: VirtualNetworkSubnet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkSubnet]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                subnet_name: str, 
                resource: VirtualNetworkSubnet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkSubnet]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                subnet_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkSubnet]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'virtual_network_name', 'subnet_name']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                subnet_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                subnet_name: str, 
                properties: VirtualNetworkSubnetUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkSubnet]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                subnet_name: str, 
                properties: VirtualNetworkSubnetUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkSubnet]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                subnet_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkSubnet]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'virtual_network_name', 'subnet_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                subnet_name: str, 
                **kwargs: Any
            ) -> VirtualNetworkSubnet: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'virtual_network_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def list_by_virtual_network(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualNetworkSubnet]: ...


    class azure.mgmt.azurestackhcivm.aio.operations.VirtualNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                resource: VirtualNetwork, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetwork]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                resource: VirtualNetwork, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetwork]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetwork]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'virtual_network_name']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_tags(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                properties: VirtualNetworkTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetwork]: ...

        @overload
        async def begin_update_tags(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                properties: VirtualNetworkTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetwork]: ...

        @overload
        async def begin_update_tags(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetwork]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'virtual_network_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                **kwargs: Any
            ) -> VirtualNetwork: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def list_all(self, **kwargs: Any) -> AsyncItemPaged[VirtualNetwork]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualNetwork]: ...


namespace azure.mgmt.azurestackhcivm.models

    class azure.mgmt.azurestackhcivm.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.azurestackhcivm.models.AttestBootIntegrityPropertyEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        UNKNOWN = "Unknown"
        VALID = "Valid"


    class azure.mgmt.azurestackhcivm.models.AttestCertPropertyEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        UNKNOWN = "Unknown"
        VALID = "Valid"


    class azure.mgmt.azurestackhcivm.models.AttestDiskSecurityEncryptionTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NON_PERSISTED_TPM = "NonPersistedTPM"
        UNKNOWN = "Unknown"


    class azure.mgmt.azurestackhcivm.models.AttestHWPlatformEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SEVSNP = "SEVSNP"
        UNKNOWN = "Unknown"


    class azure.mgmt.azurestackhcivm.models.AttestHealthStatusEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        PENDING = "Pending"
        UNHEALTHY = "Unhealthy"
        UNKNOWN = "Unknown"


    class azure.mgmt.azurestackhcivm.models.AttestSecureBootPropertyEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        UNKNOWN = "Unknown"


    class azure.mgmt.azurestackhcivm.models.AttestationStatus(ProxyResource):
        id: str
        name: str
        properties: Optional[AttestationStatusProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AttestationStatusProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.AttestationStatusProperties(_Model):
        attest_disk_security_encryption_type: Optional[Union[str, AttestDiskSecurityEncryptionTypeEnum]]
        attest_hardware_platform: Optional[Union[str, AttestHWPlatformEnum]]
        attest_secure_boot_enabled: Optional[Union[str, AttestSecureBootPropertyEnum]]
        attestation_cert_validated: Optional[Union[str, AttestCertPropertyEnum]]
        boot_integrity_validated: Optional[Union[str, AttestBootIntegrityPropertyEnum]]
        error_message: Optional[str]
        health_status: Optional[Union[str, AttestHealthStatusEnum]]
        linux_kernel_version: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        timestamp: Optional[str]


    class azure.mgmt.azurestackhcivm.models.BackendAddressPool(_Model):
        name: str
        properties: BackendAddressPoolProperties

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: BackendAddressPoolProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.BackendAddressPoolProperties(_Model):
        load_balancer_backend_addresses: Optional[list[LoadBalancerBackendAddress]]
        logical_network: Optional[LogicalNetworkArmReference]
        virtual_network: Optional[VirtualNetworkArmReference]

        @overload
        def __init__(
                self, 
                *, 
                load_balancer_backend_addresses: Optional[list[LoadBalancerBackendAddress]] = ..., 
                logical_network: Optional[LogicalNetworkArmReference] = ..., 
                virtual_network: Optional[VirtualNetworkArmReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.CloudInitDataSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE = "Azure"
        NO_CLOUD = "NoCloud"


    class azure.mgmt.azurestackhcivm.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.azurestackhcivm.models.CreationData(_Model):
        create_option: Union[str, DiskCreateOption]
        source_resource_id: Optional[str]
        source_unique_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                create_option: Union[str, DiskCreateOption], 
                source_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.DiskCreateOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COPY = "Copy"
        EMPTY = "Empty"


    class azure.mgmt.azurestackhcivm.models.DiskFileFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VHD = "vhd"
        VHDX = "vhdx"


    class azure.mgmt.azurestackhcivm.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.azurestackhcivm.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.azurestackhcivm.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.ExtendedLocation(_Model):
        name: Optional[str]
        type: Optional[Union[str, ExtendedLocationTypes]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[Union[str, ExtendedLocationTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.ExtendedLocationTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_LOCATION = "CustomLocation"


    class azure.mgmt.azurestackhcivm.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhcivm.models.FabricConnectionHealthEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        HEALTHY = "Healthy"
        UNKNOWN = "Unknown"
        WARNING = "Warning"


    class azure.mgmt.azurestackhcivm.models.FabricIntegrationStateEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTED = "Connected"
        CONNECTING = "Connecting"
        DISCONNECTED = "Disconnected"
        MISCONFIGURED = "Misconfigured"
        NOT_APPLICABLE = "NotApplicable"


    class azure.mgmt.azurestackhcivm.models.FabricIntegrationStatus(_Model):
        health: Optional[Union[str, FabricConnectionHealthEnum]]
        issues: Optional[list[FabricIssue]]
        last_checked: Optional[datetime]
        resource_type: Optional[Union[str, FabricResourceTypeEnum]]
        state: Optional[Union[str, FabricIntegrationStateEnum]]


    class azure.mgmt.azurestackhcivm.models.FabricIssue(_Model):
        code: Optional[str]
        message: Optional[str]
        severity: Optional[str]
        target: Optional[str]
        timestamp: Optional[datetime]


    class azure.mgmt.azurestackhcivm.models.FabricResourceTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        L2_ISOLATION_DOMAIN = "L2IsolationDomain"
        L3_INTERNAL_NETWORK = "L3InternalNetwork"


    class azure.mgmt.azurestackhcivm.models.FrontendIPConfiguration(_Model):
        name: str
        properties: FrontendIPConfigurationProperties

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: FrontendIPConfigurationProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.FrontendIPConfigurationProperties(_Model):
        private_ip_address: Optional[str]
        private_ip_allocation_method: Optional[Union[str, IpAllocationMethodEnum]]
        public_ip_address: Optional[PublicIPAddressArmReference]
        subnet: Optional[VirtualNetworkSubnetArmReference]

        @overload
        def __init__(
                self, 
                *, 
                private_ip_address: Optional[str] = ..., 
                private_ip_allocation_method: Optional[Union[str, IpAllocationMethodEnum]] = ..., 
                public_ip_address: Optional[PublicIPAddressArmReference] = ..., 
                subnet: Optional[VirtualNetworkSubnetArmReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.GalleryImage(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: Optional[GalleryImageProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: Optional[GalleryImageProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.GalleryImageIdentifier(_Model):
        offer: str
        publisher: str
        sku: str

        @overload
        def __init__(
                self, 
                *, 
                offer: str, 
                publisher: str, 
                sku: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.GalleryImageProperties(_Model):
        cloud_init_data_source: Optional[Union[str, CloudInitDataSource]]
        container_id: Optional[str]
        hyper_v_generation: Optional[Union[str, HyperVGeneration]]
        identifier: Optional[GalleryImageIdentifier]
        image_path: Optional[str]
        os_type: Union[str, OperatingSystemTypes]
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        source_virtual_machine_id: Optional[str]
        status: Optional[GalleryImageStatus]
        version: Optional[GalleryImageVersion]

        @overload
        def __init__(
                self, 
                *, 
                cloud_init_data_source: Optional[Union[str, CloudInitDataSource]] = ..., 
                container_id: Optional[str] = ..., 
                hyper_v_generation: Optional[Union[str, HyperVGeneration]] = ..., 
                identifier: Optional[GalleryImageIdentifier] = ..., 
                image_path: Optional[str] = ..., 
                os_type: Union[str, OperatingSystemTypes], 
                source_virtual_machine_id: Optional[str] = ..., 
                version: Optional[GalleryImageVersion] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.GalleryImageStatus(_Model):
        download_status: Optional[GalleryImageStatusDownloadStatus]
        error_code: Optional[str]
        error_message: Optional[str]
        progress_percentage: Optional[int]
        provisioning_status: Optional[GalleryImageStatusProvisioningStatus]

        @overload
        def __init__(
                self, 
                *, 
                download_status: Optional[GalleryImageStatusDownloadStatus] = ..., 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                progress_percentage: Optional[int] = ..., 
                provisioning_status: Optional[GalleryImageStatusProvisioningStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.GalleryImageStatusDownloadStatus(_Model):
        download_size_in_mb: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                download_size_in_mb: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.GalleryImageStatusProvisioningStatus(_Model):
        operation_id: Optional[str]
        status: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                operation_id: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.GalleryImageTagsUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.GalleryImageVersion(_Model):
        name: Optional[str]
        properties: Optional[GalleryImageVersionProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[GalleryImageVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.azurestackhcivm.models.GalleryImageVersionProperties(_Model):
        storage_profile: GalleryImageVersionStorageProfile

        @overload
        def __init__(
                self, 
                *, 
                storage_profile: GalleryImageVersionStorageProfile
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.GalleryImageVersionStorageProfile(_Model):
        os_disk_image: Optional[GalleryOSDiskImage]

        @overload
        def __init__(
                self, 
                *, 
                os_disk_image: Optional[GalleryOSDiskImage] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.GalleryOSDiskImage(_Model):
        size_in_mb: Optional[int]


    class azure.mgmt.azurestackhcivm.models.GpuAssignmentTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GPU_DDA = "GpuDDA"
        GPU_P = "GpuP"


    class azure.mgmt.azurestackhcivm.models.GuestAgent(ProxyResource):
        id: str
        name: str
        properties: Optional[GuestAgentProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GuestAgentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.GuestAgentInstallStatus(_Model):
        agent_version: Optional[str]
        error_details: Optional[list[ErrorDetail]]
        last_status_change: Optional[datetime]
        status: Optional[Union[str, StatusTypes]]
        vm_uuid: Optional[str]


    class azure.mgmt.azurestackhcivm.models.GuestAgentProperties(_Model):
        credentials: Optional[GuestCredential]
        provisioning_action: Optional[Union[str, ProvisioningAction]]
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                credentials: Optional[GuestCredential] = ..., 
                provisioning_action: Optional[Union[str, ProvisioningAction]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.GuestCredential(_Model):
        password: Optional[str]
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                password: Optional[str] = ..., 
                username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.HardwareProfileUpdate(_Model):
        dynamic_memory_config: Optional[VirtualMachineInstancePropertiesHardwareProfileDynamicMemoryConfig]
        memory_mb: Optional[int]
        processors: Optional[int]
        virtual_machine_gp_us: Optional[list[VirtualMachineInstancePropertiesHardwareProfileVirtualMachineGPU]]
        vm_size: Optional[Union[str, VmSizeEnum]]

        @overload
        def __init__(
                self, 
                *, 
                dynamic_memory_config: Optional[VirtualMachineInstancePropertiesHardwareProfileDynamicMemoryConfig] = ..., 
                memory_mb: Optional[int] = ..., 
                processors: Optional[int] = ..., 
                virtual_machine_gp_us: Optional[list[VirtualMachineInstancePropertiesHardwareProfileVirtualMachineGPU]] = ..., 
                vm_size: Optional[Union[str, VmSizeEnum]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.HttpProxyConfiguration(_Model):
        http_proxy: Optional[str]
        https_proxy: Optional[str]
        no_proxy: Optional[list[str]]
        trusted_ca: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                http_proxy: Optional[str] = ..., 
                https_proxy: Optional[str] = ..., 
                no_proxy: Optional[list[str]] = ..., 
                trusted_ca: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.HybridIdentityMetadata(ProxyResource):
        id: str
        name: str
        properties: Optional[HybridIdentityMetadataProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HybridIdentityMetadataProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.HybridIdentityMetadataProperties(_Model):
        identity: Optional[Identity]
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        public_key: Optional[str]
        resource_uid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                public_key: Optional[str] = ..., 
                resource_uid: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.HyperVGeneration(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NA = "NA"
        V1 = "V1"
        V2 = "V2"


    class azure.mgmt.azurestackhcivm.models.IPConfiguration(_Model):
        name: Optional[str]
        properties: Optional[IPConfigurationProperties]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[IPConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.IPConfigurationArmReference(_Model):
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.IPConfigurationProperties(_Model):
        gateway: Optional[str]
        prefix_length: Optional[str]
        private_ip_address: Optional[str]
        subnet: Optional[LogicalNetworkArmReference]

        @overload
        def __init__(
                self, 
                *, 
                private_ip_address: Optional[str] = ..., 
                subnet: Optional[LogicalNetworkArmReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.IPPool(_Model):
        end: Optional[str]
        info: Optional[IPPoolInfo]
        ip_pool_type: Optional[Union[str, IPPoolTypeEnum]]
        name: Optional[str]
        start: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                end: Optional[str] = ..., 
                info: Optional[IPPoolInfo] = ..., 
                ip_pool_type: Optional[Union[str, IPPoolTypeEnum]] = ..., 
                name: Optional[str] = ..., 
                start: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.IPPoolInfo(_Model):
        available: Optional[str]
        used: Optional[str]


    class azure.mgmt.azurestackhcivm.models.IPPoolTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VIPPOOL = "vippool"
        VM = "vm"


    class azure.mgmt.azurestackhcivm.models.Identity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Literal["SystemAssigned"]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Literal[SystemAssigned]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.ImageArmReference(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.InboundNATRuleProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TCP = "Tcp"
        UDP = "Udp"


    class azure.mgmt.azurestackhcivm.models.InboundRule(ProxyResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        name: str
        properties: Optional[InboundRuleProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                properties: Optional[InboundRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.InboundRuleProperties(_Model):
        backend_ip_configuration: IPConfigurationArmReference
        backend_port: int
        frontend_port: int
        protocol: Union[str, InboundNATRuleProtocol]
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        public_ip_address: PublicIPAddressArmReference
        status: Optional[InboundRuleStatus]

        @overload
        def __init__(
                self, 
                *, 
                backend_ip_configuration: IPConfigurationArmReference, 
                backend_port: int, 
                frontend_port: int, 
                protocol: Union[str, InboundNATRuleProtocol], 
                public_ip_address: PublicIPAddressArmReference
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.InboundRuleStatus(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        provisioning_status: Optional[InboundRuleStatusProvisioningStatus]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                provisioning_status: Optional[InboundRuleStatusProvisioningStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.InboundRuleStatusProvisioningStatus(_Model):
        operation_id: Optional[str]
        status: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                operation_id: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.InstanceViewStatus(_Model):
        code: Optional[str]
        display_status: Optional[str]
        level: Optional[Union[str, StatusLevelTypes]]
        message: Optional[str]
        time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                display_status: Optional[str] = ..., 
                level: Optional[Union[str, StatusLevelTypes]] = ..., 
                message: Optional[str] = ..., 
                time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.InterfaceDNSSettings(_Model):
        dns_servers: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                dns_servers: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.IpAllocationMethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DYNAMIC = "Dynamic"
        STATIC = "Static"


    class azure.mgmt.azurestackhcivm.models.LoadBalancer(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: Optional[LoadBalancerProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: Optional[LoadBalancerProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.LoadBalancerBackendAddress(_Model):
        name: str
        properties: LoadBalancerBackendAddressProperties

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: LoadBalancerBackendAddressProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.LoadBalancerBackendAddressAdminState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOWN = "Down"
        UP = "Up"


    class azure.mgmt.azurestackhcivm.models.LoadBalancerBackendAddressPoolReference(_Model):
        name: str

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.LoadBalancerBackendAddressProperties(_Model):
        admin_state: Optional[Union[str, LoadBalancerBackendAddressAdminState]]
        ip_address: Optional[str]
        logical_network: Optional[LogicalNetworkArmReference]
        network_interface_ip_configuration: Optional[IPConfigurationArmReference]
        subnet: Optional[VirtualNetworkSubnetArmReference]
        virtual_network: Optional[VirtualNetworkArmReference]

        @overload
        def __init__(
                self, 
                *, 
                admin_state: Optional[Union[str, LoadBalancerBackendAddressAdminState]] = ..., 
                network_interface_ip_configuration: Optional[IPConfigurationArmReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.LoadBalancerFrontendIPConfigurationReference(_Model):
        name: str

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.LoadBalancerProbeProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "Http"
        TCP = "Tcp"


    class azure.mgmt.azurestackhcivm.models.LoadBalancerProbeReference(_Model):
        name: str

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.LoadBalancerProperties(_Model):
        backend_address_pools: Optional[list[BackendAddressPool]]
        frontend_ip_configurations: list[FrontendIPConfiguration]
        load_balancing_rules: Optional[list[LoadBalancerRule]]
        probes: Optional[list[Probe]]
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        status: Optional[LoadBalancerStatus]

        @overload
        def __init__(
                self, 
                *, 
                backend_address_pools: Optional[list[BackendAddressPool]] = ..., 
                frontend_ip_configurations: list[FrontendIPConfiguration], 
                load_balancing_rules: Optional[list[LoadBalancerRule]] = ..., 
                probes: Optional[list[Probe]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.LoadBalancerRule(_Model):
        name: str
        properties: LoadBalancerRuleProperties

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: LoadBalancerRuleProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.LoadBalancerRuleProperties(_Model):
        backend_address_pool: LoadBalancerBackendAddressPoolReference
        backend_port: int
        frontend_ip_configuration: LoadBalancerFrontendIPConfigurationReference
        frontend_port: int
        idle_timeout_in_minutes: Optional[int]
        load_distribution: Optional[Union[str, LoadBalancerRuleSessionPersistenceType]]
        probe: Optional[LoadBalancerProbeReference]
        protocol: Union[str, LoadBalancerRuleTransportProtocol]

        @overload
        def __init__(
                self, 
                *, 
                backend_address_pool: LoadBalancerBackendAddressPoolReference, 
                backend_port: int, 
                frontend_ip_configuration: LoadBalancerFrontendIPConfigurationReference, 
                frontend_port: int, 
                idle_timeout_in_minutes: Optional[int] = ..., 
                load_distribution: Optional[Union[str, LoadBalancerRuleSessionPersistenceType]] = ..., 
                probe: Optional[LoadBalancerProbeReference] = ..., 
                protocol: Union[str, LoadBalancerRuleTransportProtocol]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.LoadBalancerRuleSessionPersistenceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        SOURCE_IP = "SourceIP"
        SOURCE_IP_PROTOCOL = "SourceIPProtocol"


    class azure.mgmt.azurestackhcivm.models.LoadBalancerRuleTransportProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        TCP = "Tcp"
        UDP = "Udp"


    class azure.mgmt.azurestackhcivm.models.LoadBalancerStatus(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        provisioning_status: Optional[LoadBalancerStatusProvisioningStatus]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                provisioning_status: Optional[LoadBalancerStatusProvisioningStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.LoadBalancerStatusProvisioningStatus(_Model):
        operation_id: Optional[str]
        status: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                operation_id: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.LoadBalancerTagsUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.LogicalNetwork(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: Optional[LogicalNetworkProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: Optional[LogicalNetworkProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.LogicalNetworkArmReference(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.LogicalNetworkProperties(_Model):
        dhcp_options: Optional[LogicalNetworkPropertiesDhcpOptions]
        fabric_network_configuration: Optional[ManagedNetworkFabricArmReference]
        network_type: Optional[Union[str, LogicalNetworkTypeEnum]]
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        status: Optional[LogicalNetworkStatus]
        subnets: Optional[list[Subnet]]
        vm_switch_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                dhcp_options: Optional[LogicalNetworkPropertiesDhcpOptions] = ..., 
                fabric_network_configuration: Optional[ManagedNetworkFabricArmReference] = ..., 
                subnets: Optional[list[Subnet]] = ..., 
                vm_switch_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.LogicalNetworkPropertiesDhcpOptions(_Model):
        dns_servers: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                dns_servers: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.LogicalNetworkStatus(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        fabric_integration: Optional[FabricIntegrationStatus]
        provisioning_status: Optional[LogicalNetworkStatusProvisioningStatus]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                fabric_integration: Optional[FabricIntegrationStatus] = ..., 
                provisioning_status: Optional[LogicalNetworkStatusProvisioningStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.LogicalNetworkStatusProvisioningStatus(_Model):
        operation_id: Optional[str]
        status: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                operation_id: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.LogicalNetworkTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INFRASTRUCTURE = "Infrastructure"
        WORKLOAD = "Workload"


    class azure.mgmt.azurestackhcivm.models.LogicalNetworksUpdateRequest(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.ManagedNetworkFabricArmReference(_Model):
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.azurestackhcivm.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.azurestackhcivm.models.MarketplaceGalleryImage(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: Optional[MarketplaceGalleryImageProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: Optional[MarketplaceGalleryImageProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.MarketplaceGalleryImageProperties(_Model):
        cloud_init_data_source: Optional[Union[str, CloudInitDataSource]]
        container_id: Optional[str]
        hyper_v_generation: Optional[Union[str, HyperVGeneration]]
        identifier: Optional[GalleryImageIdentifier]
        os_type: Union[str, OperatingSystemTypes]
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        status: Optional[MarketplaceGalleryImageStatus]
        version: Optional[GalleryImageVersion]

        @overload
        def __init__(
                self, 
                *, 
                cloud_init_data_source: Optional[Union[str, CloudInitDataSource]] = ..., 
                container_id: Optional[str] = ..., 
                hyper_v_generation: Optional[Union[str, HyperVGeneration]] = ..., 
                identifier: Optional[GalleryImageIdentifier] = ..., 
                os_type: Union[str, OperatingSystemTypes], 
                version: Optional[GalleryImageVersion] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.MarketplaceGalleryImageStatus(_Model):
        download_status: Optional[MarketplaceGalleryImageStatusDownloadStatus]
        error_code: Optional[str]
        error_message: Optional[str]
        progress_percentage: Optional[int]
        provisioning_status: Optional[MarketplaceGalleryImageStatusProvisioningStatus]

        @overload
        def __init__(
                self, 
                *, 
                download_status: Optional[MarketplaceGalleryImageStatusDownloadStatus] = ..., 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                progress_percentage: Optional[int] = ..., 
                provisioning_status: Optional[MarketplaceGalleryImageStatusProvisioningStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.MarketplaceGalleryImageStatusDownloadStatus(_Model):
        download_size_in_mb: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                download_size_in_mb: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.MarketplaceGalleryImageStatusProvisioningStatus(_Model):
        operation_id: Optional[str]
        status: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                operation_id: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.MarketplaceGalleryImageTagsUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.NatGateway(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: Optional[NatGatewayProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: Optional[NatGatewayProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.NatGatewayArmReference(_Model):
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.NatGatewayProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        public_ip_addresses: Optional[list[PublicIPAddressArmReference]]
        status: Optional[NatGatewayStatus]
        subnets: Optional[list[VirtualNetworkSubnetArmReference]]

        @overload
        def __init__(
                self, 
                *, 
                public_ip_addresses: Optional[list[PublicIPAddressArmReference]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.NatGatewayStatus(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        provisioning_status: Optional[NatGatewayStatusProvisioningStatus]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                provisioning_status: Optional[NatGatewayStatusProvisioningStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.NatGatewayStatusProvisioningStatus(_Model):
        operation_id: Optional[str]
        status: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                operation_id: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.NatGatewayTagsUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.NetworkInterface(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: Optional[NetworkInterfaceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: Optional[NetworkInterfaceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.NetworkInterfaceArmReference(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.NetworkInterfaceProperties(_Model):
        bypass_sdn_policies: Optional[bool]
        create_from_local: Optional[bool]
        dns_settings: Optional[InterfaceDNSSettings]
        ip_configurations: Optional[list[IPConfiguration]]
        mac_address: Optional[str]
        network_security_group: Optional[NetworkSecurityGroupArmReference]
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        status: Optional[NetworkInterfaceStatus]

        @overload
        def __init__(
                self, 
                *, 
                bypass_sdn_policies: Optional[bool] = ..., 
                create_from_local: Optional[bool] = ..., 
                dns_settings: Optional[InterfaceDNSSettings] = ..., 
                ip_configurations: Optional[list[IPConfiguration]] = ..., 
                mac_address: Optional[str] = ..., 
                network_security_group: Optional[NetworkSecurityGroupArmReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.NetworkInterfaceStatus(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        provisioning_status: Optional[NetworkInterfaceStatusProvisioningStatus]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                provisioning_status: Optional[NetworkInterfaceStatusProvisioningStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.NetworkInterfaceStatusProvisioningStatus(_Model):
        operation_id: Optional[str]
        status: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                operation_id: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.NetworkInterfacesUpdateProperties(_Model):
        bypass_sdn_policies: Optional[bool]
        dns_settings: Optional[InterfaceDNSSettings]
        network_security_group: Optional[NetworkSecurityGroupArmReference]

        @overload
        def __init__(
                self, 
                *, 
                bypass_sdn_policies: Optional[bool] = ..., 
                dns_settings: Optional[InterfaceDNSSettings] = ..., 
                network_security_group: Optional[NetworkSecurityGroupArmReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.NetworkInterfacesUpdateRequest(_Model):
        properties: Optional[NetworkInterfacesUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NetworkInterfacesUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.NetworkProfileUpdate(_Model):
        network_interfaces: Optional[list[NetworkInterfaceArmReference]]

        @overload
        def __init__(
                self, 
                *, 
                network_interfaces: Optional[list[NetworkInterfaceArmReference]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.NetworkSecurityGroup(TrackedResource):
        e_tag: Optional[str]
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: Optional[NetworkSecurityGroupProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: Optional[NetworkSecurityGroupProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.NetworkSecurityGroupArmReference(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.NetworkSecurityGroupProperties(_Model):
        network_interfaces: Optional[list[NetworkInterfaceArmReference]]
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        status: Optional[NetworkSecurityGroupStatus]
        subnets: Optional[list[LogicalNetworkArmReference]]


    class azure.mgmt.azurestackhcivm.models.NetworkSecurityGroupStatus(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        provisioning_status: Optional[NetworkSecurityGroupStatusProvisioningStatus]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                provisioning_status: Optional[NetworkSecurityGroupStatusProvisioningStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.NetworkSecurityGroupStatusProvisioningStatus(_Model):
        operation_id: Optional[str]
        status: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                operation_id: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.NetworkSecurityGroupTagsUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.OperatingSystemTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.azurestackhcivm.models.Operation(_Model):
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


    class azure.mgmt.azurestackhcivm.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.azurestackhcivm.models.OperationStatusResult(_Model):
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


    class azure.mgmt.azurestackhcivm.models.OperationStepResult(_Model):
        completed_time: Optional[datetime]
        message: Optional[str]
        name: str
        status: Union[str, Status]

        @overload
        def __init__(
                self, 
                *, 
                completed_time: Optional[datetime] = ..., 
                message: Optional[str] = ..., 
                name: str, 
                status: Union[str, Status]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.azurestackhcivm.models.OsProfileUpdate(_Model):
        computer_name: Optional[str]
        linux_configuration: Optional[OsProfileUpdateLinuxConfiguration]
        windows_configuration: Optional[OsProfileUpdateWindowsConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                computer_name: Optional[str] = ..., 
                linux_configuration: Optional[OsProfileUpdateLinuxConfiguration] = ..., 
                windows_configuration: Optional[OsProfileUpdateWindowsConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.OsProfileUpdateLinuxConfiguration(_Model):
        provision_vm_agent: Optional[bool]
        provision_vm_config_agent: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                provision_vm_agent: Optional[bool] = ..., 
                provision_vm_config_agent: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.OsProfileUpdateWindowsConfiguration(_Model):
        provision_vm_agent: Optional[bool]
        provision_vm_config_agent: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                provision_vm_agent: Optional[bool] = ..., 
                provision_vm_config_agent: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.PowerOffVirtualMachineOptions(_Model):
        skip_shutdown: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                skip_shutdown: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.PowerStateEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEALLOCATED = "Deallocated"
        DEALLOCATING = "Deallocating"
        PAUSED = "Paused"
        RUNNING = "Running"
        SAVED = "Saved"
        STARTING = "Starting"
        STOPPED = "Stopped"
        STOPPING = "Stopping"
        UNKNOWN = "Unknown"


    class azure.mgmt.azurestackhcivm.models.Probe(_Model):
        name: str
        properties: ProbeProperties

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: ProbeProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.ProbeProperties(_Model):
        interval_in_seconds: Optional[int]
        number_of_probes: Optional[int]
        port: int
        protocol: Union[str, LoadBalancerProbeProtocol]
        request_path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                interval_in_seconds: Optional[int] = ..., 
                number_of_probes: Optional[int] = ..., 
                port: int, 
                protocol: Union[str, LoadBalancerProbeProtocol], 
                request_path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.ProvisioningAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INSTALL = "install"
        REPAIR = "repair"
        UNINSTALL = "uninstall"


    class azure.mgmt.azurestackhcivm.models.ProvisioningStateEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.azurestackhcivm.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhcivm.models.PublicIPAddress(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: Optional[PublicIPAddressProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: Optional[PublicIPAddressProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.PublicIPAddressArmReference(_Model):
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.PublicIPAddressProperties(_Model):
        ip_address: Optional[str]
        ip_allocation_scope: Optional[str]
        ip_configuration: Optional[IPConfigurationArmReference]
        nat_gateway: Optional[NatGatewayArmReference]
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        public_ip_address_version: Optional[Union[str, PublicIPAddressType]]

        @overload
        def __init__(
                self, 
                *, 
                ip_address: Optional[str] = ..., 
                ip_allocation_scope: Optional[str] = ..., 
                public_ip_address_version: Optional[Union[str, PublicIPAddressType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.PublicIPAddressTagsUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.PublicIPAddressType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        I_PV4 = "IPv4"
        I_PV6 = "IPv6"


    class azure.mgmt.azurestackhcivm.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.azurestackhcivm.models.Route(_Model):
        name: Optional[str]
        properties: Optional[RouteProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[RouteProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.azurestackhcivm.models.RouteProperties(_Model):
        address_prefix: Optional[str]
        next_hop_ip_address: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                address_prefix: Optional[str] = ..., 
                next_hop_ip_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.RouteTable(_Model):
        etag: Optional[str]
        name: Optional[str]
        properties: Optional[RouteTableProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RouteTableProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.azurestackhcivm.models.RouteTableProperties(_Model):
        routes: Optional[list[Route]]

        @overload
        def __init__(
                self, 
                *, 
                routes: Optional[list[Route]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.SecurityEncryptionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NON_PERSISTED_TPM = "NonPersistedTPM"


    class azure.mgmt.azurestackhcivm.models.SecurityRule(ProxyResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        name: str
        properties: Optional[SecurityRuleProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                properties: Optional[SecurityRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.SecurityRuleAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.azurestackhcivm.models.SecurityRuleDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INBOUND = "Inbound"
        OUTBOUND = "Outbound"


    class azure.mgmt.azurestackhcivm.models.SecurityRuleProperties(_Model):
        access: Union[str, SecurityRuleAccess]
        description: Optional[str]
        destination_address_prefixes: Optional[list[str]]
        destination_port_ranges: Optional[list[str]]
        direction: Union[str, SecurityRuleDirection]
        priority: int
        protocol: Union[str, SecurityRuleProtocol]
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        source_address_prefixes: Optional[list[str]]
        source_port_ranges: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                access: Union[str, SecurityRuleAccess], 
                description: Optional[str] = ..., 
                destination_address_prefixes: Optional[list[str]] = ..., 
                destination_port_ranges: Optional[list[str]] = ..., 
                direction: Union[str, SecurityRuleDirection], 
                priority: int, 
                protocol: Union[str, SecurityRuleProtocol], 
                source_address_prefixes: Optional[list[str]] = ..., 
                source_port_ranges: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.SecurityRuleProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASTERISK = "*"
        ICMP = "Icmp"
        TCP = "Tcp"
        UDP = "Udp"


    class azure.mgmt.azurestackhcivm.models.SecurityTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIDENTIAL_VM = "ConfidentialVM"
        TRUSTED_LAUNCH = "TrustedLaunch"


    class azure.mgmt.azurestackhcivm.models.Snapshot(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: Optional[SnapshotProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: Optional[SnapshotProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.SnapshotProperties(_Model):
        creation_data: Optional[CreationData]
        disk_size_bytes: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        status: Optional[SnapshotStatus]
        time_created: Optional[datetime]
        unique_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                creation_data: Optional[CreationData] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.SnapshotStatus(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        provisioning_status: Optional[SnapshotStatusProvisioningStatus]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                provisioning_status: Optional[SnapshotStatusProvisioningStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.SnapshotStatusProvisioningStatus(_Model):
        operation_id: Optional[str]
        status: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                operation_id: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.SnapshotTagsUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.SshConfiguration(_Model):
        public_keys: Optional[list[SshPublicKey]]

        @overload
        def __init__(
                self, 
                *, 
                public_keys: Optional[list[SshPublicKey]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.SshPublicKey(_Model):
        key_data: Optional[str]
        path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_data: Optional[str] = ..., 
                path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.azurestackhcivm.models.StatusLevelTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        INFO = "Info"
        WARNING = "Warning"


    class azure.mgmt.azurestackhcivm.models.StatusTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.azurestackhcivm.models.StorageContainer(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: Optional[StorageContainerProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: Optional[StorageContainerProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.StorageContainerProperties(_Model):
        path: str
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        status: Optional[StorageContainerStatus]

        @overload
        def __init__(
                self, 
                *, 
                path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.StorageContainerStatus(_Model):
        available_size_mb: Optional[int]
        container_size_mb: Optional[int]
        error_code: Optional[str]
        error_message: Optional[str]
        provisioning_status: Optional[StorageContainerStatusProvisioningStatus]

        @overload
        def __init__(
                self, 
                *, 
                available_size_mb: Optional[int] = ..., 
                container_size_mb: Optional[int] = ..., 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                provisioning_status: Optional[StorageContainerStatusProvisioningStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.StorageContainerStatusProvisioningStatus(_Model):
        operation_id: Optional[str]
        status: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                operation_id: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.StorageContainerTagsUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.StorageProfileUpdate(_Model):
        data_disks: Optional[list[VirtualHardDiskArmReference]]

        @overload
        def __init__(
                self, 
                *, 
                data_disks: Optional[list[VirtualHardDiskArmReference]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.Subnet(_Model):
        name: Optional[str]
        properties: Optional[SubnetProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[SubnetProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.azurestackhcivm.models.SubnetIpConfigurationReference(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.SubnetProperties(_Model):
        address_prefix: Optional[str]
        address_prefixes: Optional[list[str]]
        ip_allocation_method: Optional[Union[str, IpAllocationMethodEnum]]
        ip_configuration_references: Optional[list[SubnetIpConfigurationReference]]
        ip_pools: Optional[list[IPPool]]
        network_security_group: Optional[NetworkSecurityGroupArmReference]
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        route_table: Optional[RouteTable]
        vlan: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                address_prefix: Optional[str] = ..., 
                address_prefixes: Optional[list[str]] = ..., 
                ip_allocation_method: Optional[Union[str, IpAllocationMethodEnum]] = ..., 
                ip_configuration_references: Optional[list[SubnetIpConfigurationReference]] = ..., 
                ip_pools: Optional[list[IPPool]] = ..., 
                network_security_group: Optional[NetworkSecurityGroupArmReference] = ..., 
                route_table: Optional[RouteTable] = ..., 
                vlan: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.SystemData(_Model):
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


    class azure.mgmt.azurestackhcivm.models.TrackedResource(Resource):
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


    class azure.mgmt.azurestackhcivm.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.azurestackhcivm.models.VMDiskSecurityProfile(_Model):
        security_encryption_type: Optional[Union[str, SecurityEncryptionType]]

        @overload
        def __init__(
                self, 
                *, 
                security_encryption_type: Optional[Union[str, SecurityEncryptionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualHardDisk(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: Optional[VirtualHardDiskProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: Optional[VirtualHardDiskProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualHardDiskArmReference(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualHardDiskDownloadStatus(_Model):
        downloaded_size_in_mb: Optional[int]
        progress_percentage: Optional[int]
        status: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                downloaded_size_in_mb: Optional[int] = ..., 
                progress_percentage: Optional[int] = ..., 
                status: Optional[Union[str, Status]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualHardDiskProperties(_Model):
        block_size_bytes: Optional[int]
        container_id: Optional[str]
        create_from_local: Optional[bool]
        creation_data: Optional[CreationData]
        disk_file_format: Optional[Union[str, DiskFileFormat]]
        disk_size_gb: Optional[int]
        download_url: Optional[str]
        dynamic: Optional[bool]
        hyper_v_generation: Optional[Union[str, HyperVGeneration]]
        local_vhd_path: Optional[str]
        logical_sector_bytes: Optional[int]
        max_shares: Optional[int]
        physical_sector_bytes: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        status: Optional[VirtualHardDiskStatus]

        @overload
        def __init__(
                self, 
                *, 
                block_size_bytes: Optional[int] = ..., 
                container_id: Optional[str] = ..., 
                create_from_local: Optional[bool] = ..., 
                creation_data: Optional[CreationData] = ..., 
                disk_file_format: Optional[Union[str, DiskFileFormat]] = ..., 
                disk_size_gb: Optional[int] = ..., 
                download_url: Optional[str] = ..., 
                dynamic: Optional[bool] = ..., 
                hyper_v_generation: Optional[Union[str, HyperVGeneration]] = ..., 
                local_vhd_path: Optional[str] = ..., 
                logical_sector_bytes: Optional[int] = ..., 
                max_shares: Optional[int] = ..., 
                physical_sector_bytes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualHardDiskStatus(_Model):
        download_status: Optional[VirtualHardDiskDownloadStatus]
        error_code: Optional[str]
        error_message: Optional[str]
        managed_by: Optional[list[str]]
        provisioning_status: Optional[VirtualHardDiskStatusProvisioningStatus]
        unique_id: Optional[str]
        upload_status: Optional[VirtualHardDiskUploadStatus]

        @overload
        def __init__(
                self, 
                *, 
                download_status: Optional[VirtualHardDiskDownloadStatus] = ..., 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                managed_by: Optional[list[str]] = ..., 
                provisioning_status: Optional[VirtualHardDiskStatusProvisioningStatus] = ..., 
                unique_id: Optional[str] = ..., 
                upload_status: Optional[VirtualHardDiskUploadStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualHardDiskStatusProvisioningStatus(_Model):
        operation_id: Optional[str]
        status: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                operation_id: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualHardDiskUploadRequest(_Model):
        azure_managed_disk_upload_url: str

        @overload
        def __init__(
                self, 
                *, 
                azure_managed_disk_upload_url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualHardDiskUploadResponse(_Model):
        upload_status: Optional[VirtualHardDiskUploadStatus]
        virtual_hard_disk_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                upload_status: Optional[VirtualHardDiskUploadStatus] = ..., 
                virtual_hard_disk_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualHardDiskUploadStatus(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        progress_percentage: Optional[int]
        status: Optional[Union[str, Status]]
        uploaded_size_in_mb: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                progress_percentage: Optional[int] = ..., 
                status: Optional[Union[str, Status]] = ..., 
                uploaded_size_in_mb: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualHardDisksUpdateProperties(_Model):
        disk_size_gb: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                disk_size_gb: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualHardDisksUpdateRequest(_Model):
        properties: Optional[VirtualHardDisksUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VirtualHardDisksUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualMachineConfigAgentInstanceView(_Model):
        statuses: Optional[list[InstanceViewStatus]]
        vm_config_agent_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                statuses: Optional[list[InstanceViewStatus]] = ..., 
                vm_config_agent_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualMachineInstance(ExtensionResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        identity: Optional[ManagedServiceIdentity]
        name: str
        properties: Optional[VirtualMachineInstanceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[VirtualMachineInstanceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualMachineInstanceManagedDiskParameters(_Model):
        security_profile: Optional[VMDiskSecurityProfile]

        @overload
        def __init__(
                self, 
                *, 
                security_profile: Optional[VMDiskSecurityProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualMachineInstanceProperties(_Model):
        create_from_local: Optional[bool]
        guest_agent_install_status: Optional[GuestAgentInstallStatus]
        hardware_profile: Optional[VirtualMachineInstancePropertiesHardwareProfile]
        host_node_ip_address: Optional[str]
        host_node_name: Optional[str]
        http_proxy_config: Optional[HttpProxyConfiguration]
        hyper_v_vm_id: Optional[str]
        instance_view: Optional[VirtualMachineInstanceView]
        local_vm_name: Optional[str]
        network_profile: Optional[VirtualMachineInstancePropertiesNetworkProfile]
        os_profile: Optional[VirtualMachineInstancePropertiesOsProfile]
        placement_profile: Optional[VirtualMachineInstancePropertiesPlacementProfile]
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        resource_uid: Optional[str]
        security_profile: Optional[VirtualMachineInstancePropertiesSecurityProfile]
        status: Optional[VirtualMachineInstanceStatus]
        storage_profile: Optional[VirtualMachineInstancePropertiesStorageProfile]
        vm_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                create_from_local: Optional[bool] = ..., 
                guest_agent_install_status: Optional[GuestAgentInstallStatus] = ..., 
                hardware_profile: Optional[VirtualMachineInstancePropertiesHardwareProfile] = ..., 
                http_proxy_config: Optional[HttpProxyConfiguration] = ..., 
                local_vm_name: Optional[str] = ..., 
                network_profile: Optional[VirtualMachineInstancePropertiesNetworkProfile] = ..., 
                os_profile: Optional[VirtualMachineInstancePropertiesOsProfile] = ..., 
                placement_profile: Optional[VirtualMachineInstancePropertiesPlacementProfile] = ..., 
                resource_uid: Optional[str] = ..., 
                security_profile: Optional[VirtualMachineInstancePropertiesSecurityProfile] = ..., 
                storage_profile: Optional[VirtualMachineInstancePropertiesStorageProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualMachineInstancePropertiesHardwareProfile(_Model):
        dynamic_memory_config: Optional[VirtualMachineInstancePropertiesHardwareProfileDynamicMemoryConfig]
        memory_mb: Optional[int]
        processors: Optional[int]
        virtual_machine_gp_us: Optional[list[VirtualMachineInstancePropertiesHardwareProfileVirtualMachineGPU]]
        vm_size: Optional[Union[str, VmSizeEnum]]

        @overload
        def __init__(
                self, 
                *, 
                dynamic_memory_config: Optional[VirtualMachineInstancePropertiesHardwareProfileDynamicMemoryConfig] = ..., 
                memory_mb: Optional[int] = ..., 
                processors: Optional[int] = ..., 
                virtual_machine_gp_us: Optional[list[VirtualMachineInstancePropertiesHardwareProfileVirtualMachineGPU]] = ..., 
                vm_size: Optional[Union[str, VmSizeEnum]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualMachineInstancePropertiesHardwareProfileDynamicMemoryConfig(_Model):
        enabled: Optional[bool]
        maximum_memory_mb: Optional[int]
        minimum_memory_mb: Optional[int]
        target_memory_buffer: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                maximum_memory_mb: Optional[int] = ..., 
                minimum_memory_mb: Optional[int] = ..., 
                target_memory_buffer: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualMachineInstancePropertiesHardwareProfileVirtualMachineGPU(_Model):
        assignment_type: Union[str, GpuAssignmentTypeEnum]
        gpu_name: Optional[str]
        partition_size_mb: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                assignment_type: Union[str, GpuAssignmentTypeEnum], 
                gpu_name: Optional[str] = ..., 
                partition_size_mb: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualMachineInstancePropertiesNetworkProfile(_Model):
        network_interfaces: Optional[list[NetworkInterfaceArmReference]]

        @overload
        def __init__(
                self, 
                *, 
                network_interfaces: Optional[list[NetworkInterfaceArmReference]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualMachineInstancePropertiesOsProfile(_Model):
        admin_password: Optional[str]
        admin_username: Optional[str]
        computer_name: Optional[str]
        linux_configuration: Optional[VirtualMachineInstancePropertiesOsProfileLinuxConfiguration]
        windows_configuration: Optional[VirtualMachineInstancePropertiesOsProfileWindowsConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                admin_password: Optional[str] = ..., 
                admin_username: Optional[str] = ..., 
                computer_name: Optional[str] = ..., 
                linux_configuration: Optional[VirtualMachineInstancePropertiesOsProfileLinuxConfiguration] = ..., 
                windows_configuration: Optional[VirtualMachineInstancePropertiesOsProfileWindowsConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualMachineInstancePropertiesOsProfileLinuxConfiguration(_Model):
        disable_password_authentication: Optional[bool]
        provision_vm_agent: Optional[bool]
        provision_vm_config_agent: Optional[bool]
        ssh: Optional[SshConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                disable_password_authentication: Optional[bool] = ..., 
                provision_vm_agent: Optional[bool] = ..., 
                provision_vm_config_agent: Optional[bool] = ..., 
                ssh: Optional[SshConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualMachineInstancePropertiesOsProfileWindowsConfiguration(_Model):
        enable_automatic_updates: Optional[bool]
        provision_vm_agent: Optional[bool]
        provision_vm_config_agent: Optional[bool]
        ssh: Optional[SshConfiguration]
        time_zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enable_automatic_updates: Optional[bool] = ..., 
                provision_vm_agent: Optional[bool] = ..., 
                provision_vm_config_agent: Optional[bool] = ..., 
                ssh: Optional[SshConfiguration] = ..., 
                time_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualMachineInstancePropertiesPlacementProfile(_Model):
        strict_placement_policy: Optional[bool]
        zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                strict_placement_policy: Optional[bool] = ..., 
                zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualMachineInstancePropertiesSecurityProfile(_Model):
        enable_tpm: Optional[bool]
        security_type: Optional[Union[str, SecurityTypes]]
        uefi_settings: Optional[VirtualMachineInstancePropertiesSecurityProfileUefiSettings]

        @overload
        def __init__(
                self, 
                *, 
                enable_tpm: Optional[bool] = ..., 
                security_type: Optional[Union[str, SecurityTypes]] = ..., 
                uefi_settings: Optional[VirtualMachineInstancePropertiesSecurityProfileUefiSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualMachineInstancePropertiesSecurityProfileUefiSettings(_Model):
        secure_boot_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                secure_boot_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualMachineInstancePropertiesStorageProfile(_Model):
        data_disks: Optional[list[VirtualHardDiskArmReference]]
        image_reference: Optional[ImageArmReference]
        os_disk: Optional[VirtualMachineInstancePropertiesStorageProfileOsDisk]
        vm_config_storage_path_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_disks: Optional[list[VirtualHardDiskArmReference]] = ..., 
                image_reference: Optional[ImageArmReference] = ..., 
                os_disk: Optional[VirtualMachineInstancePropertiesStorageProfileOsDisk] = ..., 
                vm_config_storage_path_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualMachineInstancePropertiesStorageProfileOsDisk(_Model):
        id: Optional[str]
        managed_disk: Optional[VirtualMachineInstanceManagedDiskParameters]
        os_type: Optional[Union[str, OperatingSystemTypes]]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                managed_disk: Optional[VirtualMachineInstanceManagedDiskParameters] = ..., 
                os_type: Optional[Union[str, OperatingSystemTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualMachineInstanceStatus(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        operation_details: Optional[list[OperationStepResult]]
        power_state: Optional[Union[str, PowerStateEnum]]
        provisioning_status: Optional[VirtualMachineInstanceStatusProvisioningStatus]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                power_state: Optional[Union[str, PowerStateEnum]] = ..., 
                provisioning_status: Optional[VirtualMachineInstanceStatusProvisioningStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualMachineInstanceStatusProvisioningStatus(_Model):
        operation_id: Optional[str]
        status: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                operation_id: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualMachineInstanceUpdateProperties(_Model):
        hardware_profile: Optional[HardwareProfileUpdate]
        network_profile: Optional[NetworkProfileUpdate]
        os_profile: Optional[OsProfileUpdate]
        storage_profile: Optional[StorageProfileUpdate]

        @overload
        def __init__(
                self, 
                *, 
                hardware_profile: Optional[HardwareProfileUpdate] = ..., 
                network_profile: Optional[NetworkProfileUpdate] = ..., 
                os_profile: Optional[OsProfileUpdate] = ..., 
                storage_profile: Optional[StorageProfileUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualMachineInstanceUpdateRequest(_Model):
        identity: Optional[Identity]
        properties: Optional[VirtualMachineInstanceUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                properties: Optional[VirtualMachineInstanceUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualMachineInstanceView(_Model):
        vm_agent: Optional[VirtualMachineConfigAgentInstanceView]

        @overload
        def __init__(
                self, 
                *, 
                vm_agent: Optional[VirtualMachineConfigAgentInstanceView] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualNetwork(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: Optional[VirtualNetworkProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: Optional[VirtualNetworkProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualNetworkAddressSpace(_Model):
        address_prefixes: list[str]

        @overload
        def __init__(
                self, 
                *, 
                address_prefixes: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualNetworkArmReference(_Model):
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualNetworkDhcpOptions(_Model):
        dns_servers: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                dns_servers: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualNetworkProperties(_Model):
        address_space: VirtualNetworkAddressSpace
        dhcp_options: VirtualNetworkDhcpOptions
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        status: Optional[VirtualNetworkStatus]

        @overload
        def __init__(
                self, 
                *, 
                address_space: VirtualNetworkAddressSpace, 
                dhcp_options: VirtualNetworkDhcpOptions, 
                status: Optional[VirtualNetworkStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualNetworkStatus(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        provisioning_status: Optional[VirtualNetworkStatusProvisioningStatus]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                provisioning_status: Optional[VirtualNetworkStatusProvisioningStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualNetworkStatusProvisioningStatus(_Model):
        operation_id: Optional[str]
        status: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                operation_id: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualNetworkSubnet(ProxyResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        name: str
        properties: Optional[VirtualNetworkSubnetProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                properties: Optional[VirtualNetworkSubnetProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualNetworkSubnetArmReference(_Model):
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualNetworkSubnetIpConfigurationReference(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualNetworkSubnetProperties(_Model):
        address_prefix: str
        ip_configurations: Optional[list[VirtualNetworkSubnetIpConfigurationReference]]
        nat_gateway: Optional[NatGatewayArmReference]
        network_security_group: Optional[NetworkSecurityGroupArmReference]
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        route_table: Optional[RouteTable]
        status: Optional[VirtualNetworkSubnetStatus]

        @overload
        def __init__(
                self, 
                *, 
                address_prefix: str, 
                nat_gateway: Optional[NatGatewayArmReference] = ..., 
                network_security_group: Optional[NetworkSecurityGroupArmReference] = ..., 
                route_table: Optional[RouteTable] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualNetworkSubnetStatus(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        provisioning_status: Optional[VirtualNetworkSubnetStatusProvisioningStatus]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                provisioning_status: Optional[VirtualNetworkSubnetStatusProvisioningStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualNetworkSubnetStatusProvisioningStatus(_Model):
        operation_id: Optional[str]
        status: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                operation_id: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualNetworkSubnetUpdateProperties(_Model):
        nat_gateway: Optional[NatGatewayArmReference]
        network_security_group: Optional[NetworkSecurityGroupArmReference]

        @overload
        def __init__(
                self, 
                *, 
                nat_gateway: Optional[NatGatewayArmReference] = ..., 
                network_security_group: Optional[NetworkSecurityGroupArmReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualNetworkSubnetUpdateRequest(_Model):
        properties: Optional[VirtualNetworkSubnetUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VirtualNetworkSubnetUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualNetworkTagsUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VmSizeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"
        DEFAULT = "Default"
        STANDARD_A2_V2 = "Standard_A2_v2"
        STANDARD_A4_V2 = "Standard_A4_v2"
        STANDARD_D16_S_V3 = "Standard_D16s_v3"
        STANDARD_D2_S_V3 = "Standard_D2s_v3"
        STANDARD_D32_S_V3 = "Standard_D32s_v3"
        STANDARD_D4_S_V3 = "Standard_D4s_v3"
        STANDARD_D8_S_V3 = "Standard_D8s_v3"
        STANDARD_DS13_V2 = "Standard_DS13_v2"
        STANDARD_DS2_V2 = "Standard_DS2_v2"
        STANDARD_DS3_V2 = "Standard_DS3_v2"
        STANDARD_DS4_V2 = "Standard_DS4_v2"
        STANDARD_DS5_V2 = "Standard_DS5_v2"
        STANDARD_K8_S2_V1 = "Standard_K8S2_v1"
        STANDARD_K8_S3_V1 = "Standard_K8S3_v1"
        STANDARD_K8_S4_V1 = "Standard_K8S4_v1"
        STANDARD_K8_S5_V1 = "Standard_K8S5_v1"
        STANDARD_K8_S_V1 = "Standard_K8S_v1"
        STANDARD_NK12 = "Standard_NK12"
        STANDARD_NK6 = "Standard_NK6"
        STANDARD_NV12 = "Standard_NV12"
        STANDARD_NV6 = "Standard_NV6"


namespace azure.mgmt.azurestackhcivm.operations

    class azure.mgmt.azurestackhcivm.operations.AttestationStatusesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AttestationStatus: ...


    class azure.mgmt.azurestackhcivm.operations.GalleryImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_image_name: str, 
                resource: GalleryImage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryImage]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_image_name: str, 
                resource: GalleryImage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryImage]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_image_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryImage]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                gallery_image_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_image_name: str, 
                properties: GalleryImageTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryImage]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_image_name: str, 
                properties: GalleryImageTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryImage]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_image_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryImage]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                gallery_image_name: str, 
                **kwargs: Any
            ) -> GalleryImage: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> ItemPaged[GalleryImage]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GalleryImage]: ...


    class azure.mgmt.azurestackhcivm.operations.GuestAgentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_uri: str, 
                resource: GuestAgent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GuestAgent]: ...

        @overload
        def begin_create(
                self, 
                resource_uri: str, 
                resource: GuestAgent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GuestAgent]: ...

        @overload
        def begin_create(
                self, 
                resource_uri: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GuestAgent]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> GuestAgent: ...

        @distributed_trace
        def list_by_virtual_machine_instance(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> ItemPaged[GuestAgent]: ...


    class azure.mgmt.azurestackhcivm.operations.HybridIdentityMetadataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> HybridIdentityMetadata: ...

        @distributed_trace
        def list_by_virtual_machine_instance(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> ItemPaged[HybridIdentityMetadata]: ...


    class azure.mgmt.azurestackhcivm.operations.InboundRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                inbound_rule_name: str, 
                resource: InboundRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InboundRule]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                inbound_rule_name: str, 
                resource: InboundRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InboundRule]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                inbound_rule_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InboundRule]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'nat_gateway_name', 'inbound_rule_name']}, api_versions_list=['2026-04-01-preview', '2026-07-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                inbound_rule_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'nat_gateway_name', 'inbound_rule_name', 'accept']}, api_versions_list=['2026-04-01-preview', '2026-07-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                inbound_rule_name: str, 
                **kwargs: Any
            ) -> InboundRule: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'nat_gateway_name', 'accept']}, api_versions_list=['2026-04-01-preview', '2026-07-01-preview'])
        def list_by_nat_gateway(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                **kwargs: Any
            ) -> ItemPaged[InboundRule]: ...


    class azure.mgmt.azurestackhcivm.operations.LoadBalancersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                load_balancer_name: str, 
                resource: LoadBalancer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LoadBalancer]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                load_balancer_name: str, 
                resource: LoadBalancer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LoadBalancer]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                load_balancer_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LoadBalancer]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'load_balancer_name']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                load_balancer_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_tags(
                self, 
                resource_group_name: str, 
                load_balancer_name: str, 
                properties: LoadBalancerTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LoadBalancer]: ...

        @overload
        def begin_update_tags(
                self, 
                resource_group_name: str, 
                load_balancer_name: str, 
                properties: LoadBalancerTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LoadBalancer]: ...

        @overload
        def begin_update_tags(
                self, 
                resource_group_name: str, 
                load_balancer_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LoadBalancer]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'load_balancer_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                load_balancer_name: str, 
                **kwargs: Any
            ) -> LoadBalancer: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def list_all(self, **kwargs: Any) -> ItemPaged[LoadBalancer]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[LoadBalancer]: ...


    class azure.mgmt.azurestackhcivm.operations.LogicalNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                logical_network_name: str, 
                resource: LogicalNetwork, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LogicalNetwork]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                logical_network_name: str, 
                resource: LogicalNetwork, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LogicalNetwork]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                logical_network_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LogicalNetwork]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                logical_network_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                logical_network_name: str, 
                properties: LogicalNetworksUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LogicalNetwork]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                logical_network_name: str, 
                properties: LogicalNetworksUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LogicalNetwork]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                logical_network_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LogicalNetwork]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                logical_network_name: str, 
                **kwargs: Any
            ) -> LogicalNetwork: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> ItemPaged[LogicalNetwork]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[LogicalNetwork]: ...


    class azure.mgmt.azurestackhcivm.operations.MarketplaceGalleryImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                marketplace_gallery_image_name: str, 
                resource: MarketplaceGalleryImage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MarketplaceGalleryImage]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                marketplace_gallery_image_name: str, 
                resource: MarketplaceGalleryImage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MarketplaceGalleryImage]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                marketplace_gallery_image_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MarketplaceGalleryImage]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                marketplace_gallery_image_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                marketplace_gallery_image_name: str, 
                properties: MarketplaceGalleryImageTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MarketplaceGalleryImage]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                marketplace_gallery_image_name: str, 
                properties: MarketplaceGalleryImageTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MarketplaceGalleryImage]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                marketplace_gallery_image_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MarketplaceGalleryImage]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                marketplace_gallery_image_name: str, 
                **kwargs: Any
            ) -> MarketplaceGalleryImage: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> ItemPaged[MarketplaceGalleryImage]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MarketplaceGalleryImage]: ...


    class azure.mgmt.azurestackhcivm.operations.NatGatewaysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                resource: NatGateway, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NatGateway]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                resource: NatGateway, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NatGateway]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NatGateway]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'nat_gateway_name']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_tags(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                properties: NatGatewayTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NatGateway]: ...

        @overload
        def begin_update_tags(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                properties: NatGatewayTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NatGateway]: ...

        @overload
        def begin_update_tags(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NatGateway]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'nat_gateway_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                nat_gateway_name: str, 
                **kwargs: Any
            ) -> NatGateway: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def list_all(self, **kwargs: Any) -> ItemPaged[NatGateway]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NatGateway]: ...


    class azure.mgmt.azurestackhcivm.operations.NetworkInterfacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_interface_name: str, 
                resource: NetworkInterface, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkInterface]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_interface_name: str, 
                resource: NetworkInterface, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkInterface]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_interface_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkInterface]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_interface_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_interface_name: str, 
                properties: NetworkInterfacesUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkInterface]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_interface_name: str, 
                properties: NetworkInterfacesUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkInterface]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_interface_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkInterface]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                network_interface_name: str, 
                **kwargs: Any
            ) -> NetworkInterface: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> ItemPaged[NetworkInterface]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkInterface]: ...


    class azure.mgmt.azurestackhcivm.operations.NetworkSecurityGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                resource: NetworkSecurityGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkSecurityGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                resource: NetworkSecurityGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkSecurityGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkSecurityGroup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_tags(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                properties: NetworkSecurityGroupTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkSecurityGroup]: ...

        @overload
        def begin_update_tags(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                properties: NetworkSecurityGroupTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkSecurityGroup]: ...

        @overload
        def begin_update_tags(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkSecurityGroup]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityGroup: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> ItemPaged[NetworkSecurityGroup]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkSecurityGroup]: ...


    class azure.mgmt.azurestackhcivm.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.azurestackhcivm.operations.PublicIPAddressesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                public_ip_address_name: str, 
                resource: PublicIPAddress, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PublicIPAddress]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                public_ip_address_name: str, 
                resource: PublicIPAddress, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PublicIPAddress]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                public_ip_address_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PublicIPAddress]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'public_ip_address_name']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                public_ip_address_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_tags(
                self, 
                resource_group_name: str, 
                public_ip_address_name: str, 
                properties: PublicIPAddressTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PublicIPAddress]: ...

        @overload
        def begin_update_tags(
                self, 
                resource_group_name: str, 
                public_ip_address_name: str, 
                properties: PublicIPAddressTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PublicIPAddress]: ...

        @overload
        def begin_update_tags(
                self, 
                resource_group_name: str, 
                public_ip_address_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PublicIPAddress]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'public_ip_address_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                public_ip_address_name: str, 
                **kwargs: Any
            ) -> PublicIPAddress: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def list_all(self, **kwargs: Any) -> ItemPaged[PublicIPAddress]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PublicIPAddress]: ...


    class azure.mgmt.azurestackhcivm.operations.SecurityRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                security_rule_name: str, 
                resource: SecurityRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SecurityRule]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                security_rule_name: str, 
                resource: SecurityRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SecurityRule]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                security_rule_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SecurityRule]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                security_rule_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                security_rule_name: str, 
                **kwargs: Any
            ) -> SecurityRule: ...

        @distributed_trace
        def list_by_network_security_group(
                self, 
                resource_group_name: str, 
                network_security_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SecurityRule]: ...


    class azure.mgmt.azurestackhcivm.operations.SnapshotsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                resource: Snapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Snapshot]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                resource: Snapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Snapshot]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Snapshot]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-02-01-preview', params_added_on={'2026-02-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'snapshot_name']}, api_versions_list=['2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                properties: SnapshotTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Snapshot]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                properties: SnapshotTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Snapshot]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Snapshot]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-02-01-preview', params_added_on={'2026-02-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'snapshot_name', 'accept']}, api_versions_list=['2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                **kwargs: Any
            ) -> Snapshot: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-02-01-preview', params_added_on={'2026-02-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def list_all(self, **kwargs: Any) -> ItemPaged[Snapshot]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-02-01-preview', params_added_on={'2026-02-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Snapshot]: ...


    class azure.mgmt.azurestackhcivm.operations.StorageContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                resource: StorageContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageContainer]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                resource: StorageContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageContainer]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageContainer]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                properties: StorageContainerTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageContainer]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                properties: StorageContainerTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageContainer]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageContainer]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                **kwargs: Any
            ) -> StorageContainer: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> ItemPaged[StorageContainer]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[StorageContainer]: ...


    class azure.mgmt.azurestackhcivm.operations.VirtualHardDisksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_hard_disk_name: str, 
                resource: VirtualHardDisk, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualHardDisk]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_hard_disk_name: str, 
                resource: VirtualHardDisk, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualHardDisk]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_hard_disk_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualHardDisk]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_hard_disk_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_hard_disk_name: str, 
                properties: VirtualHardDisksUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualHardDisk]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_hard_disk_name: str, 
                properties: VirtualHardDisksUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualHardDisk]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_hard_disk_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualHardDisk]: ...

        @overload
        def begin_upload(
                self, 
                resource_group_name: str, 
                virtual_hard_disk_name: str, 
                body: VirtualHardDiskUploadRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualHardDiskUploadResponse]: ...

        @overload
        def begin_upload(
                self, 
                resource_group_name: str, 
                virtual_hard_disk_name: str, 
                body: VirtualHardDiskUploadRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualHardDiskUploadResponse]: ...

        @overload
        def begin_upload(
                self, 
                resource_group_name: str, 
                virtual_hard_disk_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualHardDiskUploadResponse]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                virtual_hard_disk_name: str, 
                **kwargs: Any
            ) -> VirtualHardDisk: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> ItemPaged[VirtualHardDisk]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VirtualHardDisk]: ...


    class azure.mgmt.azurestackhcivm.operations.VirtualMachineInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                resource: VirtualMachineInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineInstance]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                resource: VirtualMachineInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineInstance]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineInstance]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_pause(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_power_off(
                self, 
                resource_uri: str, 
                body: PowerOffVirtualMachineOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_power_off(
                self, 
                resource_uri: str, 
                body: PowerOffVirtualMachineOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_power_off(
                self, 
                resource_uri: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def begin_restart(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_save(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_stop(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_uri: str, 
                properties: VirtualMachineInstanceUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineInstance]: ...

        @overload
        def begin_update(
                self, 
                resource_uri: str, 
                properties: VirtualMachineInstanceUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineInstance]: ...

        @overload
        def begin_update(
                self, 
                resource_uri: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineInstance]: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> VirtualMachineInstance: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> ItemPaged[VirtualMachineInstance]: ...


    class azure.mgmt.azurestackhcivm.operations.VirtualNetworkSubnetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                subnet_name: str, 
                resource: VirtualNetworkSubnet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkSubnet]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                subnet_name: str, 
                resource: VirtualNetworkSubnet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkSubnet]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                subnet_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkSubnet]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'virtual_network_name', 'subnet_name']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                subnet_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                subnet_name: str, 
                properties: VirtualNetworkSubnetUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkSubnet]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                subnet_name: str, 
                properties: VirtualNetworkSubnetUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkSubnet]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                subnet_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkSubnet]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'virtual_network_name', 'subnet_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                subnet_name: str, 
                **kwargs: Any
            ) -> VirtualNetworkSubnet: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'virtual_network_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def list_by_virtual_network(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VirtualNetworkSubnet]: ...


    class azure.mgmt.azurestackhcivm.operations.VirtualNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                resource: VirtualNetwork, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetwork]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                resource: VirtualNetwork, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetwork]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetwork]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'virtual_network_name']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_tags(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                properties: VirtualNetworkTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetwork]: ...

        @overload
        def begin_update_tags(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                properties: VirtualNetworkTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetwork]: ...

        @overload
        def begin_update_tags(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetwork]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'virtual_network_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                **kwargs: Any
            ) -> VirtualNetwork: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def list_all(self, **kwargs: Any) -> ItemPaged[VirtualNetwork]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-02-01-preview', '2026-04-01-preview', '2026-07-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VirtualNetwork]: ...


namespace azure.mgmt.azurestackhcivm.types

    class azure.mgmt.azurestackhcivm.types.BackendAddressPool(TypedDict, total=False):
        key "name": Required[str]
        key "properties": Required[BackendAddressPoolProperties]
        name: str
        properties: BackendAddressPoolProperties


    class azure.mgmt.azurestackhcivm.types.BackendAddressPoolProperties(TypedDict, total=False):
        key "logicalNetwork": ForwardRef('LogicalNetworkArmReference', module='types')
        key "virtualNetwork": ForwardRef('VirtualNetworkArmReference', module='types')
        loadBalancerBackendAddresses: list[LoadBalancerBackendAddress]
        logicalNetwork: LogicalNetworkArmReference
        virtualNetwork: VirtualNetworkArmReference


    class azure.mgmt.azurestackhcivm.types.CreationData(TypedDict, total=False):
        key "createOption": Required[Union[str, DiskCreateOption]]
        key "sourceResourceId": str
        key "sourceUniqueId": str
        createOption: Union[str, DiskCreateOption]
        sourceResourceId: str
        sourceUniqueId: str


    class azure.mgmt.azurestackhcivm.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.azurestackhcivm.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.azurestackhcivm.types.ExtendedLocation(TypedDict, total=False):
        key "name": str
        key "type": Union[str, ExtendedLocationTypes]
        name: str
        type: Union[str, ExtendedLocationTypes]


    class azure.mgmt.azurestackhcivm.types.ExtensionResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.azurestackhcivm.types.FabricIntegrationStatus(TypedDict, total=False):
        key "health": Union[str, FabricConnectionHealthEnum]
        key "lastChecked": str
        key "resourceType": Union[str, FabricResourceTypeEnum]
        key "state": Union[str, FabricIntegrationStateEnum]
        health: Union[str, FabricConnectionHealthEnum]
        issues: list[FabricIssue]
        lastChecked: str
        resourceType: Union[str, FabricResourceTypeEnum]
        state: Union[str, FabricIntegrationStateEnum]


    class azure.mgmt.azurestackhcivm.types.FabricIssue(TypedDict, total=False):
        key "code": str
        key "message": str
        key "severity": str
        key "target": str
        key "timestamp": str
        code: str
        message: str
        severity: str
        target: str
        timestamp: str


    class azure.mgmt.azurestackhcivm.types.FrontendIPConfiguration(TypedDict, total=False):
        key "name": Required[str]
        key "properties": Required[FrontendIPConfigurationProperties]
        name: str
        properties: FrontendIPConfigurationProperties


    class azure.mgmt.azurestackhcivm.types.FrontendIPConfigurationProperties(TypedDict, total=False):
        key "privateIPAddress": str
        key "privateIPAllocationMethod": Union[str, IpAllocationMethodEnum]
        key "publicIPAddress": ForwardRef('PublicIPAddressArmReference', module='types')
        key "subnet": ForwardRef('VirtualNetworkSubnetArmReference', module='types')
        privateIPAddress: str
        privateIPAllocationMethod: Union[str, IpAllocationMethodEnum]
        publicIPAddress: PublicIPAddressArmReference
        subnet: VirtualNetworkSubnetArmReference


    class azure.mgmt.azurestackhcivm.types.GalleryImage(TrackedResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('GalleryImageProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: GalleryImageProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurestackhcivm.types.GalleryImageIdentifier(TypedDict, total=False):
        key "offer": Required[str]
        key "publisher": Required[str]
        key "sku": Required[str]
        offer: str
        publisher: str
        sku: str


    class azure.mgmt.azurestackhcivm.types.GalleryImageProperties(TypedDict, total=False):
        key "cloudInitDataSource": Union[str, CloudInitDataSource]
        key "containerId": str
        key "hyperVGeneration": Union[str, HyperVGeneration]
        key "identifier": ForwardRef('GalleryImageIdentifier', module='types')
        key "imagePath": str
        key "osType": Required[Union[str, OperatingSystemTypes]]
        key "provisioningState": Union[str, ProvisioningStateEnum]
        key "sourceVirtualMachineId": str
        key "status": ForwardRef('GalleryImageStatus', module='types')
        key "version": ForwardRef('GalleryImageVersion', module='types')
        cloudInitDataSource: Union[str, CloudInitDataSource]
        containerId: str
        hyperVGeneration: Union[str, HyperVGeneration]
        identifier: GalleryImageIdentifier
        imagePath: str
        osType: Union[str, OperatingSystemTypes]
        provisioningState: Union[str, ProvisioningStateEnum]
        sourceVirtualMachineId: str
        status: GalleryImageStatus
        version: GalleryImageVersion


    class azure.mgmt.azurestackhcivm.types.GalleryImageStatus(TypedDict, total=False):
        key "downloadStatus": ForwardRef('GalleryImageStatusDownloadStatus', module='types')
        key "errorCode": str
        key "errorMessage": str
        key "progressPercentage": int
        key "provisioningStatus": ForwardRef('GalleryImageStatusProvisioningStatus', module='types')
        downloadStatus: GalleryImageStatusDownloadStatus
        errorCode: str
        errorMessage: str
        progressPercentage: int
        provisioningStatus: GalleryImageStatusProvisioningStatus


    class azure.mgmt.azurestackhcivm.types.GalleryImageStatusDownloadStatus(TypedDict, total=False):
        key "downloadSizeInMB": int
        downloadSizeInMB: int


    class azure.mgmt.azurestackhcivm.types.GalleryImageStatusProvisioningStatus(TypedDict, total=False):
        key "operationId": str
        key "status": Union[str, Status]
        operationId: str
        status: Union[str, Status]


    class azure.mgmt.azurestackhcivm.types.GalleryImageTagsUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.azurestackhcivm.types.GalleryImageVersion(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('GalleryImageVersionProperties', module='types')
        name: str
        properties: GalleryImageVersionProperties


    class azure.mgmt.azurestackhcivm.types.GalleryImageVersionProperties(TypedDict, total=False):
        key "storageProfile": Required[GalleryImageVersionStorageProfile]
        storageProfile: GalleryImageVersionStorageProfile


    class azure.mgmt.azurestackhcivm.types.GalleryImageVersionStorageProfile(TypedDict, total=False):
        key "osDiskImage": ForwardRef('GalleryOSDiskImage', module='types')
        osDiskImage: GalleryOSDiskImage


    class azure.mgmt.azurestackhcivm.types.GalleryOSDiskImage(TypedDict, total=False):
        key "sizeInMB": int
        sizeInMB: int


    class azure.mgmt.azurestackhcivm.types.GuestAgent(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('GuestAgentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: GuestAgentProperties
        systemData: SystemData
        type: str


    class azure.mgmt.azurestackhcivm.types.GuestAgentInstallStatus(TypedDict, total=False):
        key "agentVersion": str
        key "lastStatusChange": str
        key "status": Union[str, StatusTypes]
        key "vmUuid": str
        agentVersion: str
        errorDetails: list[ErrorDetail]
        lastStatusChange: str
        status: Union[str, StatusTypes]
        vmUuid: str


    class azure.mgmt.azurestackhcivm.types.GuestAgentProperties(TypedDict, total=False):
        key "credentials": ForwardRef('GuestCredential', module='types')
        key "provisioningAction": Union[str, ProvisioningAction]
        key "provisioningState": Union[str, ProvisioningStateEnum]
        key "status": str
        credentials: GuestCredential
        provisioningAction: Union[str, ProvisioningAction]
        provisioningState: Union[str, ProvisioningStateEnum]
        status: str


    class azure.mgmt.azurestackhcivm.types.GuestCredential(TypedDict, total=False):
        key "password": str
        key "username": str
        password: str
        username: str


    class azure.mgmt.azurestackhcivm.types.HardwareProfileUpdate(TypedDict, total=False):
        key "dynamicMemoryConfig": ForwardRef('VirtualMachineInstancePropertiesHardwareProfileDynamicMemoryConfig', module='types')
        key "memoryMB": int
        key "processors": int
        key "vmSize": Union[str, VmSizeEnum]
        dynamicMemoryConfig: VirtualMachineInstancePropertiesHardwareProfileDynamicMemoryConfig
        memoryMB: int
        processors: int
        virtualMachineGPUs: list[VirtualMachineInstancePropertiesHardwareProfileVirtualMachineGPU]
        vmSize: Union[str, VmSizeEnum]


    class azure.mgmt.azurestackhcivm.types.HttpProxyConfiguration(TypedDict, total=False):
        key "httpProxy": str
        key "httpsProxy": str
        key "trustedCa": str
        httpProxy: str
        httpsProxy: str
        noProxy: list[str]
        trustedCa: str


    class azure.mgmt.azurestackhcivm.types.IPConfiguration(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('IPConfigurationProperties', module='types')
        name: str
        properties: IPConfigurationProperties


    class azure.mgmt.azurestackhcivm.types.IPConfigurationArmReference(TypedDict, total=False):
        key "resourceId": str
        resourceId: str


    class azure.mgmt.azurestackhcivm.types.IPConfigurationProperties(TypedDict, total=False):
        key "gateway": str
        key "prefixLength": str
        key "privateIPAddress": str
        key "subnet": ForwardRef('LogicalNetworkArmReference', module='types')
        gateway: str
        prefixLength: str
        privateIPAddress: str
        subnet: LogicalNetworkArmReference


    class azure.mgmt.azurestackhcivm.types.IPPool(TypedDict, total=False):
        key "end": str
        key "info": ForwardRef('IPPoolInfo', module='types')
        key "ipPoolType": Union[str, IPPoolTypeEnum]
        key "name": str
        key "start": str
        end: str
        info: IPPoolInfo
        ipPoolType: Union[str, IPPoolTypeEnum]
        name: str
        start: str


    class azure.mgmt.azurestackhcivm.types.IPPoolInfo(TypedDict, total=False):
        key "available": str
        key "used": str
        available: str
        used: str


    class azure.mgmt.azurestackhcivm.types.Identity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Literal["SystemAssigned"]
        principalId: str
        tenantId: str
        type: Literal[SystemAssigned]


    class azure.mgmt.azurestackhcivm.types.ImageArmReference(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.azurestackhcivm.types.InboundRule(ProxyResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "name": str
        key "properties": ForwardRef('InboundRuleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        name: str
        properties: InboundRuleProperties
        systemData: SystemData
        type: str


    class azure.mgmt.azurestackhcivm.types.InboundRuleProperties(TypedDict, total=False):
        key "backendIPConfiguration": Required[IPConfigurationArmReference]
        key "backendPort": Required[int]
        key "frontendPort": Required[int]
        key "protocol": Required[Union[str, InboundNATRuleProtocol]]
        key "provisioningState": Union[str, ProvisioningStateEnum]
        key "publicIPAddress": Required[PublicIPAddressArmReference]
        key "status": ForwardRef('InboundRuleStatus', module='types')
        backendIPConfiguration: IPConfigurationArmReference
        backendPort: int
        frontendPort: int
        protocol: Union[str, InboundNATRuleProtocol]
        provisioningState: Union[str, ProvisioningStateEnum]
        publicIPAddress: PublicIPAddressArmReference
        status: InboundRuleStatus


    class azure.mgmt.azurestackhcivm.types.InboundRuleStatus(TypedDict, total=False):
        key "errorCode": str
        key "errorMessage": str
        key "provisioningStatus": ForwardRef('InboundRuleStatusProvisioningStatus', module='types')
        errorCode: str
        errorMessage: str
        provisioningStatus: InboundRuleStatusProvisioningStatus


    class azure.mgmt.azurestackhcivm.types.InboundRuleStatusProvisioningStatus(TypedDict, total=False):
        key "operationId": str
        key "status": Union[str, Status]
        operationId: str
        status: Union[str, Status]


    class azure.mgmt.azurestackhcivm.types.InstanceViewStatus(TypedDict, total=False):
        key "code": str
        key "displayStatus": str
        key "level": Union[str, StatusLevelTypes]
        key "message": str
        key "time": str
        code: str
        displayStatus: str
        level: Union[str, StatusLevelTypes]
        message: str
        time: str


    class azure.mgmt.azurestackhcivm.types.InterfaceDNSSettings(TypedDict, total=False):
        dnsServers: list[str]


    class azure.mgmt.azurestackhcivm.types.LoadBalancer(TrackedResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('LoadBalancerProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: LoadBalancerProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurestackhcivm.types.LoadBalancerBackendAddress(TypedDict, total=False):
        key "name": Required[str]
        key "properties": Required[LoadBalancerBackendAddressProperties]
        name: str
        properties: LoadBalancerBackendAddressProperties


    class azure.mgmt.azurestackhcivm.types.LoadBalancerBackendAddressPoolReference(TypedDict, total=False):
        key "name": Required[str]
        name: str


    class azure.mgmt.azurestackhcivm.types.LoadBalancerBackendAddressProperties(TypedDict, total=False):
        key "adminState": Union[str, LoadBalancerBackendAddressAdminState]
        key "ipAddress": str
        key "logicalNetwork": ForwardRef('LogicalNetworkArmReference', module='types')
        key "networkInterfaceIPConfiguration": ForwardRef('IPConfigurationArmReference', module='types')
        key "subnet": ForwardRef('VirtualNetworkSubnetArmReference', module='types')
        key "virtualNetwork": ForwardRef('VirtualNetworkArmReference', module='types')
        adminState: Union[str, LoadBalancerBackendAddressAdminState]
        ipAddress: str
        logicalNetwork: LogicalNetworkArmReference
        networkInterfaceIPConfiguration: IPConfigurationArmReference
        subnet: VirtualNetworkSubnetArmReference
        virtualNetwork: VirtualNetworkArmReference


    class azure.mgmt.azurestackhcivm.types.LoadBalancerFrontendIPConfigurationReference(TypedDict, total=False):
        key "name": Required[str]
        name: str


    class azure.mgmt.azurestackhcivm.types.LoadBalancerProbeReference(TypedDict, total=False):
        key "name": Required[str]
        name: str


    class azure.mgmt.azurestackhcivm.types.LoadBalancerProperties(TypedDict, total=False):
        key "frontendIPConfigurations": Required[list[FrontendIPConfiguration]]
        key "provisioningState": Union[str, ProvisioningStateEnum]
        key "status": ForwardRef('LoadBalancerStatus', module='types')
        backendAddressPools: list[BackendAddressPool]
        frontendIPConfigurations: list[FrontendIPConfiguration]
        loadBalancingRules: list[LoadBalancerRule]
        probes: list[Probe]
        provisioningState: Union[str, ProvisioningStateEnum]
        status: LoadBalancerStatus


    class azure.mgmt.azurestackhcivm.types.LoadBalancerRule(TypedDict, total=False):
        key "name": Required[str]
        key "properties": Required[LoadBalancerRuleProperties]
        name: str
        properties: LoadBalancerRuleProperties


    class azure.mgmt.azurestackhcivm.types.LoadBalancerRuleProperties(TypedDict, total=False):
        key "backendAddressPool": Required[LoadBalancerBackendAddressPoolReference]
        key "backendPort": Required[int]
        key "frontendIPConfiguration": Required[LoadBalancerFrontendIPConfigurationReference]
        key "frontendPort": Required[int]
        key "idleTimeoutInMinutes": int
        key "loadDistribution": Union[str, LoadBalancerRuleSessionPersistenceType]
        key "probe": ForwardRef('LoadBalancerProbeReference', module='types')
        key "protocol": Required[Union[str, LoadBalancerRuleTransportProtocol]]
        backendAddressPool: LoadBalancerBackendAddressPoolReference
        backendPort: int
        frontendIPConfiguration: LoadBalancerFrontendIPConfigurationReference
        frontendPort: int
        idleTimeoutInMinutes: int
        loadDistribution: Union[str, LoadBalancerRuleSessionPersistenceType]
        probe: LoadBalancerProbeReference
        protocol: Union[str, LoadBalancerRuleTransportProtocol]


    class azure.mgmt.azurestackhcivm.types.LoadBalancerStatus(TypedDict, total=False):
        key "errorCode": str
        key "errorMessage": str
        key "provisioningStatus": ForwardRef('LoadBalancerStatusProvisioningStatus', module='types')
        errorCode: str
        errorMessage: str
        provisioningStatus: LoadBalancerStatusProvisioningStatus


    class azure.mgmt.azurestackhcivm.types.LoadBalancerStatusProvisioningStatus(TypedDict, total=False):
        key "operationId": str
        key "status": Union[str, Status]
        operationId: str
        status: Union[str, Status]


    class azure.mgmt.azurestackhcivm.types.LoadBalancerTagsUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.azurestackhcivm.types.LogicalNetwork(TrackedResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('LogicalNetworkProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: LogicalNetworkProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurestackhcivm.types.LogicalNetworkArmReference(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.azurestackhcivm.types.LogicalNetworkProperties(TypedDict, total=False):
        key "dhcpOptions": ForwardRef('LogicalNetworkPropertiesDhcpOptions', module='types')
        key "fabricNetworkConfiguration": ForwardRef('ManagedNetworkFabricArmReference', module='types')
        key "networkType": Union[str, LogicalNetworkTypeEnum]
        key "provisioningState": Union[str, ProvisioningStateEnum]
        key "status": ForwardRef('LogicalNetworkStatus', module='types')
        key "vmSwitchName": str
        dhcpOptions: LogicalNetworkPropertiesDhcpOptions
        fabricNetworkConfiguration: ManagedNetworkFabricArmReference
        networkType: Union[str, LogicalNetworkTypeEnum]
        provisioningState: Union[str, ProvisioningStateEnum]
        status: LogicalNetworkStatus
        subnets: list[Subnet]
        vmSwitchName: str


    class azure.mgmt.azurestackhcivm.types.LogicalNetworkPropertiesDhcpOptions(TypedDict, total=False):
        dnsServers: list[str]


    class azure.mgmt.azurestackhcivm.types.LogicalNetworkStatus(TypedDict, total=False):
        key "errorCode": str
        key "errorMessage": str
        key "fabricIntegration": ForwardRef('FabricIntegrationStatus', module='types')
        key "provisioningStatus": ForwardRef('LogicalNetworkStatusProvisioningStatus', module='types')
        errorCode: str
        errorMessage: str
        fabricIntegration: FabricIntegrationStatus
        provisioningStatus: LogicalNetworkStatusProvisioningStatus


    class azure.mgmt.azurestackhcivm.types.LogicalNetworkStatusProvisioningStatus(TypedDict, total=False):
        key "operationId": str
        key "status": Union[str, Status]
        operationId: str
        status: Union[str, Status]


    class azure.mgmt.azurestackhcivm.types.LogicalNetworksUpdateRequest(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.azurestackhcivm.types.ManagedNetworkFabricArmReference(TypedDict, total=False):
        key "resourceId": str
        resourceId: str


    class azure.mgmt.azurestackhcivm.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.azurestackhcivm.types.MarketplaceGalleryImage(TrackedResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('MarketplaceGalleryImageProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: MarketplaceGalleryImageProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurestackhcivm.types.MarketplaceGalleryImageProperties(TypedDict, total=False):
        key "cloudInitDataSource": Union[str, CloudInitDataSource]
        key "containerId": str
        key "hyperVGeneration": Union[str, HyperVGeneration]
        key "identifier": ForwardRef('GalleryImageIdentifier', module='types')
        key "osType": Required[Union[str, OperatingSystemTypes]]
        key "provisioningState": Union[str, ProvisioningStateEnum]
        key "status": ForwardRef('MarketplaceGalleryImageStatus', module='types')
        key "version": ForwardRef('GalleryImageVersion', module='types')
        cloudInitDataSource: Union[str, CloudInitDataSource]
        containerId: str
        hyperVGeneration: Union[str, HyperVGeneration]
        identifier: GalleryImageIdentifier
        osType: Union[str, OperatingSystemTypes]
        provisioningState: Union[str, ProvisioningStateEnum]
        status: MarketplaceGalleryImageStatus
        version: GalleryImageVersion


    class azure.mgmt.azurestackhcivm.types.MarketplaceGalleryImageStatus(TypedDict, total=False):
        key "downloadStatus": ForwardRef('MarketplaceGalleryImageStatusDownloadStatus', module='types')
        key "errorCode": str
        key "errorMessage": str
        key "progressPercentage": int
        key "provisioningStatus": ForwardRef('MarketplaceGalleryImageStatusProvisioningStatus', module='types')
        downloadStatus: MarketplaceGalleryImageStatusDownloadStatus
        errorCode: str
        errorMessage: str
        progressPercentage: int
        provisioningStatus: MarketplaceGalleryImageStatusProvisioningStatus


    class azure.mgmt.azurestackhcivm.types.MarketplaceGalleryImageStatusDownloadStatus(TypedDict, total=False):
        key "downloadSizeInMB": int
        downloadSizeInMB: int


    class azure.mgmt.azurestackhcivm.types.MarketplaceGalleryImageStatusProvisioningStatus(TypedDict, total=False):
        key "operationId": str
        key "status": Union[str, Status]
        operationId: str
        status: Union[str, Status]


    class azure.mgmt.azurestackhcivm.types.MarketplaceGalleryImageTagsUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.azurestackhcivm.types.NatGateway(TrackedResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('NatGatewayProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: NatGatewayProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurestackhcivm.types.NatGatewayArmReference(TypedDict, total=False):
        key "resourceId": str
        resourceId: str


    class azure.mgmt.azurestackhcivm.types.NatGatewayProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningStateEnum]
        key "status": ForwardRef('NatGatewayStatus', module='types')
        provisioningState: Union[str, ProvisioningStateEnum]
        publicIPAddresses: list[PublicIPAddressArmReference]
        status: NatGatewayStatus
        subnets: list[VirtualNetworkSubnetArmReference]


    class azure.mgmt.azurestackhcivm.types.NatGatewayStatus(TypedDict, total=False):
        key "errorCode": str
        key "errorMessage": str
        key "provisioningStatus": ForwardRef('NatGatewayStatusProvisioningStatus', module='types')
        errorCode: str
        errorMessage: str
        provisioningStatus: NatGatewayStatusProvisioningStatus


    class azure.mgmt.azurestackhcivm.types.NatGatewayStatusProvisioningStatus(TypedDict, total=False):
        key "operationId": str
        key "status": Union[str, Status]
        operationId: str
        status: Union[str, Status]


    class azure.mgmt.azurestackhcivm.types.NatGatewayTagsUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.azurestackhcivm.types.NetworkInterface(TrackedResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('NetworkInterfaceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: NetworkInterfaceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurestackhcivm.types.NetworkInterfaceArmReference(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.azurestackhcivm.types.NetworkInterfaceProperties(TypedDict, total=False):
        key "bypassSdnPolicies": bool
        key "createFromLocal": bool
        key "dnsSettings": ForwardRef('InterfaceDNSSettings', module='types')
        key "macAddress": str
        key "networkSecurityGroup": ForwardRef('NetworkSecurityGroupArmReference', module='types')
        key "provisioningState": Union[str, ProvisioningStateEnum]
        key "status": ForwardRef('NetworkInterfaceStatus', module='types')
        bypassSdnPolicies: bool
        createFromLocal: bool
        dnsSettings: InterfaceDNSSettings
        ipConfigurations: list[IPConfiguration]
        macAddress: str
        networkSecurityGroup: NetworkSecurityGroupArmReference
        provisioningState: Union[str, ProvisioningStateEnum]
        status: NetworkInterfaceStatus


    class azure.mgmt.azurestackhcivm.types.NetworkInterfaceStatus(TypedDict, total=False):
        key "errorCode": str
        key "errorMessage": str
        key "provisioningStatus": ForwardRef('NetworkInterfaceStatusProvisioningStatus', module='types')
        errorCode: str
        errorMessage: str
        provisioningStatus: NetworkInterfaceStatusProvisioningStatus


    class azure.mgmt.azurestackhcivm.types.NetworkInterfaceStatusProvisioningStatus(TypedDict, total=False):
        key "operationId": str
        key "status": Union[str, Status]
        operationId: str
        status: Union[str, Status]


    class azure.mgmt.azurestackhcivm.types.NetworkInterfacesUpdateProperties(TypedDict, total=False):
        key "bypassSdnPolicies": bool
        key "dnsSettings": ForwardRef('InterfaceDNSSettings', module='types')
        key "networkSecurityGroup": ForwardRef('NetworkSecurityGroupArmReference', module='types')
        bypassSdnPolicies: bool
        dnsSettings: InterfaceDNSSettings
        networkSecurityGroup: NetworkSecurityGroupArmReference


    class azure.mgmt.azurestackhcivm.types.NetworkInterfacesUpdateRequest(TypedDict, total=False):
        key "properties": ForwardRef('NetworkInterfacesUpdateProperties', module='types')
        properties: NetworkInterfacesUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.azurestackhcivm.types.NetworkProfileUpdate(TypedDict, total=False):
        networkInterfaces: list[NetworkInterfaceArmReference]


    class azure.mgmt.azurestackhcivm.types.NetworkSecurityGroup(TrackedResource):
        key "eTag": str
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('NetworkSecurityGroupProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: NetworkSecurityGroupProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurestackhcivm.types.NetworkSecurityGroupArmReference(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.azurestackhcivm.types.NetworkSecurityGroupProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningStateEnum]
        key "status": ForwardRef('NetworkSecurityGroupStatus', module='types')
        networkInterfaces: list[NetworkInterfaceArmReference]
        provisioningState: Union[str, ProvisioningStateEnum]
        status: NetworkSecurityGroupStatus
        subnets: list[LogicalNetworkArmReference]


    class azure.mgmt.azurestackhcivm.types.NetworkSecurityGroupStatus(TypedDict, total=False):
        key "errorCode": str
        key "errorMessage": str
        key "provisioningStatus": ForwardRef('NetworkSecurityGroupStatusProvisioningStatus', module='types')
        errorCode: str
        errorMessage: str
        provisioningStatus: NetworkSecurityGroupStatusProvisioningStatus


    class azure.mgmt.azurestackhcivm.types.NetworkSecurityGroupStatusProvisioningStatus(TypedDict, total=False):
        key "operationId": str
        key "status": Union[str, Status]
        operationId: str
        status: Union[str, Status]


    class azure.mgmt.azurestackhcivm.types.NetworkSecurityGroupTagsUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.azurestackhcivm.types.OperationStepResult(TypedDict, total=False):
        key "completedTime": str
        key "message": str
        key "name": Required[str]
        key "status": Required[Union[str, Status]]
        completedTime: str
        message: str
        name: str
        status: Union[str, Status]


    class azure.mgmt.azurestackhcivm.types.OsProfileUpdate(TypedDict, total=False):
        key "computerName": str
        key "linuxConfiguration": ForwardRef('OsProfileUpdateLinuxConfiguration', module='types')
        key "windowsConfiguration": ForwardRef('OsProfileUpdateWindowsConfiguration', module='types')
        computerName: str
        linuxConfiguration: OsProfileUpdateLinuxConfiguration
        windowsConfiguration: OsProfileUpdateWindowsConfiguration


    class azure.mgmt.azurestackhcivm.types.OsProfileUpdateLinuxConfiguration(TypedDict, total=False):
        key "provisionVMAgent": bool
        key "provisionVMConfigAgent": bool
        provisionVMAgent: bool
        provisionVMConfigAgent: bool


    class azure.mgmt.azurestackhcivm.types.OsProfileUpdateWindowsConfiguration(TypedDict, total=False):
        key "provisionVMAgent": bool
        key "provisionVMConfigAgent": bool
        provisionVMAgent: bool
        provisionVMConfigAgent: bool


    class azure.mgmt.azurestackhcivm.types.PowerOffVirtualMachineOptions(TypedDict, total=False):
        key "skipShutdown": bool
        skipShutdown: bool


    class azure.mgmt.azurestackhcivm.types.Probe(TypedDict, total=False):
        key "name": Required[str]
        key "properties": Required[ProbeProperties]
        name: str
        properties: ProbeProperties


    class azure.mgmt.azurestackhcivm.types.ProbeProperties(TypedDict, total=False):
        key "intervalInSeconds": int
        key "numberOfProbes": int
        key "port": Required[int]
        key "protocol": Required[Union[str, LoadBalancerProbeProtocol]]
        key "requestPath": str
        intervalInSeconds: int
        numberOfProbes: int
        port: int
        protocol: Union[str, LoadBalancerProbeProtocol]
        requestPath: str


    class azure.mgmt.azurestackhcivm.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.azurestackhcivm.types.PublicIPAddress(TrackedResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('PublicIPAddressProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: PublicIPAddressProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurestackhcivm.types.PublicIPAddressArmReference(TypedDict, total=False):
        key "resourceId": str
        resourceId: str


    class azure.mgmt.azurestackhcivm.types.PublicIPAddressProperties(TypedDict, total=False):
        key "ipAddress": str
        key "ipAllocationScope": str
        key "ipConfiguration": ForwardRef('IPConfigurationArmReference', module='types')
        key "natGateway": ForwardRef('NatGatewayArmReference', module='types')
        key "provisioningState": Union[str, ProvisioningStateEnum]
        key "publicIPAddressVersion": Union[str, PublicIPAddressType]
        ipAddress: str
        ipAllocationScope: str
        ipConfiguration: IPConfigurationArmReference
        natGateway: NatGatewayArmReference
        provisioningState: Union[str, ProvisioningStateEnum]
        publicIPAddressVersion: Union[str, PublicIPAddressType]


    class azure.mgmt.azurestackhcivm.types.PublicIPAddressTagsUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.azurestackhcivm.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.azurestackhcivm.types.Route(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('RouteProperties', module='types')
        name: str
        properties: RouteProperties


    class azure.mgmt.azurestackhcivm.types.RouteProperties(TypedDict, total=False):
        key "addressPrefix": str
        key "nextHopIpAddress": str
        addressPrefix: str
        nextHopIpAddress: str


    class azure.mgmt.azurestackhcivm.types.RouteTable(TypedDict, total=False):
        key "etag": str
        key "name": str
        key "properties": ForwardRef('RouteTableProperties', module='types')
        key "type": str
        etag: str
        name: str
        properties: RouteTableProperties
        type: str


    class azure.mgmt.azurestackhcivm.types.RouteTableProperties(TypedDict, total=False):
        routes: list[Route]


    class azure.mgmt.azurestackhcivm.types.SecurityRule(ProxyResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "name": str
        key "properties": ForwardRef('SecurityRuleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        name: str
        properties: SecurityRuleProperties
        systemData: SystemData
        type: str


    class azure.mgmt.azurestackhcivm.types.SecurityRuleProperties(TypedDict, total=False):
        key "access": Required[Union[str, SecurityRuleAccess]]
        key "description": str
        key "direction": Required[Union[str, SecurityRuleDirection]]
        key "priority": Required[int]
        key "protocol": Required[Union[str, SecurityRuleProtocol]]
        key "provisioningState": Union[str, ProvisioningStateEnum]
        access: Union[str, SecurityRuleAccess]
        description: str
        destinationAddressPrefixes: list[str]
        destinationPortRanges: list[str]
        direction: Union[str, SecurityRuleDirection]
        priority: int
        protocol: Union[str, SecurityRuleProtocol]
        provisioningState: Union[str, ProvisioningStateEnum]
        sourceAddressPrefixes: list[str]
        sourcePortRanges: list[str]


    class azure.mgmt.azurestackhcivm.types.Snapshot(TrackedResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('SnapshotProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: SnapshotProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurestackhcivm.types.SnapshotProperties(TypedDict, total=False):
        key "creationData": ForwardRef('CreationData', module='types')
        key "diskSizeBytes": int
        key "provisioningState": Union[str, ProvisioningStateEnum]
        key "status": ForwardRef('SnapshotStatus', module='types')
        key "timeCreated": str
        key "uniqueId": str
        creationData: CreationData
        diskSizeBytes: int
        provisioningState: Union[str, ProvisioningStateEnum]
        status: SnapshotStatus
        timeCreated: str
        uniqueId: str


    class azure.mgmt.azurestackhcivm.types.SnapshotStatus(TypedDict, total=False):
        key "errorCode": str
        key "errorMessage": str
        key "provisioningStatus": ForwardRef('SnapshotStatusProvisioningStatus', module='types')
        errorCode: str
        errorMessage: str
        provisioningStatus: SnapshotStatusProvisioningStatus


    class azure.mgmt.azurestackhcivm.types.SnapshotStatusProvisioningStatus(TypedDict, total=False):
        key "operationId": str
        key "status": Union[str, Status]
        operationId: str
        status: Union[str, Status]


    class azure.mgmt.azurestackhcivm.types.SnapshotTagsUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.azurestackhcivm.types.SshConfiguration(TypedDict, total=False):
        publicKeys: list[SshPublicKey]


    class azure.mgmt.azurestackhcivm.types.SshPublicKey(TypedDict, total=False):
        key "keyData": str
        key "path": str
        keyData: str
        path: str


    class azure.mgmt.azurestackhcivm.types.StorageContainer(TrackedResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('StorageContainerProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: StorageContainerProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurestackhcivm.types.StorageContainerProperties(TypedDict, total=False):
        key "path": Required[str]
        key "provisioningState": Union[str, ProvisioningStateEnum]
        key "status": ForwardRef('StorageContainerStatus', module='types')
        path: str
        provisioningState: Union[str, ProvisioningStateEnum]
        status: StorageContainerStatus


    class azure.mgmt.azurestackhcivm.types.StorageContainerStatus(TypedDict, total=False):
        key "availableSizeMB": int
        key "containerSizeMB": int
        key "errorCode": str
        key "errorMessage": str
        key "provisioningStatus": ForwardRef('StorageContainerStatusProvisioningStatus', module='types')
        availableSizeMB: int
        containerSizeMB: int
        errorCode: str
        errorMessage: str
        provisioningStatus: StorageContainerStatusProvisioningStatus


    class azure.mgmt.azurestackhcivm.types.StorageContainerStatusProvisioningStatus(TypedDict, total=False):
        key "operationId": str
        key "status": Union[str, Status]
        operationId: str
        status: Union[str, Status]


    class azure.mgmt.azurestackhcivm.types.StorageContainerTagsUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.azurestackhcivm.types.StorageProfileUpdate(TypedDict, total=False):
        dataDisks: list[VirtualHardDiskArmReference]


    class azure.mgmt.azurestackhcivm.types.Subnet(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('SubnetProperties', module='types')
        name: str
        properties: SubnetProperties


    class azure.mgmt.azurestackhcivm.types.SubnetIpConfigurationReference(TypedDict, total=False):
        key "ID": str
        ID: str


    class azure.mgmt.azurestackhcivm.types.SubnetProperties(TypedDict, total=False):
        key "addressPrefix": str
        key "ipAllocationMethod": Union[str, IpAllocationMethodEnum]
        key "networkSecurityGroup": ForwardRef('NetworkSecurityGroupArmReference', module='types')
        key "provisioningState": Union[str, ProvisioningStateEnum]
        key "routeTable": ForwardRef('RouteTable', module='types')
        key "vlan": int
        addressPrefix: str
        addressPrefixes: list[str]
        ipAllocationMethod: Union[str, IpAllocationMethodEnum]
        ipConfigurationReferences: list[SubnetIpConfigurationReference]
        ipPools: list[IPPool]
        networkSecurityGroup: NetworkSecurityGroupArmReference
        provisioningState: Union[str, ProvisioningStateEnum]
        routeTable: RouteTable
        vlan: int


    class azure.mgmt.azurestackhcivm.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.azurestackhcivm.types.TrackedResource(Resource):
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


    class azure.mgmt.azurestackhcivm.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.azurestackhcivm.types.VMDiskSecurityProfile(TypedDict, total=False):
        key "securityEncryptionType": Union[str, SecurityEncryptionType]
        securityEncryptionType: Union[str, SecurityEncryptionType]


    class azure.mgmt.azurestackhcivm.types.VirtualHardDisk(TrackedResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('VirtualHardDiskProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: VirtualHardDiskProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurestackhcivm.types.VirtualHardDiskArmReference(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.azurestackhcivm.types.VirtualHardDiskDownloadStatus(TypedDict, total=False):
        key "downloadedSizeInMB": int
        key "progressPercentage": int
        key "status": Union[str, Status]
        downloadedSizeInMB: int
        progressPercentage: int
        status: Union[str, Status]


    class azure.mgmt.azurestackhcivm.types.VirtualHardDiskProperties(TypedDict, total=False):
        key "blockSizeBytes": int
        key "containerId": str
        key "createFromLocal": bool
        key "creationData": ForwardRef('CreationData', module='types')
        key "diskFileFormat": Union[str, DiskFileFormat]
        key "diskSizeGB": int
        key "downloadUrl": str
        key "dynamic": bool
        key "hyperVGeneration": Union[str, HyperVGeneration]
        key "localVhdPath": str
        key "logicalSectorBytes": int
        key "maxShares": int
        key "physicalSectorBytes": int
        key "provisioningState": Union[str, ProvisioningStateEnum]
        key "status": ForwardRef('VirtualHardDiskStatus', module='types')
        blockSizeBytes: int
        containerId: str
        createFromLocal: bool
        creationData: CreationData
        diskFileFormat: Union[str, DiskFileFormat]
        diskSizeGB: int
        downloadUrl: str
        dynamic: bool
        hyperVGeneration: Union[str, HyperVGeneration]
        localVhdPath: str
        logicalSectorBytes: int
        maxShares: int
        physicalSectorBytes: int
        provisioningState: Union[str, ProvisioningStateEnum]
        status: VirtualHardDiskStatus


    class azure.mgmt.azurestackhcivm.types.VirtualHardDiskStatus(TypedDict, total=False):
        key "downloadStatus": ForwardRef('VirtualHardDiskDownloadStatus', module='types')
        key "errorCode": str
        key "errorMessage": str
        key "provisioningStatus": ForwardRef('VirtualHardDiskStatusProvisioningStatus', module='types')
        key "uniqueId": str
        key "uploadStatus": ForwardRef('VirtualHardDiskUploadStatus', module='types')
        downloadStatus: VirtualHardDiskDownloadStatus
        errorCode: str
        errorMessage: str
        managedBy: list[str]
        provisioningStatus: VirtualHardDiskStatusProvisioningStatus
        uniqueId: str
        uploadStatus: VirtualHardDiskUploadStatus


    class azure.mgmt.azurestackhcivm.types.VirtualHardDiskStatusProvisioningStatus(TypedDict, total=False):
        key "operationId": str
        key "status": Union[str, Status]
        operationId: str
        status: Union[str, Status]


    class azure.mgmt.azurestackhcivm.types.VirtualHardDiskUploadRequest(TypedDict, total=False):
        key "azureManagedDiskUploadUrl": Required[str]
        azureManagedDiskUploadUrl: str


    class azure.mgmt.azurestackhcivm.types.VirtualHardDiskUploadStatus(TypedDict, total=False):
        key "errorCode": str
        key "errorMessage": str
        key "progressPercentage": int
        key "status": Union[str, Status]
        key "uploadedSizeInMB": int
        errorCode: str
        errorMessage: str
        progressPercentage: int
        status: Union[str, Status]
        uploadedSizeInMB: int


    class azure.mgmt.azurestackhcivm.types.VirtualHardDisksUpdateProperties(TypedDict, total=False):
        key "diskSizeGB": int
        diskSizeGB: int


    class azure.mgmt.azurestackhcivm.types.VirtualHardDisksUpdateRequest(TypedDict, total=False):
        key "properties": ForwardRef('VirtualHardDisksUpdateProperties', module='types')
        properties: VirtualHardDisksUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.azurestackhcivm.types.VirtualMachineConfigAgentInstanceView(TypedDict, total=False):
        key "vmConfigAgentVersion": str
        statuses: list[InstanceViewStatus]
        vmConfigAgentVersion: str


    class azure.mgmt.azurestackhcivm.types.VirtualMachineInstance(ExtensionResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "name": str
        key "properties": ForwardRef('VirtualMachineInstanceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        identity: ManagedServiceIdentity
        name: str
        properties: VirtualMachineInstanceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.azurestackhcivm.types.VirtualMachineInstanceManagedDiskParameters(TypedDict, total=False):
        key "securityProfile": ForwardRef('VMDiskSecurityProfile', module='types')
        securityProfile: VMDiskSecurityProfile


    class azure.mgmt.azurestackhcivm.types.VirtualMachineInstanceProperties(TypedDict, total=False):
        key "createFromLocal": bool
        key "guestAgentInstallStatus": ForwardRef('GuestAgentInstallStatus', module='types')
        key "hardwareProfile": ForwardRef('VirtualMachineInstancePropertiesHardwareProfile', module='types')
        key "hostNodeIpAddress": str
        key "hostNodeName": str
        key "httpProxyConfig": ForwardRef('HttpProxyConfiguration', module='types')
        key "hyperVVmId": str
        key "instanceView": ForwardRef('VirtualMachineInstanceView', module='types')
        key "localVmName": str
        key "networkProfile": ForwardRef('VirtualMachineInstancePropertiesNetworkProfile', module='types')
        key "osProfile": ForwardRef('VirtualMachineInstancePropertiesOsProfile', module='types')
        key "placementProfile": ForwardRef('VirtualMachineInstancePropertiesPlacementProfile', module='types')
        key "provisioningState": Union[str, ProvisioningStateEnum]
        key "resourceUid": str
        key "securityProfile": ForwardRef('VirtualMachineInstancePropertiesSecurityProfile', module='types')
        key "status": ForwardRef('VirtualMachineInstanceStatus', module='types')
        key "storageProfile": ForwardRef('VirtualMachineInstancePropertiesStorageProfile', module='types')
        key "vmId": str
        createFromLocal: bool
        guestAgentInstallStatus: GuestAgentInstallStatus
        hardwareProfile: VirtualMachineInstancePropertiesHardwareProfile
        hostNodeIpAddress: str
        hostNodeName: str
        httpProxyConfig: HttpProxyConfiguration
        hyperVVmId: str
        instanceView: VirtualMachineInstanceView
        localVmName: str
        networkProfile: VirtualMachineInstancePropertiesNetworkProfile
        osProfile: VirtualMachineInstancePropertiesOsProfile
        placementProfile: VirtualMachineInstancePropertiesPlacementProfile
        provisioningState: Union[str, ProvisioningStateEnum]
        resourceUid: str
        securityProfile: VirtualMachineInstancePropertiesSecurityProfile
        status: VirtualMachineInstanceStatus
        storageProfile: VirtualMachineInstancePropertiesStorageProfile
        vmId: str


    class azure.mgmt.azurestackhcivm.types.VirtualMachineInstancePropertiesHardwareProfile(TypedDict, total=False):
        key "dynamicMemoryConfig": ForwardRef('VirtualMachineInstancePropertiesHardwareProfileDynamicMemoryConfig', module='types')
        key "memoryMB": int
        key "processors": int
        key "vmSize": Union[str, VmSizeEnum]
        dynamicMemoryConfig: VirtualMachineInstancePropertiesHardwareProfileDynamicMemoryConfig
        memoryMB: int
        processors: int
        virtualMachineGPUs: list[VirtualMachineInstancePropertiesHardwareProfileVirtualMachineGPU]
        vmSize: Union[str, VmSizeEnum]


    class azure.mgmt.azurestackhcivm.types.VirtualMachineInstancePropertiesHardwareProfileDynamicMemoryConfig(TypedDict, total=False):
        key "enabled": bool
        key "maximumMemoryMB": int
        key "minimumMemoryMB": int
        key "targetMemoryBuffer": int
        enabled: bool
        maximumMemoryMB: int
        minimumMemoryMB: int
        targetMemoryBuffer: int


    class azure.mgmt.azurestackhcivm.types.VirtualMachineInstancePropertiesHardwareProfileVirtualMachineGPU(TypedDict, total=False):
        key "assignmentType": Required[Union[str, GpuAssignmentTypeEnum]]
        key "gpuName": str
        key "partitionSizeMB": int
        assignmentType: Union[str, GpuAssignmentTypeEnum]
        gpuName: str
        partitionSizeMB: int


    class azure.mgmt.azurestackhcivm.types.VirtualMachineInstancePropertiesNetworkProfile(TypedDict, total=False):
        networkInterfaces: list[NetworkInterfaceArmReference]


    class azure.mgmt.azurestackhcivm.types.VirtualMachineInstancePropertiesOsProfile(TypedDict, total=False):
        key "adminPassword": str
        key "adminUsername": str
        key "computerName": str
        key "linuxConfiguration": ForwardRef('VirtualMachineInstancePropertiesOsProfileLinuxConfiguration', module='types')
        key "windowsConfiguration": ForwardRef('VirtualMachineInstancePropertiesOsProfileWindowsConfiguration', module='types')
        adminPassword: str
        adminUsername: str
        computerName: str
        linuxConfiguration: VirtualMachineInstancePropertiesOsProfileLinuxConfiguration
        windowsConfiguration: VirtualMachineInstancePropertiesOsProfileWindowsConfiguration


    class azure.mgmt.azurestackhcivm.types.VirtualMachineInstancePropertiesOsProfileLinuxConfiguration(TypedDict, total=False):
        key "disablePasswordAuthentication": bool
        key "provisionVMAgent": bool
        key "provisionVMConfigAgent": bool
        key "ssh": ForwardRef('SshConfiguration', module='types')
        disablePasswordAuthentication: bool
        provisionVMAgent: bool
        provisionVMConfigAgent: bool
        ssh: SshConfiguration


    class azure.mgmt.azurestackhcivm.types.VirtualMachineInstancePropertiesOsProfileWindowsConfiguration(TypedDict, total=False):
        key "enableAutomaticUpdates": bool
        key "provisionVMAgent": bool
        key "provisionVMConfigAgent": bool
        key "ssh": ForwardRef('SshConfiguration', module='types')
        key "timeZone": str
        enableAutomaticUpdates: bool
        provisionVMAgent: bool
        provisionVMConfigAgent: bool
        ssh: SshConfiguration
        timeZone: str


    class azure.mgmt.azurestackhcivm.types.VirtualMachineInstancePropertiesPlacementProfile(TypedDict, total=False):
        key "strictPlacementPolicy": bool
        key "zone": str
        strictPlacementPolicy: bool
        zone: str


    class azure.mgmt.azurestackhcivm.types.VirtualMachineInstancePropertiesSecurityProfile(TypedDict, total=False):
        key "enableTPM": bool
        key "securityType": Union[str, SecurityTypes]
        key "uefiSettings": ForwardRef('VirtualMachineInstancePropertiesSecurityProfileUefiSettings', module='types')
        enableTPM: bool
        securityType: Union[str, SecurityTypes]
        uefiSettings: VirtualMachineInstancePropertiesSecurityProfileUefiSettings


    class azure.mgmt.azurestackhcivm.types.VirtualMachineInstancePropertiesSecurityProfileUefiSettings(TypedDict, total=False):
        key "secureBootEnabled": bool
        secureBootEnabled: bool


    class azure.mgmt.azurestackhcivm.types.VirtualMachineInstancePropertiesStorageProfile(TypedDict, total=False):
        key "imageReference": ForwardRef('ImageArmReference', module='types')
        key "osDisk": ForwardRef('VirtualMachineInstancePropertiesStorageProfileOsDisk', module='types')
        key "vmConfigStoragePathId": str
        dataDisks: list[VirtualHardDiskArmReference]
        imageReference: ImageArmReference
        osDisk: VirtualMachineInstancePropertiesStorageProfileOsDisk
        vmConfigStoragePathId: str


    class azure.mgmt.azurestackhcivm.types.VirtualMachineInstancePropertiesStorageProfileOsDisk(TypedDict, total=False):
        key "id": str
        key "managedDisk": ForwardRef('VirtualMachineInstanceManagedDiskParameters', module='types')
        key "osType": Union[str, OperatingSystemTypes]
        id: str
        managedDisk: VirtualMachineInstanceManagedDiskParameters
        osType: Union[str, OperatingSystemTypes]


    class azure.mgmt.azurestackhcivm.types.VirtualMachineInstanceStatus(TypedDict, total=False):
        key "errorCode": str
        key "errorMessage": str
        key "powerState": Union[str, PowerStateEnum]
        key "provisioningStatus": ForwardRef('VirtualMachineInstanceStatusProvisioningStatus', module='types')
        errorCode: str
        errorMessage: str
        operationDetails: list[OperationStepResult]
        powerState: Union[str, PowerStateEnum]
        provisioningStatus: VirtualMachineInstanceStatusProvisioningStatus


    class azure.mgmt.azurestackhcivm.types.VirtualMachineInstanceStatusProvisioningStatus(TypedDict, total=False):
        key "operationId": str
        key "status": Union[str, Status]
        operationId: str
        status: Union[str, Status]


    class azure.mgmt.azurestackhcivm.types.VirtualMachineInstanceUpdateProperties(TypedDict, total=False):
        key "hardwareProfile": ForwardRef('HardwareProfileUpdate', module='types')
        key "networkProfile": ForwardRef('NetworkProfileUpdate', module='types')
        key "osProfile": ForwardRef('OsProfileUpdate', module='types')
        key "storageProfile": ForwardRef('StorageProfileUpdate', module='types')
        hardwareProfile: HardwareProfileUpdate
        networkProfile: NetworkProfileUpdate
        osProfile: OsProfileUpdate
        storageProfile: StorageProfileUpdate


    class azure.mgmt.azurestackhcivm.types.VirtualMachineInstanceUpdateRequest(TypedDict, total=False):
        key "identity": ForwardRef('Identity', module='types')
        key "properties": ForwardRef('VirtualMachineInstanceUpdateProperties', module='types')
        identity: Identity
        properties: VirtualMachineInstanceUpdateProperties


    class azure.mgmt.azurestackhcivm.types.VirtualMachineInstanceView(TypedDict, total=False):
        key "vmAgent": ForwardRef('VirtualMachineConfigAgentInstanceView', module='types')
        vmAgent: VirtualMachineConfigAgentInstanceView


    class azure.mgmt.azurestackhcivm.types.VirtualNetwork(TrackedResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('VirtualNetworkProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: VirtualNetworkProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurestackhcivm.types.VirtualNetworkAddressSpace(TypedDict, total=False):
        key "addressPrefixes": Required[list[str]]
        addressPrefixes: list[str]


    class azure.mgmt.azurestackhcivm.types.VirtualNetworkArmReference(TypedDict, total=False):
        key "resourceId": str
        resourceId: str


    class azure.mgmt.azurestackhcivm.types.VirtualNetworkDhcpOptions(TypedDict, total=False):
        dnsServers: list[str]


    class azure.mgmt.azurestackhcivm.types.VirtualNetworkProperties(TypedDict, total=False):
        key "addressSpace": Required[VirtualNetworkAddressSpace]
        key "dhcpOptions": Required[VirtualNetworkDhcpOptions]
        key "provisioningState": Union[str, ProvisioningStateEnum]
        key "status": ForwardRef('VirtualNetworkStatus', module='types')
        addressSpace: VirtualNetworkAddressSpace
        dhcpOptions: VirtualNetworkDhcpOptions
        provisioningState: Union[str, ProvisioningStateEnum]
        status: VirtualNetworkStatus


    class azure.mgmt.azurestackhcivm.types.VirtualNetworkStatus(TypedDict, total=False):
        key "errorCode": str
        key "errorMessage": str
        key "provisioningStatus": ForwardRef('VirtualNetworkStatusProvisioningStatus', module='types')
        errorCode: str
        errorMessage: str
        provisioningStatus: VirtualNetworkStatusProvisioningStatus


    class azure.mgmt.azurestackhcivm.types.VirtualNetworkStatusProvisioningStatus(TypedDict, total=False):
        key "operationId": str
        key "status": Union[str, Status]
        operationId: str
        status: Union[str, Status]


    class azure.mgmt.azurestackhcivm.types.VirtualNetworkSubnet(ProxyResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "name": str
        key "properties": ForwardRef('VirtualNetworkSubnetProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        name: str
        properties: VirtualNetworkSubnetProperties
        systemData: SystemData
        type: str


    class azure.mgmt.azurestackhcivm.types.VirtualNetworkSubnetArmReference(TypedDict, total=False):
        key "resourceId": str
        resourceId: str


    class azure.mgmt.azurestackhcivm.types.VirtualNetworkSubnetIpConfigurationReference(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.azurestackhcivm.types.VirtualNetworkSubnetProperties(TypedDict, total=False):
        key "addressPrefix": Required[str]
        key "natGateway": ForwardRef('NatGatewayArmReference', module='types')
        key "networkSecurityGroup": ForwardRef('NetworkSecurityGroupArmReference', module='types')
        key "provisioningState": Union[str, ProvisioningStateEnum]
        key "routeTable": ForwardRef('RouteTable', module='types')
        key "status": ForwardRef('VirtualNetworkSubnetStatus', module='types')
        addressPrefix: str
        ipConfigurations: list[VirtualNetworkSubnetIpConfigurationReference]
        natGateway: NatGatewayArmReference
        networkSecurityGroup: NetworkSecurityGroupArmReference
        provisioningState: Union[str, ProvisioningStateEnum]
        routeTable: RouteTable
        status: VirtualNetworkSubnetStatus


    class azure.mgmt.azurestackhcivm.types.VirtualNetworkSubnetStatus(TypedDict, total=False):
        key "errorCode": str
        key "errorMessage": str
        key "provisioningStatus": ForwardRef('VirtualNetworkSubnetStatusProvisioningStatus', module='types')
        errorCode: str
        errorMessage: str
        provisioningStatus: VirtualNetworkSubnetStatusProvisioningStatus


    class azure.mgmt.azurestackhcivm.types.VirtualNetworkSubnetStatusProvisioningStatus(TypedDict, total=False):
        key "operationId": str
        key "status": Union[str, Status]
        operationId: str
        status: Union[str, Status]


    class azure.mgmt.azurestackhcivm.types.VirtualNetworkSubnetUpdateProperties(TypedDict, total=False):
        key "natGateway": ForwardRef('NatGatewayArmReference', module='types')
        key "networkSecurityGroup": ForwardRef('NetworkSecurityGroupArmReference', module='types')
        natGateway: NatGatewayArmReference
        networkSecurityGroup: NetworkSecurityGroupArmReference


    class azure.mgmt.azurestackhcivm.types.VirtualNetworkSubnetUpdateRequest(TypedDict, total=False):
        key "properties": ForwardRef('VirtualNetworkSubnetUpdateProperties', module='types')
        properties: VirtualNetworkSubnetUpdateProperties


    class azure.mgmt.azurestackhcivm.types.VirtualNetworkTagsUpdate(TypedDict, total=False):
        tags: dict[str, str]


```