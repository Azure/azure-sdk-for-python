```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.standbypool

    class azure.mgmt.standbypool.StandbyPoolMgmtClient: implements ContextManager 
        operations: Operations
        standby_container_group_pool_runtime_views: StandbyContainerGroupPoolRuntimeViewsOperations
        standby_container_group_pools: StandbyContainerGroupPoolsOperations
        standby_virtual_machine_pool_runtime_views: StandbyVirtualMachinePoolRuntimeViewsOperations
        standby_virtual_machine_pools: StandbyVirtualMachinePoolsOperations
        standby_virtual_machines: StandbyVirtualMachinesOperations

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


namespace azure.mgmt.standbypool.aio

    class azure.mgmt.standbypool.aio.StandbyPoolMgmtClient: implements AsyncContextManager 
        operations: Operations
        standby_container_group_pool_runtime_views: StandbyContainerGroupPoolRuntimeViewsOperations
        standby_container_group_pools: StandbyContainerGroupPoolsOperations
        standby_virtual_machine_pool_runtime_views: StandbyVirtualMachinePoolRuntimeViewsOperations
        standby_virtual_machine_pools: StandbyVirtualMachinePoolsOperations
        standby_virtual_machines: StandbyVirtualMachinesOperations

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


namespace azure.mgmt.standbypool.aio.operations

    class azure.mgmt.standbypool.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.standbypool.aio.operations.StandbyContainerGroupPoolRuntimeViewsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-03-01-preview', params_added_on={'2024-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'standby_container_group_pool_name', 'runtime_view', 'accept']}, api_versions_list=['2024-03-01-preview', '2024-03-01', '2025-03-01', '2025-10-01'])
        async def get(
                self, 
                resource_group_name: str, 
                standby_container_group_pool_name: str, 
                runtime_view: str, 
                **kwargs: Any
            ) -> StandbyContainerGroupPoolRuntimeViewResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-03-01-preview', params_added_on={'2024-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'standby_container_group_pool_name', 'accept']}, api_versions_list=['2024-03-01-preview', '2024-03-01', '2025-03-01', '2025-10-01'])
        def list_by_standby_pool(
                self, 
                resource_group_name: str, 
                standby_container_group_pool_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StandbyContainerGroupPoolRuntimeViewResource]: ...


    class azure.mgmt.standbypool.aio.operations.StandbyContainerGroupPoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                standby_container_group_pool_name: str, 
                resource: StandbyContainerGroupPoolResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StandbyContainerGroupPoolResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                standby_container_group_pool_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StandbyContainerGroupPoolResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                standby_container_group_pool_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StandbyContainerGroupPoolResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                standby_container_group_pool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                standby_container_group_pool_name: str, 
                **kwargs: Any
            ) -> StandbyContainerGroupPoolResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StandbyContainerGroupPoolResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[StandbyContainerGroupPoolResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                standby_container_group_pool_name: str, 
                properties: StandbyContainerGroupPoolResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StandbyContainerGroupPoolResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                standby_container_group_pool_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StandbyContainerGroupPoolResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                standby_container_group_pool_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StandbyContainerGroupPoolResource: ...


    class azure.mgmt.standbypool.aio.operations.StandbyVirtualMachinePoolRuntimeViewsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-03-01-preview', params_added_on={'2024-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'standby_virtual_machine_pool_name', 'runtime_view', 'accept']}, api_versions_list=['2024-03-01-preview', '2024-03-01', '2025-03-01', '2025-10-01'])
        async def get(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                runtime_view: str, 
                **kwargs: Any
            ) -> StandbyVirtualMachinePoolRuntimeViewResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-03-01-preview', params_added_on={'2024-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'standby_virtual_machine_pool_name', 'accept']}, api_versions_list=['2024-03-01-preview', '2024-03-01', '2025-03-01', '2025-10-01'])
        def list_by_standby_pool(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StandbyVirtualMachinePoolRuntimeViewResource]: ...


    class azure.mgmt.standbypool.aio.operations.StandbyVirtualMachinePoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                resource: StandbyVirtualMachinePoolResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StandbyVirtualMachinePoolResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StandbyVirtualMachinePoolResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StandbyVirtualMachinePoolResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                **kwargs: Any
            ) -> StandbyVirtualMachinePoolResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StandbyVirtualMachinePoolResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[StandbyVirtualMachinePoolResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                properties: StandbyVirtualMachinePoolResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StandbyVirtualMachinePoolResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StandbyVirtualMachinePoolResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StandbyVirtualMachinePoolResource: ...


    class azure.mgmt.standbypool.aio.operations.StandbyVirtualMachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                standby_virtual_machine_name: str, 
                **kwargs: Any
            ) -> StandbyVirtualMachineResource: ...

        @distributed_trace
        def list_by_standby_virtual_machine_pool_resource(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StandbyVirtualMachineResource]: ...


namespace azure.mgmt.standbypool.models

    class azure.mgmt.standbypool.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.standbypool.models.ContainerGroupInstanceCountSummary(_Model):
        instance_counts_by_state: list[PoolContainerGroupStateCount]
        zone: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                instance_counts_by_state: list[PoolContainerGroupStateCount], 
                zone: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.standbypool.models.ContainerGroupProfile(_Model):
        id: str
        revision: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                revision: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.standbypool.models.ContainerGroupProperties(_Model):
        container_group_profile: ContainerGroupProfile
        subnet_ids: Optional[list[Subnet]]

        @overload
        def __init__(
                self, 
                *, 
                container_group_profile: ContainerGroupProfile, 
                subnet_ids: Optional[list[Subnet]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.standbypool.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.standbypool.models.DynamicSizing(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.standbypool.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.standbypool.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.standbypool.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.standbypool.models.HealthStateCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEGRADED = "HealthState/degraded"
        HEALTHY = "HealthState/healthy"


    class azure.mgmt.standbypool.models.Operation(_Model):
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


    class azure.mgmt.standbypool.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.standbypool.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.standbypool.models.PoolContainerGroupState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        RUNNING = "Running"


    class azure.mgmt.standbypool.models.PoolContainerGroupStateCount(_Model):
        count: int
        state: Union[str, PoolContainerGroupState]

        @overload
        def __init__(
                self, 
                *, 
                count: int, 
                state: Union[str, PoolContainerGroupState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.standbypool.models.PoolStatus(_Model):
        code: Union[str, HealthStateCode]
        message: Optional[str]


    class azure.mgmt.standbypool.models.PoolVirtualMachineState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DEALLOCATED = "Deallocated"
        DEALLOCATING = "Deallocating"
        DELETING = "Deleting"
        HIBERNATED = "Hibernated"
        HIBERNATING = "Hibernating"
        RUNNING = "Running"
        STARTING = "Starting"


    class azure.mgmt.standbypool.models.PoolVirtualMachineStateCount(_Model):
        count: int
        state: Union[str, PoolVirtualMachineState]

        @overload
        def __init__(
                self, 
                *, 
                count: int, 
                state: Union[str, PoolVirtualMachineState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.standbypool.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.standbypool.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.standbypool.models.RefillPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "always"


    class azure.mgmt.standbypool.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.standbypool.models.StandbyContainerGroupPoolElasticityProfile(_Model):
        dynamic_sizing: Optional[DynamicSizing]
        max_ready_capacity: int
        refill_policy: Optional[Union[str, RefillPolicy]]

        @overload
        def __init__(
                self, 
                *, 
                dynamic_sizing: Optional[DynamicSizing] = ..., 
                max_ready_capacity: int, 
                refill_policy: Optional[Union[str, RefillPolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.standbypool.models.StandbyContainerGroupPoolForecastValues(_Model):
        instances_requested_count: list[int]


    class azure.mgmt.standbypool.models.StandbyContainerGroupPoolPrediction(_Model):
        forecast_info: str
        forecast_start_time: datetime
        forecast_values: StandbyContainerGroupPoolForecastValues


    class azure.mgmt.standbypool.models.StandbyContainerGroupPoolResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[StandbyContainerGroupPoolResourceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[StandbyContainerGroupPoolResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.standbypool.models.StandbyContainerGroupPoolResourceProperties(_Model):
        container_group_properties: ContainerGroupProperties
        elasticity_profile: StandbyContainerGroupPoolElasticityProfile
        provisioning_state: Optional[Union[str, ProvisioningState]]
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                container_group_properties: ContainerGroupProperties, 
                elasticity_profile: StandbyContainerGroupPoolElasticityProfile, 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.standbypool.models.StandbyContainerGroupPoolResourceUpdate(_Model):
        properties: Optional[StandbyContainerGroupPoolResourceUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StandbyContainerGroupPoolResourceUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.standbypool.models.StandbyContainerGroupPoolResourceUpdateProperties(_Model):
        container_group_properties: Optional[ContainerGroupProperties]
        elasticity_profile: Optional[StandbyContainerGroupPoolElasticityProfile]
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                container_group_properties: Optional[ContainerGroupProperties] = ..., 
                elasticity_profile: Optional[StandbyContainerGroupPoolElasticityProfile] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.standbypool.models.StandbyContainerGroupPoolRuntimeViewResource(ProxyResource):
        id: str
        name: str
        properties: Optional[StandbyContainerGroupPoolRuntimeViewResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StandbyContainerGroupPoolRuntimeViewResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.standbypool.models.StandbyContainerGroupPoolRuntimeViewResourceProperties(_Model):
        instance_count_summary: list[ContainerGroupInstanceCountSummary]
        prediction: Optional[StandbyContainerGroupPoolPrediction]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: Optional[PoolStatus]


    class azure.mgmt.standbypool.models.StandbyVirtualMachinePoolElasticityProfile(_Model):
        dynamic_sizing: Optional[DynamicSizing]
        max_ready_capacity: int
        min_ready_capacity: Optional[int]
        post_provisioning_delay: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                dynamic_sizing: Optional[DynamicSizing] = ..., 
                max_ready_capacity: int, 
                min_ready_capacity: Optional[int] = ..., 
                post_provisioning_delay: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.standbypool.models.StandbyVirtualMachinePoolForecastValues(_Model):
        instances_requested_count: list[int]


    class azure.mgmt.standbypool.models.StandbyVirtualMachinePoolPrediction(_Model):
        forecast_info: str
        forecast_start_time: datetime
        forecast_values: StandbyVirtualMachinePoolForecastValues


    class azure.mgmt.standbypool.models.StandbyVirtualMachinePoolResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[StandbyVirtualMachinePoolResourceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[StandbyVirtualMachinePoolResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.standbypool.models.StandbyVirtualMachinePoolResourceProperties(_Model):
        attached_virtual_machine_scale_set_id: Optional[str]
        elasticity_profile: Optional[StandbyVirtualMachinePoolElasticityProfile]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        virtual_machine_state: Union[str, VirtualMachineState]

        @overload
        def __init__(
                self, 
                *, 
                attached_virtual_machine_scale_set_id: Optional[str] = ..., 
                elasticity_profile: Optional[StandbyVirtualMachinePoolElasticityProfile] = ..., 
                virtual_machine_state: Union[str, VirtualMachineState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.standbypool.models.StandbyVirtualMachinePoolResourceUpdate(_Model):
        properties: Optional[StandbyVirtualMachinePoolResourceUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StandbyVirtualMachinePoolResourceUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.standbypool.models.StandbyVirtualMachinePoolResourceUpdateProperties(_Model):
        attached_virtual_machine_scale_set_id: Optional[str]
        elasticity_profile: Optional[StandbyVirtualMachinePoolElasticityProfile]
        virtual_machine_state: Optional[Union[str, VirtualMachineState]]

        @overload
        def __init__(
                self, 
                *, 
                attached_virtual_machine_scale_set_id: Optional[str] = ..., 
                elasticity_profile: Optional[StandbyVirtualMachinePoolElasticityProfile] = ..., 
                virtual_machine_state: Optional[Union[str, VirtualMachineState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.standbypool.models.StandbyVirtualMachinePoolRuntimeViewResource(ProxyResource):
        id: str
        name: str
        properties: Optional[StandbyVirtualMachinePoolRuntimeViewResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StandbyVirtualMachinePoolRuntimeViewResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.standbypool.models.StandbyVirtualMachinePoolRuntimeViewResourceProperties(_Model):
        instance_count_summary: list[VirtualMachineInstanceCountSummary]
        prediction: Optional[StandbyVirtualMachinePoolPrediction]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: Optional[PoolStatus]


    class azure.mgmt.standbypool.models.StandbyVirtualMachineResource(ProxyResource):
        id: str
        name: str
        properties: Optional[StandbyVirtualMachineResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StandbyVirtualMachineResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.standbypool.models.StandbyVirtualMachineResourceProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        virtual_machine_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                virtual_machine_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.standbypool.models.Subnet(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.standbypool.models.SystemData(_Model):
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


    class azure.mgmt.standbypool.models.TrackedResource(Resource):
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


    class azure.mgmt.standbypool.models.VirtualMachineInstanceCountSummary(_Model):
        instance_counts_by_state: list[PoolVirtualMachineStateCount]
        zone: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                instance_counts_by_state: list[PoolVirtualMachineStateCount], 
                zone: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.standbypool.models.VirtualMachineState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEALLOCATED = "Deallocated"
        HIBERNATED = "Hibernated"
        RUNNING = "Running"


namespace azure.mgmt.standbypool.operations

    class azure.mgmt.standbypool.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.standbypool.operations.StandbyContainerGroupPoolRuntimeViewsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-03-01-preview', params_added_on={'2024-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'standby_container_group_pool_name', 'runtime_view', 'accept']}, api_versions_list=['2024-03-01-preview', '2024-03-01', '2025-03-01', '2025-10-01'])
        def get(
                self, 
                resource_group_name: str, 
                standby_container_group_pool_name: str, 
                runtime_view: str, 
                **kwargs: Any
            ) -> StandbyContainerGroupPoolRuntimeViewResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-03-01-preview', params_added_on={'2024-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'standby_container_group_pool_name', 'accept']}, api_versions_list=['2024-03-01-preview', '2024-03-01', '2025-03-01', '2025-10-01'])
        def list_by_standby_pool(
                self, 
                resource_group_name: str, 
                standby_container_group_pool_name: str, 
                **kwargs: Any
            ) -> ItemPaged[StandbyContainerGroupPoolRuntimeViewResource]: ...


    class azure.mgmt.standbypool.operations.StandbyContainerGroupPoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                standby_container_group_pool_name: str, 
                resource: StandbyContainerGroupPoolResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StandbyContainerGroupPoolResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                standby_container_group_pool_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StandbyContainerGroupPoolResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                standby_container_group_pool_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StandbyContainerGroupPoolResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                standby_container_group_pool_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                standby_container_group_pool_name: str, 
                **kwargs: Any
            ) -> StandbyContainerGroupPoolResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[StandbyContainerGroupPoolResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[StandbyContainerGroupPoolResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                standby_container_group_pool_name: str, 
                properties: StandbyContainerGroupPoolResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StandbyContainerGroupPoolResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                standby_container_group_pool_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StandbyContainerGroupPoolResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                standby_container_group_pool_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StandbyContainerGroupPoolResource: ...


    class azure.mgmt.standbypool.operations.StandbyVirtualMachinePoolRuntimeViewsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-03-01-preview', params_added_on={'2024-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'standby_virtual_machine_pool_name', 'runtime_view', 'accept']}, api_versions_list=['2024-03-01-preview', '2024-03-01', '2025-03-01', '2025-10-01'])
        def get(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                runtime_view: str, 
                **kwargs: Any
            ) -> StandbyVirtualMachinePoolRuntimeViewResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-03-01-preview', params_added_on={'2024-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'standby_virtual_machine_pool_name', 'accept']}, api_versions_list=['2024-03-01-preview', '2024-03-01', '2025-03-01', '2025-10-01'])
        def list_by_standby_pool(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                **kwargs: Any
            ) -> ItemPaged[StandbyVirtualMachinePoolRuntimeViewResource]: ...


    class azure.mgmt.standbypool.operations.StandbyVirtualMachinePoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                resource: StandbyVirtualMachinePoolResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StandbyVirtualMachinePoolResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StandbyVirtualMachinePoolResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StandbyVirtualMachinePoolResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                **kwargs: Any
            ) -> StandbyVirtualMachinePoolResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[StandbyVirtualMachinePoolResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[StandbyVirtualMachinePoolResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                properties: StandbyVirtualMachinePoolResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StandbyVirtualMachinePoolResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StandbyVirtualMachinePoolResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StandbyVirtualMachinePoolResource: ...


    class azure.mgmt.standbypool.operations.StandbyVirtualMachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                standby_virtual_machine_name: str, 
                **kwargs: Any
            ) -> StandbyVirtualMachineResource: ...

        @distributed_trace
        def list_by_standby_virtual_machine_pool_resource(
                self, 
                resource_group_name: str, 
                standby_virtual_machine_pool_name: str, 
                **kwargs: Any
            ) -> ItemPaged[StandbyVirtualMachineResource]: ...


```