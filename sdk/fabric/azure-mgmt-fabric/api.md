```py
namespace azure.mgmt.fabric

    class azure.mgmt.fabric.FabricMgmtClient: implements ContextManager 
        fabric_capacities: FabricCapacitiesOperations
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


namespace azure.mgmt.fabric.aio

    class azure.mgmt.fabric.aio.FabricMgmtClient: implements AsyncContextManager 
        fabric_capacities: FabricCapacitiesOperations
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
                body: CheckNameAvailabilityRequest, 
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
            ) -> AsyncItemPaged[FabricCapacity]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[FabricCapacity]: ...

        @distributed_trace
        def list_skus(self, **kwargs: Any) -> AsyncItemPaged[RpSkuDetailsForNewResource]: ...

        @distributed_trace
        def list_skus_for_capacity(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RpSkuDetailsForExistingResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-01-15-preview', params_added_on={'2025-01-15-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2025-01-15-preview', '2026-08-01-preview'])
        def list_usages(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Quota]: ...


    class azure.mgmt.fabric.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.fabric.models

    class azure.mgmt.fabric.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.fabric.models.CapacityAdministration(_Model):
        members: list[str]

        @overload
        def __init__(
                self, 
                *, 
                members: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fabric.models.CapacityOverageProperties(_Model):
        state: Optional[Union[str, CapacityOverageState]]
        threshold_capacity_unit_hours: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                state: Optional[Union[str, CapacityOverageState]] = ..., 
                threshold_capacity_unit_hours: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fabric.models.CapacityOverageState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.fabric.models.CheckNameAvailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.fabric.models.CheckNameAvailabilityRequest(_Model):
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


    class azure.mgmt.fabric.models.CheckNameAvailabilityResponse(_Model):
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


    class azure.mgmt.fabric.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.fabric.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.fabric.models.ErrorResponse(_Model):
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
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fabric.models.FabricCapacityProperties(_Model):
        administration: CapacityAdministration
        overage: Optional[CapacityOverageProperties]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        state: Optional[Union[str, ResourceState]]

        @overload
        def __init__(
                self, 
                *, 
                administration: CapacityAdministration, 
                overage: Optional[CapacityOverageProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fabric.models.FabricCapacityUpdate(_Model):
        properties: Optional[FabricCapacityUpdateProperties]
        sku: Optional[RpSku]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FabricCapacityUpdateProperties] = ..., 
                sku: Optional[RpSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fabric.models.FabricCapacityUpdateProperties(_Model):
        administration: Optional[CapacityAdministration]
        overage: Optional[CapacityOverageProperties]

        @overload
        def __init__(
                self, 
                *, 
                administration: Optional[CapacityAdministration] = ..., 
                overage: Optional[CapacityOverageProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fabric.models.Operation(_Model):
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


    class azure.mgmt.fabric.models.OperationDisplay(_Model):
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


    class azure.mgmt.fabric.models.Quota(_Model):
        current_value: int
        limit: int
        name: Optional[QuotaName]
        unit: str

        @overload
        def __init__(
                self, 
                *, 
                current_value: int, 
                limit: int, 
                unit: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fabric.models.QuotaName(_Model):
        localized_value: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                localized_value: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fabric.models.Resource(_Model):
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


    class azure.mgmt.fabric.models.RpSku(_Model):
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


    class azure.mgmt.fabric.models.RpSkuDetailsForExistingResource(_Model):
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


    class azure.mgmt.fabric.models.RpSkuDetailsForNewResource(_Model):
        locations: list[str]
        name: str
        resource_type: str

        @overload
        def __init__(
                self, 
                *, 
                locations: list[str], 
                name: str, 
                resource_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fabric.models.RpSkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FABRIC = "Fabric"


    class azure.mgmt.fabric.models.SystemData(_Model):
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


namespace azure.mgmt.fabric.operations

    class azure.mgmt.fabric.operations.FabricCapacitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                body: CheckNameAvailabilityRequest, 
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
            ) -> ItemPaged[FabricCapacity]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[FabricCapacity]: ...

        @distributed_trace
        def list_skus(self, **kwargs: Any) -> ItemPaged[RpSkuDetailsForNewResource]: ...

        @distributed_trace
        def list_skus_for_capacity(
                self, 
                resource_group_name: str, 
                capacity_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RpSkuDetailsForExistingResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-01-15-preview', params_added_on={'2025-01-15-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2025-01-15-preview', '2026-08-01-preview'])
        def list_usages(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[Quota]: ...


    class azure.mgmt.fabric.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


namespace azure.mgmt.fabric.types

    class azure.mgmt.fabric.types.CapacityAdministration(TypedDict, total=False):
        key "members": Required[list[str]]
        members: list[str]


    class azure.mgmt.fabric.types.CapacityOverageProperties(TypedDict, total=False):
        key "state": Union[str, CapacityOverageState]
        key "thresholdCapacityUnitHours": int
        state: Union[str, CapacityOverageState]
        thresholdCapacityUnitHours: int


    class azure.mgmt.fabric.types.CheckNameAvailabilityRequest(TypedDict, total=False):
        key "name": str
        key "type": str
        name: str
        type: str


    class azure.mgmt.fabric.types.FabricCapacity(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[FabricCapacityProperties]
        key "sku": Required[RpSku]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: FabricCapacityProperties
        sku: RpSku
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.fabric.types.FabricCapacityProperties(TypedDict, total=False):
        key "administration": Required[CapacityAdministration]
        key "overage": ForwardRef('CapacityOverageProperties', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "state": Union[str, ResourceState]
        administration: CapacityAdministration
        overage: CapacityOverageProperties
        provisioningState: Union[str, ProvisioningState]
        state: Union[str, ResourceState]


    class azure.mgmt.fabric.types.FabricCapacityUpdate(TypedDict, total=False):
        key "properties": ForwardRef('FabricCapacityUpdateProperties', module='types')
        key "sku": ForwardRef('RpSku', module='types')
        properties: FabricCapacityUpdateProperties
        sku: RpSku
        tags: dict[str, str]


    class azure.mgmt.fabric.types.FabricCapacityUpdateProperties(TypedDict, total=False):
        key "administration": ForwardRef('CapacityAdministration', module='types')
        key "overage": ForwardRef('CapacityOverageProperties', module='types')
        administration: CapacityAdministration
        overage: CapacityOverageProperties


    class azure.mgmt.fabric.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.fabric.types.RpSku(TypedDict, total=False):
        key "name": Required[str]
        key "tier": Required[Union[str, RpSkuTier]]
        name: str
        tier: Union[str, RpSkuTier]


    class azure.mgmt.fabric.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.fabric.types.TrackedResource(Resource):
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


```