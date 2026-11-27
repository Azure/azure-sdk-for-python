```py
namespace azure.mgmt.saas

    class azure.mgmt.saas.SaaSMgmtClient: implements ContextManager 
        operations: Operations
        saas_operation_statuses: SaasOperationStatusesOperations
        saas_subscription_level: SaasSubscriptionLevelOperations
        saas_subscription_level_global: SaasSubscriptionLevelGlobalOperations
        saas_tenant_level: SaasTenantLevelOperations

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


namespace azure.mgmt.saas.aio

    class azure.mgmt.saas.aio.SaaSMgmtClient: implements AsyncContextManager 
        operations: Operations
        saas_operation_statuses: SaasOperationStatusesOperations
        saas_subscription_level: SaasSubscriptionLevelOperations
        saas_subscription_level_global: SaasSubscriptionLevelGlobalOperations
        saas_tenant_level: SaasTenantLevelOperations

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


namespace azure.mgmt.saas.aio.operations

    class azure.mgmt.saas.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.saas.aio.operations.SaasOperationStatusesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_subscription_operation_status(
                self, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...

        @distributed_trace_async
        async def get_tenant_operation_status(
                self, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


    class azure.mgmt.saas.aio.operations.SaasSubscriptionLevelGlobalOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def check_name_availability(
                self, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @distributed_trace
        def list_by_azure_subscription(self, **kwargs: Any) -> AsyncItemPaged[SaasResource]: ...

        @overload
        async def validate_purchase(
                self, 
                resource_group_name: str, 
                body: SaasPurchaseValidationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...

        @overload
        async def validate_purchase(
                self, 
                resource_group_name: str, 
                body: SaasPurchaseValidationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...

        @overload
        async def validate_purchase(
                self, 
                resource_group_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...

        @overload
        async def validate_purchase_by_subscription(
                self, 
                body: SaasPurchaseValidationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...

        @overload
        async def validate_purchase_by_subscription(
                self, 
                body: SaasPurchaseValidationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...

        @overload
        async def validate_purchase_by_subscription(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...


    class azure.mgmt.saas.aio.operations.SaasSubscriptionLevelOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                resource: SaasResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SaasResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                resource: SaasResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SaasResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SaasResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_unsubscribe(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: UnsubscribeOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SaasResource]: ...

        @overload
        async def begin_unsubscribe(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: UnsubscribeOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SaasResource]: ...

        @overload
        async def begin_unsubscribe(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SaasResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: SaasResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SaasResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: SaasResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SaasResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SaasResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                expand_customer_data: Optional[bool] = ..., 
                **kwargs: Any
            ) -> SaasResource: ...

        @distributed_trace_async
        async def list_access_token(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AccessTokenResult: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SaasResource]: ...

        @overload
        async def validate_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: SaasResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...

        @overload
        async def validate_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: SaasResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...

        @overload
        async def validate_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...


    class azure.mgmt.saas.aio.operations.SaasTenantLevelOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete_resource(
                self, 
                resource_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_resource(
                self, 
                resource_id: str, 
                properties: SaasTenantResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SaasTenantResource]: ...

        @overload
        async def begin_update_resource(
                self, 
                resource_id: str, 
                properties: SaasTenantResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SaasTenantResource]: ...

        @overload
        async def begin_update_resource(
                self, 
                resource_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SaasTenantResource]: ...

        @distributed_trace_async
        async def get_resource(
                self, 
                resource_id: str, 
                *, 
                expand_customer_data: Optional[bool] = ..., 
                **kwargs: Any
            ) -> SaasTenantResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[SaasTenantResource]: ...

        @distributed_trace_async
        async def list_access_token(
                self, 
                resource_id: str, 
                **kwargs: Any
            ) -> AccessTokenResult: ...


namespace azure.mgmt.saas.models

    class azure.mgmt.saas.models.AccessTokenResult(_Model):
        expiry_time: Optional[datetime]
        offer_uri_with_token: Optional[str]
        publisher_offer_base_uri: Optional[str]
        token: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                expiry_time: Optional[datetime] = ..., 
                offer_uri_with_token: Optional[str] = ..., 
                publisher_offer_base_uri: Optional[str] = ..., 
                token: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.saas.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.saas.models.CheckNameAvailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.saas.models.CheckNameAvailabilityRequest(_Model):
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


    class azure.mgmt.saas.models.CheckNameAvailabilityResponse(_Model):
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


    class azure.mgmt.saas.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.saas.models.DeletionSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SUBSCRIPTION_DELETION = "AzureSubscriptionDeletion"
        CUSTOMER_CANCELLATION = "CustomerCancellation"


    class azure.mgmt.saas.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.saas.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.saas.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.saas.models.Operation(_Model):
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


    class azure.mgmt.saas.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.saas.models.OperationStatusResult(_Model):
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


    class azure.mgmt.saas.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.saas.models.PatchIntent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESET = "Reset"
        RETAIN = "Retain"
        SCHEDULE_CHANGE = "ScheduleChange"


    class azure.mgmt.saas.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.saas.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.saas.models.ResourceValidationError(_Model):
        code: str
        message: str

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.saas.models.ResourceValidationResult(_Model):
        details: list[ResourceValidationError]
        is_valid: bool

        @overload
        def __init__(
                self, 
                *, 
                details: list[ResourceValidationError], 
                is_valid: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.saas.models.SaasProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NOT_STARTED = "NotStarted"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.saas.models.SaasPurchaseValidationProperties(_Model):
        asset_id: Optional[str]
        auto_renew: Optional[bool]
        billing_period: Optional[str]
        description: Optional[str]
        future_start_date: Optional[datetime]
        intent: Optional[Union[str, PatchIntent]]
        is_free_trial: Optional[bool]
        name: str
        offer_name: Optional[str]
        plan_name: Optional[str]
        private_offer_id: Optional[str]
        product_code: Optional[str]
        provisioning_state: Optional[Union[str, SaasProvisioningState]]
        publisher_name: Optional[str]
        purchaser_email: Optional[str]
        quantity: Optional[int]
        quote_id: Optional[str]
        risk_property_bag_header: Optional[str]
        status: Optional[Union[str, SaasResourceStatus]]
        status_reason: Optional[Union[str, SubscriptionStatusReason]]
        storefront: Optional[str]
        term_end_date: Optional[datetime]
        term_start_date: Optional[datetime]
        term_unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_renew: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                intent: Optional[Union[str, PatchIntent]] = ..., 
                name: str, 
                private_offer_id: Optional[str] = ..., 
                product_code: Optional[str] = ..., 
                quantity: Optional[int] = ..., 
                quote_id: Optional[str] = ..., 
                risk_property_bag_header: Optional[str] = ..., 
                storefront: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.saas.models.SaasPurchaseValidationRequest(_Model):
        location: str
        properties: SaasPurchaseValidationProperties
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: SaasPurchaseValidationProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.saas.models.SaasResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[SaasResourceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[SaasResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.saas.models.SaasResourceProperties(_Model):
        asset_id: Optional[str]
        auto_renew: Optional[bool]
        billing_period: Optional[str]
        description: Optional[str]
        future_start_date: Optional[datetime]
        intent: Optional[Union[str, PatchIntent]]
        is_free_trial: Optional[bool]
        offer_name: Optional[str]
        plan_name: Optional[str]
        private_offer_id: Optional[str]
        product_code: Optional[str]
        provisioning_state: Optional[Union[str, SaasProvisioningState]]
        publisher_name: Optional[str]
        purchaser_email: Optional[str]
        quantity: Optional[int]
        quote_id: Optional[str]
        risk_property_bag_header: Optional[str]
        status: Optional[Union[str, SaasResourceStatus]]
        status_reason: Optional[Union[str, SubscriptionStatusReason]]
        storefront: Optional[str]
        term_end_date: Optional[datetime]
        term_start_date: Optional[datetime]
        term_unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_renew: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                intent: Optional[Union[str, PatchIntent]] = ..., 
                private_offer_id: Optional[str] = ..., 
                product_code: Optional[str] = ..., 
                quantity: Optional[int] = ..., 
                quote_id: Optional[str] = ..., 
                risk_property_bag_header: Optional[str] = ..., 
                storefront: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.saas.models.SaasResourceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_STARTED = "NotStarted"
        PENDING_FULFILLMENT_START = "PendingFulfillmentStart"
        SUBSCRIBED = "Subscribed"
        SUSPENDED = "Suspended"
        UNSUBSCRIBED = "Unsubscribed"


    class azure.mgmt.saas.models.SaasResourceUpdate(_Model):
        properties: Optional[SaasResourceUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SaasResourceUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.saas.models.SaasResourceUpdateProperties(_Model):
        auto_renew: Optional[bool]
        description: Optional[str]
        intent: Optional[Union[str, PatchIntent]]
        private_offer_id: Optional[str]
        product_code: Optional[str]
        quantity: Optional[int]
        quote_id: Optional[str]
        risk_property_bag_header: Optional[str]
        storefront: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_renew: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                intent: Optional[Union[str, PatchIntent]] = ..., 
                private_offer_id: Optional[str] = ..., 
                product_code: Optional[str] = ..., 
                quantity: Optional[int] = ..., 
                quote_id: Optional[str] = ..., 
                risk_property_bag_header: Optional[str] = ..., 
                storefront: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.saas.models.SaasTenantResource(ProxyResource):
        id: str
        name: str
        properties: Optional[SaasResourceProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SaasResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.saas.models.SaasTenantResourceUpdate(_Model):
        properties: Optional[SaasTenantResourceUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SaasTenantResourceUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.saas.models.SaasTenantResourceUpdateProperties(_Model):
        auto_renew: Optional[bool]
        description: Optional[str]
        intent: Optional[Union[str, PatchIntent]]
        private_offer_id: Optional[str]
        product_code: Optional[str]
        quantity: Optional[int]
        quote_id: Optional[str]
        risk_property_bag_header: Optional[str]
        storefront: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_renew: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                intent: Optional[Union[str, PatchIntent]] = ..., 
                private_offer_id: Optional[str] = ..., 
                product_code: Optional[str] = ..., 
                quantity: Optional[int] = ..., 
                quote_id: Optional[str] = ..., 
                risk_property_bag_header: Optional[str] = ..., 
                storefront: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.saas.models.SubscriptionStatusReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SUBSCRIPTION_DELETION = "AzureSubscriptionDeletion"
        NONE = "None"
        SUSPENDED_INTERNAL = "SuspendedInternal"


    class azure.mgmt.saas.models.SystemData(_Model):
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


    class azure.mgmt.saas.models.TrackedResource(Resource):
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


    class azure.mgmt.saas.models.UnsubscribeOptions(_Model):
        deletion_source: Optional[Union[str, DeletionSource]]
        feedback: Optional[str]
        reason_code: Optional[int]
        unsubscribe_only: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                deletion_source: Optional[Union[str, DeletionSource]] = ..., 
                feedback: Optional[str] = ..., 
                reason_code: Optional[int] = ..., 
                unsubscribe_only: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.saas.operations

    class azure.mgmt.saas.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.saas.operations.SaasOperationStatusesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_subscription_operation_status(
                self, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...

        @distributed_trace
        def get_tenant_operation_status(
                self, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


    class azure.mgmt.saas.operations.SaasSubscriptionLevelGlobalOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def check_name_availability(
                self, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @distributed_trace
        def list_by_azure_subscription(self, **kwargs: Any) -> ItemPaged[SaasResource]: ...

        @overload
        def validate_purchase(
                self, 
                resource_group_name: str, 
                body: SaasPurchaseValidationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...

        @overload
        def validate_purchase(
                self, 
                resource_group_name: str, 
                body: SaasPurchaseValidationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...

        @overload
        def validate_purchase(
                self, 
                resource_group_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...

        @overload
        def validate_purchase_by_subscription(
                self, 
                body: SaasPurchaseValidationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...

        @overload
        def validate_purchase_by_subscription(
                self, 
                body: SaasPurchaseValidationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...

        @overload
        def validate_purchase_by_subscription(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...


    class azure.mgmt.saas.operations.SaasSubscriptionLevelOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                resource: SaasResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SaasResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                resource: SaasResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SaasResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SaasResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_unsubscribe(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: UnsubscribeOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SaasResource]: ...

        @overload
        def begin_unsubscribe(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: UnsubscribeOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SaasResource]: ...

        @overload
        def begin_unsubscribe(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SaasResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: SaasResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SaasResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: SaasResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SaasResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SaasResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                expand_customer_data: Optional[bool] = ..., 
                **kwargs: Any
            ) -> SaasResource: ...

        @distributed_trace
        def list_access_token(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AccessTokenResult: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SaasResource]: ...

        @overload
        def validate_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: SaasResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...

        @overload
        def validate_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: SaasResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...

        @overload
        def validate_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...


    class azure.mgmt.saas.operations.SaasTenantLevelOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete_resource(
                self, 
                resource_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_resource(
                self, 
                resource_id: str, 
                properties: SaasTenantResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SaasTenantResource]: ...

        @overload
        def begin_update_resource(
                self, 
                resource_id: str, 
                properties: SaasTenantResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SaasTenantResource]: ...

        @overload
        def begin_update_resource(
                self, 
                resource_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SaasTenantResource]: ...

        @distributed_trace
        def get_resource(
                self, 
                resource_id: str, 
                *, 
                expand_customer_data: Optional[bool] = ..., 
                **kwargs: Any
            ) -> SaasTenantResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[SaasTenantResource]: ...

        @distributed_trace
        def list_access_token(
                self, 
                resource_id: str, 
                **kwargs: Any
            ) -> AccessTokenResult: ...


namespace azure.mgmt.saas.types

    class azure.mgmt.saas.types.CheckNameAvailabilityRequest(TypedDict, total=False):
        key "name": str
        key "type": str
        name: str
        type: str


    class azure.mgmt.saas.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.saas.types.SaasPurchaseValidationProperties(TypedDict, total=False):
        key "assetId": str
        key "autoRenew": bool
        key "billingPeriod": str
        key "description": str
        key "futureStartDate": str
        key "intent": Union[str, PatchIntent]
        key "isFreeTrial": bool
        key "name": Required[str]
        key "offerName": str
        key "planName": str
        key "privateOfferId": str
        key "productCode": str
        key "provisioningState": Union[str, SaasProvisioningState]
        key "publisherName": str
        key "purchaserEmail": str
        key "quantity": int
        key "quoteId": str
        key "riskPropertyBagHeader": str
        key "status": Union[str, SaasResourceStatus]
        key "statusReason": Union[str, SubscriptionStatusReason]
        key "storefront": str
        key "termEndDate": str
        key "termStartDate": str
        key "termUnit": str
        assetId: str
        autoRenew: bool
        billingPeriod: str
        description: str
        futureStartDate: str
        intent: Union[str, PatchIntent]
        isFreeTrial: bool
        name: str
        offerName: str
        planName: str
        privateOfferId: str
        productCode: str
        provisioningState: Union[str, SaasProvisioningState]
        publisherName: str
        purchaserEmail: str
        quantity: int
        quoteId: str
        riskPropertyBagHeader: str
        status: Union[str, SaasResourceStatus]
        statusReason: Union[str, SubscriptionStatusReason]
        storefront: str
        termEndDate: str
        termStartDate: str
        termUnit: str


    class azure.mgmt.saas.types.SaasPurchaseValidationRequest(TypedDict, total=False):
        key "location": Required[str]
        key "properties": Required[SaasPurchaseValidationProperties]
        location: str
        properties: SaasPurchaseValidationProperties
        tags: dict[str, str]


    class azure.mgmt.saas.types.SaasResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('SaasResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: SaasResourceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.saas.types.SaasResourceProperties(TypedDict, total=False):
        key "assetId": str
        key "autoRenew": bool
        key "billingPeriod": str
        key "description": str
        key "futureStartDate": str
        key "intent": Union[str, PatchIntent]
        key "isFreeTrial": bool
        key "offerName": str
        key "planName": str
        key "privateOfferId": str
        key "productCode": str
        key "provisioningState": Union[str, SaasProvisioningState]
        key "publisherName": str
        key "purchaserEmail": str
        key "quantity": int
        key "quoteId": str
        key "riskPropertyBagHeader": str
        key "status": Union[str, SaasResourceStatus]
        key "statusReason": Union[str, SubscriptionStatusReason]
        key "storefront": str
        key "termEndDate": str
        key "termStartDate": str
        key "termUnit": str
        assetId: str
        autoRenew: bool
        billingPeriod: str
        description: str
        futureStartDate: str
        intent: Union[str, PatchIntent]
        isFreeTrial: bool
        offerName: str
        planName: str
        privateOfferId: str
        productCode: str
        provisioningState: Union[str, SaasProvisioningState]
        publisherName: str
        purchaserEmail: str
        quantity: int
        quoteId: str
        riskPropertyBagHeader: str
        status: Union[str, SaasResourceStatus]
        statusReason: Union[str, SubscriptionStatusReason]
        storefront: str
        termEndDate: str
        termStartDate: str
        termUnit: str


    class azure.mgmt.saas.types.SaasResourceUpdate(TypedDict, total=False):
        key "properties": ForwardRef('SaasResourceUpdateProperties', module='types')
        properties: SaasResourceUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.saas.types.SaasResourceUpdateProperties(TypedDict, total=False):
        key "autoRenew": bool
        key "description": str
        key "intent": Union[str, PatchIntent]
        key "privateOfferId": str
        key "productCode": str
        key "quantity": int
        key "quoteId": str
        key "riskPropertyBagHeader": str
        key "storefront": str
        autoRenew: bool
        description: str
        intent: Union[str, PatchIntent]
        privateOfferId: str
        productCode: str
        quantity: int
        quoteId: str
        riskPropertyBagHeader: str
        storefront: str


    class azure.mgmt.saas.types.SaasTenantResourceUpdate(TypedDict, total=False):
        key "properties": ForwardRef('SaasTenantResourceUpdateProperties', module='types')
        properties: SaasTenantResourceUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.saas.types.SaasTenantResourceUpdateProperties(TypedDict, total=False):
        key "autoRenew": bool
        key "description": str
        key "intent": Union[str, PatchIntent]
        key "privateOfferId": str
        key "productCode": str
        key "quantity": int
        key "quoteId": str
        key "riskPropertyBagHeader": str
        key "storefront": str
        autoRenew: bool
        description: str
        intent: Union[str, PatchIntent]
        privateOfferId: str
        productCode: str
        quantity: int
        quoteId: str
        riskPropertyBagHeader: str
        storefront: str


    class azure.mgmt.saas.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.saas.types.TrackedResource(Resource):
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


    class azure.mgmt.saas.types.UnsubscribeOptions(TypedDict, total=False):
        key "deletionSource": Union[str, DeletionSource]
        key "feedback": str
        key "reasonCode": int
        key "unsubscribeOnly": bool
        deletionSource: Union[str, DeletionSource]
        feedback: str
        reasonCode: int
        unsubscribeOnly: bool


```