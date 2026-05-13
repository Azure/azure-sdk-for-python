```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.reservations

    class azure.mgmt.reservations.AzureReservationAPI(AzureReservationAPIOperationsMixin): implements ContextManager 
        calculate_exchange: CalculateExchangeOperations
        calculate_refund: CalculateRefundOperations
        exchange: ExchangeOperations
        operation: OperationOperations
        quota: QuotaOperations
        quota_request_status: QuotaRequestStatusOperations
        reservation: ReservationOperations
        reservation_order: ReservationOrderOperations
        return_operations: ReturnOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                base_url: str = "https://management.azure.com", 
                *, 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def get_applied_reservation_list(
                self, 
                subscription_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AppliedReservations: ...

        @distributed_trace
        def get_catalog(
                self, 
                subscription_id: str, 
                reserved_resource_type: Optional[str] = None, 
                location: Optional[str] = None, 
                publisher_id: Optional[str] = None, 
                offer_id: Optional[str] = None, 
                plan_id: Optional[str] = None, 
                filter: Optional[str] = None, 
                skip: Optional[float] = None, 
                take: Optional[float] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Catalog]: ...


namespace azure.mgmt.reservations.aio

    class azure.mgmt.reservations.aio.AzureReservationAPI(AzureReservationAPIOperationsMixin): implements AsyncContextManager 
        calculate_exchange: CalculateExchangeOperations
        calculate_refund: CalculateRefundOperations
        exchange: ExchangeOperations
        operation: OperationOperations
        quota: QuotaOperations
        quota_request_status: QuotaRequestStatusOperations
        reservation: ReservationOperations
        reservation_order: ReservationOrderOperations
        return_operations: ReturnOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                base_url: str = "https://management.azure.com", 
                *, 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def get_applied_reservation_list(
                self, 
                subscription_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AppliedReservations: ...

        @distributed_trace
        def get_catalog(
                self, 
                subscription_id: str, 
                reserved_resource_type: Optional[str] = None, 
                location: Optional[str] = None, 
                publisher_id: Optional[str] = None, 
                offer_id: Optional[str] = None, 
                plan_id: Optional[str] = None, 
                filter: Optional[str] = None, 
                skip: Optional[float] = None, 
                take: Optional[float] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Catalog]: ...


namespace azure.mgmt.reservations.aio.operations

    class azure.mgmt.reservations.aio.operations.AzureReservationAPIOperationsMixin(AzureReservationAPIMixinABC):

        @distributed_trace_async
        async def get_applied_reservation_list(
                self, 
                subscription_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AppliedReservations: ...

        @distributed_trace
        def get_catalog(
                self, 
                subscription_id: str, 
                reserved_resource_type: Optional[str] = None, 
                location: Optional[str] = None, 
                publisher_id: Optional[str] = None, 
                offer_id: Optional[str] = None, 
                plan_id: Optional[str] = None, 
                filter: Optional[str] = None, 
                skip: Optional[float] = None, 
                take: Optional[float] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Catalog]: ...


    class azure.mgmt.reservations.aio.operations.CalculateExchangeOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_post(
                self, 
                body: CalculateExchangeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CalculateExchangeOperationResultResponse]: ...

        @overload
        async def begin_post(
                self, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CalculateExchangeOperationResultResponse]: ...


    class azure.mgmt.reservations.aio.operations.CalculateRefundOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def post(
                self, 
                reservation_order_id: str, 
                body: CalculateRefundRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculateRefundResponse: ...

        @overload
        async def post(
                self, 
                reservation_order_id: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculateRefundResponse: ...


    class azure.mgmt.reservations.aio.operations.ExchangeOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_post(
                self, 
                body: ExchangeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExchangeOperationResultResponse]: ...

        @overload
        async def begin_post(
                self, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExchangeOperationResultResponse]: ...


    class azure.mgmt.reservations.aio.operations.OperationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[OperationResponse]: ...


    class azure.mgmt.reservations.aio.operations.QuotaOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                subscription_id: str, 
                provider_id: str, 
                location: str, 
                resource_name: str, 
                create_quota_request: CurrentQuotaLimitBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CurrentQuotaLimitBase]: ...

        @overload
        async def begin_create_or_update(
                self, 
                subscription_id: str, 
                provider_id: str, 
                location: str, 
                resource_name: str, 
                create_quota_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CurrentQuotaLimitBase]: ...

        @overload
        async def begin_update(
                self, 
                subscription_id: str, 
                provider_id: str, 
                location: str, 
                resource_name: str, 
                create_quota_request: CurrentQuotaLimitBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CurrentQuotaLimitBase]: ...

        @overload
        async def begin_update(
                self, 
                subscription_id: str, 
                provider_id: str, 
                location: str, 
                resource_name: str, 
                create_quota_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CurrentQuotaLimitBase]: ...

        @distributed_trace_async
        async def get(
                self, 
                subscription_id: str, 
                provider_id: str, 
                location: str, 
                resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CurrentQuotaLimitBase: ...

        @distributed_trace
        def list(
                self, 
                subscription_id: str, 
                provider_id: str, 
                location: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[CurrentQuotaLimitBase]: ...


    class azure.mgmt.reservations.aio.operations.QuotaRequestStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                subscription_id: str, 
                provider_id: str, 
                location: str, 
                id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> QuotaRequestDetails: ...

        @distributed_trace
        def list(
                self, 
                subscription_id: str, 
                provider_id: str, 
                location: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skiptoken: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[QuotaRequestDetails]: ...


    class azure.mgmt.reservations.aio.operations.ReservationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def archive(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def begin_available_scopes(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                body: AvailableScopeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AvailableScopeProperties]: ...

        @overload
        async def begin_available_scopes(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AvailableScopeProperties]: ...

        @overload
        async def begin_merge(
                self, 
                reservation_order_id: str, 
                body: MergeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[List[ReservationResponse]]: ...

        @overload
        async def begin_merge(
                self, 
                reservation_order_id: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[List[ReservationResponse]]: ...

        @overload
        async def begin_split(
                self, 
                reservation_order_id: str, 
                body: SplitRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[List[ReservationResponse]]: ...

        @overload
        async def begin_split(
                self, 
                reservation_order_id: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[List[ReservationResponse]]: ...

        @overload
        async def begin_update(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                parameters: Patch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReservationResponse]: ...

        @overload
        async def begin_update(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReservationResponse]: ...

        @distributed_trace_async
        async def get(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                expand: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ReservationResponse: ...

        @distributed_trace
        def list(
                self, 
                reservation_order_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ReservationResponse]: ...

        @distributed_trace
        def list_all(
                self, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                refresh_summary: Optional[str] = None, 
                skiptoken: Optional[float] = None, 
                selected_state: Optional[str] = None, 
                take: Optional[float] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ReservationResponse]: ...

        @distributed_trace
        def list_revisions(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ReservationResponse]: ...

        @distributed_trace_async
        async def unarchive(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.reservations.aio.operations.ReservationOrderOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_purchase(
                self, 
                reservation_order_id: str, 
                body: PurchaseRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReservationOrderResponse]: ...

        @overload
        async def begin_purchase(
                self, 
                reservation_order_id: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReservationOrderResponse]: ...

        @overload
        async def calculate(
                self, 
                body: PurchaseRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculatePriceResponse: ...

        @overload
        async def calculate(
                self, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculatePriceResponse: ...

        @overload
        async def change_directory(
                self, 
                reservation_order_id: str, 
                body: ChangeDirectoryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ChangeDirectoryResponse: ...

        @overload
        async def change_directory(
                self, 
                reservation_order_id: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ChangeDirectoryResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                reservation_order_id: str, 
                expand: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ReservationOrderResponse: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ReservationOrderResponse]: ...


    class azure.mgmt.reservations.aio.operations.ReturnOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_post(
                self, 
                reservation_order_id: str, 
                body: RefundRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReservationOrderResponse]: ...

        @overload
        async def begin_post(
                self, 
                reservation_order_id: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReservationOrderResponse]: ...


namespace azure.mgmt.reservations.models

    class azure.mgmt.reservations.models.AppliedReservationList(Model):
        next_link: str
        value: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.AppliedReservations(Model):
        id: str
        name: str
        reservation_order_ids: AppliedReservationList
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                reservation_order_ids: Optional[AppliedReservationList] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.AppliedScopeProperties(Model):
        display_name: str
        management_group_id: str
        resource_group_id: str
        subscription_id: str
        tenant_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                management_group_id: Optional[str] = ..., 
                resource_group_id: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.AppliedScopeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGEMENT_GROUP = "ManagementGroup"
        SHARED = "Shared"
        SINGLE = "Single"


    class azure.mgmt.reservations.models.AvailableScopeProperties(Model):
        properties: SubscriptionScopeProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[SubscriptionScopeProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.AvailableScopeRequest(Model):
        properties: AvailableScopeRequestProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[AvailableScopeRequestProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.AvailableScopeRequestProperties(Model):
        scopes: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                scopes: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.BillingInformation(Model):
        billing_currency_prorated_amount: Price
        billing_currency_remaining_commitment_amount: Price
        billing_currency_total_paid_amount: Price

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_currency_prorated_amount: Optional[Price] = ..., 
                billing_currency_remaining_commitment_amount: Optional[Price] = ..., 
                billing_currency_total_paid_amount: Optional[Price] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.BillingPlan(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P1_M = "P1M"


    class azure.mgmt.reservations.models.CalculateExchangeOperationResultResponse(Model):
        error: OperationResultError
        id: str
        name: str
        properties: CalculateExchangeResponseProperties
        status: Union[str, CalculateExchangeOperationResultStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[OperationResultError] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[CalculateExchangeResponseProperties] = ..., 
                status: Optional[Union[str, CalculateExchangeOperationResultStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.CalculateExchangeOperationResultStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        FAILED = "Failed"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.reservations.models.CalculateExchangeRequest(Model):
        properties: CalculateExchangeRequestProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[CalculateExchangeRequestProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.CalculateExchangeRequestProperties(Model):
        reservations_to_exchange: list[ReservationToReturn]
        reservations_to_purchase: list[PurchaseRequest]
        savings_plans_to_purchase: list[SavingsPlanPurchaseRequest]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                reservations_to_exchange: Optional[List[ReservationToReturn]] = ..., 
                reservations_to_purchase: Optional[List[PurchaseRequest]] = ..., 
                savings_plans_to_purchase: Optional[List[SavingsPlanPurchaseRequest]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.CalculateExchangeResponseProperties(Model):
        net_payable: Price
        policy_result: ExchangePolicyErrors
        purchases_total: Price
        refunds_total: Price
        reservations_to_exchange: list[ReservationToExchange]
        reservations_to_purchase: list[ReservationToPurchaseCalculateExchange]
        savings_plans_to_purchase: list[SavingsPlanToPurchaseCalculateExchange]
        session_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                net_payable: Optional[Price] = ..., 
                policy_result: Optional[ExchangePolicyErrors] = ..., 
                purchases_total: Optional[Price] = ..., 
                refunds_total: Optional[Price] = ..., 
                reservations_to_exchange: Optional[List[ReservationToExchange]] = ..., 
                reservations_to_purchase: Optional[List[ReservationToPurchaseCalculateExchange]] = ..., 
                savings_plans_to_purchase: Optional[List[SavingsPlanToPurchaseCalculateExchange]] = ..., 
                session_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.CalculatePriceResponse(Model):
        properties: CalculatePriceResponseProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[CalculatePriceResponseProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.CalculatePriceResponseProperties(Model):
        billing_currency_total: CalculatePriceResponsePropertiesBillingCurrencyTotal
        grand_total: float
        is_billing_partner_managed: bool
        is_tax_included: bool
        net_total: float
        payment_schedule: list[PaymentDetail]
        pricing_currency_total: CalculatePriceResponsePropertiesPricingCurrencyTotal
        reservation_order_id: str
        sku_description: str
        sku_title: str
        tax_total: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_currency_total: Optional[CalculatePriceResponsePropertiesBillingCurrencyTotal] = ..., 
                grand_total: Optional[float] = ..., 
                is_billing_partner_managed: Optional[bool] = ..., 
                is_tax_included: Optional[bool] = ..., 
                net_total: Optional[float] = ..., 
                payment_schedule: Optional[List[PaymentDetail]] = ..., 
                pricing_currency_total: Optional[CalculatePriceResponsePropertiesPricingCurrencyTotal] = ..., 
                reservation_order_id: Optional[str] = ..., 
                sku_description: Optional[str] = ..., 
                sku_title: Optional[str] = ..., 
                tax_total: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.CalculatePriceResponsePropertiesBillingCurrencyTotal(Model):
        amount: float
        currency_code: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                amount: Optional[float] = ..., 
                currency_code: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.CalculatePriceResponsePropertiesPricingCurrencyTotal(Model):
        amount: float
        currency_code: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                amount: Optional[float] = ..., 
                currency_code: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.CalculateRefundRequest(Model):
        id: str
        properties: CalculateRefundRequestProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                properties: Optional[CalculateRefundRequestProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.CalculateRefundRequestProperties(Model):
        reservation_to_return: ReservationToReturn
        scope: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                reservation_to_return: Optional[ReservationToReturn] = ..., 
                scope: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.CalculateRefundResponse(Model):
        id: str
        properties: RefundResponseProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                properties: Optional[RefundResponseProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.Catalog(Model):
        billing_plans: Union[dict[str, list[str, ReservationBillingPlan]]]
        capabilities: list[SkuCapability]
        locations: list[str]
        msrp: CatalogMsrp
        name: str
        resource_type: str
        restrictions: list[SkuRestriction]
        size: str
        sku_properties: list[SkuProperty]
        terms: Union[list[str, ReservationTerm]]
        tier: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_plans: Optional[Dict[str, List[Union[str, ReservationBillingPlan]]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.CatalogMsrp(Model):
        p1_y: Price
        p3_y: Price
        p5_y: Price

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                p1_y: Optional[Price] = ..., 
                p3_y: Optional[Price] = ..., 
                p5_y: Optional[Price] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.CatalogsResult(Model):
        next_link: str
        total_items: int
        value: list[Catalog]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                total_items: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ChangeDirectoryRequest(Model):
        destination_tenant_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                destination_tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ChangeDirectoryResponse(Model):
        reservation_order: ChangeDirectoryResult
        reservations: list[ChangeDirectoryResult]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                reservation_order: Optional[ChangeDirectoryResult] = ..., 
                reservations: Optional[List[ChangeDirectoryResult]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ChangeDirectoryResult(Model):
        error: str
        id: str
        is_succeeded: bool
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[str] = ..., 
                id: Optional[str] = ..., 
                is_succeeded: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.Commitment(Price):
        amount: float
        currency_code: str
        grain: Union[str, CommitmentGrain]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                amount: Optional[float] = ..., 
                currency_code: Optional[str] = ..., 
                grain: Optional[Union[str, CommitmentGrain]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.CommitmentGrain(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HOURLY = "Hourly"


    class azure.mgmt.reservations.models.CreateGenericQuotaRequestParameters(Model):
        value: list[CurrentQuotaLimitBase]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[CurrentQuotaLimitBase]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.reservations.models.CurrentQuotaLimit(Model):
        id: str
        message: str
        name: str
        properties: QuotaProperties
        provisioning_state: Union[str, QuotaRequestState]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[QuotaProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.CurrentQuotaLimitBase(Model):
        id: str
        name: str
        properties: QuotaProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[QuotaProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.DisplayProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        EXPIRED = "Expired"
        EXPIRING = "Expiring"
        FAILED = "Failed"
        NO_BENEFIT = "NoBenefit"
        PENDING = "Pending"
        PROCESSING = "Processing"
        SUCCEEDED = "Succeeded"
        WARNING = "Warning"


    class azure.mgmt.reservations.models.Error(Model):
        error: ExtendedErrorInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ExtendedErrorInfo] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ErrorDetails(Model):
        code: str
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ErrorResponse(Model):
        error: ErrorDetails

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetails] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ErrorResponseCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVATE_QUOTE_FAILED = "ActivateQuoteFailed"
        APPLIED_SCOPES_NOT_ASSOCIATED_WITH_COMMERCE_ACCOUNT = "AppliedScopesNotAssociatedWithCommerceAccount"
        APPLIED_SCOPES_SAME_AS_EXISTING = "AppliedScopesSameAsExisting"
        AUTHORIZATION_FAILED = "AuthorizationFailed"
        BAD_REQUEST = "BadRequest"
        BILLING_CUSTOMER_INPUT_ERROR = "BillingCustomerInputError"
        BILLING_ERROR = "BillingError"
        BILLING_PAYMENT_INSTRUMENT_HARD_ERROR = "BillingPaymentInstrumentHardError"
        BILLING_PAYMENT_INSTRUMENT_SOFT_ERROR = "BillingPaymentInstrumentSoftError"
        BILLING_SCOPE_ID_CANNOT_BE_CHANGED = "BillingScopeIdCannotBeChanged"
        BILLING_TRANSIENT_ERROR = "BillingTransientError"
        CALCULATE_PRICE_FAILED = "CalculatePriceFailed"
        CAPACITY_UPDATE_SCOPES_FAILED = "CapacityUpdateScopesFailed"
        CLIENT_CERTIFICATE_THUMBPRINT_NOT_SET = "ClientCertificateThumbprintNotSet"
        CREATE_QUOTE_FAILED = "CreateQuoteFailed"
        FORBIDDEN = "Forbidden"
        FULFILLMENT_CONFIGURATION_ERROR = "FulfillmentConfigurationError"
        FULFILLMENT_ERROR = "FulfillmentError"
        FULFILLMENT_OUT_OF_STOCK_ERROR = "FulfillmentOutOfStockError"
        FULFILLMENT_TRANSIENT_ERROR = "FulfillmentTransientError"
        HTTP_METHOD_NOT_SUPPORTED = "HttpMethodNotSupported"
        INTERNAL_SERVER_ERROR = "InternalServerError"
        INVALID_ACCESS_TOKEN = "InvalidAccessToken"
        INVALID_FULFILLMENT_REQUEST_PARAMETERS = "InvalidFulfillmentRequestParameters"
        INVALID_HEALTH_CHECK_TYPE = "InvalidHealthCheckType"
        INVALID_LOCATION_ID = "InvalidLocationId"
        INVALID_REFUND_QUANTITY = "InvalidRefundQuantity"
        INVALID_REQUEST_CONTENT = "InvalidRequestContent"
        INVALID_REQUEST_URI = "InvalidRequestUri"
        INVALID_RESERVATION_ID = "InvalidReservationId"
        INVALID_RESERVATION_ORDER_ID = "InvalidReservationOrderId"
        INVALID_SINGLE_APPLIED_SCOPES_COUNT = "InvalidSingleAppliedScopesCount"
        INVALID_SUBSCRIPTION_ID = "InvalidSubscriptionId"
        INVALID_TENANT_ID = "InvalidTenantId"
        MISSING_APPLIED_SCOPES_FOR_SINGLE = "MissingAppliedScopesForSingle"
        MISSING_TENANT_ID = "MissingTenantId"
        NONSUPPORTED_ACCOUNT_ID = "NonsupportedAccountId"
        NOT_SPECIFIED = "NotSpecified"
        NOT_SUPPORTED_COUNTRY = "NotSupportedCountry"
        NO_VALID_RESERVATIONS_TO_RE_RATE = "NoValidReservationsToReRate"
        OPERATION_CANNOT_BE_PERFORMED_IN_CURRENT_STATE = "OperationCannotBePerformedInCurrentState"
        OPERATION_FAILED = "OperationFailed"
        PATCH_VALUES_SAME_AS_EXISTING = "PatchValuesSameAsExisting"
        PAYMENT_INSTRUMENT_NOT_FOUND = "PaymentInstrumentNotFound"
        PURCHASE_ERROR = "PurchaseError"
        REFUND_LIMIT_EXCEEDED = "RefundLimitExceeded"
        RESERVATION_ID_NOT_IN_RESERVATION_ORDER = "ReservationIdNotInReservationOrder"
        RESERVATION_ORDER_CREATION_FAILED = "ReservationOrderCreationFailed"
        RESERVATION_ORDER_ID_ALREADY_EXISTS = "ReservationOrderIdAlreadyExists"
        RESERVATION_ORDER_NOT_ENABLED = "ReservationOrderNotEnabled"
        RESERVATION_ORDER_NOT_FOUND = "ReservationOrderNotFound"
        RE_RATE_ONLY_ALLOWED_FOR_EA = "ReRateOnlyAllowedForEA"
        RISK_CHECK_FAILED = "RiskCheckFailed"
        ROLE_ASSIGNMENT_CREATION_FAILED = "RoleAssignmentCreationFailed"
        SELF_SERVICE_REFUND_NOT_SUPPORTED = "SelfServiceRefundNotSupported"
        SERVER_TIMEOUT = "ServerTimeout"
        UNAUTHENTICATED_REQUESTS_THROTTLED = "UnauthenticatedRequestsThrottled"
        UNSUPPORTED_RESERVATION_TERM = "UnsupportedReservationTerm"


    class azure.mgmt.reservations.models.ExceptionResponse(Model):
        error: ServiceError

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ServiceError] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ExchangeOperationResultResponse(Model):
        error: OperationResultError
        id: str
        name: str
        properties: ExchangeResponseProperties
        status: Union[str, ExchangeOperationResultStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[OperationResultError] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[ExchangeResponseProperties] = ..., 
                status: Optional[Union[str, ExchangeOperationResultStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ExchangeOperationResultStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        FAILED = "Failed"
        PENDING_PURCHASES = "PendingPurchases"
        PENDING_REFUNDS = "PendingRefunds"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.reservations.models.ExchangePolicyError(Model):
        code: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ExchangePolicyErrors(Model):
        policy_errors: list[ExchangePolicyError]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                policy_errors: Optional[List[ExchangePolicyError]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ExchangeRequest(Model):
        properties: ExchangeRequestProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[ExchangeRequestProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ExchangeRequestProperties(Model):
        session_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                session_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ExchangeResponseProperties(Model):
        net_payable: Price
        policy_result: ExchangePolicyErrors
        purchases_total: Price
        refunds_total: Price
        reservations_to_exchange: list[ReservationToReturnForExchange]
        reservations_to_purchase: list[ReservationToPurchaseExchange]
        savings_plans_to_purchase: list[SavingsPlanToPurchaseExchange]
        session_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                net_payable: Optional[Price] = ..., 
                policy_result: Optional[ExchangePolicyErrors] = ..., 
                purchases_total: Optional[Price] = ..., 
                refunds_total: Optional[Price] = ..., 
                reservations_to_exchange: Optional[List[ReservationToReturnForExchange]] = ..., 
                reservations_to_purchase: Optional[List[ReservationToPurchaseExchange]] = ..., 
                savings_plans_to_purchase: Optional[List[SavingsPlanToPurchaseExchange]] = ..., 
                session_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ExtendedErrorInfo(Model):
        code: Union[str, ErrorResponseCode]
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[Union[str, ErrorResponseCode]] = ..., 
                message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ExtendedStatusInfo(Model):
        message: str
        status_code: Union[str, ReservationStatusCode]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                status_code: Optional[Union[str, ReservationStatusCode]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.InstanceFlexibility(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFF = "Off"
        ON = "On"


    class azure.mgmt.reservations.models.Location(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUSTRALIAEAST = "australiaeast"
        AUSTRALIASOUTHEAST = "australiasoutheast"
        BRAZILSOUTH = "brazilsouth"
        CANADACENTRAL = "canadacentral"
        CANADAEAST = "canadaeast"
        CENTRALINDIA = "centralindia"
        CENTRALUS = "centralus"
        EASTASIA = "eastasia"
        EASTUS = "eastus"
        EASTUS2 = "eastus2"
        JAPANEAST = "japaneast"
        JAPANWEST = "japanwest"
        NORTHCENTRALUS = "northcentralus"
        NORTHEUROPE = "northeurope"
        SOUTHCENTRALUS = "southcentralus"
        SOUTHEASTASIA = "southeastasia"
        SOUTHINDIA = "southindia"
        UKSOUTH = "uksouth"
        UKWEST = "ukwest"
        WESTCENTRALUS = "westcentralus"
        WESTEUROPE = "westeurope"
        WESTINDIA = "westindia"
        WESTUS = "westus"
        WESTUS2 = "westus2"


    class azure.mgmt.reservations.models.MergeRequest(Model):
        sources: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                sources: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.OperationList(Model):
        next_link: str
        value: list[OperationResponse]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[OperationResponse]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.OperationResponse(Model):
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: str
        properties: JSON

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[JSON] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.OperationResultError(Model):
        code: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.OperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        FAILED = "Failed"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.reservations.models.Patch(Model):
        applied_scope_properties: AppliedScopeProperties
        applied_scope_type: Union[str, AppliedScopeType]
        applied_scopes: list[str]
        instance_flexibility: Union[str, InstanceFlexibility]
        name: str
        renew: bool
        renew_properties: PatchPropertiesRenewProperties
        review_date_time: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                applied_scope_properties: Optional[AppliedScopeProperties] = ..., 
                applied_scope_type: Optional[Union[str, AppliedScopeType]] = ..., 
                applied_scopes: Optional[List[str]] = ..., 
                instance_flexibility: Optional[Union[str, InstanceFlexibility]] = ..., 
                name: Optional[str] = ..., 
                renew: bool = False, 
                renew_properties: Optional[PatchPropertiesRenewProperties] = ..., 
                review_date_time: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.PatchPropertiesRenewProperties(Model):
        purchase_properties: PurchaseRequest

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                purchase_properties: Optional[PurchaseRequest] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.PaymentDetail(Model):
        billing_account: str
        billing_currency_total: Price
        due_date: date
        extended_status_info: ExtendedStatusInfo
        payment_date: date
        pricing_currency_total: Price
        status: Union[str, PaymentStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_account: Optional[str] = ..., 
                billing_currency_total: Optional[Price] = ..., 
                due_date: Optional[date] = ..., 
                extended_status_info: Optional[ExtendedStatusInfo] = ..., 
                payment_date: Optional[date] = ..., 
                pricing_currency_total: Optional[Price] = ..., 
                status: Optional[Union[str, PaymentStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.PaymentStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        FAILED = "Failed"
        SCHEDULED = "Scheduled"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.reservations.models.Price(Model):
        amount: float
        currency_code: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                amount: Optional[float] = ..., 
                currency_code: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BILLING_FAILED = "BillingFailed"
        CANCELLED = "Cancelled"
        CONFIRMED_BILLING = "ConfirmedBilling"
        CONFIRMED_RESOURCE_HOLD = "ConfirmedResourceHold"
        CREATED = "Created"
        CREATING = "Creating"
        EXPIRED = "Expired"
        FAILED = "Failed"
        MERGED = "Merged"
        PENDING_BILLING = "PendingBilling"
        PENDING_RESOURCE_HOLD = "PendingResourceHold"
        SPLIT = "Split"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.reservations.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.PurchaseRequest(Model):
        applied_scope_properties: AppliedScopeProperties
        applied_scope_type: Union[str, AppliedScopeType]
        applied_scopes: list[str]
        billing_plan: Union[str, ReservationBillingPlan]
        billing_scope_id: str
        display_name: str
        location: str
        quantity: int
        renew: bool
        reserved_resource_properties: PurchaseRequestPropertiesReservedResourceProperties
        reserved_resource_type: Union[str, ReservedResourceType]
        review_date_time: datetime
        sku: SkuName
        term: Union[str, ReservationTerm]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                applied_scope_properties: Optional[AppliedScopeProperties] = ..., 
                applied_scope_type: Optional[Union[str, AppliedScopeType]] = ..., 
                applied_scopes: Optional[List[str]] = ..., 
                billing_plan: Optional[Union[str, ReservationBillingPlan]] = ..., 
                billing_scope_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                location: Optional[str] = ..., 
                quantity: Optional[int] = ..., 
                renew: bool = False, 
                reserved_resource_properties: Optional[PurchaseRequestPropertiesReservedResourceProperties] = ..., 
                reserved_resource_type: Optional[Union[str, ReservedResourceType]] = ..., 
                review_date_time: Optional[datetime] = ..., 
                sku: Optional[SkuName] = ..., 
                term: Optional[Union[str, ReservationTerm]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.PurchaseRequestPropertiesReservedResourceProperties(Model):
        instance_flexibility: Union[str, InstanceFlexibility]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                instance_flexibility: Optional[Union[str, InstanceFlexibility]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.QuotaLimits(Model):
        next_link: str
        value: list[CurrentQuotaLimitBase]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[CurrentQuotaLimitBase]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.QuotaLimitsResponse(Model):
        next_link: str
        value: list[CurrentQuotaLimit]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[CurrentQuotaLimit]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.QuotaProperties(Model):
        current_value: int
        limit: int
        name: ResourceName
        properties: JSON
        quota_period: str
        resource_type: Union[str, ResourceType]
        unit: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                limit: Optional[int] = ..., 
                name: Optional[ResourceName] = ..., 
                properties: Optional[JSON] = ..., 
                resource_type: Optional[Union[str, ResourceType]] = ..., 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.QuotaRequestDetails(Model):
        id: str
        message: str
        name: str
        provisioning_state: Union[str, QuotaRequestState]
        request_submit_time: datetime
        type: str
        value: list[SubRequest]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                provisioning_state: Optional[Union[str, QuotaRequestState]] = ..., 
                value: Optional[List[SubRequest]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.QuotaRequestDetailsList(Model):
        next_link: str
        value: list[QuotaRequestDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[QuotaRequestDetails]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.QuotaRequestOneResourceSubmitResponse(Model):
        id: str
        id_properties_id: str
        message: str
        name: str
        name_properties_name: str
        properties: QuotaProperties
        provisioning_state: Union[str, QuotaRequestState]
        request_submit_time: datetime
        type: str
        type_properties_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[QuotaProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.QuotaRequestProperties(Model):
        message: str
        provisioning_state: Union[str, QuotaRequestState]
        request_submit_time: datetime
        value: list[SubRequest]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                provisioning_state: Optional[Union[str, QuotaRequestState]] = ..., 
                value: Optional[List[SubRequest]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.QuotaRequestState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        FAILED = "Failed"
        INVALID = "Invalid"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.reservations.models.QuotaRequestSubmitResponse(Model):
        id: str
        name: str
        properties: QuotaRequestProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[QuotaRequestProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.QuotaRequestSubmitResponse201(Model):
        id: str
        message: str
        name: str
        provisioning_state: Union[str, QuotaRequestState]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.RefundBillingInformation(Model):
        billing_currency_prorated_amount: Price
        billing_currency_remaining_commitment_amount: Price
        billing_currency_total_paid_amount: Price
        billing_plan: Union[str, ReservationBillingPlan]
        completed_transactions: int
        total_transactions: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_currency_prorated_amount: Optional[Price] = ..., 
                billing_currency_remaining_commitment_amount: Optional[Price] = ..., 
                billing_currency_total_paid_amount: Optional[Price] = ..., 
                billing_plan: Optional[Union[str, ReservationBillingPlan]] = ..., 
                completed_transactions: Optional[int] = ..., 
                total_transactions: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.RefundPolicyError(Model):
        code: Union[str, ErrorResponseCode]
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[Union[str, ErrorResponseCode]] = ..., 
                message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.RefundPolicyResult(Model):
        properties: RefundPolicyResultProperty

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[RefundPolicyResultProperty] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.RefundPolicyResultProperty(Model):
        consumed_refunds_total: Price
        max_refund_limit: Price
        policy_errors: list[RefundPolicyError]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                consumed_refunds_total: Optional[Price] = ..., 
                max_refund_limit: Optional[Price] = ..., 
                policy_errors: Optional[List[RefundPolicyError]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.RefundRequest(Model):
        properties: RefundRequestProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[RefundRequestProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.RefundRequestProperties(Model):
        reservation_to_return: ReservationToReturn
        return_reason: str
        scope: str
        session_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                reservation_to_return: Optional[ReservationToReturn] = ..., 
                return_reason: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                session_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.RefundResponse(Model):
        id: str
        properties: RefundResponseProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                properties: Optional[RefundResponseProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.RefundResponseProperties(Model):
        billing_information: RefundBillingInformation
        billing_refund_amount: Price
        policy_result: RefundPolicyResult
        pricing_refund_amount: Price
        quantity: int
        session_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_information: Optional[RefundBillingInformation] = ..., 
                billing_refund_amount: Optional[Price] = ..., 
                policy_result: Optional[RefundPolicyResult] = ..., 
                pricing_refund_amount: Optional[Price] = ..., 
                quantity: Optional[int] = ..., 
                session_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.RenewPropertiesResponse(Model):
        billing_currency_total: RenewPropertiesResponseBillingCurrencyTotal
        pricing_currency_total: RenewPropertiesResponsePricingCurrencyTotal
        purchase_properties: PurchaseRequest

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_currency_total: Optional[RenewPropertiesResponseBillingCurrencyTotal] = ..., 
                pricing_currency_total: Optional[RenewPropertiesResponsePricingCurrencyTotal] = ..., 
                purchase_properties: Optional[PurchaseRequest] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.RenewPropertiesResponseBillingCurrencyTotal(Model):
        amount: float
        currency_code: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                amount: Optional[float] = ..., 
                currency_code: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.RenewPropertiesResponsePricingCurrencyTotal(Model):
        amount: float
        currency_code: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                amount: Optional[float] = ..., 
                currency_code: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ReservationBillingPlan(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONTHLY = "Monthly"
        UPFRONT = "Upfront"


    class azure.mgmt.reservations.models.ReservationList(Model):
        next_link: str
        value: list[ReservationResponse]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ReservationResponse]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ReservationMergeProperties(Model):
        merge_destination: str
        merge_sources: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                merge_destination: Optional[str] = ..., 
                merge_sources: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ReservationOrderBillingPlanInformation(Model):
        next_payment_due_date: date
        pricing_currency_total: Price
        start_date: date
        transactions: list[PaymentDetail]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_payment_due_date: Optional[date] = ..., 
                pricing_currency_total: Optional[Price] = ..., 
                start_date: Optional[date] = ..., 
                transactions: Optional[List[PaymentDetail]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ReservationOrderList(Model):
        next_link: str
        value: list[ReservationOrderResponse]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ReservationOrderResponse]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ReservationOrderResponse(Model):
        benefit_start_time: datetime
        billing_plan: Union[str, ReservationBillingPlan]
        created_date_time: datetime
        display_name: str
        etag: int
        expiry_date: date
        expiry_date_time: datetime
        id: str
        name: str
        original_quantity: int
        plan_information: ReservationOrderBillingPlanInformation
        provisioning_state: Union[str, ProvisioningState]
        request_date_time: datetime
        reservations: list[ReservationResponse]
        review_date_time: datetime
        system_data: SystemData
        term: Union[str, ReservationTerm]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                benefit_start_time: Optional[datetime] = ..., 
                billing_plan: Optional[Union[str, ReservationBillingPlan]] = ..., 
                created_date_time: Optional[datetime] = ..., 
                display_name: Optional[str] = ..., 
                etag: Optional[int] = ..., 
                expiry_date: Optional[date] = ..., 
                expiry_date_time: Optional[datetime] = ..., 
                original_quantity: Optional[int] = ..., 
                plan_information: Optional[ReservationOrderBillingPlanInformation] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                request_date_time: Optional[datetime] = ..., 
                reservations: Optional[List[ReservationResponse]] = ..., 
                review_date_time: Optional[datetime] = ..., 
                term: Optional[Union[str, ReservationTerm]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ReservationResponse(ProxyResource):
        etag: int
        id: str
        kind: str
        location: str
        name: str
        properties: ReservationsProperties
        sku: SkuName
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                etag: Optional[int] = ..., 
                kind: Optional[Literal[Compute]] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ReservationsProperties] = ..., 
                sku: Optional[SkuName] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ReservationSplitProperties(Model):
        split_destinations: list[str]
        split_source: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                split_destinations: Optional[List[str]] = ..., 
                split_source: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ReservationStatusCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        EXPIRED = "Expired"
        MERGED = "Merged"
        NONE = "None"
        PAYMENT_INSTRUMENT_ERROR = "PaymentInstrumentError"
        PENDING = "Pending"
        PROCESSING = "Processing"
        PURCHASE_ERROR = "PurchaseError"
        SPLIT = "Split"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.reservations.models.ReservationSummary(Model):
        cancelled_count: float
        expired_count: float
        expiring_count: float
        failed_count: float
        no_benefit_count: float
        pending_count: float
        processing_count: float
        succeeded_count: float
        warning_count: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ReservationSwapProperties(Model):
        swap_destination: str
        swap_source: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                swap_destination: Optional[str] = ..., 
                swap_source: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ReservationTerm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P1_Y = "P1Y"
        P3_Y = "P3Y"
        P5_Y = "P5Y"


    class azure.mgmt.reservations.models.ReservationToExchange(Model):
        billing_information: BillingInformation
        billing_refund_amount: Price
        quantity: int
        reservation_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_information: Optional[BillingInformation] = ..., 
                billing_refund_amount: Optional[Price] = ..., 
                quantity: Optional[int] = ..., 
                reservation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ReservationToPurchaseCalculateExchange(Model):
        billing_currency_total: Price
        properties: PurchaseRequest

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_currency_total: Optional[Price] = ..., 
                properties: Optional[PurchaseRequest] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ReservationToPurchaseExchange(Model):
        billing_currency_total: Price
        properties: PurchaseRequest
        reservation_id: str
        reservation_order_id: str
        status: Union[str, OperationStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_currency_total: Optional[Price] = ..., 
                properties: Optional[PurchaseRequest] = ..., 
                reservation_id: Optional[str] = ..., 
                reservation_order_id: Optional[str] = ..., 
                status: Optional[Union[str, OperationStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ReservationToReturn(Model):
        quantity: int
        reservation_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                quantity: Optional[int] = ..., 
                reservation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ReservationToReturnForExchange(Model):
        billing_information: BillingInformation
        billing_refund_amount: Price
        quantity: int
        reservation_id: str
        status: Union[str, OperationStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_information: Optional[BillingInformation] = ..., 
                billing_refund_amount: Optional[Price] = ..., 
                quantity: Optional[int] = ..., 
                reservation_id: Optional[str] = ..., 
                status: Optional[Union[str, OperationStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ReservationUtilizationAggregates(Model):
        grain: float
        grain_unit: str
        value: float
        value_unit: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ReservationsListResult(Model):
        next_link: str
        summary: ReservationSummary
        value: list[ReservationResponse]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                summary: Optional[ReservationSummary] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ReservationsProperties(Model):
        applied_scope_properties: AppliedScopeProperties
        applied_scope_type: Union[str, AppliedScopeType]
        applied_scopes: list[str]
        archived: bool
        benefit_start_time: datetime
        billing_plan: Union[str, ReservationBillingPlan]
        billing_scope_id: str
        capabilities: str
        display_name: str
        display_provisioning_state: str
        effective_date_time: datetime
        expiry_date: date
        expiry_date_time: datetime
        extended_status_info: ExtendedStatusInfo
        instance_flexibility: Union[str, InstanceFlexibility]
        last_updated_date_time: datetime
        merge_properties: ReservationMergeProperties
        provisioning_state: Union[str, ProvisioningState]
        provisioning_sub_state: str
        purchase_date: date
        purchase_date_time: datetime
        quantity: int
        renew: bool
        renew_destination: str
        renew_properties: RenewPropertiesResponse
        renew_source: str
        reserved_resource_type: Union[str, ReservedResourceType]
        review_date_time: datetime
        sku_description: str
        split_properties: ReservationSplitProperties
        swap_properties: ReservationSwapProperties
        term: Union[str, ReservationTerm]
        user_friendly_applied_scope_type: str
        user_friendly_renew_state: str
        utilization: ReservationsPropertiesUtilization

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                applied_scope_properties: Optional[AppliedScopeProperties] = ..., 
                applied_scope_type: Optional[Union[str, AppliedScopeType]] = ..., 
                applied_scopes: Optional[List[str]] = ..., 
                archived: Optional[bool] = ..., 
                benefit_start_time: Optional[datetime] = ..., 
                billing_plan: Optional[Union[str, ReservationBillingPlan]] = ..., 
                billing_scope_id: Optional[str] = ..., 
                capabilities: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                effective_date_time: Optional[datetime] = ..., 
                expiry_date: Optional[date] = ..., 
                expiry_date_time: Optional[datetime] = ..., 
                extended_status_info: Optional[ExtendedStatusInfo] = ..., 
                instance_flexibility: Optional[Union[str, InstanceFlexibility]] = ..., 
                merge_properties: Optional[ReservationMergeProperties] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                purchase_date: Optional[date] = ..., 
                purchase_date_time: Optional[datetime] = ..., 
                quantity: Optional[int] = ..., 
                renew: bool = False, 
                renew_destination: Optional[str] = ..., 
                renew_properties: Optional[RenewPropertiesResponse] = ..., 
                renew_source: Optional[str] = ..., 
                reserved_resource_type: Optional[Union[str, ReservedResourceType]] = ..., 
                review_date_time: Optional[datetime] = ..., 
                sku_description: Optional[str] = ..., 
                split_properties: Optional[ReservationSplitProperties] = ..., 
                swap_properties: Optional[ReservationSwapProperties] = ..., 
                term: Optional[Union[str, ReservationTerm]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ReservationsPropertiesUtilization(Model):
        aggregates: list[ReservationUtilizationAggregates]
        trend: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                aggregates: Optional[List[ReservationUtilizationAggregates]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ReservedResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APP_SERVICE = "AppService"
        AVS = "AVS"
        AZURE_DATA_EXPLORER = "AzureDataExplorer"
        AZURE_FILES = "AzureFiles"
        BLOCK_BLOB = "BlockBlob"
        COSMOS_DB = "CosmosDb"
        DATABRICKS = "Databricks"
        DATA_FACTORY = "DataFactory"
        DEDICATED_HOST = "DedicatedHost"
        MANAGED_DISK = "ManagedDisk"
        MARIA_DB = "MariaDb"
        MY_SQL = "MySql"
        NET_APP_STORAGE = "NetAppStorage"
        POSTGRE_SQL = "PostgreSql"
        REDIS_CACHE = "RedisCache"
        RED_HAT = "RedHat"
        RED_HAT_OSA = "RedHatOsa"
        SAP_HANA = "SapHana"
        SQL_AZURE_HYBRID_BENEFIT = "SqlAzureHybridBenefit"
        SQL_DATABASES = "SqlDatabases"
        SQL_DATA_WAREHOUSE = "SqlDataWarehouse"
        SQL_EDGE = "SqlEdge"
        SUSE_LINUX = "SuseLinux"
        VIRTUAL_MACHINES = "VirtualMachines"
        VIRTUAL_MACHINE_SOFTWARE = "VirtualMachineSoftware"
        V_MWARE_CLOUD_SIMPLE = "VMwareCloudSimple"


    class azure.mgmt.reservations.models.Resource(Model):
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ResourceName(Model):
        localized_value: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEDICATED = "dedicated"
        LOW_PRIORITY = "lowPriority"
        SERVICE_SPECIFIC = "serviceSpecific"
        SHARED = "shared"
        STANDARD = "standard"


    class azure.mgmt.reservations.models.SavingsPlanPurchaseRequest(Model):
        applied_scope_properties: AppliedScopeProperties
        applied_scope_type: Union[str, AppliedScopeType]
        billing_plan: Union[str, BillingPlan]
        billing_scope_id: str
        commitment: Commitment
        display_name: str
        sku: SkuName
        term: Union[str, SavingsPlanTerm]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                applied_scope_properties: Optional[AppliedScopeProperties] = ..., 
                applied_scope_type: Optional[Union[str, AppliedScopeType]] = ..., 
                billing_plan: Optional[Union[str, BillingPlan]] = ..., 
                billing_scope_id: Optional[str] = ..., 
                commitment: Optional[Commitment] = ..., 
                display_name: Optional[str] = ..., 
                sku: Optional[SkuName] = ..., 
                term: Optional[Union[str, SavingsPlanTerm]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.SavingsPlanTerm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P1_Y = "P1Y"
        P3_Y = "P3Y"


    class azure.mgmt.reservations.models.SavingsPlanToPurchaseCalculateExchange(Model):
        billing_currency_total: Price
        properties: SavingsPlanPurchaseRequest

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_currency_total: Optional[Price] = ..., 
                properties: Optional[SavingsPlanPurchaseRequest] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.SavingsPlanToPurchaseExchange(Model):
        billing_currency_total: Price
        properties: SavingsPlanPurchaseRequest
        savings_plan_id: str
        savings_plan_order_id: str
        status: Union[str, OperationStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_currency_total: Optional[Price] = ..., 
                properties: Optional[SavingsPlanPurchaseRequest] = ..., 
                savings_plan_id: Optional[str] = ..., 
                savings_plan_order_id: Optional[str] = ..., 
                status: Optional[Union[str, OperationStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ScopeProperties(Model):
        scope: str
        valid: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                scope: Optional[str] = ..., 
                valid: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ServiceError(Model):
        code: str
        details: list[ServiceErrorDetail]
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.ServiceErrorDetail(Model):
        code: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.SkuCapability(Model):
        name: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.SkuName(Model):
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.SkuProperty(Model):
        name: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.SkuRestriction(Model):
        reason_code: str
        type: str
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                reason_code: Optional[str] = ..., 
                type: Optional[str] = ..., 
                values: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.SplitRequest(Model):
        quantities: list[int]
        reservation_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                quantities: Optional[List[int]] = ..., 
                reservation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.SubRequest(Model):
        limit: int
        message: str
        name: ResourceName
        provisioning_state: Union[str, QuotaRequestState]
        resource_type: str
        sub_request_id: str
        unit: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[ResourceName] = ..., 
                provisioning_state: Optional[Union[str, QuotaRequestState]] = ..., 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.SubscriptionScopeProperties(Model):
        scopes: list[ScopeProperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                scopes: Optional[List[ScopeProperties]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.reservations.models.UserFriendlyAppliedScopeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGEMENT_GROUP = "ManagementGroup"
        NONE = "None"
        RESOURCE_GROUP = "ResourceGroup"
        SHARED = "Shared"
        SINGLE = "Single"


    class azure.mgmt.reservations.models.UserFriendlyRenewState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_APPLICABLE = "NotApplicable"
        NOT_RENEWED = "NotRenewed"
        OFF = "Off"
        ON = "On"
        RENEWED = "Renewed"


namespace azure.mgmt.reservations.operations

    class azure.mgmt.reservations.operations.AzureReservationAPIOperationsMixin(AzureReservationAPIMixinABC):

        @distributed_trace
        def get_applied_reservation_list(
                self, 
                subscription_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AppliedReservations: ...

        @distributed_trace
        def get_catalog(
                self, 
                subscription_id: str, 
                reserved_resource_type: Optional[str] = None, 
                location: Optional[str] = None, 
                publisher_id: Optional[str] = None, 
                offer_id: Optional[str] = None, 
                plan_id: Optional[str] = None, 
                filter: Optional[str] = None, 
                skip: Optional[float] = None, 
                take: Optional[float] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Catalog]: ...


    class azure.mgmt.reservations.operations.CalculateExchangeOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_post(
                self, 
                body: CalculateExchangeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CalculateExchangeOperationResultResponse]: ...

        @overload
        def begin_post(
                self, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CalculateExchangeOperationResultResponse]: ...


    class azure.mgmt.reservations.operations.CalculateRefundOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def post(
                self, 
                reservation_order_id: str, 
                body: CalculateRefundRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculateRefundResponse: ...

        @overload
        def post(
                self, 
                reservation_order_id: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculateRefundResponse: ...


    class azure.mgmt.reservations.operations.ExchangeOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_post(
                self, 
                body: ExchangeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExchangeOperationResultResponse]: ...

        @overload
        def begin_post(
                self, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExchangeOperationResultResponse]: ...


    class azure.mgmt.reservations.operations.OperationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[OperationResponse]: ...


    class azure.mgmt.reservations.operations.QuotaOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                subscription_id: str, 
                provider_id: str, 
                location: str, 
                resource_name: str, 
                create_quota_request: CurrentQuotaLimitBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CurrentQuotaLimitBase]: ...

        @overload
        def begin_create_or_update(
                self, 
                subscription_id: str, 
                provider_id: str, 
                location: str, 
                resource_name: str, 
                create_quota_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CurrentQuotaLimitBase]: ...

        @overload
        def begin_update(
                self, 
                subscription_id: str, 
                provider_id: str, 
                location: str, 
                resource_name: str, 
                create_quota_request: CurrentQuotaLimitBase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CurrentQuotaLimitBase]: ...

        @overload
        def begin_update(
                self, 
                subscription_id: str, 
                provider_id: str, 
                location: str, 
                resource_name: str, 
                create_quota_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CurrentQuotaLimitBase]: ...

        @distributed_trace
        def get(
                self, 
                subscription_id: str, 
                provider_id: str, 
                location: str, 
                resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CurrentQuotaLimitBase: ...

        @distributed_trace
        def list(
                self, 
                subscription_id: str, 
                provider_id: str, 
                location: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[CurrentQuotaLimitBase]: ...


    class azure.mgmt.reservations.operations.QuotaRequestStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                subscription_id: str, 
                provider_id: str, 
                location: str, 
                id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> QuotaRequestDetails: ...

        @distributed_trace
        def list(
                self, 
                subscription_id: str, 
                provider_id: str, 
                location: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skiptoken: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[QuotaRequestDetails]: ...


    class azure.mgmt.reservations.operations.ReservationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def archive(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def begin_available_scopes(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                body: AvailableScopeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AvailableScopeProperties]: ...

        @overload
        def begin_available_scopes(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AvailableScopeProperties]: ...

        @overload
        def begin_merge(
                self, 
                reservation_order_id: str, 
                body: MergeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[List[ReservationResponse]]: ...

        @overload
        def begin_merge(
                self, 
                reservation_order_id: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[List[ReservationResponse]]: ...

        @overload
        def begin_split(
                self, 
                reservation_order_id: str, 
                body: SplitRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[List[ReservationResponse]]: ...

        @overload
        def begin_split(
                self, 
                reservation_order_id: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[List[ReservationResponse]]: ...

        @overload
        def begin_update(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                parameters: Patch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReservationResponse]: ...

        @overload
        def begin_update(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReservationResponse]: ...

        @distributed_trace
        def get(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                expand: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ReservationResponse: ...

        @distributed_trace
        def list(
                self, 
                reservation_order_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ReservationResponse]: ...

        @distributed_trace
        def list_all(
                self, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                refresh_summary: Optional[str] = None, 
                skiptoken: Optional[float] = None, 
                selected_state: Optional[str] = None, 
                take: Optional[float] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ReservationResponse]: ...

        @distributed_trace
        def list_revisions(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ReservationResponse]: ...

        @distributed_trace
        def unarchive(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.reservations.operations.ReservationOrderOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_purchase(
                self, 
                reservation_order_id: str, 
                body: PurchaseRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReservationOrderResponse]: ...

        @overload
        def begin_purchase(
                self, 
                reservation_order_id: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReservationOrderResponse]: ...

        @overload
        def calculate(
                self, 
                body: PurchaseRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculatePriceResponse: ...

        @overload
        def calculate(
                self, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculatePriceResponse: ...

        @overload
        def change_directory(
                self, 
                reservation_order_id: str, 
                body: ChangeDirectoryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ChangeDirectoryResponse: ...

        @overload
        def change_directory(
                self, 
                reservation_order_id: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ChangeDirectoryResponse: ...

        @distributed_trace
        def get(
                self, 
                reservation_order_id: str, 
                expand: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ReservationOrderResponse: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ReservationOrderResponse]: ...


    class azure.mgmt.reservations.operations.ReturnOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_post(
                self, 
                reservation_order_id: str, 
                body: RefundRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReservationOrderResponse]: ...

        @overload
        def begin_post(
                self, 
                reservation_order_id: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReservationOrderResponse]: ...


```