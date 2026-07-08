```py
namespace azure.mgmt.computelimit

    class azure.mgmt.computelimit.ComputeLimitMgmtClient: implements ContextManager 
        features: FeaturesOperations
        guest_subscriptions: GuestSubscriptionsOperations
        member_cap_overrides: MemberCapOverridesOperations
        operations: Operations
        shared_limit_caps: SharedLimitCapsOperations
        shared_limits: SharedLimitsOperations
        vm_families: VmFamiliesOperations

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


namespace azure.mgmt.computelimit.aio

    class azure.mgmt.computelimit.aio.ComputeLimitMgmtClient: implements AsyncContextManager 
        features: FeaturesOperations
        guest_subscriptions: GuestSubscriptionsOperations
        member_cap_overrides: MemberCapOverridesOperations
        operations: Operations
        shared_limit_caps: SharedLimitCapsOperations
        shared_limits: SharedLimitsOperations
        vm_families: VmFamiliesOperations

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


namespace azure.mgmt.computelimit.aio.operations

    class azure.mgmt.computelimit.aio.operations.FeaturesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-30', params_added_on={'2026-04-30': ['api_version', 'subscription_id', 'location', 'feature_name', 'accept']}, api_versions_list=['2026-04-30', '2026-06-01', '2026-07-01'])
        async def begin_disable(
                self, 
                location: str, 
                feature_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_enable(
                self, 
                location: str, 
                feature_name: str, 
                body: Optional[FeatureEnableRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_enable(
                self, 
                location: str, 
                feature_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_enable(
                self, 
                location: str, 
                feature_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-20', params_added_on={'2026-03-20': ['api_version', 'subscription_id', 'location', 'feature_name', 'accept']}, api_versions_list=['2026-03-20', '2026-04-30', '2026-06-01', '2026-07-01'])
        async def get(
                self, 
                location: str, 
                feature_name: str, 
                **kwargs: Any
            ) -> Feature: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-20', params_added_on={'2026-03-20': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-03-20', '2026-04-30', '2026-06-01', '2026-07-01'])
        def list_by_subscription_location_resource(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Feature]: ...


    class azure.mgmt.computelimit.aio.operations.GuestSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                location: str, 
                guest_subscription_id: str, 
                resource: GuestSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestSubscription: ...

        @overload
        async def create(
                self, 
                location: str, 
                guest_subscription_id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestSubscription: ...

        @overload
        async def create(
                self, 
                location: str, 
                guest_subscription_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestSubscription: ...

        @distributed_trace_async
        async def delete(
                self, 
                location: str, 
                guest_subscription_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                guest_subscription_id: str, 
                **kwargs: Any
            ) -> GuestSubscription: ...

        @distributed_trace
        def list_by_subscription_location_resource(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GuestSubscription]: ...


    class azure.mgmt.computelimit.aio.operations.MemberCapOverridesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                location: str, 
                vm_family_name: str, 
                member_subscription_id: str, 
                resource: MemberCapOverride, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemberCapOverride: ...

        @overload
        async def create_or_update(
                self, 
                location: str, 
                vm_family_name: str, 
                member_subscription_id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemberCapOverride: ...

        @overload
        async def create_or_update(
                self, 
                location: str, 
                vm_family_name: str, 
                member_subscription_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemberCapOverride: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'location', 'vm_family_name', 'member_subscription_id']}, api_versions_list=['2026-07-01'])
        async def delete(
                self, 
                location: str, 
                vm_family_name: str, 
                member_subscription_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'location', 'vm_family_name', 'member_subscription_id', 'accept']}, api_versions_list=['2026-07-01'])
        async def get(
                self, 
                location: str, 
                vm_family_name: str, 
                member_subscription_id: str, 
                **kwargs: Any
            ) -> MemberCapOverride: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'location', 'vm_family_name', 'accept']}, api_versions_list=['2026-07-01'])
        def list_by_parent(
                self, 
                location: str, 
                vm_family_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MemberCapOverride]: ...


    class azure.mgmt.computelimit.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.computelimit.aio.operations.SharedLimitCapsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                location: str, 
                vm_family_name: str, 
                resource: SharedLimitCap, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SharedLimitCap: ...

        @overload
        async def create_or_update(
                self, 
                location: str, 
                vm_family_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SharedLimitCap: ...

        @overload
        async def create_or_update(
                self, 
                location: str, 
                vm_family_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SharedLimitCap: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'location', 'vm_family_name']}, api_versions_list=['2026-07-01'])
        async def delete(
                self, 
                location: str, 
                vm_family_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'location', 'vm_family_name', 'accept']}, api_versions_list=['2026-07-01'])
        async def get(
                self, 
                location: str, 
                vm_family_name: str, 
                **kwargs: Any
            ) -> SharedLimitCap: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-07-01'])
        def list_by_subscription_location_resource(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SharedLimitCap]: ...

        @overload
        async def set_member_cap_overrides(
                self, 
                location: str, 
                vm_family_name: str, 
                body: SetMemberCapOverridesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SetMemberCapOverridesResult: ...

        @overload
        async def set_member_cap_overrides(
                self, 
                location: str, 
                vm_family_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SetMemberCapOverridesResult: ...

        @overload
        async def set_member_cap_overrides(
                self, 
                location: str, 
                vm_family_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SetMemberCapOverridesResult: ...


    class azure.mgmt.computelimit.aio.operations.SharedLimitsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                location: str, 
                name: str, 
                resource: SharedLimit, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SharedLimit: ...

        @overload
        async def create(
                self, 
                location: str, 
                name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SharedLimit: ...

        @overload
        async def create(
                self, 
                location: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SharedLimit: ...

        @distributed_trace_async
        async def delete(
                self, 
                location: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                name: str, 
                **kwargs: Any
            ) -> SharedLimit: ...

        @distributed_trace
        def list_by_subscription_location_resource(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SharedLimit]: ...


    class azure.mgmt.computelimit.aio.operations.VmFamiliesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-30', params_added_on={'2026-04-30': ['api_version', 'subscription_id', 'location', 'vm_family_name', 'accept']}, api_versions_list=['2026-04-30', '2026-06-01', '2026-07-01'])
        async def get(
                self, 
                location: str, 
                vm_family_name: str, 
                **kwargs: Any
            ) -> VmFamily: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-30', params_added_on={'2026-04-30': ['api_version', 'subscription_id', 'location', 'filter', 'accept']}, api_versions_list=['2026-04-30', '2026-06-01', '2026-07-01'])
        def list_by_subscription_location_resource(
                self, 
                location: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VmFamily]: ...


namespace azure.mgmt.computelimit.models

    class azure.mgmt.computelimit.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.computelimit.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.computelimit.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.computelimit.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.computelimit.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computelimit.models.Feature(ProxyResource):
        id: str
        name: str
        properties: Optional[FeatureProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FeatureProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computelimit.models.FeatureEnableRequest(_Model):
        service_tree_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                service_tree_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computelimit.models.FeatureProperties(_Model):
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        state: Optional[Union[str, FeatureState]]

        @overload
        def __init__(
                self, 
                *, 
                state: Optional[Union[str, FeatureState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computelimit.models.FeatureState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.computelimit.models.GuestSubscription(ProxyResource):
        id: str
        name: str
        properties: Optional[GuestSubscriptionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GuestSubscriptionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computelimit.models.GuestSubscriptionProperties(_Model):
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]


    class azure.mgmt.computelimit.models.LimitName(_Model):
        localized_value: Optional[str]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computelimit.models.MemberCap(_Model):
        cap: int
        subscription_id: str

        @overload
        def __init__(
                self, 
                *, 
                cap: int, 
                subscription_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computelimit.models.MemberCapOverride(ProxyResource):
        id: str
        name: str
        properties: Optional[MemberCapOverrideProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MemberCapOverrideProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computelimit.models.MemberCapOverrideProperties(_Model):
        cap: int
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                cap: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computelimit.models.Operation(_Model):
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


    class azure.mgmt.computelimit.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.computelimit.models.OperationStatusResult(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computelimit.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.computelimit.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.computelimit.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.computelimit.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.computelimit.models.SetMemberCapOverridesRequest(_Model):
        member_cap_overrides: list[MemberCap]

        @overload
        def __init__(
                self, 
                *, 
                member_cap_overrides: list[MemberCap]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computelimit.models.SetMemberCapOverridesResult(_Model):
        member_cap_overrides: list[MemberCap]

        @overload
        def __init__(
                self, 
                *, 
                member_cap_overrides: list[MemberCap]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computelimit.models.SharedLimit(ProxyResource):
        id: str
        name: str
        properties: Optional[SharedLimitProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SharedLimitProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computelimit.models.SharedLimitCap(ProxyResource):
        id: str
        name: str
        properties: Optional[SharedLimitCapProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SharedLimitCapProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computelimit.models.SharedLimitCapProperties(_Model):
        default_member_cap: Optional[int]
        is_bounded_cap: bool
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                default_member_cap: Optional[int] = ..., 
                is_bounded_cap: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computelimit.models.SharedLimitProperties(_Model):
        limit: Optional[int]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        resource_name: Optional[LimitName]
        unit: Optional[str]


    class azure.mgmt.computelimit.models.SystemData(_Model):
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


    class azure.mgmt.computelimit.models.VmFamily(ProxyResource):
        id: str
        name: str
        properties: Optional[VmFamilyProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VmFamilyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computelimit.models.VmFamilyProperties(_Model):
        category: Optional[str]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.computelimit.operations

    class azure.mgmt.computelimit.operations.FeaturesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-30', params_added_on={'2026-04-30': ['api_version', 'subscription_id', 'location', 'feature_name', 'accept']}, api_versions_list=['2026-04-30', '2026-06-01', '2026-07-01'])
        def begin_disable(
                self, 
                location: str, 
                feature_name: str, 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_enable(
                self, 
                location: str, 
                feature_name: str, 
                body: Optional[FeatureEnableRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_enable(
                self, 
                location: str, 
                feature_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_enable(
                self, 
                location: str, 
                feature_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-20', params_added_on={'2026-03-20': ['api_version', 'subscription_id', 'location', 'feature_name', 'accept']}, api_versions_list=['2026-03-20', '2026-04-30', '2026-06-01', '2026-07-01'])
        def get(
                self, 
                location: str, 
                feature_name: str, 
                **kwargs: Any
            ) -> Feature: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-20', params_added_on={'2026-03-20': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-03-20', '2026-04-30', '2026-06-01', '2026-07-01'])
        def list_by_subscription_location_resource(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[Feature]: ...


    class azure.mgmt.computelimit.operations.GuestSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                location: str, 
                guest_subscription_id: str, 
                resource: GuestSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestSubscription: ...

        @overload
        def create(
                self, 
                location: str, 
                guest_subscription_id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestSubscription: ...

        @overload
        def create(
                self, 
                location: str, 
                guest_subscription_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestSubscription: ...

        @distributed_trace
        def delete(
                self, 
                location: str, 
                guest_subscription_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                guest_subscription_id: str, 
                **kwargs: Any
            ) -> GuestSubscription: ...

        @distributed_trace
        def list_by_subscription_location_resource(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[GuestSubscription]: ...


    class azure.mgmt.computelimit.operations.MemberCapOverridesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                location: str, 
                vm_family_name: str, 
                member_subscription_id: str, 
                resource: MemberCapOverride, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemberCapOverride: ...

        @overload
        def create_or_update(
                self, 
                location: str, 
                vm_family_name: str, 
                member_subscription_id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemberCapOverride: ...

        @overload
        def create_or_update(
                self, 
                location: str, 
                vm_family_name: str, 
                member_subscription_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemberCapOverride: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'location', 'vm_family_name', 'member_subscription_id']}, api_versions_list=['2026-07-01'])
        def delete(
                self, 
                location: str, 
                vm_family_name: str, 
                member_subscription_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'location', 'vm_family_name', 'member_subscription_id', 'accept']}, api_versions_list=['2026-07-01'])
        def get(
                self, 
                location: str, 
                vm_family_name: str, 
                member_subscription_id: str, 
                **kwargs: Any
            ) -> MemberCapOverride: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'location', 'vm_family_name', 'accept']}, api_versions_list=['2026-07-01'])
        def list_by_parent(
                self, 
                location: str, 
                vm_family_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MemberCapOverride]: ...


    class azure.mgmt.computelimit.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.computelimit.operations.SharedLimitCapsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                location: str, 
                vm_family_name: str, 
                resource: SharedLimitCap, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SharedLimitCap: ...

        @overload
        def create_or_update(
                self, 
                location: str, 
                vm_family_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SharedLimitCap: ...

        @overload
        def create_or_update(
                self, 
                location: str, 
                vm_family_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SharedLimitCap: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'location', 'vm_family_name']}, api_versions_list=['2026-07-01'])
        def delete(
                self, 
                location: str, 
                vm_family_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'location', 'vm_family_name', 'accept']}, api_versions_list=['2026-07-01'])
        def get(
                self, 
                location: str, 
                vm_family_name: str, 
                **kwargs: Any
            ) -> SharedLimitCap: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01', params_added_on={'2026-07-01': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-07-01'])
        def list_by_subscription_location_resource(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[SharedLimitCap]: ...

        @overload
        def set_member_cap_overrides(
                self, 
                location: str, 
                vm_family_name: str, 
                body: SetMemberCapOverridesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SetMemberCapOverridesResult: ...

        @overload
        def set_member_cap_overrides(
                self, 
                location: str, 
                vm_family_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SetMemberCapOverridesResult: ...

        @overload
        def set_member_cap_overrides(
                self, 
                location: str, 
                vm_family_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SetMemberCapOverridesResult: ...


    class azure.mgmt.computelimit.operations.SharedLimitsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                location: str, 
                name: str, 
                resource: SharedLimit, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SharedLimit: ...

        @overload
        def create(
                self, 
                location: str, 
                name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SharedLimit: ...

        @overload
        def create(
                self, 
                location: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SharedLimit: ...

        @distributed_trace
        def delete(
                self, 
                location: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                name: str, 
                **kwargs: Any
            ) -> SharedLimit: ...

        @distributed_trace
        def list_by_subscription_location_resource(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[SharedLimit]: ...


    class azure.mgmt.computelimit.operations.VmFamiliesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-30', params_added_on={'2026-04-30': ['api_version', 'subscription_id', 'location', 'vm_family_name', 'accept']}, api_versions_list=['2026-04-30', '2026-06-01', '2026-07-01'])
        def get(
                self, 
                location: str, 
                vm_family_name: str, 
                **kwargs: Any
            ) -> VmFamily: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-30', params_added_on={'2026-04-30': ['api_version', 'subscription_id', 'location', 'filter', 'accept']}, api_versions_list=['2026-04-30', '2026-06-01', '2026-07-01'])
        def list_by_subscription_location_resource(
                self, 
                location: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VmFamily]: ...


```