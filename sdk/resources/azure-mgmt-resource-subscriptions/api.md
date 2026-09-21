```py
namespace azure.mgmt.resource.subscriptions

    class azure.mgmt.resource.subscriptions.SubscriptionClient(_SubscriptionClientOperationsMixin): implements ContextManager 
        operations: Operations
        subscriptions: SubscriptionsOperations
        tenants: TenantsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def check_resource_name(
                self, 
                resource_name_definition: Optional[ResourceName] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckResourceNameResult: ...

        @overload
        def check_resource_name(
                self, 
                resource_name_definition: Optional[ResourceName] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckResourceNameResult: ...

        @overload
        def check_resource_name(
                self, 
                resource_name_definition: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckResourceNameResult: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.resource.subscriptions.aio

    class azure.mgmt.resource.subscriptions.aio.SubscriptionClient(_SubscriptionClientOperationsMixin): implements AsyncContextManager 
        operations: Operations
        subscriptions: SubscriptionsOperations
        tenants: TenantsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def check_resource_name(
                self, 
                resource_name_definition: Optional[ResourceName] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckResourceNameResult: ...

        @overload
        async def check_resource_name(
                self, 
                resource_name_definition: Optional[ResourceName] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckResourceNameResult: ...

        @overload
        async def check_resource_name(
                self, 
                resource_name_definition: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckResourceNameResult: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.resource.subscriptions.aio.operations

    class azure.mgmt.resource.subscriptions.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.resource.subscriptions.aio.operations.SubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def check_zone_peers(
                self, 
                subscription_id: str, 
                parameters: CheckZonePeersRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckZonePeersResult: ...

        @overload
        async def check_zone_peers(
                self, 
                subscription_id: str, 
                parameters: CheckZonePeersRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckZonePeersResult: ...

        @overload
        async def check_zone_peers(
                self, 
                subscription_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckZonePeersResult: ...

        @distributed_trace_async
        async def get(
                self, 
                subscription_id: str, 
                **kwargs: Any
            ) -> Subscription: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Subscription]: ...

        @distributed_trace
        def list_locations(
                self, 
                subscription_id: str, 
                *, 
                include_extended_locations: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Location]: ...


    class azure.mgmt.resource.subscriptions.aio.operations.TenantsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[TenantIdDescription]: ...


namespace azure.mgmt.resource.subscriptions.models

    class azure.mgmt.resource.subscriptions.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.resource.subscriptions.models.AvailabilityZoneMappings(_Model):
        logical_zone: Optional[str]
        physical_zone: Optional[str]


    class azure.mgmt.resource.subscriptions.models.AvailabilityZonePeers(_Model):
        availability_zone: Optional[str]
        peers: Optional[list[Peers]]

        @overload
        def __init__(
                self, 
                *, 
                peers: Optional[list[Peers]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.subscriptions.models.CheckResourceNameResult(_Model):
        name: Optional[str]
        status: Optional[Union[str, ResourceNameStatus]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                status: Optional[Union[str, ResourceNameStatus]] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.subscriptions.models.CheckZonePeersRequest(_Model):
        location: Optional[str]
        subscription_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                subscription_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.subscriptions.models.CheckZonePeersResult(_Model):
        availability_zone_peers: Optional[list[AvailabilityZonePeers]]
        location: Optional[str]
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                availability_zone_peers: Optional[list[AvailabilityZonePeers]] = ..., 
                location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.subscriptions.models.CloudError(_Model):
        error: Optional[ErrorResponse]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponse] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.subscriptions.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.resource.subscriptions.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.resource.subscriptions.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.subscriptions.models.Location(_Model):
        availability_zone_mappings: Optional[list[AvailabilityZoneMappings]]
        display_name: Optional[str]
        id: Optional[str]
        metadata: Optional[LocationMetadata]
        name: Optional[str]
        regional_display_name: Optional[str]
        subscription_id: Optional[str]
        type: Optional[Union[str, LocationType]]

        @overload
        def __init__(
                self, 
                *, 
                availability_zone_mappings: Optional[list[AvailabilityZoneMappings]] = ..., 
                metadata: Optional[LocationMetadata] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.subscriptions.models.LocationMetadata(_Model):
        geography: Optional[str]
        geography_group: Optional[str]
        home_location: Optional[str]
        latitude: Optional[str]
        longitude: Optional[str]
        paired_region: Optional[list[PairedRegion]]
        physical_location: Optional[str]
        region_category: Optional[Union[str, RegionCategory]]
        region_type: Optional[Union[str, RegionType]]

        @overload
        def __init__(
                self, 
                *, 
                paired_region: Optional[list[PairedRegion]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.subscriptions.models.LocationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EDGE_ZONE = "EdgeZone"
        REGION = "Region"


    class azure.mgmt.resource.subscriptions.models.ManagedByTenant(_Model):
        tenant_id: Optional[str]


    class azure.mgmt.resource.subscriptions.models.Operation(_Model):
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


    class azure.mgmt.resource.subscriptions.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.resource.subscriptions.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.resource.subscriptions.models.PairedRegion(_Model):
        id: Optional[str]
        name: Optional[str]
        subscription_id: Optional[str]


    class azure.mgmt.resource.subscriptions.models.Peers(_Model):
        availability_zone: Optional[str]
        subscription_id: Optional[str]


    class azure.mgmt.resource.subscriptions.models.RegionCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTENDED = "Extended"
        OTHER = "Other"
        RECOMMENDED = "Recommended"


    class azure.mgmt.resource.subscriptions.models.RegionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOGICAL = "Logical"
        PHYSICAL = "Physical"


    class azure.mgmt.resource.subscriptions.models.ResourceName(_Model):
        name: str
        type: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.subscriptions.models.ResourceNameStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED = "Allowed"
        RESERVED = "Reserved"


    class azure.mgmt.resource.subscriptions.models.SpendingLimit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CURRENT_PERIOD_OFF = "CurrentPeriodOff"
        OFF = "Off"
        ON = "On"


    class azure.mgmt.resource.subscriptions.models.Subscription(_Model):
        authorization_source: Optional[str]
        display_name: Optional[str]
        id: Optional[str]
        managed_by_tenants: Optional[list[ManagedByTenant]]
        state: Optional[Union[str, SubscriptionState]]
        subscription_id: Optional[str]
        subscription_policies: Optional[SubscriptionPolicies]
        tags: Optional[dict[str, str]]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                authorization_source: Optional[str] = ..., 
                managed_by_tenants: Optional[list[ManagedByTenant]] = ..., 
                subscription_policies: Optional[SubscriptionPolicies] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resource.subscriptions.models.SubscriptionPolicies(_Model):
        location_placement_id: Optional[str]
        quota_id: Optional[str]
        spending_limit: Optional[Union[str, SpendingLimit]]


    class azure.mgmt.resource.subscriptions.models.SubscriptionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETED = "Deleted"
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        PAST_DUE = "PastDue"
        WARNED = "Warned"


    class azure.mgmt.resource.subscriptions.models.TenantCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HOME = "Home"
        MANAGED_BY = "ManagedBy"
        PROJECTED_BY = "ProjectedBy"


    class azure.mgmt.resource.subscriptions.models.TenantIdDescription(_Model):
        country: Optional[str]
        country_code: Optional[str]
        default_domain: Optional[str]
        display_name: Optional[str]
        domains: Optional[list[str]]
        id: Optional[str]
        tenant_branding_logo_url: Optional[str]
        tenant_category: Optional[Union[str, TenantCategory]]
        tenant_id: Optional[str]
        tenant_type: Optional[str]


namespace azure.mgmt.resource.subscriptions.operations

    class azure.mgmt.resource.subscriptions.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.resource.subscriptions.operations.SubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def check_zone_peers(
                self, 
                subscription_id: str, 
                parameters: CheckZonePeersRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckZonePeersResult: ...

        @overload
        def check_zone_peers(
                self, 
                subscription_id: str, 
                parameters: CheckZonePeersRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckZonePeersResult: ...

        @overload
        def check_zone_peers(
                self, 
                subscription_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckZonePeersResult: ...

        @distributed_trace
        def get(
                self, 
                subscription_id: str, 
                **kwargs: Any
            ) -> Subscription: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Subscription]: ...

        @distributed_trace
        def list_locations(
                self, 
                subscription_id: str, 
                *, 
                include_extended_locations: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Location]: ...


    class azure.mgmt.resource.subscriptions.operations.TenantsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[TenantIdDescription]: ...


namespace azure.mgmt.resource.subscriptions.types

    class azure.mgmt.resource.subscriptions.types.CheckZonePeersRequest(TypedDict, total=False):
        key "location": str
        location: str
        subscriptionIds: list[str]
        subscription_ids: list[str]


    class azure.mgmt.resource.subscriptions.types.ResourceName(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[str]
        name: str
        type: str


```