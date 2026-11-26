```py
namespace azure.mgmt.professionalservice

    class azure.mgmt.professionalservice.ProfessionalServiceClient: implements ContextManager 
        operations: Operations
        professional_service_operation_statuses: ProfessionalServiceOperationStatusesOperations
        professional_service_subscription_level: ProfessionalServiceSubscriptionLevelOperations
        professional_service_subscription_level_global: ProfessionalServiceSubscriptionLevelGlobalOperations

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


namespace azure.mgmt.professionalservice.aio

    class azure.mgmt.professionalservice.aio.ProfessionalServiceClient: implements AsyncContextManager 
        operations: Operations
        professional_service_operation_statuses: ProfessionalServiceOperationStatusesOperations
        professional_service_subscription_level: ProfessionalServiceSubscriptionLevelOperations
        professional_service_subscription_level_global: ProfessionalServiceSubscriptionLevelGlobalOperations

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


namespace azure.mgmt.professionalservice.aio.operations

    class azure.mgmt.professionalservice.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.professionalservice.aio.operations.ProfessionalServiceOperationStatusesOperations:

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


    class azure.mgmt.professionalservice.aio.operations.ProfessionalServiceSubscriptionLevelGlobalOperations:

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
        def list_by_azure_subscription(self, **kwargs: Any) -> AsyncItemPaged[ProfessionalServiceResource]: ...

        @overload
        async def validate_purchase(
                self, 
                resource_group_name: str, 
                body: ProfessionalServicePurchaseValidationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...

        @overload
        async def validate_purchase(
                self, 
                resource_group_name: str, 
                body: ProfessionalServicePurchaseValidationRequest, 
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
                body: ProfessionalServicePurchaseValidationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...

        @overload
        async def validate_purchase_by_subscription(
                self, 
                body: ProfessionalServicePurchaseValidationRequest, 
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


    class azure.mgmt.professionalservice.aio.operations.ProfessionalServiceSubscriptionLevelOperations:

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
                resource: ProfessionalServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProfessionalServiceResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                resource: ProfessionalServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProfessionalServiceResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProfessionalServiceResource]: ...

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
            ) -> AsyncLROPoller[ProfessionalServiceResource]: ...

        @overload
        async def begin_unsubscribe(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: UnsubscribeOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProfessionalServiceResource]: ...

        @overload
        async def begin_unsubscribe(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProfessionalServiceResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: ProfessionalServiceResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProfessionalServiceResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: ProfessionalServiceResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProfessionalServiceResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProfessionalServiceResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                expand_customer_data: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ProfessionalServiceResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ProfessionalServiceResource]: ...

        @overload
        async def validate_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: ProfessionalServiceResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...

        @overload
        async def validate_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: ProfessionalServiceResourceUpdate, 
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


namespace azure.mgmt.professionalservice.models

    class azure.mgmt.professionalservice.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.professionalservice.models.CheckNameAvailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.professionalservice.models.CheckNameAvailabilityRequest(_Model):
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


    class azure.mgmt.professionalservice.models.CheckNameAvailabilityResponse(_Model):
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


    class azure.mgmt.professionalservice.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.professionalservice.models.DeletionSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SUBSCRIPTION_DELETION = "AzureSubscriptionDeletion"
        CUSTOMER_CANCELLATION = "CustomerCancellation"


    class azure.mgmt.professionalservice.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.professionalservice.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.professionalservice.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.professionalservice.models.Operation(_Model):
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


    class azure.mgmt.professionalservice.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.professionalservice.models.OperationStatusResult(_Model):
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


    class azure.mgmt.professionalservice.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.professionalservice.models.ProfessionalServiceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NOT_STARTED = "NotStarted"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.professionalservice.models.ProfessionalServicePurchaseValidationProperties(_Model):
        asset_id: Optional[str]
        auto_renew: Optional[bool]
        billing_period: Optional[str]
        description: Optional[str]
        future_start_date: Optional[datetime]
        is_free_trial: Optional[bool]
        name: str
        offer_name: Optional[str]
        plan_name: Optional[str]
        private_offer_id: Optional[str]
        product_code: str
        provisioning_state: Optional[Union[str, ProfessionalServiceProvisioningState]]
        publisher_name: Optional[str]
        purchaser_email: Optional[str]
        quantity: Optional[int]
        quote_id: Optional[str]
        risk_property_bag_header: Optional[str]
        status: Optional[Union[str, ProfessionalServiceResourceStatus]]
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
                name: str, 
                private_offer_id: Optional[str] = ..., 
                product_code: str, 
                quantity: Optional[int] = ..., 
                quote_id: Optional[str] = ..., 
                risk_property_bag_header: Optional[str] = ..., 
                storefront: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.professionalservice.models.ProfessionalServicePurchaseValidationRequest(_Model):
        location: str
        properties: ProfessionalServicePurchaseValidationProperties
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: ProfessionalServicePurchaseValidationProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.professionalservice.models.ProfessionalServiceResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ProfessionalServiceResourceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ProfessionalServiceResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.professionalservice.models.ProfessionalServiceResourceProperties(_Model):
        asset_id: Optional[str]
        auto_renew: Optional[bool]
        billing_period: Optional[str]
        description: Optional[str]
        future_start_date: Optional[datetime]
        is_free_trial: Optional[bool]
        offer_name: Optional[str]
        plan_name: Optional[str]
        private_offer_id: Optional[str]
        product_code: str
        provisioning_state: Optional[Union[str, ProfessionalServiceProvisioningState]]
        publisher_name: Optional[str]
        purchaser_email: Optional[str]
        quantity: Optional[int]
        quote_id: Optional[str]
        risk_property_bag_header: Optional[str]
        status: Optional[Union[str, ProfessionalServiceResourceStatus]]
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
                private_offer_id: Optional[str] = ..., 
                product_code: str, 
                quantity: Optional[int] = ..., 
                quote_id: Optional[str] = ..., 
                risk_property_bag_header: Optional[str] = ..., 
                storefront: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.professionalservice.models.ProfessionalServiceResourceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_STARTED = "NotStarted"
        PENDING_FULFILLMENT_START = "PendingFulfillmentStart"
        SUBSCRIBED = "Subscribed"
        SUSPENDED = "Suspended"
        UNSUBSCRIBED = "Unsubscribed"


    class azure.mgmt.professionalservice.models.ProfessionalServiceResourceUpdate(_Model):
        properties: Optional[ProfessionalServiceResourceUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ProfessionalServiceResourceUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.professionalservice.models.ProfessionalServiceResourceUpdateProperties(_Model):
        auto_renew: Optional[bool]
        description: Optional[str]
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
                private_offer_id: Optional[str] = ..., 
                product_code: Optional[str] = ..., 
                quantity: Optional[int] = ..., 
                quote_id: Optional[str] = ..., 
                risk_property_bag_header: Optional[str] = ..., 
                storefront: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.professionalservice.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.professionalservice.models.ResourceValidationError(_Model):
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


    class azure.mgmt.professionalservice.models.ResourceValidationResult(_Model):
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


    class azure.mgmt.professionalservice.models.SubscriptionStatusReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SUBSCRIPTION_DELETION = "AzureSubscriptionDeletion"
        NONE = "None"
        SUSPENDED_INTERNAL = "SuspendedInternal"


    class azure.mgmt.professionalservice.models.SystemData(_Model):
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


    class azure.mgmt.professionalservice.models.TrackedResource(Resource):
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


    class azure.mgmt.professionalservice.models.UnsubscribeOptions(_Model):
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


namespace azure.mgmt.professionalservice.operations

    class azure.mgmt.professionalservice.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.professionalservice.operations.ProfessionalServiceOperationStatusesOperations:

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


    class azure.mgmt.professionalservice.operations.ProfessionalServiceSubscriptionLevelGlobalOperations:

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
        def list_by_azure_subscription(self, **kwargs: Any) -> ItemPaged[ProfessionalServiceResource]: ...

        @overload
        def validate_purchase(
                self, 
                resource_group_name: str, 
                body: ProfessionalServicePurchaseValidationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...

        @overload
        def validate_purchase(
                self, 
                resource_group_name: str, 
                body: ProfessionalServicePurchaseValidationRequest, 
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
                body: ProfessionalServicePurchaseValidationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...

        @overload
        def validate_purchase_by_subscription(
                self, 
                body: ProfessionalServicePurchaseValidationRequest, 
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


    class azure.mgmt.professionalservice.operations.ProfessionalServiceSubscriptionLevelOperations:

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
                resource: ProfessionalServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProfessionalServiceResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                resource: ProfessionalServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProfessionalServiceResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProfessionalServiceResource]: ...

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
            ) -> LROPoller[ProfessionalServiceResource]: ...

        @overload
        def begin_unsubscribe(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: UnsubscribeOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProfessionalServiceResource]: ...

        @overload
        def begin_unsubscribe(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProfessionalServiceResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: ProfessionalServiceResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProfessionalServiceResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: ProfessionalServiceResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProfessionalServiceResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProfessionalServiceResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                expand_customer_data: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ProfessionalServiceResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ProfessionalServiceResource]: ...

        @overload
        def validate_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: ProfessionalServiceResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceValidationResult: ...

        @overload
        def validate_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: ProfessionalServiceResourceUpdate, 
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


namespace azure.mgmt.professionalservice.types

    class azure.mgmt.professionalservice.types.CheckNameAvailabilityRequest(TypedDict, total=False):
        key "name": str
        key "type": str
        name: str
        type: str


    class azure.mgmt.professionalservice.types.ProfessionalServicePurchaseValidationProperties(TypedDict, total=False):
        key "assetId": str
        key "autoRenew": bool
        key "billingPeriod": str
        key "description": str
        key "futureStartDate": str
        key "isFreeTrial": bool
        key "name": Required[str]
        key "offerName": str
        key "planName": str
        key "privateOfferId": str
        key "productCode": Required[str]
        key "provisioningState": Union[str, ProfessionalServiceProvisioningState]
        key "publisherName": str
        key "purchaserEmail": str
        key "quantity": int
        key "quoteId": str
        key "riskPropertyBagHeader": str
        key "status": Union[str, ProfessionalServiceResourceStatus]
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
        isFreeTrial: bool
        name: str
        offerName: str
        planName: str
        privateOfferId: str
        productCode: str
        provisioningState: Union[str, ProfessionalServiceProvisioningState]
        publisherName: str
        purchaserEmail: str
        quantity: int
        quoteId: str
        riskPropertyBagHeader: str
        status: Union[str, ProfessionalServiceResourceStatus]
        statusReason: Union[str, SubscriptionStatusReason]
        storefront: str
        termEndDate: str
        termStartDate: str
        termUnit: str


    class azure.mgmt.professionalservice.types.ProfessionalServicePurchaseValidationRequest(TypedDict, total=False):
        key "location": Required[str]
        key "properties": Required[ProfessionalServicePurchaseValidationProperties]
        location: str
        properties: ProfessionalServicePurchaseValidationProperties
        tags: dict[str, str]


    class azure.mgmt.professionalservice.types.ProfessionalServiceResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ProfessionalServiceResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ProfessionalServiceResourceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.professionalservice.types.ProfessionalServiceResourceProperties(TypedDict, total=False):
        key "assetId": str
        key "autoRenew": bool
        key "billingPeriod": str
        key "description": str
        key "futureStartDate": str
        key "isFreeTrial": bool
        key "offerName": str
        key "planName": str
        key "privateOfferId": str
        key "productCode": Required[str]
        key "provisioningState": Union[str, ProfessionalServiceProvisioningState]
        key "publisherName": str
        key "purchaserEmail": str
        key "quantity": int
        key "quoteId": str
        key "riskPropertyBagHeader": str
        key "status": Union[str, ProfessionalServiceResourceStatus]
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
        isFreeTrial: bool
        offerName: str
        planName: str
        privateOfferId: str
        productCode: str
        provisioningState: Union[str, ProfessionalServiceProvisioningState]
        publisherName: str
        purchaserEmail: str
        quantity: int
        quoteId: str
        riskPropertyBagHeader: str
        status: Union[str, ProfessionalServiceResourceStatus]
        statusReason: Union[str, SubscriptionStatusReason]
        storefront: str
        termEndDate: str
        termStartDate: str
        termUnit: str


    class azure.mgmt.professionalservice.types.ProfessionalServiceResourceUpdate(TypedDict, total=False):
        key "properties": ForwardRef('ProfessionalServiceResourceUpdateProperties', module='types')
        properties: ProfessionalServiceResourceUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.professionalservice.types.ProfessionalServiceResourceUpdateProperties(TypedDict, total=False):
        key "autoRenew": bool
        key "description": str
        key "privateOfferId": str
        key "productCode": str
        key "quantity": int
        key "quoteId": str
        key "riskPropertyBagHeader": str
        key "storefront": str
        autoRenew: bool
        description: str
        privateOfferId: str
        productCode: str
        quantity: int
        quoteId: str
        riskPropertyBagHeader: str
        storefront: str


    class azure.mgmt.professionalservice.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.professionalservice.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.professionalservice.types.TrackedResource(Resource):
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


    class azure.mgmt.professionalservice.types.UnsubscribeOptions(TypedDict, total=False):
        key "deletionSource": Union[str, DeletionSource]
        key "feedback": str
        key "reasonCode": int
        key "unsubscribeOnly": bool
        deletionSource: Union[str, DeletionSource]
        feedback: str
        reasonCode: int
        unsubscribeOnly: bool


```