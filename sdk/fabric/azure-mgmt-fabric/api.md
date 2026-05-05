```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.fabric

    class azure.mgmt.fabric.FabricMgmtClient: implements ContextManager 
        fabric_capacities: FabricCapacitiesOperations
        operations: Operations

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

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.fabric.aio

    class azure.mgmt.fabric.aio.FabricMgmtClient: implements AsyncContextManager 
        fabric_capacities: FabricCapacitiesOperations
        operations: Operations

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

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.fabric.aio.operations

    class azure.mgmt.fabric.aio.operations.FabricCapacitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                resource: FabricCapacity, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FabricCapacity]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FabricCapacity]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FabricCapacity]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_resume(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_suspend(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                properties: FabricCapacityUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FabricCapacity]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FabricCapacity]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FabricCapacity]: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                **kwargs: Any
            ) -> FabricCapacity: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[FabricCapacity]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncIterable[FabricCapacity]: ...

        @distributed_trace
        def list_skus(self, **kwargs: Any) -> AsyncIterable[RpSkuDetailsForNewResource]: ...

        @distributed_trace
        def list_skus_for_capacity(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[RpSkuDetailsForExistingResource]: ...


    class azure.mgmt.fabric.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


namespace azure.mgmt.fabric.models

    class azure.mgmt.fabric.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.fabric.models.CapacityAdministration(Model):
        members: List[str]

        @overload
        def __init__(
                self, 
                *, 
                members: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fabric.models.CheckNameAvailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.fabric.models.CheckNameAvailabilityRequest(Model):
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


    class azure.mgmt.fabric.models.CheckNameAvailabilityResponse(Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[Union[str, CheckNameAvailabilityReason]]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[Union[str, CheckNameAvailabilityReason]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fabric.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.fabric.models.ErrorAdditionalInfo(Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.fabric.models.ErrorDetail(Model):
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.fabric.models.ErrorResponse(Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fabric.models.FabricCapacity(TrackedResource):
        id: str
        location: str
        name: str
        properties: FabricCapacityProperties
        sku: RpSku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: FabricCapacityProperties, 
                sku: RpSku, 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fabric.models.FabricCapacityProperties(Model):
        administration: CapacityAdministration
        provisioning_state: Optional[Union[str, ProvisioningState]]
        state: Optional[Union[str, ResourceState]]

        @overload
        def __init__(
                self, 
                *, 
                administration: CapacityAdministration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fabric.models.FabricCapacityUpdate(Model):
        properties: Optional[FabricCapacityUpdateProperties]
        sku: Optional[RpSku]
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FabricCapacityUpdateProperties] = ..., 
                sku: Optional[RpSku] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fabric.models.FabricCapacityUpdateProperties(Model):
        administration: Optional[CapacityAdministration]

        @overload
        def __init__(
                self, 
                *, 
                administration: Optional[CapacityAdministration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fabric.models.Operation(Model):
        action_type: Optional[Union[str, ActionType]]
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[Union[str, Origin]]

        @overload
        def __init__(
                self, 
                *, 
                action_type: Optional[Union[str, ActionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fabric.models.OperationDisplay(Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.fabric.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.fabric.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.fabric.models.Resource(Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.fabric.models.ResourceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DELETING = "Deleting"
        FAILED = "Failed"
        PAUSED = "Paused"
        PAUSING = "Pausing"
        PREPARING = "Preparing"
        PROVISIONING = "Provisioning"
        RESUMING = "Resuming"
        SCALING = "Scaling"
        SUSPENDED = "Suspended"
        SUSPENDING = "Suspending"
        UPDATING = "Updating"


    class azure.mgmt.fabric.models.RpSku(Model):
        name: str
        tier: Union[str, RpSkuTier]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                tier: Union[str, RpSkuTier]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fabric.models.RpSkuDetailsForExistingResource(Model):
        resource_type: str
        sku: RpSku

        @overload
        def __init__(
                self, 
                *, 
                resource_type: str, 
                sku: RpSku
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fabric.models.RpSkuDetailsForNewResource(Model):
        locations: List[str]
        name: str
        resource_type: str

        @overload
        def __init__(
                self, 
                *, 
                locations: List[str], 
                name: str, 
                resource_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fabric.models.RpSkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FABRIC = "Fabric"


    class azure.mgmt.fabric.models.SystemData(Model):
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


    class azure.mgmt.fabric.models.TrackedResource(Resource):
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


namespace azure.mgmt.fabric.operations

    class azure.mgmt.fabric.operations.FabricCapacitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                resource: FabricCapacity, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FabricCapacity]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FabricCapacity]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FabricCapacity]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_resume(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_suspend(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                properties: FabricCapacityUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FabricCapacity]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FabricCapacity]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FabricCapacity]: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                **kwargs: Any
            ) -> FabricCapacity: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Iterable[FabricCapacity]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> Iterable[FabricCapacity]: ...

        @distributed_trace
        def list_skus(self, **kwargs: Any) -> Iterable[RpSkuDetailsForNewResource]: ...

        @distributed_trace
        def list_skus_for_capacity(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                **kwargs: Any
            ) -> Iterable[RpSkuDetailsForExistingResource]: ...


    class azure.mgmt.fabric.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


```