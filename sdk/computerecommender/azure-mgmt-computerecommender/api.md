```py
namespace azure.mgmt.computerecommender

    class azure.mgmt.computerecommender.RecommenderMgmtClient: implements ContextManager 
        operations: Operations
        sku_mix_placement_scores: SkuMixPlacementScoresOperations
        spot_placement_scores: SpotPlacementScoresOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
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


namespace azure.mgmt.computerecommender.aio

    class azure.mgmt.computerecommender.aio.RecommenderMgmtClient: implements AsyncContextManager 
        operations: Operations
        sku_mix_placement_scores: SkuMixPlacementScoresOperations
        spot_placement_scores: SpotPlacementScoresOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
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


namespace azure.mgmt.computerecommender.aio.operations

    class azure.mgmt.computerecommender.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.computerecommender.aio.operations.SkuMixPlacementScoresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-05-preview', params_added_on={'2026-05-05-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-05-05-preview'])
        async def get(
                self, 
                location: str, 
                **kwargs: Any
            ) -> SkuMixPlacementBase: ...

        @overload
        async def post(
                self, 
                location: str, 
                sku_mix_placement_request: SkuMixPlacementRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuMixPlacementResponse: ...

        @overload
        async def post(
                self, 
                location: str, 
                sku_mix_placement_request: SkuMixPlacementRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuMixPlacementResponse: ...

        @overload
        async def post(
                self, 
                location: str, 
                sku_mix_placement_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuMixPlacementResponse: ...


    class azure.mgmt.computerecommender.aio.operations.SpotPlacementScoresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ComputeDiagnosticBase: ...

        @overload
        async def post(
                self, 
                location: str, 
                spot_placement_scores_input: SpotPlacementScoresInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SpotPlacementScoresResponse: ...

        @overload
        async def post(
                self, 
                location: str, 
                spot_placement_scores_input: SpotPlacementScoresInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SpotPlacementScoresResponse: ...

        @overload
        async def post(
                self, 
                location: str, 
                spot_placement_scores_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SpotPlacementScoresResponse: ...


namespace azure.mgmt.computerecommender.models

    class azure.mgmt.computerecommender.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.computerecommender.models.ComputeDiagnosticBase(ProxyResource):
        id: str
        name: str
        properties: Optional[DiagnosticProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DiagnosticProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.computerecommender.models.DiagnosticProperties(_Model):
        supported_resource_types: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                supported_resource_types: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.computerecommender.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.computerecommender.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.Operation(_Model):
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


    class azure.mgmt.computerecommender.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.computerecommender.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.computerecommender.models.PlacementScore(_Model):
        availability_zone: Optional[str]
        is_quota_available: Optional[bool]
        region: Optional[str]
        score: Optional[str]
        sku: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                availability_zone: Optional[str] = ..., 
                is_quota_available: Optional[bool] = ..., 
                region: Optional[str] = ..., 
                score: Optional[str] = ..., 
                sku: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.computerecommender.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.computerecommender.models.ResourceSize(_Model):
        sku: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                sku: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.SkuMixPlacementAllocationStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVICTION_OPTIMIZED = "EvictionOptimized"
        LOWEST_PRICE = "LowestPrice"
        PRIORITIZED = "Prioritized"


    class azure.mgmt.computerecommender.models.SkuMixPlacementBase(ProxyResource):
        id: str
        name: str
        properties: Optional[SkuMixPlacementProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SkuMixPlacementProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.SkuMixPlacementCapacityProfile(_Model):
        allocation_strategy: Optional[Union[str, SkuMixPlacementAllocationStrategy]]
        capacity: int
        capacity_type: Union[str, SkuMixPlacementCapacityType]
        os_type: Optional[Union[str, SkuMixPlacementOSType]]
        priority: Union[str, SkuMixPlacementPriority]
        spot_priority_profile: Optional[SkuMixPlacementSpotPriorityProfile]
        zone_allocation_policy: Optional[SkuMixPlacementZoneAllocationPolicy]

        @overload
        def __init__(
                self, 
                *, 
                allocation_strategy: Optional[Union[str, SkuMixPlacementAllocationStrategy]] = ..., 
                capacity: int, 
                capacity_type: Union[str, SkuMixPlacementCapacityType], 
                os_type: Optional[Union[str, SkuMixPlacementOSType]] = ..., 
                priority: Union[str, SkuMixPlacementPriority], 
                spot_priority_profile: Optional[SkuMixPlacementSpotPriorityProfile] = ..., 
                zone_allocation_policy: Optional[SkuMixPlacementZoneAllocationPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.SkuMixPlacementCapacityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VM = "VM"
        V_CPU = "VCpu"


    class azure.mgmt.computerecommender.models.SkuMixPlacementDeploymentChoice(_Model):
        id: str
        score: int
        sku_split: list[SkuMixPlacementItem]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                score: int, 
                sku_split: list[SkuMixPlacementItem]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.SkuMixPlacementInstanceDescription(_Model):
        vm_sizes: list[SkuMixPlacementVMSize]

        @overload
        def __init__(
                self, 
                *, 
                vm_sizes: list[SkuMixPlacementVMSize]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.SkuMixPlacementItem(_Model):
        capacity: int
        capacity_max: Optional[int]
        name: str
        priority: Union[str, SkuMixPlacementPriority]
        zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                capacity: int, 
                capacity_max: Optional[int] = ..., 
                name: str, 
                priority: Union[str, SkuMixPlacementPriority], 
                zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.SkuMixPlacementOSType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.computerecommender.models.SkuMixPlacementPartialFulfillmentReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INSUFFICIENT_CAPACITY = "InsufficientCapacity"
        INSUFFICIENT_QUOTA = "InsufficientQuota"
        NONE = "None"


    class azure.mgmt.computerecommender.models.SkuMixPlacementPriority(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REGULAR = "Regular"
        SPOT = "Spot"


    class azure.mgmt.computerecommender.models.SkuMixPlacementProperties(_Model):
        supported_resource_types: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                supported_resource_types: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.SkuMixPlacementRequest(_Model):
        capacity_profile: SkuMixPlacementCapacityProfile
        instance_description: SkuMixPlacementInstanceDescription
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                capacity_profile: SkuMixPlacementCapacityProfile, 
                instance_description: SkuMixPlacementInstanceDescription, 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.SkuMixPlacementResponse(_Model):
        partial_fulfillment_reason: Union[str, SkuMixPlacementPartialFulfillmentReason]
        placement_choices: list[SkuMixPlacementDeploymentChoice]
        valid_until: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                partial_fulfillment_reason: Union[str, SkuMixPlacementPartialFulfillmentReason], 
                placement_choices: list[SkuMixPlacementDeploymentChoice], 
                valid_until: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.SkuMixPlacementSpotPriorityProfile(_Model):
        max_price_per_vm: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                max_price_per_vm: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.SkuMixPlacementVMSize(_Model):
        name: str
        rank: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                rank: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.SkuMixPlacementZonalDistributionStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BEST_EFFORT_BALANCED = "BestEffortBalanced"
        BEST_EFFORT_SINGLE_ZONE = "BestEffortSingleZone"
        PRIORITIZED = "Prioritized"


    class azure.mgmt.computerecommender.models.SkuMixPlacementZoneAllocationPolicy(_Model):
        distribution_strategy: Optional[Union[str, SkuMixPlacementZonalDistributionStrategy]]
        zone_preferences: Optional[list[SkuMixPlacementZonePreference]]

        @overload
        def __init__(
                self, 
                *, 
                distribution_strategy: Optional[Union[str, SkuMixPlacementZonalDistributionStrategy]] = ..., 
                zone_preferences: Optional[list[SkuMixPlacementZonePreference]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.SkuMixPlacementZonePreference(_Model):
        rank: Optional[int]
        target_max_capacity: Optional[int]
        zone: str

        @overload
        def __init__(
                self, 
                *, 
                rank: Optional[int] = ..., 
                target_max_capacity: Optional[int] = ..., 
                zone: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.SpotPlacementScoresInput(_Model):
        availability_zones: Optional[bool]
        desired_count: Optional[int]
        desired_locations: Optional[list[str]]
        desired_sizes: Optional[list[ResourceSize]]

        @overload
        def __init__(
                self, 
                *, 
                availability_zones: Optional[bool] = ..., 
                desired_count: Optional[int] = ..., 
                desired_locations: Optional[list[str]] = ..., 
                desired_sizes: Optional[list[ResourceSize]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.SpotPlacementScoresResponse(_Model):
        availability_zones: Optional[bool]
        desired_count: Optional[int]
        desired_locations: Optional[list[str]]
        desired_sizes: Optional[list[ResourceSize]]
        placement_scores: Optional[list[PlacementScore]]

        @overload
        def __init__(
                self, 
                *, 
                availability_zones: Optional[bool] = ..., 
                desired_count: Optional[int] = ..., 
                desired_locations: Optional[list[str]] = ..., 
                desired_sizes: Optional[list[ResourceSize]] = ..., 
                placement_scores: Optional[list[PlacementScore]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computerecommender.models.SystemData(_Model):
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


namespace azure.mgmt.computerecommender.operations

    class azure.mgmt.computerecommender.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.computerecommender.operations.SkuMixPlacementScoresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-05-preview', params_added_on={'2026-05-05-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-05-05-preview'])
        def get(
                self, 
                location: str, 
                **kwargs: Any
            ) -> SkuMixPlacementBase: ...

        @overload
        def post(
                self, 
                location: str, 
                sku_mix_placement_request: SkuMixPlacementRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuMixPlacementResponse: ...

        @overload
        def post(
                self, 
                location: str, 
                sku_mix_placement_request: SkuMixPlacementRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuMixPlacementResponse: ...

        @overload
        def post(
                self, 
                location: str, 
                sku_mix_placement_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuMixPlacementResponse: ...


    class azure.mgmt.computerecommender.operations.SpotPlacementScoresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ComputeDiagnosticBase: ...

        @overload
        def post(
                self, 
                location: str, 
                spot_placement_scores_input: SpotPlacementScoresInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SpotPlacementScoresResponse: ...

        @overload
        def post(
                self, 
                location: str, 
                spot_placement_scores_input: SpotPlacementScoresInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SpotPlacementScoresResponse: ...

        @overload
        def post(
                self, 
                location: str, 
                spot_placement_scores_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SpotPlacementScoresResponse: ...


namespace azure.mgmt.computerecommender.types

    class azure.mgmt.computerecommender.types.ResourceSize(TypedDict, total=False):
        key "sku": str
        sku: str


    class azure.mgmt.computerecommender.types.SkuMixPlacementCapacityProfile(TypedDict, total=False):
        key "allocationStrategy": Union[str, SkuMixPlacementAllocationStrategy]
        key "capacity": Required[int]
        key "capacityType": Required[Union[str, SkuMixPlacementCapacityType]]
        key "osType": Union[str, SkuMixPlacementOSType]
        key "priority": Required[Union[str, SkuMixPlacementPriority]]
        key "spotPriorityProfile": ForwardRef('SkuMixPlacementSpotPriorityProfile', module='types')
        key "zoneAllocationPolicy": ForwardRef('SkuMixPlacementZoneAllocationPolicy', module='types')
        allocationStrategy: Union[str, SkuMixPlacementAllocationStrategy]
        capacity: int
        capacityType: Union[str, SkuMixPlacementCapacityType]
        osType: Union[str, SkuMixPlacementOSType]
        priority: Union[str, SkuMixPlacementPriority]
        spotPriorityProfile: SkuMixPlacementSpotPriorityProfile
        zoneAllocationPolicy: SkuMixPlacementZoneAllocationPolicy


    class azure.mgmt.computerecommender.types.SkuMixPlacementInstanceDescription(TypedDict, total=False):
        key "vmSizes": Required[list[SkuMixPlacementVMSize]]
        vmSizes: list[SkuMixPlacementVMSize]


    class azure.mgmt.computerecommender.types.SkuMixPlacementRequest(TypedDict, total=False):
        key "capacityProfile": Required[SkuMixPlacementCapacityProfile]
        key "instanceDescription": Required[SkuMixPlacementInstanceDescription]
        capacityProfile: SkuMixPlacementCapacityProfile
        instanceDescription: SkuMixPlacementInstanceDescription
        zones: list[str]


    class azure.mgmt.computerecommender.types.SkuMixPlacementSpotPriorityProfile(TypedDict, total=False):
        key "maxPricePerVm": float
        maxPricePerVm: float


    class azure.mgmt.computerecommender.types.SkuMixPlacementVMSize(TypedDict, total=False):
        key "name": Required[str]
        key "rank": int
        name: str
        rank: int


    class azure.mgmt.computerecommender.types.SkuMixPlacementZoneAllocationPolicy(TypedDict, total=False):
        key "distributionStrategy": Union[str, SkuMixPlacementZonalDistributionStrategy]
        distributionStrategy: Union[str, SkuMixPlacementZonalDistributionStrategy]
        zonePreferences: list[SkuMixPlacementZonePreference]


    class azure.mgmt.computerecommender.types.SkuMixPlacementZonePreference(TypedDict, total=False):
        key "rank": int
        key "targetMaxCapacity": int
        key "zone": Required[str]
        rank: int
        targetMaxCapacity: int
        zone: str


    class azure.mgmt.computerecommender.types.SpotPlacementScoresInput(TypedDict, total=False):
        key "availabilityZones": bool
        key "desiredCount": int
        availabilityZones: bool
        desiredCount: int
        desiredLocations: list[str]
        desiredSizes: list[ResourceSize]


```