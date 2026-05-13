```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.vmwarecloudsimple

    class azure.mgmt.vmwarecloudsimple.VMwareCloudSimple: implements ContextManager 
        customization_policies: CustomizationPoliciesOperations
        dedicated_cloud_nodes: DedicatedCloudNodesOperations
        dedicated_cloud_services: DedicatedCloudServicesOperations
        operations: Operations
        private_clouds: PrivateCloudsOperations
        resource_pools: ResourcePoolsOperations
        skus_availability: SkusAvailabilityOperations
        usages: UsagesOperations
        virtual_machine_templates: VirtualMachineTemplatesOperations
        virtual_machines: VirtualMachinesOperations
        virtual_networks: VirtualNetworksOperations

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


namespace azure.mgmt.vmwarecloudsimple.aio

    class azure.mgmt.vmwarecloudsimple.aio.VMwareCloudSimple: implements AsyncContextManager 
        customization_policies: CustomizationPoliciesOperations
        dedicated_cloud_nodes: DedicatedCloudNodesOperations
        dedicated_cloud_services: DedicatedCloudServicesOperations
        operations: Operations
        private_clouds: PrivateCloudsOperations
        resource_pools: ResourcePoolsOperations
        skus_availability: SkusAvailabilityOperations
        usages: UsagesOperations
        virtual_machine_templates: VirtualMachineTemplatesOperations
        virtual_machines: VirtualMachinesOperations
        virtual_networks: VirtualNetworksOperations

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


namespace azure.mgmt.vmwarecloudsimple.aio.operations

    class azure.mgmt.vmwarecloudsimple.aio.operations.CustomizationPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                region_id: str, 
                pc_name: str, 
                customization_policy_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CustomizationPolicy: ...

        @distributed_trace
        def list(
                self, 
                region_id: str, 
                pc_name: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[CustomizationPolicy]: ...


    class azure.mgmt.vmwarecloudsimple.aio.operations.DedicatedCloudNodesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                referer: str, 
                dedicated_cloud_node_name: str, 
                dedicated_cloud_node_request: DedicatedCloudNode, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedCloudNode]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                referer: str, 
                dedicated_cloud_node_name: str, 
                dedicated_cloud_node_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedCloudNode]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                dedicated_cloud_node_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dedicated_cloud_node_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DedicatedCloudNode: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[DedicatedCloudNode]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[DedicatedCloudNode]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                dedicated_cloud_node_name: str, 
                dedicated_cloud_node_request: PatchPayload, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedCloudNode: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                dedicated_cloud_node_name: str, 
                dedicated_cloud_node_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedCloudNode: ...


    class azure.mgmt.vmwarecloudsimple.aio.operations.DedicatedCloudServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                dedicated_cloud_service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                dedicated_cloud_service_name: str, 
                dedicated_cloud_service_request: DedicatedCloudService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedCloudService: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                dedicated_cloud_service_name: str, 
                dedicated_cloud_service_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedCloudService: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dedicated_cloud_service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DedicatedCloudService: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[DedicatedCloudService]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[DedicatedCloudService]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                dedicated_cloud_service_name: str, 
                dedicated_cloud_service_request: PatchPayload, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedCloudService: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                dedicated_cloud_service_name: str, 
                dedicated_cloud_service_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedCloudService: ...


    class azure.mgmt.vmwarecloudsimple.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                region_id: str, 
                referer: str, 
                operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Optional[OperationResource]: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AvailableOperation]: ...


    class azure.mgmt.vmwarecloudsimple.aio.operations.PrivateCloudsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                pc_name: str, 
                region_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrivateCloud: ...

        @distributed_trace
        def list(
                self, 
                region_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[PrivateCloud]: ...


    class azure.mgmt.vmwarecloudsimple.aio.operations.ResourcePoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                region_id: str, 
                pc_name: str, 
                resource_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ResourcePool: ...

        @distributed_trace
        def list(
                self, 
                region_id: str, 
                pc_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ResourcePool]: ...


    class azure.mgmt.vmwarecloudsimple.aio.operations.SkusAvailabilityOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                region_id: str, 
                sku_id: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SkuAvailability]: ...


    class azure.mgmt.vmwarecloudsimple.aio.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                region_id: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Usage]: ...


    class azure.mgmt.vmwarecloudsimple.aio.operations.VirtualMachineTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                region_id: str, 
                pc_name: str, 
                virtual_machine_template_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VirtualMachineTemplate: ...

        @distributed_trace
        def list(
                self, 
                pc_name: str, 
                region_id: str, 
                resource_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[VirtualMachineTemplate]: ...


    class azure.mgmt.vmwarecloudsimple.aio.operations.VirtualMachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                referer: str, 
                virtual_machine_name: str, 
                virtual_machine_request: VirtualMachine, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachine]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                referer: str, 
                virtual_machine_name: str, 
                virtual_machine_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachine]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                referer: str, 
                virtual_machine_name: str, 
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
                resource_group_name: str, 
                referer: str, 
                virtual_machine_name: str, 
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
                resource_group_name: str, 
                referer: str, 
                virtual_machine_name: str, 
                mode: Optional[Union[str, StopMode]] = None, 
                m: Optional[VirtualMachineStopMode] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_stop(
                self, 
                resource_group_name: str, 
                referer: str, 
                virtual_machine_name: str, 
                mode: Optional[Union[str, StopMode]] = None, 
                m: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_request: PatchPayload, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachine]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachine]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VirtualMachine: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[VirtualMachine]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[VirtualMachine]: ...


    class azure.mgmt.vmwarecloudsimple.aio.operations.VirtualNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                region_id: str, 
                pc_name: str, 
                virtual_network_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VirtualNetwork: ...

        @distributed_trace
        def list(
                self, 
                region_id: str, 
                pc_name: str, 
                resource_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[VirtualNetwork]: ...


namespace azure.mgmt.vmwarecloudsimple.models

    class azure.mgmt.vmwarecloudsimple.models.AggregationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "Average"
        TOTAL = "Total"


    class azure.mgmt.vmwarecloudsimple.models.AvailableOperation(Model):
        display: AvailableOperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, OperationOrigin]
        service_specification: AvailableOperationDisplayPropertyServiceSpecificationMetricsList

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display: Optional[AvailableOperationDisplay] = ..., 
                is_data_action: bool = False, 
                name: Optional[str] = ..., 
                origin: Optional[Union[str, OperationOrigin]] = ..., 
                service_specification: Optional[AvailableOperationDisplayPropertyServiceSpecificationMetricsList] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.AvailableOperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.AvailableOperationDisplayPropertyServiceSpecificationMetricsItem(Model):
        aggregation_type: Union[str, AggregationType]
        display_description: str
        display_name: str
        name: str
        unit: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                aggregation_type: Union[str, AggregationType], 
                display_description: str, 
                display_name: str, 
                name: str, 
                unit: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.AvailableOperationDisplayPropertyServiceSpecificationMetricsList(Model):
        metric_specifications: list[AvailableOperationDisplayPropertyServiceSpecificationMetricsItem]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                metric_specifications: Optional[List[AvailableOperationDisplayPropertyServiceSpecificationMetricsItem]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.AvailableOperationsListResponse(Model):
        next_link: str
        value: list[AvailableOperation]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[AvailableOperation]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.CSRPError(Model):
        error: CSRPErrorBody

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[CSRPErrorBody] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.CSRPErrorBody(Model):
        code: str
        details: list[CSRPErrorBody]
        message: str
        target: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                target: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.CustomizationHostName(Model):
        name: str
        type: Union[str, CustomizationHostNameType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[Union[str, CustomizationHostNameType]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.CustomizationHostNameType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_NAME = "CUSTOM_NAME"
        FIXED = "FIXED"
        PREFIX_BASED = "PREFIX_BASED"
        USER_DEFINED = "USER_DEFINED"
        VIRTUAL_MACHINE_NAME = "VIRTUAL_MACHINE_NAME"


    class azure.mgmt.vmwarecloudsimple.models.CustomizationIPAddress(Model):
        argument: str
        ip_address: str
        type: Union[str, CustomizationIPAddressType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                argument: Optional[str] = ..., 
                ip_address: Optional[str] = ..., 
                type: Optional[Union[str, CustomizationIPAddressType]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.CustomizationIPAddressType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "CUSTOM"
        DHCP_IP = "DHCP_IP"
        FIXED_IP = "FIXED_IP"
        USER_DEFINED = "USER_DEFINED"


    class azure.mgmt.vmwarecloudsimple.models.CustomizationIPSettings(Model):
        gateway: list[str]
        ip: CustomizationIPAddress
        subnet_mask: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                gateway: Optional[List[str]] = ..., 
                ip: Optional[CustomizationIPAddress] = ..., 
                subnet_mask: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.CustomizationIdentity(Model):
        data: str
        host_name: CustomizationHostName
        type: Union[str, CustomizationIdentityType]
        user_data: CustomizationIdentityUserData

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                data: Optional[str] = ..., 
                host_name: Optional[CustomizationHostName] = ..., 
                type: Optional[Union[str, CustomizationIdentityType]] = ..., 
                user_data: Optional[CustomizationIdentityUserData] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.CustomizationIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "LINUX"
        WINDOWS = "WINDOWS"
        WINDOWS_TEXT = "WINDOWS_TEXT"


    class azure.mgmt.vmwarecloudsimple.models.CustomizationIdentityUserData(Model):
        is_password_predefined: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                is_password_predefined: bool = False, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.CustomizationNicSetting(Model):
        adapter: CustomizationIPSettings
        mac_address: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                adapter: Optional[CustomizationIPSettings] = ..., 
                mac_address: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.CustomizationPoliciesListResponse(Model):
        next_link: str
        value: list[CustomizationPolicy]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[CustomizationPolicy]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.CustomizationPolicy(Model):
        description: str
        id: str
        location: str
        name: str
        private_cloud_id: str
        specification: CustomizationSpecification
        type: str
        type_properties_type: Union[str, CustomizationPolicyPropertiesType]
        version: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                private_cloud_id: Optional[str] = ..., 
                specification: Optional[CustomizationSpecification] = ..., 
                type_properties_type: Optional[Union[str, CustomizationPolicyPropertiesType]] = ..., 
                version: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.CustomizationPolicyPropertiesType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "LINUX"
        WINDOWS = "WINDOWS"


    class azure.mgmt.vmwarecloudsimple.models.CustomizationSpecification(Model):
        identity: CustomizationIdentity
        nic_settings: list[CustomizationNicSetting]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                identity: Optional[CustomizationIdentity] = ..., 
                nic_settings: Optional[List[CustomizationNicSetting]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.DedicatedCloudNode(Model):
        availability_zone_id: str
        availability_zone_name: str
        cloud_rack_name: str
        created: datetime
        id: str
        id_properties_sku_description_id: str
        location: str
        name: str
        name_properties_sku_description_name: str
        nodes_count: int
        placement_group_id: str
        placement_group_name: str
        private_cloud_id: str
        private_cloud_name: str
        provisioning_state: str
        purchase_id: str
        sku: Sku
        status: Union[str, NodeStatus]
        tags: dict[str, str]
        type: str
        vmware_cluster_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                availability_zone_id: Optional[str] = ..., 
                id_properties_sku_description_id: Optional[str] = ..., 
                location: str, 
                name_properties_sku_description_name: Optional[str] = ..., 
                nodes_count: Optional[int] = ..., 
                placement_group_id: Optional[str] = ..., 
                purchase_id: Optional[str] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.DedicatedCloudNodeListResponse(Model):
        next_link: str
        value: list[DedicatedCloudNode]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[DedicatedCloudNode]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.DedicatedCloudService(Model):
        gateway_subnet: str
        id: str
        is_account_onboarded: Union[str, OnboardingStatus]
        location: str
        name: str
        nodes: int
        service_url: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                gateway_subnet: Optional[str] = ..., 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.DedicatedCloudServiceListResponse(Model):
        next_link: str
        value: list[DedicatedCloudService]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[DedicatedCloudService]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.DiskIndependenceMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INDEPENDENT_NONPERSISTENT = "independent_nonpersistent"
        INDEPENDENT_PERSISTENT = "independent_persistent"
        PERSISTENT = "persistent"


    class azure.mgmt.vmwarecloudsimple.models.GuestOSCustomization(Model):
        dns_servers: list[str]
        host_name: str
        password: str
        policy_id: str
        username: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                dns_servers: Optional[List[str]] = ..., 
                host_name: Optional[str] = ..., 
                password: Optional[str] = ..., 
                policy_id: Optional[str] = ..., 
                username: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.GuestOSNICCustomization(Model):
        allocation: Union[str, GuestOSNICCustomizationAllocation]
        dns_servers: list[str]
        gateway: list[str]
        ip_address: str
        mask: str
        primary_wins_server: str
        secondary_wins_server: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                allocation: Optional[Union[str, GuestOSNICCustomizationAllocation]] = ..., 
                dns_servers: Optional[List[str]] = ..., 
                gateway: Optional[List[str]] = ..., 
                ip_address: Optional[str] = ..., 
                mask: Optional[str] = ..., 
                primary_wins_server: Optional[str] = ..., 
                secondary_wins_server: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.GuestOSNICCustomizationAllocation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DYNAMIC = "dynamic"
        STATIC = "static"


    class azure.mgmt.vmwarecloudsimple.models.GuestOSType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "linux"
        OTHER = "other"
        WINDOWS = "windows"


    class azure.mgmt.vmwarecloudsimple.models.NICType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        E1000 = "E1000"
        E1000_E = "E1000E"
        PCNET32 = "PCNET32"
        VMXNET = "VMXNET"
        VMXNET2 = "VMXNET2"
        VMXNET3 = "VMXNET3"


    class azure.mgmt.vmwarecloudsimple.models.NodeStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        UNUSED = "unused"
        USED = "used"


    class azure.mgmt.vmwarecloudsimple.models.OnboardingStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_ON_BOARDED = "notOnBoarded"
        ON_BOARDED = "onBoarded"
        ON_BOARDING = "onBoarding"
        ON_BOARDING_FAILED = "onBoardingFailed"


    class azure.mgmt.vmwarecloudsimple.models.OperationError(Model):
        code: str
        message: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.OperationOrigin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.vmwarecloudsimple.models.OperationResource(Model):
        end_time: datetime
        error: OperationError
        id: str
        name: str
        start_time: datetime
        status: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[OperationError] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.PatchPayload(Model):
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.PrivateCloud(Model):
        availability_zone_id: str
        availability_zone_name: str
        clusters_number: int
        created_by: str
        created_on: datetime
        dns_servers: list[str]
        expires: str
        id: str
        location: str
        name: str
        nsx_type: str
        placement_group_id: str
        placement_group_name: str
        private_cloud_id: str
        resource_pools: list[ResourcePool]
        state: str
        total_cpu_cores: int
        total_nodes: int
        total_ram: int
        total_storage: float
        type: str
        type_properties_type: str
        v_sphere_version: str
        vcenter_fqdn: str
        vcenter_refid: str
        virtual_machine_templates: list[VirtualMachineTemplate]
        virtual_networks: list[VirtualNetwork]
        vr_ops_enabled: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                availability_zone_id: Optional[str] = ..., 
                availability_zone_name: Optional[str] = ..., 
                clusters_number: Optional[int] = ..., 
                created_by: Optional[str] = ..., 
                created_on: Optional[datetime] = ..., 
                dns_servers: Optional[List[str]] = ..., 
                expires: Optional[str] = ..., 
                id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                nsx_type: Optional[str] = ..., 
                placement_group_id: Optional[str] = ..., 
                placement_group_name: Optional[str] = ..., 
                private_cloud_id: Optional[str] = ..., 
                resource_pools: Optional[List[ResourcePool]] = ..., 
                state: Optional[str] = ..., 
                total_cpu_cores: Optional[int] = ..., 
                total_nodes: Optional[int] = ..., 
                total_ram: Optional[int] = ..., 
                total_storage: Optional[float] = ..., 
                type: Optional[Literal[VMwareCloudSimple/privateClouds]] = ..., 
                type_properties_type: Optional[str] = ..., 
                v_sphere_version: Optional[str] = ..., 
                vcenter_fqdn: Optional[str] = ..., 
                vcenter_refid: Optional[str] = ..., 
                virtual_machine_templates: Optional[List[VirtualMachineTemplate]] = ..., 
                virtual_networks: Optional[List[VirtualNetwork]] = ..., 
                vr_ops_enabled: Optional[bool] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.PrivateCloudList(Model):
        next_link: str
        value: list[PrivateCloud]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[PrivateCloud]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.ResourcePool(Model):
        full_name: str
        id: str
        location: str
        name: str
        private_cloud_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.ResourcePoolsListResponse(Model):
        next_link: str
        value: list[ResourcePool]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ResourcePool]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.Sku(Model):
        capacity: str
        description: str
        family: str
        name: str
        tier: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                capacity: Optional[str] = ..., 
                description: Optional[str] = ..., 
                family: Optional[str] = ..., 
                name: str, 
                tier: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.SkuAvailability(Model):
        dedicated_availability_zone_id: str
        dedicated_availability_zone_name: str
        dedicated_placement_group_id: str
        dedicated_placement_group_name: str
        limit: int
        resource_type: str
        sku_id: str
        sku_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                dedicated_availability_zone_id: Optional[str] = ..., 
                dedicated_availability_zone_name: Optional[str] = ..., 
                dedicated_placement_group_id: Optional[str] = ..., 
                dedicated_placement_group_name: Optional[str] = ..., 
                limit: int, 
                resource_type: Optional[str] = ..., 
                sku_id: Optional[str] = ..., 
                sku_name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.SkuAvailabilityListResponse(Model):
        next_link: str
        value: list[SkuAvailability]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SkuAvailability]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.StopMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        POWEROFF = "poweroff"
        REBOOT = "reboot"
        SHUTDOWN = "shutdown"
        SUSPEND = "suspend"


    class azure.mgmt.vmwarecloudsimple.models.Usage(Model):
        current_value: int
        limit: int
        name: UsageName
        unit: Union[str, UsageCount]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                current_value: int = 0, 
                limit: int = 0, 
                name: Optional[UsageName] = ..., 
                unit: Optional[Union[str, UsageCount]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.UsageCount(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BYTES = "Bytes"
        BYTES_PER_SECOND = "BytesPerSecond"
        COUNT = "Count"
        COUNT_PER_SECOND = "CountPerSecond"
        PERCENT = "Percent"
        SECONDS = "Seconds"


    class azure.mgmt.vmwarecloudsimple.models.UsageListResponse(Model):
        next_link: str
        value: list[Usage]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.UsageName(Model):
        localized_value: str
        value: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                localized_value: Optional[str] = ..., 
                value: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.VirtualDisk(Model):
        controller_id: str
        independence_mode: Union[str, DiskIndependenceMode]
        total_size: int
        virtual_disk_id: str
        virtual_disk_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                controller_id: str, 
                independence_mode: Union[str, DiskIndependenceMode], 
                total_size: int, 
                virtual_disk_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.VirtualDiskController(Model):
        id: str
        name: str
        sub_type: str
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.VirtualMachine(Model):
        amount_of_ram: int
        controllers: list[VirtualDiskController]
        customization: GuestOSCustomization
        disks: list[VirtualDisk]
        dnsname: str
        expose_to_guest_vm: bool
        folder: str
        guest_os: str
        guest_os_type: Union[str, GuestOSType]
        id: str
        location: str
        name: str
        nics: list[VirtualNic]
        number_of_cores: int
        password: str
        private_cloud_id: str
        provisioning_state: str
        public_ip: str
        resource_pool: ResourcePool
        status: Union[str, VirtualMachineStatus]
        tags: dict[str, str]
        template_id: str
        type: str
        username: str
        v_sphere_networks: list[str]
        vm_id: str
        vmwaretools: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                amount_of_ram: Optional[int] = ..., 
                customization: Optional[GuestOSCustomization] = ..., 
                disks: Optional[List[VirtualDisk]] = ..., 
                expose_to_guest_vm: Optional[bool] = ..., 
                location: str, 
                nics: Optional[List[VirtualNic]] = ..., 
                number_of_cores: Optional[int] = ..., 
                password: Optional[str] = ..., 
                private_cloud_id: Optional[str] = ..., 
                resource_pool: Optional[ResourcePool] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                template_id: Optional[str] = ..., 
                username: Optional[str] = ..., 
                v_sphere_networks: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.VirtualMachineListResponse(Model):
        next_link: str
        value: list[VirtualMachine]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[VirtualMachine]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.VirtualMachineStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEALLOCATING = "deallocating"
        DELETING = "deleting"
        POWEREDOFF = "poweredoff"
        RUNNING = "running"
        SUSPENDED = "suspended"
        UPDATING = "updating"


    class azure.mgmt.vmwarecloudsimple.models.VirtualMachineStopMode(Model):
        mode: Union[str, StopMode]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, StopMode]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.VirtualMachineTemplate(Model):
        amount_of_ram: int
        controllers: list[VirtualDiskController]
        description: str
        disks: list[VirtualDisk]
        expose_to_guest_vm: bool
        guest_os: str
        guest_os_type: str
        id: str
        location: str
        name: str
        nics: list[VirtualNic]
        number_of_cores: int
        path: str
        private_cloud_id: str
        type: str
        v_sphere_networks: list[str]
        v_sphere_tags: list[str]
        vmwaretools: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                amount_of_ram: Optional[int] = ..., 
                controllers: Optional[List[VirtualDiskController]] = ..., 
                description: Optional[str] = ..., 
                disks: Optional[List[VirtualDisk]] = ..., 
                expose_to_guest_vm: Optional[bool] = ..., 
                location: Optional[str] = ..., 
                nics: Optional[List[VirtualNic]] = ..., 
                number_of_cores: Optional[int] = ..., 
                path: Optional[str] = ..., 
                private_cloud_id: Optional[str] = ..., 
                v_sphere_networks: Optional[List[str]] = ..., 
                v_sphere_tags: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.VirtualMachineTemplateListResponse(Model):
        next_link: str
        value: list[VirtualMachineTemplate]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[VirtualMachineTemplate]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.VirtualNetwork(Model):
        assignable: bool
        id: str
        location: str
        name: str
        private_cloud_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.VirtualNetworkListResponse(Model):
        next_link: str
        value: list[VirtualNetwork]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[VirtualNetwork]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.vmwarecloudsimple.models.VirtualNic(Model):
        customization: GuestOSNICCustomization
        ip_addresses: list[str]
        mac_address: str
        network: VirtualNetwork
        nic_type: Union[str, NICType]
        power_on_boot: bool
        virtual_nic_id: str
        virtual_nic_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                customization: Optional[GuestOSNICCustomization] = ..., 
                ip_addresses: Optional[List[str]] = ..., 
                mac_address: Optional[str] = ..., 
                network: VirtualNetwork, 
                nic_type: Union[str, NICType], 
                power_on_boot: Optional[bool] = ..., 
                virtual_nic_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


namespace azure.mgmt.vmwarecloudsimple.operations

    class azure.mgmt.vmwarecloudsimple.operations.CustomizationPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                region_id: str, 
                pc_name: str, 
                customization_policy_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CustomizationPolicy: ...

        @distributed_trace
        def list(
                self, 
                region_id: str, 
                pc_name: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[CustomizationPolicy]: ...


    class azure.mgmt.vmwarecloudsimple.operations.DedicatedCloudNodesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                referer: str, 
                dedicated_cloud_node_name: str, 
                dedicated_cloud_node_request: DedicatedCloudNode, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedCloudNode]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                referer: str, 
                dedicated_cloud_node_name: str, 
                dedicated_cloud_node_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedCloudNode]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                dedicated_cloud_node_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dedicated_cloud_node_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DedicatedCloudNode: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[DedicatedCloudNode]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[DedicatedCloudNode]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                dedicated_cloud_node_name: str, 
                dedicated_cloud_node_request: PatchPayload, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedCloudNode: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                dedicated_cloud_node_name: str, 
                dedicated_cloud_node_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedCloudNode: ...


    class azure.mgmt.vmwarecloudsimple.operations.DedicatedCloudServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                dedicated_cloud_service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                dedicated_cloud_service_name: str, 
                dedicated_cloud_service_request: DedicatedCloudService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedCloudService: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                dedicated_cloud_service_name: str, 
                dedicated_cloud_service_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedCloudService: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dedicated_cloud_service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> DedicatedCloudService: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[DedicatedCloudService]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[DedicatedCloudService]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                dedicated_cloud_service_name: str, 
                dedicated_cloud_service_request: PatchPayload, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedCloudService: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                dedicated_cloud_service_name: str, 
                dedicated_cloud_service_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedCloudService: ...


    class azure.mgmt.vmwarecloudsimple.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                region_id: str, 
                referer: str, 
                operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Optional[OperationResource]: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AvailableOperation]: ...


    class azure.mgmt.vmwarecloudsimple.operations.PrivateCloudsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                pc_name: str, 
                region_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PrivateCloud: ...

        @distributed_trace
        def list(
                self, 
                region_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[PrivateCloud]: ...


    class azure.mgmt.vmwarecloudsimple.operations.ResourcePoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                region_id: str, 
                pc_name: str, 
                resource_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ResourcePool: ...

        @distributed_trace
        def list(
                self, 
                region_id: str, 
                pc_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ResourcePool]: ...


    class azure.mgmt.vmwarecloudsimple.operations.SkusAvailabilityOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                region_id: str, 
                sku_id: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SkuAvailability]: ...


    class azure.mgmt.vmwarecloudsimple.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                region_id: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Usage]: ...


    class azure.mgmt.vmwarecloudsimple.operations.VirtualMachineTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                region_id: str, 
                pc_name: str, 
                virtual_machine_template_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VirtualMachineTemplate: ...

        @distributed_trace
        def list(
                self, 
                pc_name: str, 
                region_id: str, 
                resource_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[VirtualMachineTemplate]: ...


    class azure.mgmt.vmwarecloudsimple.operations.VirtualMachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                referer: str, 
                virtual_machine_name: str, 
                virtual_machine_request: VirtualMachine, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachine]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                referer: str, 
                virtual_machine_name: str, 
                virtual_machine_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachine]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                referer: str, 
                virtual_machine_name: str, 
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
                resource_group_name: str, 
                referer: str, 
                virtual_machine_name: str, 
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
                resource_group_name: str, 
                referer: str, 
                virtual_machine_name: str, 
                mode: Optional[Union[str, StopMode]] = None, 
                m: Optional[VirtualMachineStopMode] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_stop(
                self, 
                resource_group_name: str, 
                referer: str, 
                virtual_machine_name: str, 
                mode: Optional[Union[str, StopMode]] = None, 
                m: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_request: PatchPayload, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachine]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachine]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VirtualMachine: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[VirtualMachine]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skip_token: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[VirtualMachine]: ...


    class azure.mgmt.vmwarecloudsimple.operations.VirtualNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                region_id: str, 
                pc_name: str, 
                virtual_network_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VirtualNetwork: ...

        @distributed_trace
        def list(
                self, 
                region_id: str, 
                pc_name: str, 
                resource_pool_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[VirtualNetwork]: ...


```