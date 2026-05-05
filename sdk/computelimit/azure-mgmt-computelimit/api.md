```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.computelimit

    class azure.mgmt.computelimit.ComputeLimitMgmtClient: implements ContextManager 
        features: FeaturesOperations
        guest_subscriptions: GuestSubscriptionsOperations
        operations: Operations
        shared_limits: SharedLimitsOperations

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
        operations: Operations
        shared_limits: SharedLimitsOperations

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
        @api_version_validation(method_added_on='2026-03-20', params_added_on={'2026-03-20': ['api_version', 'subscription_id', 'location', 'feature_name', 'accept']}, api_versions_list=['2026-03-20'])
        async def begin_enable(
                self, 
                location: str, 
                feature_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-20', params_added_on={'2026-03-20': ['api_version', 'subscription_id', 'location', 'feature_name', 'accept']}, api_versions_list=['2026-03-20'])
        async def get(
                self, 
                location: str, 
                feature_name: str, 
                **kwargs: Any
            ) -> Feature: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-20', params_added_on={'2026-03-20': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-03-20'])
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


    class azure.mgmt.computelimit.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


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


namespace azure.mgmt.computelimit.operations

    class azure.mgmt.computelimit.operations.FeaturesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-20', params_added_on={'2026-03-20': ['api_version', 'subscription_id', 'location', 'feature_name', 'accept']}, api_versions_list=['2026-03-20'])
        def begin_enable(
                self, 
                location: str, 
                feature_name: str, 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-20', params_added_on={'2026-03-20': ['api_version', 'subscription_id', 'location', 'feature_name', 'accept']}, api_versions_list=['2026-03-20'])
        def get(
                self, 
                location: str, 
                feature_name: str, 
                **kwargs: Any
            ) -> Feature: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-20', params_added_on={'2026-03-20': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-03-20'])
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


    class azure.mgmt.computelimit.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


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


```