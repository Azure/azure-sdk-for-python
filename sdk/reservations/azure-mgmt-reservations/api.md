```py
namespace azure.mgmt.reservations

    class azure.mgmt.reservations.ReservationsMgmtClient(_ReservationsMgmtClientOperationsMixin): implements ContextManager 
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
                base_url: Optional[str] = None, 
                *, 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2022-11-01', params_added_on={'2022-11-01': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2022-11-01'])
        def get_applied_reservation_list(
                self, 
                subscription_id: str, 
                **kwargs: Any
            ) -> AppliedReservations: ...

        @distributed_trace
        @api_version_validation(method_added_on='2022-11-01', params_added_on={'2022-11-01': ['api_version', 'subscription_id', 'reserved_resource_type', 'location', 'publisher_id', 'offer_id', 'plan_id', 'filter', 'skip', 'take', 'accept']}, api_versions_list=['2022-11-01'])
        def get_catalog(
                self, 
                subscription_id: str, 
                *, 
                filter: Optional[str] = ..., 
                location: Optional[str] = ..., 
                offer_id: Optional[str] = ..., 
                plan_id: Optional[str] = ..., 
                publisher_id: Optional[str] = ..., 
                reserved_resource_type: Optional[str] = ..., 
                skip: Optional[float] = ..., 
                take: Optional[float] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Catalog]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.reservations.aio

    class azure.mgmt.reservations.aio.ReservationsMgmtClient(_ReservationsMgmtClientOperationsMixin): implements AsyncContextManager 
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
                base_url: Optional[str] = None, 
                *, 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2022-11-01', params_added_on={'2022-11-01': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2022-11-01'])
        async def get_applied_reservation_list(
                self, 
                subscription_id: str, 
                **kwargs: Any
            ) -> AppliedReservations: ...

        @distributed_trace
        @api_version_validation(method_added_on='2022-11-01', params_added_on={'2022-11-01': ['api_version', 'subscription_id', 'reserved_resource_type', 'location', 'publisher_id', 'offer_id', 'plan_id', 'filter', 'skip', 'take', 'accept']}, api_versions_list=['2022-11-01'])
        def get_catalog(
                self, 
                subscription_id: str, 
                *, 
                filter: Optional[str] = ..., 
                location: Optional[str] = ..., 
                offer_id: Optional[str] = ..., 
                plan_id: Optional[str] = ..., 
                publisher_id: Optional[str] = ..., 
                reserved_resource_type: Optional[str] = ..., 
                skip: Optional[float] = ..., 
                take: Optional[float] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Catalog]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.reservations.aio.operations

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
                body: CalculateExchangeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CalculateExchangeOperationResultResponse]: ...

        @overload
        async def begin_post(
                self, 
                body: IO[bytes], 
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
                body: CalculateRefundRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculateRefundResponse: ...

        @overload
        async def post(
                self, 
                reservation_order_id: str, 
                body: IO[bytes], 
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
                body: ExchangeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExchangeOperationResultResponse]: ...

        @overload
        async def begin_post(
                self, 
                body: IO[bytes], 
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
        def list(self, **kwargs: Any) -> AsyncItemPaged[OperationResponse]: ...


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
                create_quota_request: IO[bytes], 
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
                create_quota_request: IO[bytes], 
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
                **kwargs: Any
            ) -> CurrentQuotaLimitBase: ...

        @distributed_trace
        def list(
                self, 
                subscription_id: str, 
                provider_id: str, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CurrentQuotaLimitBase]: ...


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
                **kwargs: Any
            ) -> QuotaRequestDetails: ...

        @distributed_trace
        def list(
                self, 
                subscription_id: str, 
                provider_id: str, 
                location: str, 
                *, 
                filter: Optional[str] = ..., 
                skiptoken: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[QuotaRequestDetails]: ...


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
                body: IO[bytes], 
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
                body: MergeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[List[ReservationResponse]]: ...

        @overload
        async def begin_merge(
                self, 
                reservation_order_id: str, 
                body: IO[bytes], 
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
                body: SplitRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[List[ReservationResponse]]: ...

        @overload
        async def begin_split(
                self, 
                reservation_order_id: str, 
                body: IO[bytes], 
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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReservationResponse]: ...

        @distributed_trace_async
        async def get(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> ReservationResponse: ...

        @distributed_trace
        def list(
                self, 
                reservation_order_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ReservationResponse]: ...

        @distributed_trace
        def list_all(
                self, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                refresh_summary: Optional[str] = ..., 
                selected_state: Optional[str] = ..., 
                skiptoken: Optional[float] = ..., 
                take: Optional[float] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ReservationResponse]: ...

        @distributed_trace
        def list_revisions(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ReservationResponse]: ...

        @distributed_trace_async
        async def unarchive(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
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
                body: PurchaseRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReservationOrderResponse]: ...

        @overload
        async def begin_purchase(
                self, 
                reservation_order_id: str, 
                body: IO[bytes], 
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
                body: PurchaseRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculatePriceResponse: ...

        @overload
        async def calculate(
                self, 
                body: IO[bytes], 
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
                body: ChangeDirectoryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ChangeDirectoryResponse: ...

        @overload
        async def change_directory(
                self, 
                reservation_order_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ChangeDirectoryResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                reservation_order_id: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> ReservationOrderResponse: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ReservationOrderResponse]: ...


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
                body: RefundRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReservationOrderResponse]: ...

        @overload
        async def begin_post(
                self, 
                reservation_order_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ReservationOrderResponse]: ...


namespace azure.mgmt.reservations.models

    class azure.mgmt.reservations.models.AppliedReservationList(_Model):
        next_link: Optional[str]
        value: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.AppliedReservations(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[AppliedReservationsProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AppliedReservationsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.reservations.models.AppliedReservationsProperties(_Model):
        reservation_order_ids: Optional[AppliedReservationList]

        @overload
        def __init__(
                self, 
                *, 
                reservation_order_ids: Optional[AppliedReservationList] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.AppliedScopeProperties(_Model):
        display_name: Optional[str]
        management_group_id: Optional[str]
        resource_group_id: Optional[str]
        subscription_id: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                management_group_id: Optional[str] = ..., 
                resource_group_id: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.AppliedScopeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGEMENT_GROUP = "ManagementGroup"
        SHARED = "Shared"
        SINGLE = "Single"


    class azure.mgmt.reservations.models.AvailableScopeProperties(_Model):
        properties: Optional[SubscriptionScopeProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SubscriptionScopeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.AvailableScopeRequest(_Model):
        properties: Optional[AvailableScopeRequestProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AvailableScopeRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.AvailableScopeRequestProperties(_Model):
        scopes: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                scopes: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.BillingInformation(_Model):
        billing_currency_prorated_amount: Optional[Price]
        billing_currency_remaining_commitment_amount: Optional[Price]
        billing_currency_total_paid_amount: Optional[Price]

        @overload
        def __init__(
                self, 
                *, 
                billing_currency_prorated_amount: Optional[Price] = ..., 
                billing_currency_remaining_commitment_amount: Optional[Price] = ..., 
                billing_currency_total_paid_amount: Optional[Price] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.BillingPlan(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P1_M = "P1M"


    class azure.mgmt.reservations.models.CalculateExchangeOperationResultResponse(_Model):
        error: Optional[OperationResultError]
        id: Optional[str]
        name: Optional[str]
        properties: Optional[CalculateExchangeResponseProperties]
        status: Optional[Union[str, CalculateExchangeOperationResultStatus]]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[OperationResultError] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[CalculateExchangeResponseProperties] = ..., 
                status: Optional[Union[str, CalculateExchangeOperationResultStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.CalculateExchangeOperationResultStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        FAILED = "Failed"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.reservations.models.CalculateExchangeRequest(_Model):
        properties: Optional[CalculateExchangeRequestProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CalculateExchangeRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.CalculateExchangeRequestProperties(_Model):
        reservations_to_exchange: Optional[list[ReservationToReturn]]
        reservations_to_purchase: Optional[list[PurchaseRequest]]
        savings_plans_to_purchase: Optional[list[SavingsPlanPurchaseRequest]]

        @overload
        def __init__(
                self, 
                *, 
                reservations_to_exchange: Optional[list[ReservationToReturn]] = ..., 
                reservations_to_purchase: Optional[list[PurchaseRequest]] = ..., 
                savings_plans_to_purchase: Optional[list[SavingsPlanPurchaseRequest]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.CalculateExchangeResponseProperties(_Model):
        net_payable: Optional[Price]
        policy_result: Optional[ExchangePolicyErrors]
        purchases_total: Optional[Price]
        refunds_total: Optional[Price]
        reservations_to_exchange: Optional[list[ReservationToExchange]]
        reservations_to_purchase: Optional[list[ReservationToPurchaseCalculateExchange]]
        savings_plans_to_purchase: Optional[list[SavingsPlanToPurchaseCalculateExchange]]
        session_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                net_payable: Optional[Price] = ..., 
                policy_result: Optional[ExchangePolicyErrors] = ..., 
                purchases_total: Optional[Price] = ..., 
                refunds_total: Optional[Price] = ..., 
                reservations_to_exchange: Optional[list[ReservationToExchange]] = ..., 
                reservations_to_purchase: Optional[list[ReservationToPurchaseCalculateExchange]] = ..., 
                savings_plans_to_purchase: Optional[list[SavingsPlanToPurchaseCalculateExchange]] = ..., 
                session_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.CalculatePriceResponse(_Model):
        properties: Optional[CalculatePriceResponseProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CalculatePriceResponseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.CalculatePriceResponseProperties(_Model):
        billing_currency_total: Optional[CalculatePriceResponsePropertiesBillingCurrencyTotal]
        grand_total: Optional[float]
        is_billing_partner_managed: Optional[bool]
        is_tax_included: Optional[bool]
        net_total: Optional[float]
        payment_schedule: Optional[list[PaymentDetail]]
        pricing_currency_total: Optional[CalculatePriceResponsePropertiesPricingCurrencyTotal]
        reservation_order_id: Optional[str]
        sku_description: Optional[str]
        sku_title: Optional[str]
        tax_total: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                billing_currency_total: Optional[CalculatePriceResponsePropertiesBillingCurrencyTotal] = ..., 
                grand_total: Optional[float] = ..., 
                is_billing_partner_managed: Optional[bool] = ..., 
                is_tax_included: Optional[bool] = ..., 
                net_total: Optional[float] = ..., 
                payment_schedule: Optional[list[PaymentDetail]] = ..., 
                pricing_currency_total: Optional[CalculatePriceResponsePropertiesPricingCurrencyTotal] = ..., 
                reservation_order_id: Optional[str] = ..., 
                sku_description: Optional[str] = ..., 
                sku_title: Optional[str] = ..., 
                tax_total: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.CalculatePriceResponsePropertiesBillingCurrencyTotal(_Model):
        amount: Optional[float]
        currency_code: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                amount: Optional[float] = ..., 
                currency_code: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.CalculatePriceResponsePropertiesPricingCurrencyTotal(_Model):
        amount: Optional[float]
        currency_code: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                amount: Optional[float] = ..., 
                currency_code: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.CalculateRefundRequest(_Model):
        id: Optional[str]
        properties: Optional[CalculateRefundRequestProperties]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                properties: Optional[CalculateRefundRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.CalculateRefundRequestProperties(_Model):
        reservation_to_return: Optional[ReservationToReturn]
        scope: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                reservation_to_return: Optional[ReservationToReturn] = ..., 
                scope: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.CalculateRefundResponse(_Model):
        id: Optional[str]
        properties: Optional[RefundResponseProperties]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                properties: Optional[RefundResponseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.Catalog(_Model):
        billing_plans: Optional[dict[str, list[Union[str, ReservationBillingPlan]]]]
        capabilities: Optional[list[SkuCapability]]
        locations: Optional[list[str]]
        msrp: Optional[CatalogMsrp]
        name: Optional[str]
        resource_type: Optional[str]
        restrictions: Optional[list[SkuRestriction]]
        size: Optional[str]
        sku_properties: Optional[list[SkuProperty]]
        terms: Optional[list[Union[str, ReservationTerm]]]
        tier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                billing_plans: Optional[dict[str, list[Union[str, ReservationBillingPlan]]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.CatalogMsrp(_Model):
        p1_y: Optional[Price]
        p3_y: Optional[Price]
        p5_y: Optional[Price]

        @overload
        def __init__(
                self, 
                *, 
                p1_y: Optional[Price] = ..., 
                p3_y: Optional[Price] = ..., 
                p5_y: Optional[Price] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ChangeDirectoryRequest(_Model):
        destination_tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                destination_tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ChangeDirectoryResponse(_Model):
        reservation_order: Optional[ChangeDirectoryResult]
        reservations: Optional[list[ChangeDirectoryResult]]

        @overload
        def __init__(
                self, 
                *, 
                reservation_order: Optional[ChangeDirectoryResult] = ..., 
                reservations: Optional[list[ChangeDirectoryResult]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ChangeDirectoryResult(_Model):
        error: Optional[str]
        id: Optional[str]
        is_succeeded: Optional[bool]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[str] = ..., 
                id: Optional[str] = ..., 
                is_succeeded: Optional[bool] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.Commitment(Price):
        amount: float
        currency_code: str
        grain: Optional[Union[str, CommitmentGrain]]

        @overload
        def __init__(
                self, 
                *, 
                amount: Optional[float] = ..., 
                currency_code: Optional[str] = ..., 
                grain: Optional[Union[str, CommitmentGrain]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.CommitmentGrain(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HOURLY = "Hourly"


    class azure.mgmt.reservations.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.reservations.models.CurrentQuotaLimitBase(ProxyResource):
        id: str
        name: str
        properties: Optional[QuotaProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[QuotaProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.Error(_Model):
        error: Optional[ExtendedErrorInfo]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ExtendedErrorInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ErrorDetails(_Model):
        code: Optional[str]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.reservations.models.ErrorResponse(_Model):
        error: Optional[ErrorDetails]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.reservations.models.ExceptionResponse(_Model):
        error: Optional[ServiceError]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ServiceError] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ExchangeOperationResultResponse(_Model):
        error: Optional[OperationResultError]
        id: Optional[str]
        name: Optional[str]
        properties: Optional[ExchangeResponseProperties]
        status: Optional[Union[str, ExchangeOperationResultStatus]]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[OperationResultError] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[ExchangeResponseProperties] = ..., 
                status: Optional[Union[str, ExchangeOperationResultStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ExchangeOperationResultStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        FAILED = "Failed"
        PENDING_PURCHASES = "PendingPurchases"
        PENDING_REFUNDS = "PendingRefunds"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.reservations.models.ExchangePolicyError(_Model):
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


    class azure.mgmt.reservations.models.ExchangePolicyErrors(_Model):
        policy_errors: Optional[list[ExchangePolicyError]]

        @overload
        def __init__(
                self, 
                *, 
                policy_errors: Optional[list[ExchangePolicyError]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ExchangeRequest(_Model):
        properties: Optional[ExchangeRequestProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ExchangeRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ExchangeRequestProperties(_Model):
        session_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                session_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ExchangeResponseProperties(_Model):
        net_payable: Optional[Price]
        policy_result: Optional[ExchangePolicyErrors]
        purchases_total: Optional[Price]
        refunds_total: Optional[Price]
        reservations_to_exchange: Optional[list[ReservationToReturnForExchange]]
        reservations_to_purchase: Optional[list[ReservationToPurchaseExchange]]
        savings_plans_to_purchase: Optional[list[SavingsPlanToPurchaseExchange]]
        session_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                net_payable: Optional[Price] = ..., 
                policy_result: Optional[ExchangePolicyErrors] = ..., 
                purchases_total: Optional[Price] = ..., 
                refunds_total: Optional[Price] = ..., 
                reservations_to_exchange: Optional[list[ReservationToReturnForExchange]] = ..., 
                reservations_to_purchase: Optional[list[ReservationToPurchaseExchange]] = ..., 
                savings_plans_to_purchase: Optional[list[SavingsPlanToPurchaseExchange]] = ..., 
                session_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ExtendedErrorInfo(_Model):
        code: Optional[Union[str, ErrorResponseCode]]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[Union[str, ErrorResponseCode]] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ExtendedStatusInfo(_Model):
        message: Optional[str]
        status_code: Optional[Union[str, ReservationStatusCode]]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                status_code: Optional[Union[str, ReservationStatusCode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.InstanceFlexibility(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFF = "Off"
        ON = "On"


    class azure.mgmt.reservations.models.MergeProperties(_Model):
        sources: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                sources: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.MergeRequest(_Model):
        properties: Optional[MergeProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MergeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.reservations.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.OperationResponse(_Model):
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.OperationResultError(_Model):
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


    class azure.mgmt.reservations.models.OperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        FAILED = "Failed"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.reservations.models.Patch(_Model):
        properties: Optional[PatchProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PatchProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.reservations.models.PatchProperties(_Model):
        applied_scope_properties: Optional[AppliedScopeProperties]
        applied_scope_type: Optional[Union[str, AppliedScopeType]]
        applied_scopes: Optional[list[str]]
        instance_flexibility: Optional[Union[str, InstanceFlexibility]]
        name: Optional[str]
        renew: Optional[bool]
        renew_properties: Optional[PatchPropertiesRenewProperties]
        review_date_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                applied_scope_properties: Optional[AppliedScopeProperties] = ..., 
                applied_scope_type: Optional[Union[str, AppliedScopeType]] = ..., 
                applied_scopes: Optional[list[str]] = ..., 
                instance_flexibility: Optional[Union[str, InstanceFlexibility]] = ..., 
                name: Optional[str] = ..., 
                renew: Optional[bool] = ..., 
                renew_properties: Optional[PatchPropertiesRenewProperties] = ..., 
                review_date_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.PatchPropertiesRenewProperties(_Model):
        purchase_properties: Optional[PurchaseRequest]

        @overload
        def __init__(
                self, 
                *, 
                purchase_properties: Optional[PurchaseRequest] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.PaymentDetail(_Model):
        billing_account: Optional[str]
        billing_currency_total: Optional[Price]
        due_date: Optional[date]
        extended_status_info: Optional[ExtendedStatusInfo]
        payment_date: Optional[date]
        pricing_currency_total: Optional[Price]
        status: Optional[Union[str, PaymentStatus]]

        @overload
        def __init__(
                self, 
                *, 
                billing_account: Optional[str] = ..., 
                billing_currency_total: Optional[Price] = ..., 
                due_date: Optional[date] = ..., 
                extended_status_info: Optional[ExtendedStatusInfo] = ..., 
                payment_date: Optional[date] = ..., 
                pricing_currency_total: Optional[Price] = ..., 
                status: Optional[Union[str, PaymentStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.PaymentStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        FAILED = "Failed"
        SCHEDULED = "Scheduled"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.reservations.models.Price(_Model):
        amount: Optional[float]
        currency_code: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                amount: Optional[float] = ..., 
                currency_code: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.reservations.models.PurchaseRequest(_Model):
        location: Optional[str]
        properties: Optional[PurchaseRequestProperties]
        sku: Optional[SkuName]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[PurchaseRequestProperties] = ..., 
                sku: Optional[SkuName] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.reservations.models.PurchaseRequestProperties(_Model):
        applied_scope_properties: Optional[AppliedScopeProperties]
        applied_scope_type: Optional[Union[str, AppliedScopeType]]
        applied_scopes: Optional[list[str]]
        billing_plan: Optional[Union[str, ReservationBillingPlan]]
        billing_scope_id: Optional[str]
        display_name: Optional[str]
        quantity: Optional[int]
        renew: Optional[bool]
        reserved_resource_properties: Optional[PurchaseRequestPropertiesReservedResourceProperties]
        reserved_resource_type: Optional[Union[str, ReservedResourceType]]
        review_date_time: Optional[datetime]
        term: Optional[Union[str, ReservationTerm]]

        @overload
        def __init__(
                self, 
                *, 
                applied_scope_properties: Optional[AppliedScopeProperties] = ..., 
                applied_scope_type: Optional[Union[str, AppliedScopeType]] = ..., 
                applied_scopes: Optional[list[str]] = ..., 
                billing_plan: Optional[Union[str, ReservationBillingPlan]] = ..., 
                billing_scope_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                quantity: Optional[int] = ..., 
                renew: Optional[bool] = ..., 
                reserved_resource_properties: Optional[PurchaseRequestPropertiesReservedResourceProperties] = ..., 
                reserved_resource_type: Optional[Union[str, ReservedResourceType]] = ..., 
                review_date_time: Optional[datetime] = ..., 
                term: Optional[Union[str, ReservationTerm]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.PurchaseRequestPropertiesReservedResourceProperties(_Model):
        instance_flexibility: Optional[Union[str, InstanceFlexibility]]

        @overload
        def __init__(
                self, 
                *, 
                instance_flexibility: Optional[Union[str, InstanceFlexibility]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.QuotaProperties(_Model):
        current_value: Optional[int]
        limit: Optional[int]
        name: Optional[ResourceName]
        properties: Optional[Any]
        quota_period: Optional[str]
        resource_type: Optional[Union[str, ResourceType]]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                limit: Optional[int] = ..., 
                name: Optional[ResourceName] = ..., 
                properties: Optional[Any] = ..., 
                resource_type: Optional[Union[str, ResourceType]] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.QuotaRequestDetails(ProxyResource):
        id: str
        name: str
        properties: Optional[QuotaRequestProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[QuotaRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.reservations.models.QuotaRequestProperties(_Model):
        message: Optional[str]
        provisioning_state: Optional[Union[str, QuotaRequestState]]
        request_submit_time: Optional[datetime]
        value: Optional[list[SubRequest]]

        @overload
        def __init__(
                self, 
                *, 
                provisioning_state: Optional[Union[str, QuotaRequestState]] = ..., 
                value: Optional[list[SubRequest]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.QuotaRequestState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        FAILED = "Failed"
        INVALID = "Invalid"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.reservations.models.RefundBillingInformation(_Model):
        billing_currency_prorated_amount: Optional[Price]
        billing_currency_remaining_commitment_amount: Optional[Price]
        billing_currency_total_paid_amount: Optional[Price]
        billing_plan: Optional[Union[str, ReservationBillingPlan]]
        completed_transactions: Optional[int]
        total_transactions: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                billing_currency_prorated_amount: Optional[Price] = ..., 
                billing_currency_remaining_commitment_amount: Optional[Price] = ..., 
                billing_currency_total_paid_amount: Optional[Price] = ..., 
                billing_plan: Optional[Union[str, ReservationBillingPlan]] = ..., 
                completed_transactions: Optional[int] = ..., 
                total_transactions: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.RefundPolicyError(_Model):
        code: Optional[Union[str, ErrorResponseCode]]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[Union[str, ErrorResponseCode]] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.RefundPolicyResult(_Model):
        properties: Optional[RefundPolicyResultProperty]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RefundPolicyResultProperty] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.RefundPolicyResultProperty(_Model):
        consumed_refunds_total: Optional[Price]
        max_refund_limit: Optional[Price]
        policy_errors: Optional[list[RefundPolicyError]]

        @overload
        def __init__(
                self, 
                *, 
                consumed_refunds_total: Optional[Price] = ..., 
                max_refund_limit: Optional[Price] = ..., 
                policy_errors: Optional[list[RefundPolicyError]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.RefundRequest(_Model):
        properties: Optional[RefundRequestProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RefundRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.RefundRequestProperties(_Model):
        reservation_to_return: Optional[ReservationToReturn]
        return_reason: Optional[str]
        scope: Optional[str]
        session_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                reservation_to_return: Optional[ReservationToReturn] = ..., 
                return_reason: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                session_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.RefundResponseProperties(_Model):
        billing_information: Optional[RefundBillingInformation]
        billing_refund_amount: Optional[Price]
        policy_result: Optional[RefundPolicyResult]
        pricing_refund_amount: Optional[Price]
        quantity: Optional[int]
        session_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                billing_information: Optional[RefundBillingInformation] = ..., 
                billing_refund_amount: Optional[Price] = ..., 
                policy_result: Optional[RefundPolicyResult] = ..., 
                pricing_refund_amount: Optional[Price] = ..., 
                quantity: Optional[int] = ..., 
                session_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.RenewPropertiesResponse(_Model):
        billing_currency_total: Optional[RenewPropertiesResponseBillingCurrencyTotal]
        pricing_currency_total: Optional[RenewPropertiesResponsePricingCurrencyTotal]
        purchase_properties: Optional[PurchaseRequest]

        @overload
        def __init__(
                self, 
                *, 
                billing_currency_total: Optional[RenewPropertiesResponseBillingCurrencyTotal] = ..., 
                pricing_currency_total: Optional[RenewPropertiesResponsePricingCurrencyTotal] = ..., 
                purchase_properties: Optional[PurchaseRequest] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.RenewPropertiesResponseBillingCurrencyTotal(_Model):
        amount: Optional[float]
        currency_code: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                amount: Optional[float] = ..., 
                currency_code: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.RenewPropertiesResponsePricingCurrencyTotal(_Model):
        amount: Optional[float]
        currency_code: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                amount: Optional[float] = ..., 
                currency_code: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ReservationBillingPlan(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONTHLY = "Monthly"
        UPFRONT = "Upfront"


    class azure.mgmt.reservations.models.ReservationMergeProperties(_Model):
        merge_destination: Optional[str]
        merge_sources: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                merge_destination: Optional[str] = ..., 
                merge_sources: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ReservationOrderBillingPlanInformation(_Model):
        next_payment_due_date: Optional[date]
        pricing_currency_total: Optional[Price]
        start_date: Optional[date]
        transactions: Optional[list[PaymentDetail]]

        @overload
        def __init__(
                self, 
                *, 
                next_payment_due_date: Optional[date] = ..., 
                pricing_currency_total: Optional[Price] = ..., 
                start_date: Optional[date] = ..., 
                transactions: Optional[list[PaymentDetail]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ReservationOrderProperties(_Model):
        benefit_start_time: Optional[datetime]
        billing_plan: Optional[Union[str, ReservationBillingPlan]]
        created_date_time: Optional[datetime]
        display_name: Optional[str]
        expiry_date: Optional[date]
        expiry_date_time: Optional[datetime]
        original_quantity: Optional[int]
        plan_information: Optional[ReservationOrderBillingPlanInformation]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        request_date_time: Optional[datetime]
        reservations: Optional[list[ReservationResponse]]
        review_date_time: Optional[datetime]
        term: Optional[Union[str, ReservationTerm]]

        @overload
        def __init__(
                self, 
                *, 
                benefit_start_time: Optional[datetime] = ..., 
                billing_plan: Optional[Union[str, ReservationBillingPlan]] = ..., 
                created_date_time: Optional[datetime] = ..., 
                display_name: Optional[str] = ..., 
                expiry_date: Optional[date] = ..., 
                expiry_date_time: Optional[datetime] = ..., 
                original_quantity: Optional[int] = ..., 
                plan_information: Optional[ReservationOrderBillingPlanInformation] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                request_date_time: Optional[datetime] = ..., 
                reservations: Optional[list[ReservationResponse]] = ..., 
                review_date_time: Optional[datetime] = ..., 
                term: Optional[Union[str, ReservationTerm]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ReservationOrderResponse(ProxyResource):
        etag: Optional[int]
        id: str
        name: str
        properties: Optional[ReservationOrderProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[int] = ..., 
                properties: Optional[ReservationOrderProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.reservations.models.ReservationResponse(ProxyResource):
        etag: Optional[int]
        id: str
        kind: Optional[Literal["Compute"]]
        location: Optional[str]
        name: str
        properties: Optional[ReservationsProperties]
        sku: Optional[SkuName]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[int] = ..., 
                kind: Optional[Literal[Compute]] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ReservationsProperties] = ..., 
                sku: Optional[SkuName] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ReservationSplitProperties(_Model):
        split_destinations: Optional[list[str]]
        split_source: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                split_destinations: Optional[list[str]] = ..., 
                split_source: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.reservations.models.ReservationSummary(_Model):
        cancelled_count: Optional[float]
        expired_count: Optional[float]
        expiring_count: Optional[float]
        failed_count: Optional[float]
        no_benefit_count: Optional[float]
        pending_count: Optional[float]
        processing_count: Optional[float]
        succeeded_count: Optional[float]
        warning_count: Optional[float]


    class azure.mgmt.reservations.models.ReservationSwapProperties(_Model):
        swap_destination: Optional[str]
        swap_source: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                swap_destination: Optional[str] = ..., 
                swap_source: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ReservationTerm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P1_Y = "P1Y"
        P3_Y = "P3Y"
        P5_Y = "P5Y"


    class azure.mgmt.reservations.models.ReservationToExchange(_Model):
        billing_information: Optional[BillingInformation]
        billing_refund_amount: Optional[Price]
        quantity: Optional[int]
        reservation_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                billing_information: Optional[BillingInformation] = ..., 
                billing_refund_amount: Optional[Price] = ..., 
                quantity: Optional[int] = ..., 
                reservation_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ReservationToPurchaseCalculateExchange(_Model):
        billing_currency_total: Optional[Price]
        properties: Optional[PurchaseRequest]

        @overload
        def __init__(
                self, 
                *, 
                billing_currency_total: Optional[Price] = ..., 
                properties: Optional[PurchaseRequest] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ReservationToPurchaseExchange(_Model):
        billing_currency_total: Optional[Price]
        properties: Optional[PurchaseRequest]
        reservation_id: Optional[str]
        reservation_order_id: Optional[str]
        status: Optional[Union[str, OperationStatus]]

        @overload
        def __init__(
                self, 
                *, 
                billing_currency_total: Optional[Price] = ..., 
                properties: Optional[PurchaseRequest] = ..., 
                reservation_id: Optional[str] = ..., 
                reservation_order_id: Optional[str] = ..., 
                status: Optional[Union[str, OperationStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ReservationToReturn(_Model):
        quantity: Optional[int]
        reservation_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                quantity: Optional[int] = ..., 
                reservation_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ReservationToReturnForExchange(_Model):
        billing_information: Optional[BillingInformation]
        billing_refund_amount: Optional[Price]
        quantity: Optional[int]
        reservation_id: Optional[str]
        status: Optional[Union[str, OperationStatus]]

        @overload
        def __init__(
                self, 
                *, 
                billing_information: Optional[BillingInformation] = ..., 
                billing_refund_amount: Optional[Price] = ..., 
                quantity: Optional[int] = ..., 
                reservation_id: Optional[str] = ..., 
                status: Optional[Union[str, OperationStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ReservationUtilizationAggregates(_Model):
        grain: Optional[float]
        grain_unit: Optional[str]
        value: Optional[float]
        value_unit: Optional[str]


    class azure.mgmt.reservations.models.ReservationsProperties(_Model):
        applied_scope_properties: Optional[AppliedScopeProperties]
        applied_scope_type: Optional[Union[str, AppliedScopeType]]
        applied_scopes: Optional[list[str]]
        archived: Optional[bool]
        benefit_start_time: Optional[datetime]
        billing_plan: Optional[Union[str, ReservationBillingPlan]]
        billing_scope_id: Optional[str]
        capabilities: Optional[str]
        display_name: Optional[str]
        display_provisioning_state: Optional[str]
        effective_date_time: Optional[datetime]
        expiry_date: Optional[date]
        expiry_date_time: Optional[datetime]
        extended_status_info: Optional[ExtendedStatusInfo]
        instance_flexibility: Optional[Union[str, InstanceFlexibility]]
        last_updated_date_time: Optional[datetime]
        merge_properties: Optional[ReservationMergeProperties]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        provisioning_sub_state: Optional[str]
        purchase_date: Optional[date]
        purchase_date_time: Optional[datetime]
        quantity: Optional[int]
        renew: Optional[bool]
        renew_destination: Optional[str]
        renew_properties: Optional[RenewPropertiesResponse]
        renew_source: Optional[str]
        reserved_resource_type: Optional[Union[str, ReservedResourceType]]
        review_date_time: Optional[datetime]
        sku_description: Optional[str]
        split_properties: Optional[ReservationSplitProperties]
        swap_properties: Optional[ReservationSwapProperties]
        term: Optional[Union[str, ReservationTerm]]
        user_friendly_applied_scope_type: Optional[str]
        user_friendly_renew_state: Optional[str]
        utilization: Optional[ReservationsPropertiesUtilization]

        @overload
        def __init__(
                self, 
                *, 
                applied_scope_properties: Optional[AppliedScopeProperties] = ..., 
                applied_scope_type: Optional[Union[str, AppliedScopeType]] = ..., 
                applied_scopes: Optional[list[str]] = ..., 
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
                renew: Optional[bool] = ..., 
                renew_destination: Optional[str] = ..., 
                renew_properties: Optional[RenewPropertiesResponse] = ..., 
                renew_source: Optional[str] = ..., 
                reserved_resource_type: Optional[Union[str, ReservedResourceType]] = ..., 
                review_date_time: Optional[datetime] = ..., 
                sku_description: Optional[str] = ..., 
                split_properties: Optional[ReservationSplitProperties] = ..., 
                swap_properties: Optional[ReservationSwapProperties] = ..., 
                term: Optional[Union[str, ReservationTerm]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ReservationsPropertiesUtilization(_Model):
        aggregates: Optional[list[ReservationUtilizationAggregates]]
        trend: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aggregates: Optional[list[ReservationUtilizationAggregates]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.reservations.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.reservations.models.ResourceName(_Model):
        localized_value: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEDICATED = "dedicated"
        LOW_PRIORITY = "lowPriority"
        SERVICE_SPECIFIC = "serviceSpecific"
        SHARED = "shared"
        STANDARD = "standard"


    class azure.mgmt.reservations.models.SavingsPlanPurchaseRequest(_Model):
        properties: Optional[SavingsPlanPurchaseRequestProperties]
        sku: Optional[SkuName]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SavingsPlanPurchaseRequestProperties] = ..., 
                sku: Optional[SkuName] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.reservations.models.SavingsPlanPurchaseRequestProperties(_Model):
        applied_scope_properties: Optional[AppliedScopeProperties]
        applied_scope_type: Optional[Union[str, AppliedScopeType]]
        billing_plan: Optional[Union[str, BillingPlan]]
        billing_scope_id: Optional[str]
        commitment: Optional[Commitment]
        display_name: Optional[str]
        term: Optional[Union[str, SavingsPlanTerm]]

        @overload
        def __init__(
                self, 
                *, 
                applied_scope_properties: Optional[AppliedScopeProperties] = ..., 
                applied_scope_type: Optional[Union[str, AppliedScopeType]] = ..., 
                billing_plan: Optional[Union[str, BillingPlan]] = ..., 
                billing_scope_id: Optional[str] = ..., 
                commitment: Optional[Commitment] = ..., 
                display_name: Optional[str] = ..., 
                term: Optional[Union[str, SavingsPlanTerm]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.SavingsPlanTerm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P1_Y = "P1Y"
        P3_Y = "P3Y"


    class azure.mgmt.reservations.models.SavingsPlanToPurchaseCalculateExchange(_Model):
        billing_currency_total: Optional[Price]
        properties: Optional[SavingsPlanPurchaseRequest]

        @overload
        def __init__(
                self, 
                *, 
                billing_currency_total: Optional[Price] = ..., 
                properties: Optional[SavingsPlanPurchaseRequest] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.SavingsPlanToPurchaseExchange(_Model):
        billing_currency_total: Optional[Price]
        properties: Optional[SavingsPlanPurchaseRequest]
        savings_plan_id: Optional[str]
        savings_plan_order_id: Optional[str]
        status: Optional[Union[str, OperationStatus]]

        @overload
        def __init__(
                self, 
                *, 
                billing_currency_total: Optional[Price] = ..., 
                properties: Optional[SavingsPlanPurchaseRequest] = ..., 
                savings_plan_id: Optional[str] = ..., 
                savings_plan_order_id: Optional[str] = ..., 
                status: Optional[Union[str, OperationStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ScopeProperties(_Model):
        scope: Optional[str]
        valid: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                scope: Optional[str] = ..., 
                valid: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.ServiceError(_Model):
        code: Optional[str]
        details: Optional[list[ServiceErrorDetail]]
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


    class azure.mgmt.reservations.models.ServiceErrorDetail(_Model):
        code: Optional[str]
        message: Optional[str]


    class azure.mgmt.reservations.models.SkuCapability(_Model):
        name: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.SkuName(_Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.SkuProperty(_Model):
        name: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.SkuRestriction(_Model):
        reason_code: Optional[str]
        type: Optional[str]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                reason_code: Optional[str] = ..., 
                type: Optional[str] = ..., 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.SplitProperties(_Model):
        quantities: Optional[list[int]]
        reservation_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                quantities: Optional[list[int]] = ..., 
                reservation_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.SplitRequest(_Model):
        properties: Optional[SplitProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SplitProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.reservations.models.SubRequest(_Model):
        limit: Optional[int]
        message: Optional[str]
        name: Optional[ResourceName]
        provisioning_state: Optional[Union[str, QuotaRequestState]]
        resource_type: Optional[str]
        sub_request_id: Optional[str]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[ResourceName] = ..., 
                provisioning_state: Optional[Union[str, QuotaRequestState]] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.SubscriptionScopeProperties(_Model):
        scopes: Optional[list[ScopeProperties]]

        @overload
        def __init__(
                self, 
                *, 
                scopes: Optional[list[ScopeProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.reservations.models.SystemData(_Model):
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


namespace azure.mgmt.reservations.operations

    class azure.mgmt.reservations.operations.CalculateExchangeOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                body: CalculateExchangeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CalculateExchangeOperationResultResponse]: ...

        @overload
        def begin_post(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CalculateExchangeOperationResultResponse]: ...


    class azure.mgmt.reservations.operations.CalculateRefundOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                body: CalculateRefundRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculateRefundResponse: ...

        @overload
        def post(
                self, 
                reservation_order_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculateRefundResponse: ...


    class azure.mgmt.reservations.operations.ExchangeOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                body: ExchangeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExchangeOperationResultResponse]: ...

        @overload
        def begin_post(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExchangeOperationResultResponse]: ...


    class azure.mgmt.reservations.operations.OperationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[OperationResponse]: ...


    class azure.mgmt.reservations.operations.QuotaOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                create_quota_request: IO[bytes], 
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
                create_quota_request: IO[bytes], 
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
                **kwargs: Any
            ) -> CurrentQuotaLimitBase: ...

        @distributed_trace
        def list(
                self, 
                subscription_id: str, 
                provider_id: str, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[CurrentQuotaLimitBase]: ...


    class azure.mgmt.reservations.operations.QuotaRequestStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                subscription_id: str, 
                provider_id: str, 
                location: str, 
                id: str, 
                **kwargs: Any
            ) -> QuotaRequestDetails: ...

        @distributed_trace
        def list(
                self, 
                subscription_id: str, 
                provider_id: str, 
                location: str, 
                *, 
                filter: Optional[str] = ..., 
                skiptoken: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[QuotaRequestDetails]: ...


    class azure.mgmt.reservations.operations.ReservationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def archive(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
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
                body: IO[bytes], 
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
                body: MergeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[List[ReservationResponse]]: ...

        @overload
        def begin_merge(
                self, 
                reservation_order_id: str, 
                body: IO[bytes], 
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
                body: SplitRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[List[ReservationResponse]]: ...

        @overload
        def begin_split(
                self, 
                reservation_order_id: str, 
                body: IO[bytes], 
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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReservationResponse]: ...

        @distributed_trace
        def get(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> ReservationResponse: ...

        @distributed_trace
        def list(
                self, 
                reservation_order_id: str, 
                **kwargs: Any
            ) -> ItemPaged[ReservationResponse]: ...

        @distributed_trace
        def list_all(
                self, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                refresh_summary: Optional[str] = ..., 
                selected_state: Optional[str] = ..., 
                skiptoken: Optional[float] = ..., 
                take: Optional[float] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ReservationResponse]: ...

        @distributed_trace
        def list_revisions(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                **kwargs: Any
            ) -> ItemPaged[ReservationResponse]: ...

        @distributed_trace
        def unarchive(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.reservations.operations.ReservationOrderOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                body: PurchaseRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReservationOrderResponse]: ...

        @overload
        def begin_purchase(
                self, 
                reservation_order_id: str, 
                body: IO[bytes], 
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
                body: PurchaseRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculatePriceResponse: ...

        @overload
        def calculate(
                self, 
                body: IO[bytes], 
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
                body: ChangeDirectoryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ChangeDirectoryResponse: ...

        @overload
        def change_directory(
                self, 
                reservation_order_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ChangeDirectoryResponse: ...

        @distributed_trace
        def get(
                self, 
                reservation_order_id: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> ReservationOrderResponse: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ReservationOrderResponse]: ...


    class azure.mgmt.reservations.operations.ReturnOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                body: RefundRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReservationOrderResponse]: ...

        @overload
        def begin_post(
                self, 
                reservation_order_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ReservationOrderResponse]: ...


namespace azure.mgmt.reservations.types

    class azure.mgmt.reservations.types.AppliedScopeProperties(TypedDict, total=False):
        key "displayName": str
        key "managementGroupId": str
        key "resourceGroupId": str
        key "subscriptionId": str
        key "tenantId": str
        display_name: str
        management_group_id: str
        resource_group_id: str
        subscription_id: str
        tenant_id: str


    class azure.mgmt.reservations.types.AvailableScopeRequest(TypedDict, total=False):
        key "properties": ForwardRef('AvailableScopeRequestProperties', module='types')
        properties: AvailableScopeRequestProperties


    class azure.mgmt.reservations.types.AvailableScopeRequestProperties(TypedDict, total=False):
        scopes: list[str]


    class azure.mgmt.reservations.types.CalculateExchangeRequest(TypedDict, total=False):
        key "properties": ForwardRef('CalculateExchangeRequestProperties', module='types')
        properties: CalculateExchangeRequestProperties


    class azure.mgmt.reservations.types.CalculateExchangeRequestProperties(TypedDict, total=False):
        reservationsToExchange: list[ReservationToReturn]
        reservationsToPurchase: list[PurchaseRequest]
        reservations_to_exchange: list[ReservationToReturn]
        reservations_to_purchase: list[PurchaseRequest]
        savingsPlansToPurchase: list[SavingsPlanPurchaseRequest]
        savings_plans_to_purchase: list[SavingsPlanPurchaseRequest]


    class azure.mgmt.reservations.types.CalculateRefundRequest(TypedDict, total=False):
        key "id": str
        key "properties": ForwardRef('CalculateRefundRequestProperties', module='types')
        id: str
        properties: CalculateRefundRequestProperties


    class azure.mgmt.reservations.types.CalculateRefundRequestProperties(TypedDict, total=False):
        key "reservationToReturn": ForwardRef('ReservationToReturn', module='types')
        key "scope": str
        reservation_to_return: ReservationToReturn
        scope: str


    class azure.mgmt.reservations.types.ChangeDirectoryRequest(TypedDict, total=False):
        key "destinationTenantId": str
        destination_tenant_id: str


    class azure.mgmt.reservations.types.Commitment(Price):
        key "amount": float
        key "currencyCode": str
        key "grain": Union[str, CommitmentGrain]
        amount: float
        currency_code: str
        grain: Union[str, CommitmentGrain]


    class azure.mgmt.reservations.types.CurrentQuotaLimitBase(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('QuotaProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: QuotaProperties
        system_data: SystemData
        type: str


    class azure.mgmt.reservations.types.ExchangeRequest(TypedDict, total=False):
        key "properties": ForwardRef('ExchangeRequestProperties', module='types')
        properties: ExchangeRequestProperties


    class azure.mgmt.reservations.types.ExchangeRequestProperties(TypedDict, total=False):
        key "sessionId": str
        session_id: str


    class azure.mgmt.reservations.types.MergeProperties(TypedDict, total=False):
        sources: list[str]


    class azure.mgmt.reservations.types.MergeRequest(TypedDict, total=False):
        key "properties": ForwardRef('MergeProperties', module='types')
        properties: MergeProperties


    class azure.mgmt.reservations.types.Patch(TypedDict, total=False):
        key "properties": ForwardRef('PatchProperties', module='types')
        properties: PatchProperties


    class azure.mgmt.reservations.types.PatchProperties(TypedDict, total=False):
        key "appliedScopeProperties": ForwardRef('AppliedScopeProperties', module='types')
        key "appliedScopeType": Union[str, AppliedScopeType]
        key "instanceFlexibility": Union[str, InstanceFlexibility]
        key "name": str
        key "renew": bool
        key "renewProperties": ForwardRef('PatchPropertiesRenewProperties', module='types')
        key "reviewDateTime": str
        appliedScopes: list[str]
        applied_scope_properties: AppliedScopeProperties
        applied_scope_type: Union[str, AppliedScopeType]
        applied_scopes: list[str]
        instance_flexibility: Union[str, InstanceFlexibility]
        name: str
        renew: bool
        renew_properties: PatchPropertiesRenewProperties
        review_date_time: str


    class azure.mgmt.reservations.types.PatchPropertiesRenewProperties(TypedDict, total=False):
        key "purchaseProperties": ForwardRef('PurchaseRequest', module='types')
        purchase_properties: PurchaseRequest


    class azure.mgmt.reservations.types.Price(TypedDict, total=False):
        key "amount": float
        key "currencyCode": str
        amount: float
        currency_code: str


    class azure.mgmt.reservations.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.reservations.types.PurchaseRequest(TypedDict, total=False):
        key "location": str
        key "properties": ForwardRef('PurchaseRequestProperties', module='types')
        key "sku": ForwardRef('SkuName', module='types')
        location: str
        properties: PurchaseRequestProperties
        sku: SkuName


    class azure.mgmt.reservations.types.PurchaseRequestProperties(TypedDict, total=False):
        key "appliedScopeProperties": ForwardRef('AppliedScopeProperties', module='types')
        key "appliedScopeType": Union[str, AppliedScopeType]
        key "billingPlan": Union[str, ReservationBillingPlan]
        key "billingScopeId": str
        key "displayName": str
        key "quantity": int
        key "renew": bool
        key "reservedResourceProperties": ForwardRef('PurchaseRequestPropertiesReservedResourceProperties', module='types')
        key "reservedResourceType": Union[str, ReservedResourceType]
        key "reviewDateTime": str
        key "term": Union[str, ReservationTerm]
        appliedScopes: list[str]
        applied_scope_properties: AppliedScopeProperties
        applied_scope_type: Union[str, AppliedScopeType]
        applied_scopes: list[str]
        billing_plan: Union[str, ReservationBillingPlan]
        billing_scope_id: str
        display_name: str
        quantity: int
        renew: bool
        reserved_resource_properties: PurchaseRequestPropertiesReservedResourceProperties
        reserved_resource_type: Union[str, ReservedResourceType]
        review_date_time: str
        term: Union[str, ReservationTerm]


    class azure.mgmt.reservations.types.PurchaseRequestPropertiesReservedResourceProperties(TypedDict, total=False):
        key "instanceFlexibility": Union[str, InstanceFlexibility]
        instance_flexibility: Union[str, InstanceFlexibility]


    class azure.mgmt.reservations.types.QuotaProperties(TypedDict, total=False):
        key "currentValue": int
        key "limit": int
        key "name": ForwardRef('ResourceName', module='types')
        key "properties": Any
        key "quotaPeriod": str
        key "resourceType": Union[str, ResourceType]
        key "unit": str
        current_value: int
        limit: int
        name: ResourceName
        properties: Any
        quota_period: str
        resource_type: Union[str, ResourceType]
        unit: str


    class azure.mgmt.reservations.types.RefundRequest(TypedDict, total=False):
        key "properties": ForwardRef('RefundRequestProperties', module='types')
        properties: RefundRequestProperties


    class azure.mgmt.reservations.types.RefundRequestProperties(TypedDict, total=False):
        key "reservationToReturn": ForwardRef('ReservationToReturn', module='types')
        key "returnReason": str
        key "scope": str
        key "sessionId": str
        reservation_to_return: ReservationToReturn
        return_reason: str
        scope: str
        session_id: str


    class azure.mgmt.reservations.types.ReservationToReturn(TypedDict, total=False):
        key "quantity": int
        key "reservationId": str
        quantity: int
        reservation_id: str


    class azure.mgmt.reservations.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.reservations.types.ResourceName(TypedDict, total=False):
        key "localizedValue": str
        key "value": str
        localized_value: str
        value: str


    class azure.mgmt.reservations.types.SavingsPlanPurchaseRequest(TypedDict, total=False):
        key "properties": ForwardRef('SavingsPlanPurchaseRequestProperties', module='types')
        key "sku": ForwardRef('SkuName', module='types')
        properties: SavingsPlanPurchaseRequestProperties
        sku: SkuName


    class azure.mgmt.reservations.types.SavingsPlanPurchaseRequestProperties(TypedDict, total=False):
        key "appliedScopeProperties": ForwardRef('AppliedScopeProperties', module='types')
        key "appliedScopeType": Union[str, AppliedScopeType]
        key "billingPlan": Union[str, BillingPlan]
        key "billingScopeId": str
        key "commitment": ForwardRef('Commitment', module='types')
        key "displayName": str
        key "term": Union[str, SavingsPlanTerm]
        applied_scope_properties: AppliedScopeProperties
        applied_scope_type: Union[str, AppliedScopeType]
        billing_plan: Union[str, BillingPlan]
        billing_scope_id: str
        commitment: Commitment
        display_name: str
        term: Union[str, SavingsPlanTerm]


    class azure.mgmt.reservations.types.SkuName(TypedDict, total=False):
        key "name": str
        name: str


    class azure.mgmt.reservations.types.SplitProperties(TypedDict, total=False):
        key "reservationId": str
        quantities: list[int]
        reservation_id: str


    class azure.mgmt.reservations.types.SplitRequest(TypedDict, total=False):
        key "properties": ForwardRef('SplitProperties', module='types')
        properties: SplitProperties


    class azure.mgmt.reservations.types.SystemData(TypedDict, total=False):
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


```