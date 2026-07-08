```py
namespace azure.mgmt.powerbidedicated

    class azure.mgmt.powerbidedicated.PowerBIDedicatedMgmtClient: implements ContextManager 
        auto_scale_vcores: AutoScaleVCoresOperations
        capacities: CapacitiesOperations
        operations: Operations

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


namespace azure.mgmt.powerbidedicated.aio

    class azure.mgmt.powerbidedicated.aio.PowerBIDedicatedMgmtClient: implements AsyncContextManager 
        auto_scale_vcores: AutoScaleVCoresOperations
        capacities: CapacitiesOperations
        operations: Operations

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


namespace azure.mgmt.powerbidedicated.aio.operations

    class azure.mgmt.powerbidedicated.aio.operations.AutoScaleVCoresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                v_core_parameters: AutoScaleVCore, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoScaleVCore: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                v_core_parameters: AutoScaleVCore, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoScaleVCore: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                v_core_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoScaleVCore: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                **kwargs: Any
            ) -> AutoScaleVCore: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AutoScaleVCore]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[AutoScaleVCore]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                v_core_update_parameters: AutoScaleVCoreUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoScaleVCore: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                v_core_update_parameters: AutoScaleVCoreUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoScaleVCore: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                v_core_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoScaleVCore: ...


    class azure.mgmt.powerbidedicated.aio.operations.CapacitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                capacity_parameters: DedicatedCapacity, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedCapacity]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                capacity_parameters: DedicatedCapacity, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedCapacity]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                capacity_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedCapacity]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_resume(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_suspend(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                capacity_update_parameters: DedicatedCapacityUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedCapacity]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                capacity_update_parameters: DedicatedCapacityUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedCapacity]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                capacity_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedCapacity]: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                capacity_parameters: CheckCapacityNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckCapacityNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                capacity_parameters: CheckCapacityNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckCapacityNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                capacity_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckCapacityNameAvailabilityResult: ...

        @distributed_trace_async
        async def get_details(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                **kwargs: Any
            ) -> DedicatedCapacity: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[DedicatedCapacity]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DedicatedCapacity]: ...

        @distributed_trace_async
        async def list_skus(self, **kwargs: Any) -> SkuEnumerationForNewResourceResult: ...

        @distributed_trace_async
        async def list_skus_for_capacity(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                **kwargs: Any
            ) -> SkuEnumerationForExistingResourceResult: ...


    class azure.mgmt.powerbidedicated.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.powerbidedicated.models

    class azure.mgmt.powerbidedicated.models.AutoScaleVCore(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[AutoScaleVCoreProperties]
        sku: AutoScaleVCoreSku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[AutoScaleVCoreProperties] = ..., 
                sku: AutoScaleVCoreSku, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.powerbidedicated.models.AutoScaleVCoreMutableProperties(_Model):
        capacity_limit: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                capacity_limit: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerbidedicated.models.AutoScaleVCoreProperties(AutoScaleVCoreMutableProperties):
        capacity_limit: int
        capacity_object_id: Optional[str]
        provisioning_state: Optional[Union[str, VCoreProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                capacity_limit: Optional[int] = ..., 
                capacity_object_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerbidedicated.models.AutoScaleVCoreSku(_Model):
        capacity: Optional[int]
        name: str
        tier: Optional[Union[str, VCoreSkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: str, 
                tier: Optional[Union[str, VCoreSkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerbidedicated.models.AutoScaleVCoreUpdateParameters(_Model):
        properties: Optional[AutoScaleVCoreMutableProperties]
        sku: Optional[AutoScaleVCoreSku]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AutoScaleVCoreMutableProperties] = ..., 
                sku: Optional[AutoScaleVCoreSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.powerbidedicated.models.CapacityProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETING = "Deleting"
        FAILED = "Failed"
        PAUSED = "Paused"
        PAUSING = "Pausing"
        PREPARING = "Preparing"
        PROVISIONING = "Provisioning"
        RESUMING = "Resuming"
        SCALING = "Scaling"
        SUCCEEDED = "Succeeded"
        SUSPENDED = "Suspended"
        SUSPENDING = "Suspending"
        UPDATING = "Updating"


    class azure.mgmt.powerbidedicated.models.CapacitySku(_Model):
        capacity: Optional[int]
        name: str
        tier: Optional[Union[str, CapacitySkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: str, 
                tier: Optional[Union[str, CapacitySkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerbidedicated.models.CapacitySkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_PREMIUM_HOST = "AutoPremiumHost"
        PBIE_AZURE = "PBIE_Azure"
        PREMIUM = "Premium"


    class azure.mgmt.powerbidedicated.models.CheckCapacityNameAvailabilityParameters(_Model):
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


    class azure.mgmt.powerbidedicated.models.CheckCapacityNameAvailabilityResult(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerbidedicated.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.powerbidedicated.models.DedicatedCapacity(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[DedicatedCapacityProperties]
        sku: CapacitySku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[DedicatedCapacityProperties] = ..., 
                sku: CapacitySku, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.powerbidedicated.models.DedicatedCapacityAdministrators(_Model):
        members: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                members: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerbidedicated.models.DedicatedCapacityMutableProperties(_Model):
        administration: Optional[DedicatedCapacityAdministrators]
        friendly_name: Optional[str]
        mode: Optional[Union[str, Mode]]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                administration: Optional[DedicatedCapacityAdministrators] = ..., 
                mode: Optional[Union[str, Mode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerbidedicated.models.DedicatedCapacityProperties(DedicatedCapacityMutableProperties):
        administration: DedicatedCapacityAdministrators
        friendly_name: str
        mode: Union[str, Mode]
        provisioning_state: Optional[Union[str, CapacityProvisioningState]]
        state: Optional[Union[str, State]]
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                administration: Optional[DedicatedCapacityAdministrators] = ..., 
                mode: Optional[Union[str, Mode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerbidedicated.models.DedicatedCapacityUpdateParameters(_Model):
        properties: Optional[DedicatedCapacityMutableProperties]
        sku: Optional[CapacitySku]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DedicatedCapacityMutableProperties] = ..., 
                sku: Optional[CapacitySku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.powerbidedicated.models.ErrorResponse(_Model):
        error: Optional[ErrorResponseError]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponseError] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerbidedicated.models.ErrorResponseError(_Model):
        code: Optional[str]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerbidedicated.models.LogSpecification(_Model):
        blob_duration: Optional[str]
        display_name: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerbidedicated.models.MetricSpecification(_Model):
        aggregation_type: Optional[str]
        dimensions: Optional[list[MetricSpecificationDimensionsItem]]
        display_description: Optional[str]
        display_name: Optional[str]
        metric_filter_pattern: Optional[str]
        name: Optional[str]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                dimensions: Optional[list[MetricSpecificationDimensionsItem]] = ..., 
                display_description: Optional[str] = ..., 
                display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerbidedicated.models.MetricSpecificationDimensionsItem(_Model):
        display_name: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerbidedicated.models.Mode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GEN1 = "Gen1"
        GEN2 = "Gen2"


    class azure.mgmt.powerbidedicated.models.Operation(_Model):
        display: Optional[OperationDisplay]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[OperationProperties]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                properties: Optional[OperationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerbidedicated.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerbidedicated.models.OperationProperties(_Model):
        service_specification: Optional[ServiceSpecification]

        @overload
        def __init__(
                self, 
                *, 
                service_specification: Optional[ServiceSpecification] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerbidedicated.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.powerbidedicated.models.ServiceSpecification(_Model):
        log_specifications: Optional[list[LogSpecification]]
        metric_specifications: Optional[list[MetricSpecification]]

        @overload
        def __init__(
                self, 
                *, 
                log_specifications: Optional[list[LogSpecification]] = ..., 
                metric_specifications: Optional[list[MetricSpecification]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerbidedicated.models.SkuDetailsForExistingResource(_Model):
        resource_type: Optional[str]
        sku: Optional[CapacitySku]

        @overload
        def __init__(
                self, 
                *, 
                resource_type: Optional[str] = ..., 
                sku: Optional[CapacitySku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerbidedicated.models.SkuEnumerationForExistingResourceResult(_Model):
        value: Optional[list[SkuDetailsForExistingResource]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[SkuDetailsForExistingResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerbidedicated.models.SkuEnumerationForNewResourceResult(_Model):
        value: Optional[list[CapacitySku]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[CapacitySku]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerbidedicated.models.State(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETING = "Deleting"
        FAILED = "Failed"
        PAUSED = "Paused"
        PAUSING = "Pausing"
        PREPARING = "Preparing"
        PROVISIONING = "Provisioning"
        RESUMING = "Resuming"
        SCALING = "Scaling"
        SUCCEEDED = "Succeeded"
        SUSPENDED = "Suspended"
        SUSPENDING = "Suspending"
        UPDATING = "Updating"


    class azure.mgmt.powerbidedicated.models.SystemData(_Model):
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


    class azure.mgmt.powerbidedicated.models.TrackedResource(Resource):
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


    class azure.mgmt.powerbidedicated.models.VCoreProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SUCCEEDED = "Succeeded"


    class azure.mgmt.powerbidedicated.models.VCoreSkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_SCALE = "AutoScale"


namespace azure.mgmt.powerbidedicated.operations

    class azure.mgmt.powerbidedicated.operations.AutoScaleVCoresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                v_core_parameters: AutoScaleVCore, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoScaleVCore: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                v_core_parameters: AutoScaleVCore, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoScaleVCore: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                v_core_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoScaleVCore: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                **kwargs: Any
            ) -> AutoScaleVCore: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AutoScaleVCore]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[AutoScaleVCore]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                v_core_update_parameters: AutoScaleVCoreUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoScaleVCore: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                v_core_update_parameters: AutoScaleVCoreUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoScaleVCore: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vcore_name: str, 
                v_core_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutoScaleVCore: ...


    class azure.mgmt.powerbidedicated.operations.CapacitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                capacity_parameters: DedicatedCapacity, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedCapacity]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                capacity_parameters: DedicatedCapacity, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedCapacity]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                capacity_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedCapacity]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_resume(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_suspend(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                capacity_update_parameters: DedicatedCapacityUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedCapacity]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                capacity_update_parameters: DedicatedCapacityUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedCapacity]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                capacity_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedCapacity]: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                capacity_parameters: CheckCapacityNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckCapacityNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                capacity_parameters: CheckCapacityNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckCapacityNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                capacity_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckCapacityNameAvailabilityResult: ...

        @distributed_trace
        def get_details(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                **kwargs: Any
            ) -> DedicatedCapacity: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[DedicatedCapacity]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DedicatedCapacity]: ...

        @distributed_trace
        def list_skus(self, **kwargs: Any) -> SkuEnumerationForNewResourceResult: ...

        @distributed_trace
        def list_skus_for_capacity(
                self, 
                resource_group_name: str, 
                dedicated_capacity_name: str, 
                **kwargs: Any
            ) -> SkuEnumerationForExistingResourceResult: ...


    class azure.mgmt.powerbidedicated.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


namespace azure.mgmt.powerbidedicated.types

    class azure.mgmt.powerbidedicated.types.AutoScaleVCore(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('AutoScaleVCoreProperties', module='types')
        key "sku": Required[AutoScaleVCoreSku]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: AutoScaleVCoreProperties
        sku: AutoScaleVCoreSku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.powerbidedicated.types.AutoScaleVCoreMutableProperties(TypedDict, total=False):
        key "capacityLimit": int
        capacity_limit: int


    class azure.mgmt.powerbidedicated.types.AutoScaleVCoreProperties(AutoScaleVCoreMutableProperties):
        key "capacityLimit": int
        key "capacityObjectId": str
        key "provisioningState": Union[str, VCoreProvisioningState]
        capacity_limit: int
        capacity_object_id: str
        provisioning_state: Union[str, VCoreProvisioningState]


    class azure.mgmt.powerbidedicated.types.AutoScaleVCoreSku(TypedDict, total=False):
        key "capacity": int
        key "name": Required[str]
        key "tier": Union[str, VCoreSkuTier]
        capacity: int
        name: str
        tier: Union[str, VCoreSkuTier]


    class azure.mgmt.powerbidedicated.types.AutoScaleVCoreUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('AutoScaleVCoreMutableProperties', module='types')
        key "sku": ForwardRef('AutoScaleVCoreSku', module='types')
        properties: AutoScaleVCoreMutableProperties
        sku: AutoScaleVCoreSku
        tags: dict[str, str]


    class azure.mgmt.powerbidedicated.types.CapacitySku(TypedDict, total=False):
        key "capacity": int
        key "name": Required[str]
        key "tier": Union[str, CapacitySkuTier]
        capacity: int
        name: str
        tier: Union[str, CapacitySkuTier]


    class azure.mgmt.powerbidedicated.types.CheckCapacityNameAvailabilityParameters(TypedDict, total=False):
        key "name": str
        key "type": str
        name: str
        type: str


    class azure.mgmt.powerbidedicated.types.CheckCapacityNameAvailabilityResult(TypedDict, total=False):
        key "message": str
        key "nameAvailable": bool
        key "reason": str
        message: str
        name_available: bool
        reason: str


    class azure.mgmt.powerbidedicated.types.DedicatedCapacity(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('DedicatedCapacityProperties', module='types')
        key "sku": Required[CapacitySku]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: DedicatedCapacityProperties
        sku: CapacitySku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.powerbidedicated.types.DedicatedCapacityAdministrators(TypedDict, total=False):
        members: list[str]


    class azure.mgmt.powerbidedicated.types.DedicatedCapacityMutableProperties(TypedDict, total=False):
        key "administration": ForwardRef('DedicatedCapacityAdministrators', module='types')
        key "friendlyName": str
        key "mode": Union[str, Mode]
        key "tenantId": str
        administration: DedicatedCapacityAdministrators
        friendly_name: str
        mode: Union[str, Mode]
        tenant_id: str


    class azure.mgmt.powerbidedicated.types.DedicatedCapacityProperties(DedicatedCapacityMutableProperties):
        key "administration": ForwardRef('DedicatedCapacityAdministrators', module='types')
        key "friendlyName": str
        key "mode": Union[str, Mode]
        key "provisioningState": Union[str, CapacityProvisioningState]
        key "state": Union[str, State]
        key "tenantId": str
        administration: DedicatedCapacityAdministrators
        friendly_name: str
        mode: Union[str, Mode]
        provisioning_state: Union[str, CapacityProvisioningState]
        state: Union[str, State]
        tenant_id: str


    class azure.mgmt.powerbidedicated.types.DedicatedCapacityUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('DedicatedCapacityMutableProperties', module='types')
        key "sku": ForwardRef('CapacitySku', module='types')
        properties: DedicatedCapacityMutableProperties
        sku: CapacitySku
        tags: dict[str, str]


    class azure.mgmt.powerbidedicated.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorResponseError', module='types')
        error: ErrorResponseError


    class azure.mgmt.powerbidedicated.types.ErrorResponseError(TypedDict, total=False):
        key "code": str
        key "message": str
        code: str
        message: str


    class azure.mgmt.powerbidedicated.types.LogSpecification(TypedDict, total=False):
        key "blobDuration": str
        key "displayName": str
        key "name": str
        blob_duration: str
        display_name: str
        name: str


    class azure.mgmt.powerbidedicated.types.MetricSpecification(TypedDict, total=False):
        key "aggregationType": str
        key "displayDescription": str
        key "displayName": str
        key "metricFilterPattern": str
        key "name": str
        key "unit": str
        aggregation_type: str
        dimensions: list[MetricSpecificationDimensionsItem]
        display_description: str
        display_name: str
        metric_filter_pattern: str
        name: str
        unit: str


    class azure.mgmt.powerbidedicated.types.MetricSpecificationDimensionsItem(TypedDict, total=False):
        key "displayName": str
        key "name": str
        display_name: str
        name: str


    class azure.mgmt.powerbidedicated.types.Operation(TypedDict, total=False):
        key "display": ForwardRef('OperationDisplay', module='types')
        key "name": str
        key "origin": str
        key "properties": ForwardRef('OperationProperties', module='types')
        display: OperationDisplay
        name: str
        origin: str
        properties: OperationProperties


    class azure.mgmt.powerbidedicated.types.OperationDisplay(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.powerbidedicated.types.OperationProperties(TypedDict, total=False):
        key "serviceSpecification": ForwardRef('ServiceSpecification', module='types')
        service_specification: ServiceSpecification


    class azure.mgmt.powerbidedicated.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.powerbidedicated.types.ServiceSpecification(TypedDict, total=False):
        logSpecifications: list[LogSpecification]
        log_specifications: list[LogSpecification]
        metricSpecifications: list[MetricSpecification]
        metric_specifications: list[MetricSpecification]


    class azure.mgmt.powerbidedicated.types.SkuDetailsForExistingResource(TypedDict, total=False):
        key "resourceType": str
        key "sku": ForwardRef('CapacitySku', module='types')
        resource_type: str
        sku: CapacitySku


    class azure.mgmt.powerbidedicated.types.SkuEnumerationForExistingResourceResult(TypedDict, total=False):
        value: list[SkuDetailsForExistingResource]


    class azure.mgmt.powerbidedicated.types.SkuEnumerationForNewResourceResult(TypedDict, total=False):
        value: list[CapacitySku]


    class azure.mgmt.powerbidedicated.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        created_at: str
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: str
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]


    class azure.mgmt.powerbidedicated.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str


```