```py
namespace azure.mgmt.scvmm

    class azure.mgmt.scvmm.ScVmmMgmtClient: implements ContextManager 
        availability_sets: AvailabilitySetsOperations
        clouds: CloudsOperations
        guest_agents: GuestAgentsOperations
        inventory_items: InventoryItemsOperations
        operations: Operations
        virtual_machine_instances: VirtualMachineInstancesOperations
        virtual_machine_templates: VirtualMachineTemplatesOperations
        virtual_networks: VirtualNetworksOperations
        vm_instance_hybrid_identity_metadatas: VmInstanceHybridIdentityMetadatasOperations
        vmm_servers: VmmServersOperations

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


namespace azure.mgmt.scvmm.aio

    class azure.mgmt.scvmm.aio.ScVmmMgmtClient: implements AsyncContextManager 
        availability_sets: AvailabilitySetsOperations
        clouds: CloudsOperations
        guest_agents: GuestAgentsOperations
        inventory_items: InventoryItemsOperations
        operations: Operations
        virtual_machine_instances: VirtualMachineInstancesOperations
        virtual_machine_templates: VirtualMachineTemplatesOperations
        virtual_networks: VirtualNetworksOperations
        vm_instance_hybrid_identity_metadatas: VmInstanceHybridIdentityMetadatasOperations
        vmm_servers: VmmServersOperations

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


namespace azure.mgmt.scvmm.aio.operations

    class azure.mgmt.scvmm.aio.operations.AvailabilitySetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                availability_set_resource_name: str, 
                resource: AvailabilitySet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AvailabilitySet]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                availability_set_resource_name: str, 
                resource: AvailabilitySet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AvailabilitySet]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                availability_set_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AvailabilitySet]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                availability_set_resource_name: str, 
                *, 
                force: Optional[Union[str, ForceDelete]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                availability_set_resource_name: str, 
                properties: AvailabilitySetTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AvailabilitySet]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                availability_set_resource_name: str, 
                properties: AvailabilitySetTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AvailabilitySet]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                availability_set_resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AvailabilitySet]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                availability_set_resource_name: str, 
                **kwargs: Any
            ) -> AvailabilitySet: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AvailabilitySet]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[AvailabilitySet]: ...


    class azure.mgmt.scvmm.aio.operations.CloudsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_resource_name: str, 
                resource: Cloud, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cloud]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_resource_name: str, 
                resource: Cloud, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cloud]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cloud]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_resource_name: str, 
                *, 
                force: Optional[Union[str, ForceDelete]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloud_resource_name: str, 
                properties: CloudTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cloud]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloud_resource_name: str, 
                properties: CloudTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cloud]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloud_resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cloud]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloud_resource_name: str, 
                **kwargs: Any
            ) -> Cloud: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Cloud]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Cloud]: ...


    class azure.mgmt.scvmm.aio.operations.GuestAgentsOperations:

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
        async def delete(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> None: ...

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


    class azure.mgmt.scvmm.aio.operations.InventoryItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                inventory_item_resource_name: str, 
                resource: InventoryItem, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InventoryItem: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                inventory_item_resource_name: str, 
                resource: InventoryItem, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InventoryItem: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                inventory_item_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InventoryItem: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                inventory_item_resource_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                inventory_item_resource_name: str, 
                **kwargs: Any
            ) -> InventoryItem: ...

        @distributed_trace
        def list_by_vmm_server(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[InventoryItem]: ...


    class azure.mgmt.scvmm.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.scvmm.aio.operations.VirtualMachineInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_checkpoint(
                self, 
                resource_uri: str, 
                body: VirtualMachineCreateCheckpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_checkpoint(
                self, 
                resource_uri: str, 
                body: VirtualMachineCreateCheckpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_checkpoint(
                self, 
                resource_uri: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

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
                *, 
                delete_from_host: Optional[Union[str, DeleteFromHost]] = ..., 
                force: Optional[Union[str, ForceDelete]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_delete_checkpoint(
                self, 
                resource_uri: str, 
                body: VirtualMachineDeleteCheckpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_delete_checkpoint(
                self, 
                resource_uri: str, 
                body: VirtualMachineDeleteCheckpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_delete_checkpoint(
                self, 
                resource_uri: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_restart(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restore_checkpoint(
                self, 
                resource_uri: str, 
                body: VirtualMachineRestoreCheckpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restore_checkpoint(
                self, 
                resource_uri: str, 
                body: VirtualMachineRestoreCheckpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restore_checkpoint(
                self, 
                resource_uri: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_stop(
                self, 
                resource_uri: str, 
                body: Optional[StopVirtualMachineOptions] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_stop(
                self, 
                resource_uri: str, 
                body: Optional[StopVirtualMachineOptions] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_stop(
                self, 
                resource_uri: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_uri: str, 
                properties: VirtualMachineInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineInstance]: ...

        @overload
        async def begin_update(
                self, 
                resource_uri: str, 
                properties: VirtualMachineInstanceUpdate, 
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


    class azure.mgmt.scvmm.aio.operations.VirtualMachineTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                resource: VirtualMachineTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineTemplate]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                resource: VirtualMachineTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineTemplate]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineTemplate]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                *, 
                force: Optional[Union[str, ForceDelete]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                properties: VirtualMachineTemplateTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineTemplate]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                properties: VirtualMachineTemplateTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineTemplate]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineTemplate]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                **kwargs: Any
            ) -> VirtualMachineTemplate: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualMachineTemplate]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[VirtualMachineTemplate]: ...


    class azure.mgmt.scvmm.aio.operations.VirtualNetworksOperations:

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
        async def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                *, 
                force: Optional[Union[str, ForceDelete]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                properties: VirtualNetworkTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetwork]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                properties: VirtualNetworkTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetwork]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetwork]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                **kwargs: Any
            ) -> VirtualNetwork: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualNetwork]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[VirtualNetwork]: ...


    class azure.mgmt.scvmm.aio.operations.VmInstanceHybridIdentityMetadatasOperations:

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
            ) -> VmInstanceHybridIdentityMetadata: ...

        @distributed_trace
        def list_by_virtual_machine_instance(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VmInstanceHybridIdentityMetadata]: ...


    class azure.mgmt.scvmm.aio.operations.VmmServersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                resource: VmmServer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VmmServer]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                resource: VmmServer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VmmServer]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VmmServer]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                *, 
                force: Optional[Union[str, ForceDelete]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                properties: VmmServerTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VmmServer]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                properties: VmmServerTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VmmServer]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VmmServer]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                **kwargs: Any
            ) -> VmmServer: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VmmServer]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[VmmServer]: ...


namespace azure.mgmt.scvmm.models

    class azure.mgmt.scvmm.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.scvmm.models.AllocationMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DYNAMIC = "Dynamic"
        STATIC = "Static"


    class azure.mgmt.scvmm.models.AvailabilitySet(TrackedResource):
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: Optional[AvailabilitySetProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                location: str, 
                properties: Optional[AvailabilitySetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.AvailabilitySetListItem(_Model):
        id: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.AvailabilitySetProperties(_Model):
        availability_set_name: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        vmm_server_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                availability_set_name: Optional[str] = ..., 
                vmm_server_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.AvailabilitySetTagsUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.Checkpoint(_Model):
        checkpoint_id: Optional[str]
        description: Optional[str]
        name: Optional[str]
        parent_checkpoint_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                checkpoint_id: Optional[str] = ..., 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                parent_checkpoint_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.Cloud(TrackedResource):
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: Optional[CloudProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                location: str, 
                properties: Optional[CloudProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.CloudCapacity(_Model):
        cpu_count: Optional[int]
        memory_mb: Optional[int]
        storage_gb: Optional[int]
        vm_count: Optional[int]


    class azure.mgmt.scvmm.models.CloudInventoryItem(InventoryItemProperties, discriminator='Cloud'):
        inventory_item_name: str
        inventory_type: Literal[InventoryType.CLOUD]
        managed_resource_id: str
        provisioning_state: Union[str, ProvisioningState]
        uuid: str

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.CloudProperties(_Model):
        cloud_capacity: Optional[CloudCapacity]
        cloud_name: Optional[str]
        inventory_item_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        storage_qos_policies: Optional[list[StorageQosPolicy]]
        uuid: Optional[str]
        vmm_server_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                inventory_item_id: Optional[str] = ..., 
                uuid: Optional[str] = ..., 
                vmm_server_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.CloudTagsUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.CreateDiffDisk(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "false"
        TRUE = "true"


    class azure.mgmt.scvmm.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.scvmm.models.DeleteFromHost(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "false"
        TRUE = "true"


    class azure.mgmt.scvmm.models.DynamicMemoryEnabled(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "false"
        TRUE = "true"


    class azure.mgmt.scvmm.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.scvmm.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.scvmm.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.ExtendedLocation(_Model):
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


    class azure.mgmt.scvmm.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.scvmm.models.ForceDelete(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "false"
        TRUE = "true"


    class azure.mgmt.scvmm.models.GuestAgent(ProxyResource):
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


    class azure.mgmt.scvmm.models.GuestAgentProperties(_Model):
        credentials: Optional[GuestCredential]
        custom_resource_name: Optional[str]
        http_proxy_config: Optional[HttpProxyConfiguration]
        private_link_scope_resource_id: Optional[str]
        provisioning_action: Optional[Union[str, ProvisioningAction]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: Optional[str]
        uuid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                credentials: Optional[GuestCredential] = ..., 
                http_proxy_config: Optional[HttpProxyConfiguration] = ..., 
                private_link_scope_resource_id: Optional[str] = ..., 
                provisioning_action: Optional[Union[str, ProvisioningAction]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.GuestCredential(_Model):
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


    class azure.mgmt.scvmm.models.HardwareProfile(_Model):
        cpu_count: Optional[int]
        dynamic_memory_enabled: Optional[Union[str, DynamicMemoryEnabled]]
        dynamic_memory_max_mb: Optional[int]
        dynamic_memory_min_mb: Optional[int]
        is_highly_available: Optional[Union[str, IsHighlyAvailable]]
        limit_cpu_for_migration: Optional[Union[str, LimitCpuForMigration]]
        memory_mb: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cpu_count: Optional[int] = ..., 
                dynamic_memory_enabled: Optional[Union[str, DynamicMemoryEnabled]] = ..., 
                dynamic_memory_max_mb: Optional[int] = ..., 
                dynamic_memory_min_mb: Optional[int] = ..., 
                limit_cpu_for_migration: Optional[Union[str, LimitCpuForMigration]] = ..., 
                memory_mb: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.HardwareProfileUpdate(_Model):
        cpu_count: Optional[int]
        dynamic_memory_enabled: Optional[Union[str, DynamicMemoryEnabled]]
        dynamic_memory_max_mb: Optional[int]
        dynamic_memory_min_mb: Optional[int]
        limit_cpu_for_migration: Optional[Union[str, LimitCpuForMigration]]
        memory_mb: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cpu_count: Optional[int] = ..., 
                dynamic_memory_enabled: Optional[Union[str, DynamicMemoryEnabled]] = ..., 
                dynamic_memory_max_mb: Optional[int] = ..., 
                dynamic_memory_min_mb: Optional[int] = ..., 
                limit_cpu_for_migration: Optional[Union[str, LimitCpuForMigration]] = ..., 
                memory_mb: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.HttpProxyConfiguration(_Model):
        https_proxy: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                https_proxy: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.InfrastructureProfile(_Model):
        bios_guid: Optional[str]
        checkpoint_type: Optional[str]
        checkpoints: Optional[list[Checkpoint]]
        cloud_id: Optional[str]
        generation: Optional[int]
        inventory_item_id: Optional[str]
        last_restored_vm_checkpoint: Optional[Checkpoint]
        template_id: Optional[str]
        uuid: Optional[str]
        vm_name: Optional[str]
        vmm_server_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                bios_guid: Optional[str] = ..., 
                checkpoint_type: Optional[str] = ..., 
                cloud_id: Optional[str] = ..., 
                generation: Optional[int] = ..., 
                inventory_item_id: Optional[str] = ..., 
                template_id: Optional[str] = ..., 
                uuid: Optional[str] = ..., 
                vm_name: Optional[str] = ..., 
                vmm_server_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.InfrastructureProfileUpdate(_Model):
        checkpoint_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                checkpoint_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.InventoryItem(ProxyResource):
        id: str
        kind: Optional[str]
        name: str
        properties: Optional[InventoryItemProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                properties: Optional[InventoryItemProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.InventoryItemDetails(_Model):
        inventory_item_id: Optional[str]
        inventory_item_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                inventory_item_id: Optional[str] = ..., 
                inventory_item_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.InventoryItemProperties(_Model):
        inventory_item_name: Optional[str]
        inventory_type: str
        managed_resource_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        uuid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                inventory_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.InventoryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOUD = "Cloud"
        VIRTUAL_MACHINE = "VirtualMachine"
        VIRTUAL_MACHINE_TEMPLATE = "VirtualMachineTemplate"
        VIRTUAL_NETWORK = "VirtualNetwork"


    class azure.mgmt.scvmm.models.IsCustomizable(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "false"
        TRUE = "true"


    class azure.mgmt.scvmm.models.IsHighlyAvailable(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "false"
        TRUE = "true"


    class azure.mgmt.scvmm.models.LimitCpuForMigration(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "false"
        TRUE = "true"


    class azure.mgmt.scvmm.models.NetworkInterface(_Model):
        display_name: Optional[str]
        ipv4_address_type: Optional[Union[str, AllocationMethod]]
        ipv4_addresses: Optional[list[str]]
        ipv6_address_type: Optional[Union[str, AllocationMethod]]
        ipv6_addresses: Optional[list[str]]
        mac_address: Optional[str]
        mac_address_type: Optional[Union[str, AllocationMethod]]
        name: Optional[str]
        network_name: Optional[str]
        nic_id: Optional[str]
        virtual_network_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ipv4_address_type: Optional[Union[str, AllocationMethod]] = ..., 
                ipv6_address_type: Optional[Union[str, AllocationMethod]] = ..., 
                mac_address: Optional[str] = ..., 
                mac_address_type: Optional[Union[str, AllocationMethod]] = ..., 
                name: Optional[str] = ..., 
                nic_id: Optional[str] = ..., 
                virtual_network_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.NetworkInterfaceUpdate(_Model):
        ipv4_address_type: Optional[Union[str, AllocationMethod]]
        ipv6_address_type: Optional[Union[str, AllocationMethod]]
        mac_address: Optional[str]
        mac_address_type: Optional[Union[str, AllocationMethod]]
        name: Optional[str]
        nic_id: Optional[str]
        virtual_network_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ipv4_address_type: Optional[Union[str, AllocationMethod]] = ..., 
                ipv6_address_type: Optional[Union[str, AllocationMethod]] = ..., 
                mac_address: Optional[str] = ..., 
                mac_address_type: Optional[Union[str, AllocationMethod]] = ..., 
                name: Optional[str] = ..., 
                nic_id: Optional[str] = ..., 
                virtual_network_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.NetworkProfile(_Model):
        network_interfaces: Optional[list[NetworkInterface]]

        @overload
        def __init__(
                self, 
                *, 
                network_interfaces: Optional[list[NetworkInterface]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.NetworkProfileUpdate(_Model):
        network_interfaces: Optional[list[NetworkInterfaceUpdate]]

        @overload
        def __init__(
                self, 
                *, 
                network_interfaces: Optional[list[NetworkInterfaceUpdate]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.Operation(_Model):
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


    class azure.mgmt.scvmm.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.scvmm.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.scvmm.models.OsProfileForVmInstance(_Model):
        admin_password: Optional[str]
        admin_username: Optional[str]
        computer_name: Optional[str]
        domain_name: Optional[str]
        domain_password: Optional[str]
        domain_username: Optional[str]
        os_sku: Optional[str]
        os_type: Optional[Union[str, OsType]]
        os_version: Optional[str]
        product_key: Optional[str]
        run_once_commands: Optional[str]
        timezone: Optional[int]
        workgroup: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                admin_password: Optional[str] = ..., 
                admin_username: Optional[str] = ..., 
                computer_name: Optional[str] = ..., 
                domain_name: Optional[str] = ..., 
                domain_password: Optional[str] = ..., 
                domain_username: Optional[str] = ..., 
                product_key: Optional[str] = ..., 
                run_once_commands: Optional[str] = ..., 
                timezone: Optional[int] = ..., 
                workgroup: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.OsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        OTHER = "Other"
        WINDOWS = "Windows"


    class azure.mgmt.scvmm.models.ProvisioningAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INSTALL = "install"
        REPAIR = "repair"
        UNINSTALL = "uninstall"


    class azure.mgmt.scvmm.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATED = "Created"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.scvmm.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.scvmm.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.scvmm.models.SkipShutdown(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "false"
        TRUE = "true"


    class azure.mgmt.scvmm.models.StopVirtualMachineOptions(_Model):
        skip_shutdown: Optional[Union[str, SkipShutdown]]

        @overload
        def __init__(
                self, 
                *, 
                skip_shutdown: Optional[Union[str, SkipShutdown]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.StorageProfile(_Model):
        disks: Optional[list[VirtualDisk]]

        @overload
        def __init__(
                self, 
                *, 
                disks: Optional[list[VirtualDisk]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.StorageProfileUpdate(_Model):
        disks: Optional[list[VirtualDiskUpdate]]

        @overload
        def __init__(
                self, 
                *, 
                disks: Optional[list[VirtualDiskUpdate]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.StorageQosPolicy(_Model):
        bandwidth_limit: Optional[int]
        id: Optional[str]
        iops_maximum: Optional[int]
        iops_minimum: Optional[int]
        name: Optional[str]
        policy_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                bandwidth_limit: Optional[int] = ..., 
                id: Optional[str] = ..., 
                iops_maximum: Optional[int] = ..., 
                iops_minimum: Optional[int] = ..., 
                name: Optional[str] = ..., 
                policy_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.StorageQosPolicyDetails(_Model):
        id: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.SystemData(_Model):
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


    class azure.mgmt.scvmm.models.TrackedResource(Resource):
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


    class azure.mgmt.scvmm.models.VirtualDisk(_Model):
        bus: Optional[int]
        bus_type: Optional[str]
        create_diff_disk: Optional[Union[str, CreateDiffDisk]]
        disk_id: Optional[str]
        disk_size_gb: Optional[int]
        display_name: Optional[str]
        lun: Optional[int]
        max_disk_size_gb: Optional[int]
        name: Optional[str]
        storage_qos_policy: Optional[StorageQosPolicyDetails]
        template_disk_id: Optional[str]
        vhd_format_type: Optional[str]
        vhd_type: Optional[str]
        volume_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                bus: Optional[int] = ..., 
                bus_type: Optional[str] = ..., 
                create_diff_disk: Optional[Union[str, CreateDiffDisk]] = ..., 
                disk_id: Optional[str] = ..., 
                disk_size_gb: Optional[int] = ..., 
                lun: Optional[int] = ..., 
                name: Optional[str] = ..., 
                storage_qos_policy: Optional[StorageQosPolicyDetails] = ..., 
                template_disk_id: Optional[str] = ..., 
                vhd_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.VirtualDiskUpdate(_Model):
        bus: Optional[int]
        bus_type: Optional[str]
        disk_id: Optional[str]
        disk_size_gb: Optional[int]
        lun: Optional[int]
        name: Optional[str]
        storage_qos_policy: Optional[StorageQosPolicyDetails]
        vhd_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                bus: Optional[int] = ..., 
                bus_type: Optional[str] = ..., 
                disk_id: Optional[str] = ..., 
                disk_size_gb: Optional[int] = ..., 
                lun: Optional[int] = ..., 
                name: Optional[str] = ..., 
                storage_qos_policy: Optional[StorageQosPolicyDetails] = ..., 
                vhd_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.VirtualMachineCreateCheckpoint(_Model):
        description: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.VirtualMachineDeleteCheckpoint(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.VirtualMachineInstance(ExtensionResource):
        extended_location: ExtendedLocation
        id: str
        name: str
        properties: Optional[VirtualMachineInstanceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                properties: Optional[VirtualMachineInstanceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.VirtualMachineInstanceProperties(_Model):
        availability_sets: Optional[list[AvailabilitySetListItem]]
        hardware_profile: Optional[HardwareProfile]
        infrastructure_profile: Optional[InfrastructureProfile]
        network_profile: Optional[NetworkProfile]
        os_profile: Optional[OsProfileForVmInstance]
        power_state: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        storage_profile: Optional[StorageProfile]

        @overload
        def __init__(
                self, 
                *, 
                availability_sets: Optional[list[AvailabilitySetListItem]] = ..., 
                hardware_profile: Optional[HardwareProfile] = ..., 
                infrastructure_profile: Optional[InfrastructureProfile] = ..., 
                network_profile: Optional[NetworkProfile] = ..., 
                os_profile: Optional[OsProfileForVmInstance] = ..., 
                storage_profile: Optional[StorageProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.VirtualMachineInstanceUpdate(_Model):
        properties: Optional[VirtualMachineInstanceUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VirtualMachineInstanceUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.scvmm.models.VirtualMachineInstanceUpdateProperties(_Model):
        availability_sets: Optional[list[AvailabilitySetListItem]]
        hardware_profile: Optional[HardwareProfileUpdate]
        infrastructure_profile: Optional[InfrastructureProfileUpdate]
        network_profile: Optional[NetworkProfileUpdate]
        storage_profile: Optional[StorageProfileUpdate]

        @overload
        def __init__(
                self, 
                *, 
                availability_sets: Optional[list[AvailabilitySetListItem]] = ..., 
                hardware_profile: Optional[HardwareProfileUpdate] = ..., 
                infrastructure_profile: Optional[InfrastructureProfileUpdate] = ..., 
                network_profile: Optional[NetworkProfileUpdate] = ..., 
                storage_profile: Optional[StorageProfileUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.VirtualMachineInventoryItem(InventoryItemProperties, discriminator='VirtualMachine'):
        bios_guid: Optional[str]
        cloud: Optional[InventoryItemDetails]
        generation: Optional[int]
        inventory_item_name: str
        inventory_type: Literal[InventoryType.VIRTUAL_MACHINE]
        ip_addresses: Optional[list[str]]
        managed_machine_resource_id: Optional[str]
        managed_resource_id: str
        os_name: Optional[str]
        os_type: Optional[Union[str, OsType]]
        os_version: Optional[str]
        power_state: Optional[str]
        provisioning_state: Union[str, ProvisioningState]
        uuid: str

        @overload
        def __init__(
                self, 
                *, 
                cloud: Optional[InventoryItemDetails] = ..., 
                ip_addresses: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.VirtualMachineRestoreCheckpoint(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.VirtualMachineTemplate(TrackedResource):
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: Optional[VirtualMachineTemplateProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                location: str, 
                properties: Optional[VirtualMachineTemplateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.VirtualMachineTemplateInventoryItem(InventoryItemProperties, discriminator='VirtualMachineTemplate'):
        cpu_count: Optional[int]
        inventory_item_name: str
        inventory_type: Literal[InventoryType.VIRTUAL_MACHINE_TEMPLATE]
        managed_resource_id: str
        memory_mb: Optional[int]
        os_name: Optional[str]
        os_type: Optional[Union[str, OsType]]
        provisioning_state: Union[str, ProvisioningState]
        uuid: str

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.VirtualMachineTemplateProperties(_Model):
        computer_name: Optional[str]
        cpu_count: Optional[int]
        disks: Optional[list[VirtualDisk]]
        dynamic_memory_enabled: Optional[Union[str, DynamicMemoryEnabled]]
        dynamic_memory_max_mb: Optional[int]
        dynamic_memory_min_mb: Optional[int]
        generation: Optional[int]
        inventory_item_id: Optional[str]
        is_customizable: Optional[Union[str, IsCustomizable]]
        is_highly_available: Optional[Union[str, IsHighlyAvailable]]
        limit_cpu_for_migration: Optional[Union[str, LimitCpuForMigration]]
        memory_mb: Optional[int]
        network_interfaces: Optional[list[NetworkInterface]]
        os_name: Optional[str]
        os_type: Optional[Union[str, OsType]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        uuid: Optional[str]
        vmm_server_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                inventory_item_id: Optional[str] = ..., 
                uuid: Optional[str] = ..., 
                vmm_server_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.VirtualMachineTemplateTagsUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.VirtualNetwork(TrackedResource):
        extended_location: ExtendedLocation
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
                extended_location: ExtendedLocation, 
                location: str, 
                properties: Optional[VirtualNetworkProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.VirtualNetworkInventoryItem(InventoryItemProperties, discriminator='VirtualNetwork'):
        inventory_item_name: str
        inventory_type: Literal[InventoryType.VIRTUAL_NETWORK]
        managed_resource_id: str
        provisioning_state: Union[str, ProvisioningState]
        uuid: str

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.VirtualNetworkProperties(_Model):
        inventory_item_id: Optional[str]
        network_name: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        uuid: Optional[str]
        vmm_server_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                inventory_item_id: Optional[str] = ..., 
                uuid: Optional[str] = ..., 
                vmm_server_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.VirtualNetworkTagsUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.VmInstanceHybridIdentityMetadata(ProxyResource):
        id: str
        name: str
        properties: Optional[VmInstanceHybridIdentityMetadataProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VmInstanceHybridIdentityMetadataProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.VmInstanceHybridIdentityMetadataProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
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


    class azure.mgmt.scvmm.models.VmmCredential(_Model):
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


    class azure.mgmt.scvmm.models.VmmServer(TrackedResource):
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: Optional[VmmServerProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                location: str, 
                properties: Optional[VmmServerProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.VmmServerProperties(_Model):
        connection_status: Optional[str]
        credentials: Optional[VmmCredential]
        error_message: Optional[str]
        fqdn: str
        port: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        uuid: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                credentials: Optional[VmmCredential] = ..., 
                fqdn: str, 
                port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.scvmm.models.VmmServerTagsUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.scvmm.operations

    class azure.mgmt.scvmm.operations.AvailabilitySetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                availability_set_resource_name: str, 
                resource: AvailabilitySet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AvailabilitySet]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                availability_set_resource_name: str, 
                resource: AvailabilitySet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AvailabilitySet]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                availability_set_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AvailabilitySet]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                availability_set_resource_name: str, 
                *, 
                force: Optional[Union[str, ForceDelete]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                availability_set_resource_name: str, 
                properties: AvailabilitySetTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AvailabilitySet]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                availability_set_resource_name: str, 
                properties: AvailabilitySetTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AvailabilitySet]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                availability_set_resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AvailabilitySet]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                availability_set_resource_name: str, 
                **kwargs: Any
            ) -> AvailabilitySet: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AvailabilitySet]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[AvailabilitySet]: ...


    class azure.mgmt.scvmm.operations.CloudsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_resource_name: str, 
                resource: Cloud, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cloud]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_resource_name: str, 
                resource: Cloud, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cloud]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cloud]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_resource_name: str, 
                *, 
                force: Optional[Union[str, ForceDelete]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloud_resource_name: str, 
                properties: CloudTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cloud]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloud_resource_name: str, 
                properties: CloudTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cloud]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloud_resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cloud]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloud_resource_name: str, 
                **kwargs: Any
            ) -> Cloud: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Cloud]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Cloud]: ...


    class azure.mgmt.scvmm.operations.GuestAgentsOperations:

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
        def delete(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> None: ...

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


    class azure.mgmt.scvmm.operations.InventoryItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                inventory_item_resource_name: str, 
                resource: InventoryItem, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InventoryItem: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                inventory_item_resource_name: str, 
                resource: InventoryItem, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InventoryItem: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                inventory_item_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InventoryItem: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                inventory_item_resource_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                inventory_item_resource_name: str, 
                **kwargs: Any
            ) -> InventoryItem: ...

        @distributed_trace
        def list_by_vmm_server(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                **kwargs: Any
            ) -> ItemPaged[InventoryItem]: ...


    class azure.mgmt.scvmm.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.scvmm.operations.VirtualMachineInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_checkpoint(
                self, 
                resource_uri: str, 
                body: VirtualMachineCreateCheckpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_checkpoint(
                self, 
                resource_uri: str, 
                body: VirtualMachineCreateCheckpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_checkpoint(
                self, 
                resource_uri: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

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
                *, 
                delete_from_host: Optional[Union[str, DeleteFromHost]] = ..., 
                force: Optional[Union[str, ForceDelete]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_delete_checkpoint(
                self, 
                resource_uri: str, 
                body: VirtualMachineDeleteCheckpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_delete_checkpoint(
                self, 
                resource_uri: str, 
                body: VirtualMachineDeleteCheckpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_delete_checkpoint(
                self, 
                resource_uri: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_restart(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restore_checkpoint(
                self, 
                resource_uri: str, 
                body: VirtualMachineRestoreCheckpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restore_checkpoint(
                self, 
                resource_uri: str, 
                body: VirtualMachineRestoreCheckpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restore_checkpoint(
                self, 
                resource_uri: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_stop(
                self, 
                resource_uri: str, 
                body: Optional[StopVirtualMachineOptions] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_stop(
                self, 
                resource_uri: str, 
                body: Optional[StopVirtualMachineOptions] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_stop(
                self, 
                resource_uri: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_uri: str, 
                properties: VirtualMachineInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineInstance]: ...

        @overload
        def begin_update(
                self, 
                resource_uri: str, 
                properties: VirtualMachineInstanceUpdate, 
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


    class azure.mgmt.scvmm.operations.VirtualMachineTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                resource: VirtualMachineTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineTemplate]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                resource: VirtualMachineTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineTemplate]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineTemplate]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                *, 
                force: Optional[Union[str, ForceDelete]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                properties: VirtualMachineTemplateTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineTemplate]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                properties: VirtualMachineTemplateTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineTemplate]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineTemplate]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                **kwargs: Any
            ) -> VirtualMachineTemplate: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VirtualMachineTemplate]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[VirtualMachineTemplate]: ...


    class azure.mgmt.scvmm.operations.VirtualNetworksOperations:

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
        def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                *, 
                force: Optional[Union[str, ForceDelete]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                properties: VirtualNetworkTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetwork]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                properties: VirtualNetworkTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetwork]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetwork]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                **kwargs: Any
            ) -> VirtualNetwork: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VirtualNetwork]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[VirtualNetwork]: ...


    class azure.mgmt.scvmm.operations.VmInstanceHybridIdentityMetadatasOperations:

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
            ) -> VmInstanceHybridIdentityMetadata: ...

        @distributed_trace
        def list_by_virtual_machine_instance(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> ItemPaged[VmInstanceHybridIdentityMetadata]: ...


    class azure.mgmt.scvmm.operations.VmmServersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                resource: VmmServer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VmmServer]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                resource: VmmServer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VmmServer]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VmmServer]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                *, 
                force: Optional[Union[str, ForceDelete]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                properties: VmmServerTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VmmServer]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                properties: VmmServerTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VmmServer]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VmmServer]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vmm_server_name: str, 
                **kwargs: Any
            ) -> VmmServer: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VmmServer]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[VmmServer]: ...


namespace azure.mgmt.scvmm.types

    class azure.mgmt.scvmm.types.AvailabilitySet(TrackedResource):
        key "extendedLocation": Required[ExtendedLocation]
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('AvailabilitySetProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: AvailabilitySetProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.scvmm.types.AvailabilitySetListItem(TypedDict, total=False):
        key "id": str
        key "name": str
        id: str
        name: str


    class azure.mgmt.scvmm.types.AvailabilitySetProperties(TypedDict, total=False):
        key "availabilitySetName": str
        key "provisioningState": Union[str, ProvisioningState]
        key "vmmServerId": str
        availabilitySetName: str
        provisioningState: Union[str, ProvisioningState]
        vmmServerId: str


    class azure.mgmt.scvmm.types.AvailabilitySetTagsUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.scvmm.types.Checkpoint(TypedDict, total=False):
        key "checkpointID": str
        key "description": str
        key "name": str
        key "parentCheckpointID": str
        checkpointID: str
        description: str
        name: str
        parentCheckpointID: str


    class azure.mgmt.scvmm.types.Cloud(TrackedResource):
        key "extendedLocation": Required[ExtendedLocation]
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('CloudProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: CloudProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.scvmm.types.CloudCapacity(TypedDict, total=False):
        key "cpuCount": int
        key "memoryMB": int
        key "storageGB": int
        key "vmCount": int
        cpuCount: int
        memoryMB: int
        storageGB: int
        vmCount: int


    class azure.mgmt.scvmm.types.CloudInventoryItem(TypedDict, total=False):
        key "inventoryItemName": str
        key "inventoryType": Required[Literal[InventoryType.CLOUD]]
        key "managedResourceId": str
        key "provisioningState": Union[str, ProvisioningState]
        key "uuid": str
        inventoryItemName: str
        inventoryType: Literal[InventoryType.CLOUD]
        managedResourceId: str
        provisioningState: Union[str, ProvisioningState]
        uuid: str


    class azure.mgmt.scvmm.types.CloudProperties(TypedDict, total=False):
        key "cloudCapacity": ForwardRef('CloudCapacity', module='types')
        key "cloudName": str
        key "inventoryItemId": str
        key "provisioningState": Union[str, ProvisioningState]
        key "uuid": str
        key "vmmServerId": str
        cloudCapacity: CloudCapacity
        cloudName: str
        inventoryItemId: str
        provisioningState: Union[str, ProvisioningState]
        storageQoSPolicies: list[StorageQosPolicy]
        uuid: str
        vmmServerId: str


    class azure.mgmt.scvmm.types.CloudTagsUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.scvmm.types.ExtendedLocation(TypedDict, total=False):
        key "name": str
        key "type": str
        name: str
        type: str


    class azure.mgmt.scvmm.types.ExtensionResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.scvmm.types.GuestAgent(ProxyResource):
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


    class azure.mgmt.scvmm.types.GuestAgentProperties(TypedDict, total=False):
        key "credentials": ForwardRef('GuestCredential', module='types')
        key "customResourceName": str
        key "httpProxyConfig": ForwardRef('HttpProxyConfiguration', module='types')
        key "privateLinkScopeResourceId": str
        key "provisioningAction": Union[str, ProvisioningAction]
        key "provisioningState": Union[str, ProvisioningState]
        key "status": str
        key "uuid": str
        credentials: GuestCredential
        customResourceName: str
        httpProxyConfig: HttpProxyConfiguration
        privateLinkScopeResourceId: str
        provisioningAction: Union[str, ProvisioningAction]
        provisioningState: Union[str, ProvisioningState]
        status: str
        uuid: str


    class azure.mgmt.scvmm.types.GuestCredential(TypedDict, total=False):
        key "password": Required[str]
        key "username": Required[str]
        password: str
        username: str


    class azure.mgmt.scvmm.types.HardwareProfile(TypedDict, total=False):
        key "cpuCount": int
        key "dynamicMemoryEnabled": Union[str, DynamicMemoryEnabled]
        key "dynamicMemoryMaxMB": int
        key "dynamicMemoryMinMB": int
        key "isHighlyAvailable": Union[str, IsHighlyAvailable]
        key "limitCpuForMigration": Union[str, LimitCpuForMigration]
        key "memoryMB": int
        cpuCount: int
        dynamicMemoryEnabled: Union[str, DynamicMemoryEnabled]
        dynamicMemoryMaxMB: int
        dynamicMemoryMinMB: int
        isHighlyAvailable: Union[str, IsHighlyAvailable]
        limitCpuForMigration: Union[str, LimitCpuForMigration]
        memoryMB: int


    class azure.mgmt.scvmm.types.HardwareProfileUpdate(TypedDict, total=False):
        key "cpuCount": int
        key "dynamicMemoryEnabled": Union[str, DynamicMemoryEnabled]
        key "dynamicMemoryMaxMB": int
        key "dynamicMemoryMinMB": int
        key "limitCpuForMigration": Union[str, LimitCpuForMigration]
        key "memoryMB": int
        cpuCount: int
        dynamicMemoryEnabled: Union[str, DynamicMemoryEnabled]
        dynamicMemoryMaxMB: int
        dynamicMemoryMinMB: int
        limitCpuForMigration: Union[str, LimitCpuForMigration]
        memoryMB: int


    class azure.mgmt.scvmm.types.HttpProxyConfiguration(TypedDict, total=False):
        key "httpsProxy": str
        httpsProxy: str


    class azure.mgmt.scvmm.types.InfrastructureProfile(TypedDict, total=False):
        key "biosGuid": str
        key "checkpointType": str
        key "cloudId": str
        key "generation": int
        key "inventoryItemId": str
        key "lastRestoredVMCheckpoint": ForwardRef('Checkpoint', module='types')
        key "templateId": str
        key "uuid": str
        key "vmName": str
        key "vmmServerId": str
        biosGuid: str
        checkpointType: str
        checkpoints: list[Checkpoint]
        cloudId: str
        generation: int
        inventoryItemId: str
        lastRestoredVMCheckpoint: Checkpoint
        templateId: str
        uuid: str
        vmName: str
        vmmServerId: str


    class azure.mgmt.scvmm.types.InfrastructureProfileUpdate(TypedDict, total=False):
        key "checkpointType": str
        checkpointType: str


    class azure.mgmt.scvmm.types.InventoryItem(ProxyResource):
        key "id": str
        key "kind": str
        key "name": str
        key "properties": ForwardRef('InventoryItemProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: str
        name: str
        properties: InventoryItemProperties
        systemData: SystemData
        type: str


    class azure.mgmt.scvmm.types.InventoryItemDetails(TypedDict, total=False):
        key "inventoryItemId": str
        key "inventoryItemName": str
        inventoryItemId: str
        inventoryItemName: str


    class azure.mgmt.scvmm.types.InventoryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOUD = "Cloud"
        VIRTUAL_MACHINE = "VirtualMachine"
        VIRTUAL_MACHINE_TEMPLATE = "VirtualMachineTemplate"
        VIRTUAL_NETWORK = "VirtualNetwork"


    class azure.mgmt.scvmm.types.NetworkInterface(TypedDict, total=False):
        key "displayName": str
        key "ipv4AddressType": Union[str, AllocationMethod]
        key "ipv6AddressType": Union[str, AllocationMethod]
        key "macAddress": str
        key "macAddressType": Union[str, AllocationMethod]
        key "name": str
        key "networkName": str
        key "nicId": str
        key "virtualNetworkId": str
        displayName: str
        ipv4AddressType: Union[str, AllocationMethod]
        ipv4Addresses: list[str]
        ipv6AddressType: Union[str, AllocationMethod]
        ipv6Addresses: list[str]
        macAddress: str
        macAddressType: Union[str, AllocationMethod]
        name: str
        networkName: str
        nicId: str
        virtualNetworkId: str


    class azure.mgmt.scvmm.types.NetworkInterfaceUpdate(TypedDict, total=False):
        key "ipv4AddressType": Union[str, AllocationMethod]
        key "ipv6AddressType": Union[str, AllocationMethod]
        key "macAddress": str
        key "macAddressType": Union[str, AllocationMethod]
        key "name": str
        key "nicId": str
        key "virtualNetworkId": str
        ipv4AddressType: Union[str, AllocationMethod]
        ipv6AddressType: Union[str, AllocationMethod]
        macAddress: str
        macAddressType: Union[str, AllocationMethod]
        name: str
        nicId: str
        virtualNetworkId: str


    class azure.mgmt.scvmm.types.NetworkProfile(TypedDict, total=False):
        networkInterfaces: list[NetworkInterface]


    class azure.mgmt.scvmm.types.NetworkProfileUpdate(TypedDict, total=False):
        networkInterfaces: list[NetworkInterfaceUpdate]


    class azure.mgmt.scvmm.types.OsProfileForVmInstance(TypedDict, total=False):
        key "adminPassword": str
        key "adminUsername": str
        key "computerName": str
        key "domainName": str
        key "domainPassword": str
        key "domainUsername": str
        key "osSku": str
        key "osType": Union[str, OsType]
        key "osVersion": str
        key "productKey": str
        key "runOnceCommands": str
        key "timezone": int
        key "workgroup": str
        adminPassword: str
        adminUsername: str
        computerName: str
        domainName: str
        domainPassword: str
        domainUsername: str
        osSku: str
        osType: Union[str, OsType]
        osVersion: str
        productKey: str
        runOnceCommands: str
        timezone: int
        workgroup: str


    class azure.mgmt.scvmm.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.scvmm.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.scvmm.types.StopVirtualMachineOptions(TypedDict, total=False):
        key "skipShutdown": Union[str, SkipShutdown]
        skipShutdown: Union[str, SkipShutdown]


    class azure.mgmt.scvmm.types.StorageProfile(TypedDict, total=False):
        disks: list[VirtualDisk]


    class azure.mgmt.scvmm.types.StorageProfileUpdate(TypedDict, total=False):
        disks: list[VirtualDiskUpdate]


    class azure.mgmt.scvmm.types.StorageQosPolicy(TypedDict, total=False):
        key "bandwidthLimit": int
        key "id": str
        key "iopsMaximum": int
        key "iopsMinimum": int
        key "name": str
        key "policyId": str
        bandwidthLimit: int
        id: str
        iopsMaximum: int
        iopsMinimum: int
        name: str
        policyId: str


    class azure.mgmt.scvmm.types.StorageQosPolicyDetails(TypedDict, total=False):
        key "id": str
        key "name": str
        id: str
        name: str


    class azure.mgmt.scvmm.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.scvmm.types.TrackedResource(Resource):
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


    class azure.mgmt.scvmm.types.VirtualDisk(TypedDict, total=False):
        key "bus": int
        key "busType": str
        key "createDiffDisk": Union[str, CreateDiffDisk]
        key "diskId": str
        key "diskSizeGB": int
        key "displayName": str
        key "lun": int
        key "maxDiskSizeGB": int
        key "name": str
        key "storageQoSPolicy": ForwardRef('StorageQosPolicyDetails', module='types')
        key "templateDiskId": str
        key "vhdFormatType": str
        key "vhdType": str
        key "volumeType": str
        bus: int
        busType: str
        createDiffDisk: Union[str, CreateDiffDisk]
        diskId: str
        diskSizeGB: int
        displayName: str
        lun: int
        maxDiskSizeGB: int
        name: str
        storageQoSPolicy: StorageQosPolicyDetails
        templateDiskId: str
        vhdFormatType: str
        vhdType: str
        volumeType: str


    class azure.mgmt.scvmm.types.VirtualDiskUpdate(TypedDict, total=False):
        key "bus": int
        key "busType": str
        key "diskId": str
        key "diskSizeGB": int
        key "lun": int
        key "name": str
        key "storageQoSPolicy": ForwardRef('StorageQosPolicyDetails', module='types')
        key "vhdType": str
        bus: int
        busType: str
        diskId: str
        diskSizeGB: int
        lun: int
        name: str
        storageQoSPolicy: StorageQosPolicyDetails
        vhdType: str


    class azure.mgmt.scvmm.types.VirtualMachineCreateCheckpoint(TypedDict, total=False):
        key "description": str
        key "name": str
        description: str
        name: str


    class azure.mgmt.scvmm.types.VirtualMachineDeleteCheckpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.scvmm.types.VirtualMachineInstance(ExtensionResource):
        key "extendedLocation": Required[ExtendedLocation]
        key "id": str
        key "name": str
        key "properties": ForwardRef('VirtualMachineInstanceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        name: str
        properties: VirtualMachineInstanceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.scvmm.types.VirtualMachineInstanceProperties(TypedDict, total=False):
        key "hardwareProfile": ForwardRef('HardwareProfile', module='types')
        key "infrastructureProfile": ForwardRef('InfrastructureProfile', module='types')
        key "networkProfile": ForwardRef('NetworkProfile', module='types')
        key "osProfile": ForwardRef('OsProfileForVmInstance', module='types')
        key "powerState": str
        key "provisioningState": Union[str, ProvisioningState]
        key "storageProfile": ForwardRef('StorageProfile', module='types')
        availabilitySets: list[AvailabilitySetListItem]
        hardwareProfile: HardwareProfile
        infrastructureProfile: InfrastructureProfile
        networkProfile: NetworkProfile
        osProfile: OsProfileForVmInstance
        powerState: str
        provisioningState: Union[str, ProvisioningState]
        storageProfile: StorageProfile


    class azure.mgmt.scvmm.types.VirtualMachineInstanceUpdate(TypedDict, total=False):
        key "properties": ForwardRef('VirtualMachineInstanceUpdateProperties', module='types')
        properties: VirtualMachineInstanceUpdateProperties


    class azure.mgmt.scvmm.types.VirtualMachineInstanceUpdateProperties(TypedDict, total=False):
        key "hardwareProfile": ForwardRef('HardwareProfileUpdate', module='types')
        key "infrastructureProfile": ForwardRef('InfrastructureProfileUpdate', module='types')
        key "networkProfile": ForwardRef('NetworkProfileUpdate', module='types')
        key "storageProfile": ForwardRef('StorageProfileUpdate', module='types')
        availabilitySets: list[AvailabilitySetListItem]
        hardwareProfile: HardwareProfileUpdate
        infrastructureProfile: InfrastructureProfileUpdate
        networkProfile: NetworkProfileUpdate
        storageProfile: StorageProfileUpdate


    class azure.mgmt.scvmm.types.VirtualMachineInventoryItem(TypedDict, total=False):
        key "biosGuid": str
        key "cloud": ForwardRef('InventoryItemDetails', module='types')
        key "generation": int
        key "inventoryItemName": str
        key "inventoryType": Required[Literal[InventoryType.VIRTUAL_MACHINE]]
        key "managedMachineResourceId": str
        key "managedResourceId": str
        key "osName": str
        key "osType": Union[str, OsType]
        key "osVersion": str
        key "powerState": str
        key "provisioningState": Union[str, ProvisioningState]
        key "uuid": str
        biosGuid: str
        cloud: InventoryItemDetails
        generation: int
        inventoryItemName: str
        inventoryType: Literal[InventoryType.VIRTUAL_MACHINE]
        ipAddresses: list[str]
        managedMachineResourceId: str
        managedResourceId: str
        osName: str
        osType: Union[str, OsType]
        osVersion: str
        powerState: str
        provisioningState: Union[str, ProvisioningState]
        uuid: str


    class azure.mgmt.scvmm.types.VirtualMachineRestoreCheckpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.scvmm.types.VirtualMachineTemplate(TrackedResource):
        key "extendedLocation": Required[ExtendedLocation]
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('VirtualMachineTemplateProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: VirtualMachineTemplateProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.scvmm.types.VirtualMachineTemplateInventoryItem(TypedDict, total=False):
        key "cpuCount": int
        key "inventoryItemName": str
        key "inventoryType": Required[Literal[InventoryType.VIRTUAL_MACHINE_TEMPLATE]]
        key "managedResourceId": str
        key "memoryMB": int
        key "osName": str
        key "osType": Union[str, OsType]
        key "provisioningState": Union[str, ProvisioningState]
        key "uuid": str
        cpuCount: int
        inventoryItemName: str
        inventoryType: Literal[InventoryType.VIRTUAL_MACHINE_TEMPLATE]
        managedResourceId: str
        memoryMB: int
        osName: str
        osType: Union[str, OsType]
        provisioningState: Union[str, ProvisioningState]
        uuid: str


    class azure.mgmt.scvmm.types.VirtualMachineTemplateProperties(TypedDict, total=False):
        key "computerName": str
        key "cpuCount": int
        key "dynamicMemoryEnabled": Union[str, DynamicMemoryEnabled]
        key "dynamicMemoryMaxMB": int
        key "dynamicMemoryMinMB": int
        key "generation": int
        key "inventoryItemId": str
        key "isCustomizable": Union[str, IsCustomizable]
        key "isHighlyAvailable": Union[str, IsHighlyAvailable]
        key "limitCpuForMigration": Union[str, LimitCpuForMigration]
        key "memoryMB": int
        key "osName": str
        key "osType": Union[str, OsType]
        key "provisioningState": Union[str, ProvisioningState]
        key "uuid": str
        key "vmmServerId": str
        computerName: str
        cpuCount: int
        disks: list[VirtualDisk]
        dynamicMemoryEnabled: Union[str, DynamicMemoryEnabled]
        dynamicMemoryMaxMB: int
        dynamicMemoryMinMB: int
        generation: int
        inventoryItemId: str
        isCustomizable: Union[str, IsCustomizable]
        isHighlyAvailable: Union[str, IsHighlyAvailable]
        limitCpuForMigration: Union[str, LimitCpuForMigration]
        memoryMB: int
        networkInterfaces: list[NetworkInterface]
        osName: str
        osType: Union[str, OsType]
        provisioningState: Union[str, ProvisioningState]
        uuid: str
        vmmServerId: str


    class azure.mgmt.scvmm.types.VirtualMachineTemplateTagsUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.scvmm.types.VirtualNetwork(TrackedResource):
        key "extendedLocation": Required[ExtendedLocation]
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


    class azure.mgmt.scvmm.types.VirtualNetworkInventoryItem(TypedDict, total=False):
        key "inventoryItemName": str
        key "inventoryType": Required[Literal[InventoryType.VIRTUAL_NETWORK]]
        key "managedResourceId": str
        key "provisioningState": Union[str, ProvisioningState]
        key "uuid": str
        inventoryItemName: str
        inventoryType: Literal[InventoryType.VIRTUAL_NETWORK]
        managedResourceId: str
        provisioningState: Union[str, ProvisioningState]
        uuid: str


    class azure.mgmt.scvmm.types.VirtualNetworkProperties(TypedDict, total=False):
        key "inventoryItemId": str
        key "networkName": str
        key "provisioningState": Union[str, ProvisioningState]
        key "uuid": str
        key "vmmServerId": str
        inventoryItemId: str
        networkName: str
        provisioningState: Union[str, ProvisioningState]
        uuid: str
        vmmServerId: str


    class azure.mgmt.scvmm.types.VirtualNetworkTagsUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.scvmm.types.VmmCredential(TypedDict, total=False):
        key "password": str
        key "username": str
        password: str
        username: str


    class azure.mgmt.scvmm.types.VmmServer(TrackedResource):
        key "extendedLocation": Required[ExtendedLocation]
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('VmmServerProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: VmmServerProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.scvmm.types.VmmServerProperties(TypedDict, total=False):
        key "connectionStatus": str
        key "credentials": ForwardRef('VmmCredential', module='types')
        key "errorMessage": str
        key "fqdn": Required[str]
        key "port": int
        key "provisioningState": Union[str, ProvisioningState]
        key "uuid": str
        key "version": str
        connectionStatus: str
        credentials: VmmCredential
        errorMessage: str
        fqdn: str
        port: int
        provisioningState: Union[str, ProvisioningState]
        uuid: str
        version: str


    class azure.mgmt.scvmm.types.VmmServerTagsUpdate(TypedDict, total=False):
        tags: dict[str, str]


```