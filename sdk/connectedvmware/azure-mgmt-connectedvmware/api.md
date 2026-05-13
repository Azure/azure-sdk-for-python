```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.connectedvmware

    class azure.mgmt.connectedvmware.ConnectedVMwareMgmtClient: implements ContextManager 
        clusters: ClustersOperations
        datastores: DatastoresOperations
        hosts: HostsOperations
        inventory_items: InventoryItemsOperations
        operations: Operations
        resource_pools: ResourcePoolsOperations
        vcenters: VCentersOperations
        virtual_machine_instances: VirtualMachineInstancesOperations
        virtual_machine_templates: VirtualMachineTemplatesOperations
        virtual_networks: VirtualNetworksOperations
        vm_instance_guest_agents: VMInstanceGuestAgentsOperations
        vm_instance_hybrid_identity_metadata: VmInstanceHybridIdentityMetadataOperations

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


namespace azure.mgmt.connectedvmware.aio

    class azure.mgmt.connectedvmware.aio.ConnectedVMwareMgmtClient: implements AsyncContextManager 
        clusters: ClustersOperations
        datastores: DatastoresOperations
        hosts: HostsOperations
        inventory_items: InventoryItemsOperations
        operations: Operations
        resource_pools: ResourcePoolsOperations
        vcenters: VCentersOperations
        virtual_machine_instances: VirtualMachineInstancesOperations
        virtual_machine_templates: VirtualMachineTemplatesOperations
        virtual_networks: VirtualNetworksOperations
        vm_instance_guest_agents: VMInstanceGuestAgentsOperations
        vm_instance_hybrid_identity_metadata: VmInstanceHybridIdentityMetadataOperations

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


namespace azure.mgmt.connectedvmware.aio.operations

    class azure.mgmt.connectedvmware.aio.operations.ClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: Optional[Cluster] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                force: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Cluster: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Cluster]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Cluster]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: Optional[ResourcePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Cluster: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Cluster: ...


    class azure.mgmt.connectedvmware.aio.operations.DatastoresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                datastore_name: str, 
                body: Optional[Datastore] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Datastore]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                datastore_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Datastore]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                datastore_name: str, 
                force: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                datastore_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Datastore: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Datastore]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Datastore]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                datastore_name: str, 
                body: Optional[ResourcePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Datastore: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                datastore_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Datastore: ...


    class azure.mgmt.connectedvmware.aio.operations.HostsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                host_name: str, 
                body: Optional[Host] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Host]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                host_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Host]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                host_name: str, 
                force: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                host_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Host: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Host]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Host]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                host_name: str, 
                body: Optional[ResourcePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Host: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                host_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Host: ...


    class azure.mgmt.connectedvmware.aio.operations.InventoryItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                vcenter_name: str, 
                inventory_item_name: str, 
                body: Optional[InventoryItem] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InventoryItem: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                vcenter_name: str, 
                inventory_item_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InventoryItem: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                vcenter_name: str, 
                inventory_item_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vcenter_name: str, 
                inventory_item_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> InventoryItem: ...

        @distributed_trace
        def list_by_v_center(
                self, 
                resource_group_name: str, 
                vcenter_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[InventoryItem]: ...


    class azure.mgmt.connectedvmware.aio.operations.Operations:

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


    class azure.mgmt.connectedvmware.aio.operations.ResourcePoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_pool_name: str, 
                body: Optional[ResourcePool] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourcePool]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_pool_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourcePool]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_pool_name: str, 
                force: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ResourcePool: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ResourcePool]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ResourcePool]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_pool_name: str, 
                body: Optional[ResourcePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourcePool: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_pool_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourcePool: ...


    class azure.mgmt.connectedvmware.aio.operations.VCentersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                vcenter_name: str, 
                body: Optional[VCenter] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VCenter]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                vcenter_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VCenter]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                vcenter_name: str, 
                force: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vcenter_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VCenter: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[VCenter]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[VCenter]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vcenter_name: str, 
                body: Optional[ResourcePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VCenter: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vcenter_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VCenter: ...


    class azure.mgmt.connectedvmware.aio.operations.VMInstanceGuestAgentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_uri: str, 
                body: Optional[GuestAgent] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GuestAgent]: ...

        @overload
        async def begin_create(
                self, 
                resource_uri: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GuestAgent]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_uri: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GuestAgent: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[GuestAgent]: ...


    class azure.mgmt.connectedvmware.aio.operations.VirtualMachineInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                body: Optional[VirtualMachineInstance] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineInstance]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineInstance]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_uri: str, 
                delete_from_host: Optional[bool] = None, 
                force: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_restart(
                self, 
                resource_uri: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_uri: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
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
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_uri: str, 
                body: Optional[VirtualMachineInstanceUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineInstance]: ...

        @overload
        async def begin_update(
                self, 
                resource_uri: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineInstance]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VirtualMachineInstance: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[VirtualMachineInstance]: ...


    class azure.mgmt.connectedvmware.aio.operations.VirtualMachineTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                body: Optional[VirtualMachineTemplate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineTemplate]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineTemplate]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                force: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VirtualMachineTemplate: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[VirtualMachineTemplate]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[VirtualMachineTemplate]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                body: Optional[ResourcePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VirtualMachineTemplate: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VirtualMachineTemplate: ...


    class azure.mgmt.connectedvmware.aio.operations.VirtualNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                body: Optional[VirtualNetwork] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetwork]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetwork]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                force: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VirtualNetwork: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[VirtualNetwork]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[VirtualNetwork]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                body: Optional[ResourcePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VirtualNetwork: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VirtualNetwork: ...


    class azure.mgmt.connectedvmware.aio.operations.VmInstanceHybridIdentityMetadataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VmInstanceHybridIdentityMetadata: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[VmInstanceHybridIdentityMetadata]: ...


namespace azure.mgmt.connectedvmware.models

    class azure.mgmt.connectedvmware.models.Cluster(Model):
        custom_resource_name: str
        datastore_ids: list[str]
        extended_location: ExtendedLocation
        id: str
        inventory_item_id: str
        kind: str
        location: str
        mo_name: str
        mo_ref_id: str
        name: str
        network_ids: list[str]
        provisioning_state: Union[str, ProvisioningState]
        statuses: list[ResourceStatus]
        system_data: SystemData
        tags: dict[str, str]
        total_cpu_m_hz: int
        total_memory_gb: int
        type: str
        used_cpu_m_hz: int
        used_memory_gb: int
        uuid: str
        v_center_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                inventory_item_id: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                mo_ref_id: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                v_center_id: Optional[str] = ..., 
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


    class azure.mgmt.connectedvmware.models.ClusterInventoryItem(InventoryItemProperties):
        inventory_type: Union[str, InventoryType]
        managed_resource_id: str
        mo_name: str
        mo_ref_id: str
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                managed_resource_id: Optional[str] = ..., 
                mo_name: Optional[str] = ..., 
                mo_ref_id: Optional[str] = ..., 
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


    class azure.mgmt.connectedvmware.models.ClustersList(Model):
        next_link: str
        value: list[Cluster]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[Cluster], 
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


    class azure.mgmt.connectedvmware.models.Condition(Model):
        message: str
        reason: str
        severity: str
        status: str

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


    class azure.mgmt.connectedvmware.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.connectedvmware.models.Datastore(Model):
        capacity_gb: int
        custom_resource_name: str
        extended_location: ExtendedLocation
        free_space_gb: int
        id: str
        inventory_item_id: str
        kind: str
        location: str
        mo_name: str
        mo_ref_id: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        statuses: list[ResourceStatus]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        uuid: str
        v_center_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                inventory_item_id: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                mo_ref_id: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                v_center_id: Optional[str] = ..., 
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


    class azure.mgmt.connectedvmware.models.DatastoreInventoryItem(InventoryItemProperties):
        capacity_gb: int
        free_space_gb: int
        inventory_type: Union[str, InventoryType]
        managed_resource_id: str
        mo_name: str
        mo_ref_id: str
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                capacity_gb: Optional[int] = ..., 
                free_space_gb: Optional[int] = ..., 
                managed_resource_id: Optional[str] = ..., 
                mo_name: Optional[str] = ..., 
                mo_ref_id: Optional[str] = ..., 
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


    class azure.mgmt.connectedvmware.models.DatastoresList(Model):
        next_link: str
        value: list[Datastore]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[Datastore], 
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


    class azure.mgmt.connectedvmware.models.DiskMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INDEPENDENT_NONPERSISTENT = "independent_nonpersistent"
        INDEPENDENT_PERSISTENT = "independent_persistent"
        PERSISTENT = "persistent"


    class azure.mgmt.connectedvmware.models.DiskType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FLAT = "flat"
        PMEM = "pmem"
        RAWPHYSICAL = "rawphysical"
        RAWVIRTUAL = "rawvirtual"
        SESPARSE = "sesparse"
        SPARSE = "sparse"
        UNKNOWN = "unknown"


    class azure.mgmt.connectedvmware.models.ErrorAdditionalInfo(Model):
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


    class azure.mgmt.connectedvmware.models.ErrorDetail(Model):
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


    class azure.mgmt.connectedvmware.models.ErrorResponse(Model):
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


    class azure.mgmt.connectedvmware.models.ExtendedLocation(Model):
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


    class azure.mgmt.connectedvmware.models.FirmwareType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BIOS = "bios"
        EFI = "efi"


    class azure.mgmt.connectedvmware.models.GuestAgent(ProxyResource):
        credentials: GuestCredential
        custom_resource_name: str
        http_proxy_config: HttpProxyConfiguration
        id: str
        name: str
        private_link_scope_resource_id: str
        provisioning_action: Union[str, ProvisioningAction]
        provisioning_state: Union[str, ProvisioningState]
        status: str
        statuses: list[ResourceStatus]
        system_data: SystemData
        type: str
        uuid: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                credentials: Optional[GuestCredential] = ..., 
                http_proxy_config: Optional[HttpProxyConfiguration] = ..., 
                private_link_scope_resource_id: Optional[str] = ..., 
                provisioning_action: Optional[Union[str, ProvisioningAction]] = ..., 
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


    class azure.mgmt.connectedvmware.models.GuestAgentList(Model):
        next_link: str
        value: list[GuestAgent]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[GuestAgent], 
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


    class azure.mgmt.connectedvmware.models.GuestCredential(Model):
        password: str
        username: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                password: Optional[str] = ..., 
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


    class azure.mgmt.connectedvmware.models.HardwareProfile(Model):
        cpu_hot_add_enabled: bool
        cpu_hot_remove_enabled: bool
        memory_hot_add_enabled: bool
        memory_size_mb: int
        num_cores_per_socket: int
        num_cp_us: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                memory_size_mb: Optional[int] = ..., 
                num_cores_per_socket: Optional[int] = ..., 
                num_cp_us: Optional[int] = ..., 
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


    class azure.mgmt.connectedvmware.models.Host(Model):
        cpu_mhz: int
        custom_resource_name: str
        datastore_ids: list[str]
        extended_location: ExtendedLocation
        id: str
        inventory_item_id: str
        kind: str
        location: str
        memory_size_gb: int
        mo_name: str
        mo_ref_id: str
        name: str
        network_ids: list[str]
        overall_cpu_usage_m_hz: int
        overall_memory_usage_gb: int
        provisioning_state: Union[str, ProvisioningState]
        statuses: list[ResourceStatus]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        uuid: str
        v_center_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                inventory_item_id: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                mo_ref_id: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                v_center_id: Optional[str] = ..., 
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


    class azure.mgmt.connectedvmware.models.HostInventoryItem(InventoryItemProperties):
        inventory_type: Union[str, InventoryType]
        managed_resource_id: str
        mo_name: str
        mo_ref_id: str
        parent: InventoryItemDetails
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                managed_resource_id: Optional[str] = ..., 
                mo_name: Optional[str] = ..., 
                mo_ref_id: Optional[str] = ..., 
                parent: Optional[InventoryItemDetails] = ..., 
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


    class azure.mgmt.connectedvmware.models.HostsList(Model):
        next_link: str
        value: list[Host]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[Host], 
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


    class azure.mgmt.connectedvmware.models.HttpProxyConfiguration(Model):
        https_proxy: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                https_proxy: Optional[str] = ..., 
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


    class azure.mgmt.connectedvmware.models.IPAddressAllocationMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DYNAMIC = "dynamic"
        LINKLAYER = "linklayer"
        OTHER = "other"
        RANDOM = "random"
        STATIC = "static"
        UNSET = "unset"


    class azure.mgmt.connectedvmware.models.InfrastructureProfile(Model):
        custom_resource_name: str
        firmware_type: Union[str, FirmwareType]
        folder_path: str
        instance_uuid: str
        inventory_item_id: str
        mo_name: str
        mo_ref_id: str
        smbios_uuid: str
        template_id: str
        v_center_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                firmware_type: Optional[Union[str, FirmwareType]] = ..., 
                inventory_item_id: Optional[str] = ..., 
                smbios_uuid: Optional[str] = ..., 
                template_id: Optional[str] = ..., 
                v_center_id: Optional[str] = ..., 
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


    class azure.mgmt.connectedvmware.models.InventoryItem(ProxyResource):
        id: str
        inventory_type: Union[str, InventoryType]
        kind: str
        managed_resource_id: str
        mo_name: str
        mo_ref_id: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                managed_resource_id: Optional[str] = ..., 
                mo_name: Optional[str] = ..., 
                mo_ref_id: Optional[str] = ..., 
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


    class azure.mgmt.connectedvmware.models.InventoryItemDetails(Model):
        inventory_item_id: str
        inventory_type: Union[str, InventoryType]
        mo_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                inventory_item_id: Optional[str] = ..., 
                inventory_type: Optional[Union[str, InventoryType]] = ..., 
                mo_name: Optional[str] = ..., 
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


    class azure.mgmt.connectedvmware.models.InventoryItemProperties(Model):
        inventory_type: Union[str, InventoryType]
        managed_resource_id: str
        mo_name: str
        mo_ref_id: str
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                managed_resource_id: Optional[str] = ..., 
                mo_name: Optional[str] = ..., 
                mo_ref_id: Optional[str] = ..., 
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


    class azure.mgmt.connectedvmware.models.InventoryItemsList(Model):
        next_link: str
        value: list[InventoryItem]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[InventoryItem], 
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


    class azure.mgmt.connectedvmware.models.InventoryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLUSTER = "Cluster"
        DATASTORE = "Datastore"
        HOST = "Host"
        RESOURCE_POOL = "ResourcePool"
        VIRTUAL_MACHINE = "VirtualMachine"
        VIRTUAL_MACHINE_TEMPLATE = "VirtualMachineTemplate"
        VIRTUAL_NETWORK = "VirtualNetwork"


    class azure.mgmt.connectedvmware.models.NICType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        E1000 = "e1000"
        E1000_E = "e1000e"
        PCNET32 = "pcnet32"
        VMXNET = "vmxnet"
        VMXNET2 = "vmxnet2"
        VMXNET3 = "vmxnet3"


    class azure.mgmt.connectedvmware.models.NetworkInterface(Model):
        device_key: int
        ip_addresses: list[str]
        ip_settings: NicIPSettings
        label: str
        mac_address: str
        name: str
        network_id: str
        network_mo_name: str
        network_mo_ref_id: str
        nic_type: Union[str, NICType]
        power_on_boot: Union[str, PowerOnBootOption]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                device_key: Optional[int] = ..., 
                ip_settings: Optional[NicIPSettings] = ..., 
                name: Optional[str] = ..., 
                network_id: Optional[str] = ..., 
                nic_type: Optional[Union[str, NICType]] = ..., 
                power_on_boot: Optional[Union[str, PowerOnBootOption]] = ..., 
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


    class azure.mgmt.connectedvmware.models.NetworkInterfaceUpdate(Model):
        device_key: int
        name: str
        network_id: str
        nic_type: Union[str, NICType]
        power_on_boot: Union[str, PowerOnBootOption]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                device_key: Optional[int] = ..., 
                name: Optional[str] = ..., 
                network_id: Optional[str] = ..., 
                nic_type: Optional[Union[str, NICType]] = ..., 
                power_on_boot: Optional[Union[str, PowerOnBootOption]] = ..., 
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


    class azure.mgmt.connectedvmware.models.NetworkProfile(Model):
        network_interfaces: list[NetworkInterface]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                network_interfaces: Optional[List[NetworkInterface]] = ..., 
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


    class azure.mgmt.connectedvmware.models.NetworkProfileUpdate(Model):
        network_interfaces: list[NetworkInterfaceUpdate]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                network_interfaces: Optional[List[NetworkInterfaceUpdate]] = ..., 
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


    class azure.mgmt.connectedvmware.models.NicIPAddressSettings(Model):
        allocation_method: str
        ip_address: str
        subnet_mask: str

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


    class azure.mgmt.connectedvmware.models.NicIPSettings(Model):
        allocation_method: Union[str, IPAddressAllocationMethod]
        dns_servers: list[str]
        gateway: list[str]
        ip_address: str
        ip_address_info: list[NicIPAddressSettings]
        primary_wins_server: str
        secondary_wins_server: str
        subnet_mask: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allocation_method: Optional[Union[str, IPAddressAllocationMethod]] = ..., 
                dns_servers: Optional[List[str]] = ..., 
                gateway: Optional[List[str]] = ..., 
                ip_address: Optional[str] = ..., 
                subnet_mask: Optional[str] = ..., 
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


    class azure.mgmt.connectedvmware.models.Operation(Model):
        display: OperationDisplay
        is_data_action: bool
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
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


    class azure.mgmt.connectedvmware.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
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


    class azure.mgmt.connectedvmware.models.OperationsList(Model):
        next_link: str
        value: list[Operation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[Operation], 
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


    class azure.mgmt.connectedvmware.models.OsProfileForVMInstance(Model):
        admin_password: str
        admin_username: str
        computer_name: str
        guest_id: str
        os_sku: str
        os_type: Union[str, OsType]
        tools_running_status: str
        tools_version: str
        tools_version_status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                admin_password: Optional[str] = ..., 
                admin_username: Optional[str] = ..., 
                computer_name: Optional[str] = ..., 
                guest_id: Optional[str] = ..., 
                os_type: Optional[Union[str, OsType]] = ..., 
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


    class azure.mgmt.connectedvmware.models.OsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        OTHER = "Other"
        WINDOWS = "Windows"


    class azure.mgmt.connectedvmware.models.PlacementProfile(Model):
        cluster_id: str
        datastore_id: str
        host_id: str
        resource_pool_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cluster_id: Optional[str] = ..., 
                datastore_id: Optional[str] = ..., 
                host_id: Optional[str] = ..., 
                resource_pool_id: Optional[str] = ..., 
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


    class azure.mgmt.connectedvmware.models.PowerOnBootOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.mgmt.connectedvmware.models.ProvisioningAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INSTALL = "install"
        REPAIR = "repair"
        UNINSTALL = "uninstall"


    class azure.mgmt.connectedvmware.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATED = "Created"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.connectedvmware.models.ProxyResource(Resource):
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


    class azure.mgmt.connectedvmware.models.Resource(Model):
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


    class azure.mgmt.connectedvmware.models.ResourcePatch(Model):
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


    class azure.mgmt.connectedvmware.models.ResourcePool(Model):
        cpu_capacity_m_hz: int
        cpu_limit_m_hz: int
        cpu_overall_usage_m_hz: int
        cpu_reservation_m_hz: int
        cpu_shares_level: str
        custom_resource_name: str
        datastore_ids: list[str]
        extended_location: ExtendedLocation
        id: str
        inventory_item_id: str
        kind: str
        location: str
        mem_capacity_gb: int
        mem_limit_mb: int
        mem_overall_usage_gb: int
        mem_reservation_mb: int
        mem_shares_level: str
        mo_name: str
        mo_ref_id: str
        name: str
        network_ids: list[str]
        provisioning_state: Union[str, ProvisioningState]
        statuses: list[ResourceStatus]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        uuid: str
        v_center_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                inventory_item_id: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                mo_ref_id: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                v_center_id: Optional[str] = ..., 
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


    class azure.mgmt.connectedvmware.models.ResourcePoolInventoryItem(InventoryItemProperties):
        inventory_type: Union[str, InventoryType]
        managed_resource_id: str
        mo_name: str
        mo_ref_id: str
        parent: InventoryItemDetails
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                managed_resource_id: Optional[str] = ..., 
                mo_name: Optional[str] = ..., 
                mo_ref_id: Optional[str] = ..., 
                parent: Optional[InventoryItemDetails] = ..., 
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


    class azure.mgmt.connectedvmware.models.ResourcePoolsList(Model):
        next_link: str
        value: list[ResourcePool]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[ResourcePool], 
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


    class azure.mgmt.connectedvmware.models.ResourceStatus(Model):
        last_updated_at: datetime
        message: str
        reason: str
        severity: str
        status: str
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


    class azure.mgmt.connectedvmware.models.SCSIControllerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUSLOGIC = "buslogic"
        LSILOGIC = "lsilogic"
        LSILOGICSAS = "lsilogicsas"
        PVSCSI = "pvscsi"


    class azure.mgmt.connectedvmware.models.SecurityProfile(Model):
        uefi_settings: UefiSettings

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                uefi_settings: Optional[UefiSettings] = ..., 
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


    class azure.mgmt.connectedvmware.models.StopVirtualMachineOptions(Model):
        skip_shutdown: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                skip_shutdown: bool = False, 
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


    class azure.mgmt.connectedvmware.models.StorageProfile(Model):
        disks: list[VirtualDisk]
        scsi_controllers: list[VirtualSCSIController]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disks: Optional[List[VirtualDisk]] = ..., 
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


    class azure.mgmt.connectedvmware.models.StorageProfileUpdate(Model):
        disks: list[VirtualDiskUpdate]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disks: Optional[List[VirtualDiskUpdate]] = ..., 
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


    class azure.mgmt.connectedvmware.models.SystemData(Model):
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


    class azure.mgmt.connectedvmware.models.UefiSettings(Model):
        secure_boot_enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                secure_boot_enabled: Optional[bool] = ..., 
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


    class azure.mgmt.connectedvmware.models.VCenter(Model):
        connection_status: str
        credentials: VICredential
        custom_resource_name: str
        extended_location: ExtendedLocation
        fqdn: str
        id: str
        instance_uuid: str
        kind: str
        location: str
        name: str
        port: int
        provisioning_state: Union[str, ProvisioningState]
        statuses: list[ResourceStatus]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        uuid: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                credentials: Optional[VICredential] = ..., 
                extended_location: Optional[ExtendedLocation] = ..., 
                fqdn: str, 
                kind: Optional[str] = ..., 
                location: str, 
                port: Optional[int] = ..., 
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


    class azure.mgmt.connectedvmware.models.VCentersList(Model):
        next_link: str
        value: list[VCenter]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[VCenter], 
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


    class azure.mgmt.connectedvmware.models.VICredential(Model):
        password: str
        username: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                password: Optional[str] = ..., 
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


    class azure.mgmt.connectedvmware.models.VirtualDisk(Model):
        controller_key: int
        device_key: int
        device_name: str
        disk_mode: Union[str, DiskMode]
        disk_object_id: str
        disk_size_gb: int
        disk_type: Union[str, DiskType]
        label: str
        name: str
        unit_number: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                controller_key: Optional[int] = ..., 
                device_key: Optional[int] = ..., 
                device_name: Optional[str] = ..., 
                disk_mode: Optional[Union[str, DiskMode]] = ..., 
                disk_size_gb: Optional[int] = ..., 
                disk_type: Optional[Union[str, DiskType]] = ..., 
                name: Optional[str] = ..., 
                unit_number: Optional[int] = ..., 
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


    class azure.mgmt.connectedvmware.models.VirtualDiskUpdate(Model):
        controller_key: int
        device_key: int
        device_name: str
        disk_mode: Union[str, DiskMode]
        disk_size_gb: int
        disk_type: Union[str, DiskType]
        name: str
        unit_number: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                controller_key: Optional[int] = ..., 
                device_key: Optional[int] = ..., 
                device_name: Optional[str] = ..., 
                disk_mode: Optional[Union[str, DiskMode]] = ..., 
                disk_size_gb: Optional[int] = ..., 
                disk_type: Optional[Union[str, DiskType]] = ..., 
                name: Optional[str] = ..., 
                unit_number: Optional[int] = ..., 
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


    class azure.mgmt.connectedvmware.models.VirtualMachineInstance(ProxyResource):
        extended_location: ExtendedLocation
        hardware_profile: HardwareProfile
        id: str
        infrastructure_profile: InfrastructureProfile
        name: str
        network_profile: NetworkProfile
        os_profile: OsProfileForVMInstance
        placement_profile: PlacementProfile
        power_state: str
        provisioning_state: Union[str, ProvisioningState]
        resource_uid: str
        security_profile: SecurityProfile
        statuses: list[ResourceStatus]
        storage_profile: StorageProfile
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                hardware_profile: Optional[HardwareProfile] = ..., 
                infrastructure_profile: Optional[InfrastructureProfile] = ..., 
                network_profile: Optional[NetworkProfile] = ..., 
                os_profile: Optional[OsProfileForVMInstance] = ..., 
                placement_profile: Optional[PlacementProfile] = ..., 
                security_profile: Optional[SecurityProfile] = ..., 
                storage_profile: Optional[StorageProfile] = ..., 
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


    class azure.mgmt.connectedvmware.models.VirtualMachineInstanceUpdate(Model):
        hardware_profile: HardwareProfile
        network_profile: NetworkProfileUpdate
        storage_profile: StorageProfileUpdate

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                hardware_profile: Optional[HardwareProfile] = ..., 
                network_profile: Optional[NetworkProfileUpdate] = ..., 
                storage_profile: Optional[StorageProfileUpdate] = ..., 
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


    class azure.mgmt.connectedvmware.models.VirtualMachineInstancesList(Model):
        next_link: str
        value: list[VirtualMachineInstance]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[VirtualMachineInstance], 
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


    class azure.mgmt.connectedvmware.models.VirtualMachineInventoryItem(InventoryItemProperties):
        cluster: InventoryItemDetails
        folder_path: str
        host: InventoryItemDetails
        instance_uuid: str
        inventory_type: Union[str, InventoryType]
        ip_addresses: list[str]
        managed_resource_id: str
        mo_name: str
        mo_ref_id: str
        os_name: str
        os_type: Union[str, OsType]
        power_state: str
        provisioning_state: Union[str, ProvisioningState]
        resource_pool: InventoryItemDetails
        smbios_uuid: str
        tools_running_status: str
        tools_version: str
        tools_version_status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cluster: Optional[InventoryItemDetails] = ..., 
                folder_path: Optional[str] = ..., 
                host: Optional[InventoryItemDetails] = ..., 
                instance_uuid: Optional[str] = ..., 
                ip_addresses: Optional[List[str]] = ..., 
                managed_resource_id: Optional[str] = ..., 
                mo_name: Optional[str] = ..., 
                mo_ref_id: Optional[str] = ..., 
                os_name: Optional[str] = ..., 
                os_type: Optional[Union[str, OsType]] = ..., 
                resource_pool: Optional[InventoryItemDetails] = ..., 
                smbios_uuid: Optional[str] = ..., 
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


    class azure.mgmt.connectedvmware.models.VirtualMachineTemplate(Model):
        custom_resource_name: str
        disks: list[VirtualDisk]
        extended_location: ExtendedLocation
        firmware_type: Union[str, FirmwareType]
        folder_path: str
        id: str
        inventory_item_id: str
        kind: str
        location: str
        memory_size_mb: int
        mo_name: str
        mo_ref_id: str
        name: str
        network_interfaces: list[NetworkInterface]
        num_cores_per_socket: int
        num_cp_us: int
        os_name: str
        os_type: Union[str, OsType]
        provisioning_state: Union[str, ProvisioningState]
        statuses: list[ResourceStatus]
        system_data: SystemData
        tags: dict[str, str]
        tools_version: str
        tools_version_status: str
        type: str
        uuid: str
        v_center_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                inventory_item_id: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                mo_ref_id: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                v_center_id: Optional[str] = ..., 
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


    class azure.mgmt.connectedvmware.models.VirtualMachineTemplateInventoryItem(InventoryItemProperties):
        folder_path: str
        inventory_type: Union[str, InventoryType]
        managed_resource_id: str
        memory_size_mb: int
        mo_name: str
        mo_ref_id: str
        num_cores_per_socket: int
        num_cp_us: int
        os_name: str
        os_type: Union[str, OsType]
        provisioning_state: Union[str, ProvisioningState]
        tools_version: str
        tools_version_status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                folder_path: Optional[str] = ..., 
                managed_resource_id: Optional[str] = ..., 
                memory_size_mb: Optional[int] = ..., 
                mo_name: Optional[str] = ..., 
                mo_ref_id: Optional[str] = ..., 
                num_cores_per_socket: Optional[int] = ..., 
                num_cp_us: Optional[int] = ..., 
                os_name: Optional[str] = ..., 
                os_type: Optional[Union[str, OsType]] = ..., 
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


    class azure.mgmt.connectedvmware.models.VirtualMachineTemplatesList(Model):
        next_link: str
        value: list[VirtualMachineTemplate]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[VirtualMachineTemplate], 
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


    class azure.mgmt.connectedvmware.models.VirtualNetwork(Model):
        custom_resource_name: str
        extended_location: ExtendedLocation
        id: str
        inventory_item_id: str
        kind: str
        location: str
        mo_name: str
        mo_ref_id: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        statuses: list[ResourceStatus]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        uuid: str
        v_center_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                inventory_item_id: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                mo_ref_id: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                v_center_id: Optional[str] = ..., 
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


    class azure.mgmt.connectedvmware.models.VirtualNetworkInventoryItem(InventoryItemProperties):
        inventory_type: Union[str, InventoryType]
        managed_resource_id: str
        mo_name: str
        mo_ref_id: str
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                managed_resource_id: Optional[str] = ..., 
                mo_name: Optional[str] = ..., 
                mo_ref_id: Optional[str] = ..., 
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


    class azure.mgmt.connectedvmware.models.VirtualNetworksList(Model):
        next_link: str
        value: list[VirtualNetwork]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[VirtualNetwork], 
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


    class azure.mgmt.connectedvmware.models.VirtualSCSIController(Model):
        bus_number: int
        controller_key: int
        scsi_ctlr_unit_number: int
        sharing: Union[str, VirtualSCSISharing]
        type: Union[str, SCSIControllerType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                bus_number: Optional[int] = ..., 
                controller_key: Optional[int] = ..., 
                scsi_ctlr_unit_number: Optional[int] = ..., 
                sharing: Optional[Union[str, VirtualSCSISharing]] = ..., 
                type: Optional[Union[str, SCSIControllerType]] = ..., 
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


    class azure.mgmt.connectedvmware.models.VirtualSCSISharing(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_SHARING = "noSharing"
        PHYSICAL_SHARING = "physicalSharing"
        VIRTUAL_SHARING = "virtualSharing"


    class azure.mgmt.connectedvmware.models.VmInstanceHybridIdentityMetadata(ProxyResource):
        id: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        public_key: str
        resource_uid: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                public_key: Optional[str] = ..., 
                resource_uid: Optional[str] = ..., 
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


    class azure.mgmt.connectedvmware.models.VmInstanceHybridIdentityMetadataList(Model):
        next_link: str
        value: list[VmInstanceHybridIdentityMetadata]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[VmInstanceHybridIdentityMetadata], 
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


namespace azure.mgmt.connectedvmware.operations

    class azure.mgmt.connectedvmware.operations.ClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: Optional[Cluster] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                force: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Cluster: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Cluster]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Cluster]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: Optional[ResourcePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Cluster: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Cluster: ...


    class azure.mgmt.connectedvmware.operations.DatastoresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                datastore_name: str, 
                body: Optional[Datastore] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Datastore]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                datastore_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Datastore]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                datastore_name: str, 
                force: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                datastore_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Datastore: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Datastore]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Datastore]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                datastore_name: str, 
                body: Optional[ResourcePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Datastore: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                datastore_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Datastore: ...


    class azure.mgmt.connectedvmware.operations.HostsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                host_name: str, 
                body: Optional[Host] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Host]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                host_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Host]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                host_name: str, 
                force: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                host_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Host: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Host]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Host]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                host_name: str, 
                body: Optional[ResourcePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Host: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                host_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Host: ...


    class azure.mgmt.connectedvmware.operations.InventoryItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                vcenter_name: str, 
                inventory_item_name: str, 
                body: Optional[InventoryItem] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InventoryItem: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                vcenter_name: str, 
                inventory_item_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InventoryItem: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                vcenter_name: str, 
                inventory_item_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vcenter_name: str, 
                inventory_item_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> InventoryItem: ...

        @distributed_trace
        def list_by_v_center(
                self, 
                resource_group_name: str, 
                vcenter_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[InventoryItem]: ...


    class azure.mgmt.connectedvmware.operations.Operations:

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


    class azure.mgmt.connectedvmware.operations.ResourcePoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_pool_name: str, 
                body: Optional[ResourcePool] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourcePool]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_pool_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourcePool]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_pool_name: str, 
                force: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ResourcePool: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ResourcePool]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ResourcePool]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_pool_name: str, 
                body: Optional[ResourcePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourcePool: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_pool_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourcePool: ...


    class azure.mgmt.connectedvmware.operations.VCentersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                vcenter_name: str, 
                body: Optional[VCenter] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VCenter]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                vcenter_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VCenter]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                vcenter_name: str, 
                force: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vcenter_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VCenter: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[VCenter]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[VCenter]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vcenter_name: str, 
                body: Optional[ResourcePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VCenter: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vcenter_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VCenter: ...


    class azure.mgmt.connectedvmware.operations.VMInstanceGuestAgentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_uri: str, 
                body: Optional[GuestAgent] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GuestAgent]: ...

        @overload
        def begin_create(
                self, 
                resource_uri: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GuestAgent]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_uri: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GuestAgent: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[GuestAgent]: ...


    class azure.mgmt.connectedvmware.operations.VirtualMachineInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                body: Optional[VirtualMachineInstance] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineInstance]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineInstance]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_uri: str, 
                delete_from_host: Optional[bool] = None, 
                force: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_restart(
                self, 
                resource_uri: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_uri: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
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
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_uri: str, 
                body: Optional[VirtualMachineInstanceUpdate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineInstance]: ...

        @overload
        def begin_update(
                self, 
                resource_uri: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineInstance]: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VirtualMachineInstance: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[VirtualMachineInstance]: ...


    class azure.mgmt.connectedvmware.operations.VirtualMachineTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                body: Optional[VirtualMachineTemplate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineTemplate]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineTemplate]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                force: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VirtualMachineTemplate: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[VirtualMachineTemplate]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[VirtualMachineTemplate]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                body: Optional[ResourcePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VirtualMachineTemplate: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                virtual_machine_template_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VirtualMachineTemplate: ...


    class azure.mgmt.connectedvmware.operations.VirtualNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                body: Optional[VirtualNetwork] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetwork]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetwork]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                force: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VirtualNetwork: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[VirtualNetwork]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[VirtualNetwork]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                body: Optional[ResourcePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VirtualNetwork: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VirtualNetwork: ...


    class azure.mgmt.connectedvmware.operations.VmInstanceHybridIdentityMetadataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VmInstanceHybridIdentityMetadata: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[VmInstanceHybridIdentityMetadata]: ...


```