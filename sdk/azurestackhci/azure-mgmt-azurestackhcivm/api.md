```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.azurestackhcivm

    class azure.mgmt.azurestackhcivm.AzureStackHCIVmClient: implements ContextManager 
        attestation_statuses: AttestationStatusesOperations
        gallery_images: GalleryImagesOperations
        guest_agents: GuestAgentsOperations
        hybrid_identity_metadata: HybridIdentityMetadataOperations
        logical_networks: LogicalNetworksOperations
        marketplace_gallery_images: MarketplaceGalleryImagesOperations
        network_interfaces: NetworkInterfacesOperations
        network_security_groups: NetworkSecurityGroupsOperations
        security_rules: SecurityRulesOperations
        storage_containers: StorageContainersOperations
        virtual_hard_disks: VirtualHardDisksOperations
        virtual_machine_instances: VirtualMachineInstancesOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
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
        logical_networks: LogicalNetworksOperations
        marketplace_gallery_images: MarketplaceGalleryImagesOperations
        network_interfaces: NetworkInterfacesOperations
        network_security_groups: NetworkSecurityGroupsOperations
        security_rules: SecurityRulesOperations
        storage_containers: StorageContainersOperations
        virtual_hard_disks: VirtualHardDisksOperations
        virtual_machine_instances: VirtualMachineInstancesOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                body: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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


namespace azure.mgmt.azurestackhcivm.models

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


    class azure.mgmt.azurestackhcivm.models.CloudInitDataSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE = "Azure"
        NO_CLOUD = "NoCloud"


    class azure.mgmt.azurestackhcivm.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.azurestackhcivm.models.DiskFileFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VHD = "vhd"
        VHDX = "vhdx"


    class azure.mgmt.azurestackhcivm.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.azurestackhcivm.models.ErrorDetail(_Model):
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
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
                tags: Optional[Dict[str, str]] = ...
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
        vm_image_repository_credentials: Optional[VmImageRepositoryCredentials]

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
                version: Optional[GalleryImageVersion] = ..., 
                vm_image_repository_credentials: Optional[VmImageRepositoryCredentials] = ...
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
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ...
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
        error_details: Optional[List[ErrorDetail]]
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
        memory_mb: Optional[int]
        processors: Optional[int]
        virtual_machine_gp_us: Optional[List[VirtualMachineInstancePropertiesHardwareProfileVirtualMachineGPU]]
        vm_size: Optional[Union[str, VmSizeEnum]]

        @overload
        def __init__(
                self, 
                *, 
                memory_mb: Optional[int] = ..., 
                processors: Optional[int] = ..., 
                virtual_machine_gp_us: Optional[List[VirtualMachineInstancePropertiesHardwareProfileVirtualMachineGPU]] = ..., 
                vm_size: Optional[Union[str, VmSizeEnum]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.HttpProxyConfiguration(_Model):
        http_proxy: Optional[str]
        https_proxy: Optional[str]
        no_proxy: Optional[List[str]]
        trusted_ca: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                http_proxy: Optional[str] = ..., 
                https_proxy: Optional[str] = ..., 
                no_proxy: Optional[List[str]] = ..., 
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
        dns_servers: Optional[List[str]]

        @overload
        def __init__(
                self, 
                *, 
                dns_servers: Optional[List[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.IpAllocationMethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DYNAMIC = "Dynamic"
        STATIC = "Static"


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
                tags: Optional[Dict[str, str]] = ...
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
        network_type: Optional[Union[str, LogicalNetworkTypeEnum]]
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        status: Optional[LogicalNetworkStatus]
        subnets: Optional[List[Subnet]]
        vm_switch_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                dhcp_options: Optional[LogicalNetworkPropertiesDhcpOptions] = ..., 
                subnets: Optional[List[Subnet]] = ..., 
                vm_switch_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.LogicalNetworkPropertiesDhcpOptions(_Model):
        dns_servers: Optional[List[str]]

        @overload
        def __init__(
                self, 
                *, 
                dns_servers: Optional[List[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.LogicalNetworkStatus(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        provisioning_status: Optional[LogicalNetworkStatusProvisioningStatus]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
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
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.ManagedServiceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]] = ...
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
                tags: Optional[Dict[str, str]] = ...
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
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ...
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
                tags: Optional[Dict[str, str]] = ...
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
        create_from_local: Optional[bool]
        dns_settings: Optional[InterfaceDNSSettings]
        ip_configurations: Optional[List[IPConfiguration]]
        mac_address: Optional[str]
        network_security_group: Optional[NetworkSecurityGroupArmReference]
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        status: Optional[NetworkInterfaceStatus]

        @overload
        def __init__(
                self, 
                *, 
                create_from_local: Optional[bool] = ..., 
                dns_settings: Optional[InterfaceDNSSettings] = ..., 
                ip_configurations: Optional[List[IPConfiguration]] = ..., 
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
        dns_settings: Optional[InterfaceDNSSettings]
        network_security_group: Optional[NetworkSecurityGroupArmReference]

        @overload
        def __init__(
                self, 
                *, 
                dns_settings: Optional[InterfaceDNSSettings] = ..., 
                network_security_group: Optional[NetworkSecurityGroupArmReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.NetworkInterfacesUpdateRequest(_Model):
        properties: Optional[NetworkInterfacesUpdateProperties]
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NetworkInterfacesUpdateProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.NetworkProfileUpdate(_Model):
        network_interfaces: Optional[List[NetworkInterfaceArmReference]]

        @overload
        def __init__(
                self, 
                *, 
                network_interfaces: Optional[List[NetworkInterfaceArmReference]] = ...
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
                tags: Optional[Dict[str, str]] = ...
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
        network_interfaces: Optional[List[NetworkInterfaceArmReference]]
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        status: Optional[NetworkSecurityGroupStatus]
        subnets: Optional[List[LogicalNetworkArmReference]]


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
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.OperatingSystemTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


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
        routes: Optional[List[Route]]

        @overload
        def __init__(
                self, 
                *, 
                routes: Optional[List[Route]] = ...
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
        destination_address_prefixes: Optional[List[str]]
        destination_port_ranges: Optional[List[str]]
        direction: Union[str, SecurityRuleDirection]
        priority: int
        protocol: Union[str, SecurityRuleProtocol]
        provisioning_state: Optional[Union[str, ProvisioningStateEnum]]
        source_address_prefixes: Optional[List[str]]
        source_port_ranges: Optional[List[str]]

        @overload
        def __init__(
                self, 
                *, 
                access: Union[str, SecurityRuleAccess], 
                description: Optional[str] = ..., 
                destination_address_prefixes: Optional[List[str]] = ..., 
                destination_port_ranges: Optional[List[str]] = ..., 
                direction: Union[str, SecurityRuleDirection], 
                priority: int, 
                protocol: Union[str, SecurityRuleProtocol], 
                source_address_prefixes: Optional[List[str]] = ..., 
                source_port_ranges: Optional[List[str]] = ...
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


    class azure.mgmt.azurestackhcivm.models.SshConfiguration(_Model):
        public_keys: Optional[List[SshPublicKey]]

        @overload
        def __init__(
                self, 
                *, 
                public_keys: Optional[List[SshPublicKey]] = ...
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
                tags: Optional[Dict[str, str]] = ...
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
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.StorageProfileUpdate(_Model):
        data_disks: Optional[List[VirtualHardDiskArmReference]]

        @overload
        def __init__(
                self, 
                *, 
                data_disks: Optional[List[VirtualHardDiskArmReference]] = ...
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
        address_prefixes: Optional[List[str]]
        ip_allocation_method: Optional[Union[str, IpAllocationMethodEnum]]
        ip_configuration_references: Optional[List[SubnetIpConfigurationReference]]
        ip_pools: Optional[List[IPPool]]
        network_security_group: Optional[NetworkSecurityGroupArmReference]
        route_table: Optional[RouteTable]
        vlan: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                address_prefix: Optional[str] = ..., 
                address_prefixes: Optional[List[str]] = ..., 
                ip_allocation_method: Optional[Union[str, IpAllocationMethodEnum]] = ..., 
                ip_configuration_references: Optional[List[SubnetIpConfigurationReference]] = ..., 
                ip_pools: Optional[List[IPPool]] = ..., 
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
        tags: Optional[Dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ...
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
                tags: Optional[Dict[str, str]] = ...
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
        disk_file_format: Optional[Union[str, DiskFileFormat]]
        disk_size_gb: Optional[int]
        download_url: Optional[str]
        dynamic: Optional[bool]
        hyper_v_generation: Optional[Union[str, HyperVGeneration]]
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
                disk_file_format: Optional[Union[str, DiskFileFormat]] = ..., 
                disk_size_gb: Optional[int] = ..., 
                download_url: Optional[str] = ..., 
                dynamic: Optional[bool] = ..., 
                hyper_v_generation: Optional[Union[str, HyperVGeneration]] = ..., 
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
        managed_by: Optional[List[str]]
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
                managed_by: Optional[List[str]] = ..., 
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
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VirtualHardDisksUpdateProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualMachineConfigAgentInstanceView(_Model):
        statuses: Optional[List[InstanceViewStatus]]
        vm_config_agent_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                statuses: Optional[List[InstanceViewStatus]] = ..., 
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
        virtual_machine_gp_us: Optional[List[VirtualMachineInstancePropertiesHardwareProfileVirtualMachineGPU]]
        vm_size: Optional[Union[str, VmSizeEnum]]

        @overload
        def __init__(
                self, 
                *, 
                dynamic_memory_config: Optional[VirtualMachineInstancePropertiesHardwareProfileDynamicMemoryConfig] = ..., 
                memory_mb: Optional[int] = ..., 
                processors: Optional[int] = ..., 
                virtual_machine_gp_us: Optional[List[VirtualMachineInstancePropertiesHardwareProfileVirtualMachineGPU]] = ..., 
                vm_size: Optional[Union[str, VmSizeEnum]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhcivm.models.VirtualMachineInstancePropertiesHardwareProfileDynamicMemoryConfig(_Model):
        maximum_memory_mb: Optional[int]
        minimum_memory_mb: Optional[int]
        target_memory_buffer: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
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
        network_interfaces: Optional[List[NetworkInterfaceArmReference]]

        @overload
        def __init__(
                self, 
                *, 
                network_interfaces: Optional[List[NetworkInterfaceArmReference]] = ...
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
        data_disks: Optional[List[VirtualHardDiskArmReference]]
        image_reference: Optional[ImageArmReference]
        os_disk: Optional[VirtualMachineInstancePropertiesStorageProfileOsDisk]
        vm_config_storage_path_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_disks: Optional[List[VirtualHardDiskArmReference]] = ..., 
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


    class azure.mgmt.azurestackhcivm.models.VmImageRepositoryCredentials(_Model):
        password: str
        username: str

        @overload
        def __init__(
                self, 
                *, 
                password: str, 
                username: str
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                body: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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


```