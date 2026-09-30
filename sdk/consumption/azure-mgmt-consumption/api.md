```py
namespace azure.mgmt.consumption

    class azure.mgmt.consumption.ConsumptionManagementClient: implements ContextManager 
        aggregated_cost: AggregatedCostOperations
        balances: BalancesOperations
        budgets: BudgetsOperations
        charges: ChargesOperations
        credits: CreditsOperations
        events: EventsOperations
        lots: LotsOperations
        marketplaces: MarketplacesOperations
        operations: Operations
        price_sheet: PriceSheetOperations
        reservation_recommendation_details: ReservationRecommendationDetailsOperations
        reservation_recommendations: ReservationRecommendationsOperations
        reservation_transactions: ReservationTransactionsOperations
        reservations_details: ReservationsDetailsOperations
        reservations_summaries: ReservationsSummariesOperations
        tags: TagsOperations
        usage_details: UsageDetailsOperations

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


namespace azure.mgmt.consumption.aio

    class azure.mgmt.consumption.aio.ConsumptionManagementClient: implements AsyncContextManager 
        aggregated_cost: AggregatedCostOperations
        balances: BalancesOperations
        budgets: BudgetsOperations
        charges: ChargesOperations
        credits: CreditsOperations
        events: EventsOperations
        lots: LotsOperations
        marketplaces: MarketplacesOperations
        operations: Operations
        price_sheet: PriceSheetOperations
        reservation_recommendation_details: ReservationRecommendationDetailsOperations
        reservation_recommendations: ReservationRecommendationsOperations
        reservation_transactions: ReservationTransactionsOperations
        reservations_details: ReservationsDetailsOperations
        reservations_summaries: ReservationsSummariesOperations
        tags: TagsOperations
        usage_details: UsageDetailsOperations

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


namespace azure.mgmt.consumption.aio.operations

    class azure.mgmt.consumption.aio.operations.AggregatedCostOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_by_management_group(
                self, 
                management_group_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ManagementGroupAggregatedCostResult: ...

        @distributed_trace_async
        async def get_for_billing_period_by_management_group(
                self, 
                management_group_id: str, 
                billing_period_name: str, 
                **kwargs: Any
            ) -> ManagementGroupAggregatedCostResult: ...


    class azure.mgmt.consumption.aio.operations.BalancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_by_billing_account(
                self, 
                billing_account_id: str, 
                **kwargs: Any
            ) -> Balance: ...

        @distributed_trace_async
        async def get_for_billing_period_by_billing_account(
                self, 
                billing_account_id: str, 
                billing_period_name: str, 
                **kwargs: Any
            ) -> Balance: ...


    class azure.mgmt.consumption.aio.operations.BudgetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                budget_name: str, 
                parameters: Budget, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Budget: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                budget_name: str, 
                parameters: Budget, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Budget: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                budget_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Budget: ...

        @distributed_trace_async
        async def delete(
                self, 
                scope: str, 
                budget_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                budget_name: str, 
                **kwargs: Any
            ) -> Budget: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Budget]: ...


    class azure.mgmt.consumption.aio.operations.ChargesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                scope: str, 
                *, 
                apply: Optional[str] = ..., 
                end_date: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                start_date: Optional[str] = ..., 
                **kwargs: Any
            ) -> ChargesListResult: ...


    class azure.mgmt.consumption.aio.operations.CreditsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                **kwargs: Any
            ) -> Optional[CreditSummary]: ...


    class azure.mgmt.consumption.aio.operations.EventsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSummary]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                *, 
                end_date: str, 
                start_date: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EventSummary]: ...


    class azure.mgmt.consumption.aio.operations.LotsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[LotSummary]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[LotSummary]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_id: str, 
                customer_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[LotSummary]: ...


    class azure.mgmt.consumption.aio.operations.MarketplacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                skiptoken: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Marketplace]: ...


    class azure.mgmt.consumption.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.consumption.aio.operations.PriceSheetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_download_by_billing_account_period(
                self, 
                billing_account_id: str, 
                billing_period_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatus]: ...

        @distributed_trace_async
        async def get(
                self, 
                *, 
                expand: Optional[str] = ..., 
                skiptoken: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> PriceSheetResult: ...

        @distributed_trace_async
        async def get_by_billing_period(
                self, 
                billing_period_name: str, 
                *, 
                expand: Optional[str] = ..., 
                skiptoken: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> PriceSheetResult: ...


    class azure.mgmt.consumption.aio.operations.ReservationRecommendationDetailsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_scope: str, 
                *, 
                filter: Optional[str] = ..., 
                look_back_period: Union[str, LookBackPeriod], 
                product: str, 
                region: str, 
                scope: Union[str, Scope], 
                term: Union[str, Term], 
                **kwargs: Any
            ) -> Optional[ReservationRecommendationDetailsModel]: ...


    class azure.mgmt.consumption.aio.operations.ReservationRecommendationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ReservationRecommendation]: ...


    class azure.mgmt.consumption.aio.operations.ReservationTransactionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                billing_account_id: str, 
                *, 
                filter: Optional[str] = ..., 
                preview_markup_percentage: Optional[Decimal] = ..., 
                use_markup_if_partner: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ReservationTransaction]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ModernReservationTransaction]: ...


    class azure.mgmt.consumption.aio.operations.ReservationsDetailsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_scope: str, 
                *, 
                end_date: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                reservation_id: Optional[str] = ..., 
                reservation_order_id: Optional[str] = ..., 
                start_date: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ReservationDetail]: ...

        @distributed_trace
        def list_by_reservation_order(
                self, 
                reservation_order_id: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ReservationDetail]: ...

        @distributed_trace
        def list_by_reservation_order_and_reservation(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ReservationDetail]: ...


    class azure.mgmt.consumption.aio.operations.ReservationsSummariesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_scope: str, 
                *, 
                end_date: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                grain: Union[str, Datagrain], 
                reservation_id: Optional[str] = ..., 
                reservation_order_id: Optional[str] = ..., 
                start_date: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ReservationSummary]: ...

        @distributed_trace
        def list_by_reservation_order(
                self, 
                reservation_order_id: str, 
                *, 
                filter: Optional[str] = ..., 
                grain: Union[str, Datagrain], 
                **kwargs: Any
            ) -> AsyncItemPaged[ReservationSummary]: ...

        @distributed_trace
        def list_by_reservation_order_and_reservation(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                *, 
                filter: Optional[str] = ..., 
                grain: Union[str, Datagrain], 
                **kwargs: Any
            ) -> AsyncItemPaged[ReservationSummary]: ...


    class azure.mgmt.consumption.aio.operations.TagsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> Optional[TagsResult]: ...


    class azure.mgmt.consumption.aio.operations.UsageDetailsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                metric: Optional[Union[str, Metrictype]] = ..., 
                skiptoken: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[UsageDetail]: ...


namespace azure.mgmt.consumption.models

    class azure.mgmt.consumption.models.Amount(_Model):
        currency: Optional[str]
        value: Optional[Decimal]


    class azure.mgmt.consumption.models.AmountWithExchangeRate(Amount):
        currency: str
        exchange_rate: Optional[Decimal]
        exchange_rate_month: Optional[int]
        value: Decimal


    class azure.mgmt.consumption.models.Balance(Resource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[BalanceProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BalanceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.consumption.models.BalanceProperties(_Model):
        adjustment_details: Optional[list[BalancePropertiesAdjustmentDetailsItem]]
        adjustments: Optional[Decimal]
        azure_marketplace_service_charges: Optional[Decimal]
        beginning_balance: Optional[Decimal]
        billing_frequency: Optional[Union[str, BillingFrequency]]
        charges_billed_separately: Optional[Decimal]
        currency: Optional[str]
        ending_balance: Optional[Decimal]
        new_purchases: Optional[Decimal]
        new_purchases_details: Optional[list[BalancePropertiesNewPurchasesDetailsItem]]
        overage_refund: Optional[Decimal]
        price_hidden: Optional[bool]
        service_overage: Optional[Decimal]
        total_overage: Optional[Decimal]
        total_usage: Optional[Decimal]
        utilized: Optional[Decimal]

        @overload
        def __init__(
                self, 
                *, 
                billing_frequency: Optional[Union[str, BillingFrequency]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.BalancePropertiesAdjustmentDetailsItem(_Model):
        name: Optional[str]
        value: Optional[Decimal]


    class azure.mgmt.consumption.models.BalancePropertiesNewPurchasesDetailsItem(_Model):
        name: Optional[str]
        value: Optional[Decimal]


    class azure.mgmt.consumption.models.BillingFrequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONTH = "Month"
        QUARTER = "Quarter"
        YEAR = "Year"


    class azure.mgmt.consumption.models.Budget(ExtensionResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[BudgetProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                properties: Optional[BudgetProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.consumption.models.BudgetComparisonExpression(_Model):
        name: str
        operator: Union[str, BudgetOperatorType]
        values_property: list[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                operator: Union[str, BudgetOperatorType], 
                values_property: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.BudgetFilter(_Model):
        and_property: Optional[list[BudgetFilterProperties]]
        dimensions: Optional[BudgetComparisonExpression]
        tags: Optional[BudgetComparisonExpression]

        @overload
        def __init__(
                self, 
                *, 
                and_property: Optional[list[BudgetFilterProperties]] = ..., 
                dimensions: Optional[BudgetComparisonExpression] = ..., 
                tags: Optional[BudgetComparisonExpression] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.BudgetFilterProperties(_Model):
        dimensions: Optional[BudgetComparisonExpression]
        tags: Optional[BudgetComparisonExpression]

        @overload
        def __init__(
                self, 
                *, 
                dimensions: Optional[BudgetComparisonExpression] = ..., 
                tags: Optional[BudgetComparisonExpression] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.BudgetOperatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IN = "In"


    class azure.mgmt.consumption.models.BudgetProperties(_Model):
        amount: Decimal
        category: Union[str, CategoryType]
        current_spend: Optional[CurrentSpend]
        filter: Optional[BudgetFilter]
        forecast_spend: Optional[ForecastSpend]
        notifications: Optional[dict[str, Notification]]
        time_grain: Union[str, TimeGrainType]
        time_period: BudgetTimePeriod

        @overload
        def __init__(
                self, 
                *, 
                amount: Decimal, 
                category: Union[str, CategoryType], 
                filter: Optional[BudgetFilter] = ..., 
                notifications: Optional[dict[str, Notification]] = ..., 
                time_grain: Union[str, TimeGrainType], 
                time_period: BudgetTimePeriod
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.BudgetTimePeriod(_Model):
        end_date: Optional[datetime]
        start_date: datetime

        @overload
        def __init__(
                self, 
                *, 
                end_date: Optional[datetime] = ..., 
                start_date: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.CategoryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COST = "Cost"


    class azure.mgmt.consumption.models.ChargeSummary(ProxyResource):
        etag: Optional[str]
        id: str
        kind: str
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.ChargeSummaryKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LEGACY = "legacy"
        MODERN = "modern"


    class azure.mgmt.consumption.models.ChargesListResult(_Model):
        value: Optional[list[ChargeSummary]]


    class azure.mgmt.consumption.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.consumption.models.CreditBalanceSummary(_Model):
        current_balance: Optional[Amount]
        estimated_balance: Optional[Amount]
        estimated_balance_in_billing_currency: Optional[AmountWithExchangeRate]


    class azure.mgmt.consumption.models.CreditSummary(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[CreditSummaryProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[CreditSummaryProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.consumption.models.CreditSummaryProperties(_Model):
        balance_summary: Optional[CreditBalanceSummary]
        billing_currency: Optional[str]
        credit_currency: Optional[str]
        e_tag: Optional[str]
        expired_credit: Optional[Amount]
        is_estimated_balance: Optional[bool]
        pending_credit_adjustments: Optional[Amount]
        pending_eligible_charges: Optional[Amount]
        reseller: Optional[Reseller]


    class azure.mgmt.consumption.models.CultureCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CS_CZ = "cs-cz"
        DA_DK = "da-dk"
        DE_DE = "de-de"
        EN_GB = "en-gb"
        EN_US = "en-us"
        ES_ES = "es-es"
        FR_FR = "fr-fr"
        HU_HU = "hu-hu"
        IT_IT = "it-it"
        JA_JP = "ja-jp"
        KO_KR = "ko-kr"
        NB_NO = "nb-no"
        NL_NL = "nl-nl"
        PL_PL = "pl-pl"
        PT_BR = "pt-br"
        PT_PT = "pt-pt"
        RU_RU = "ru-ru"
        SV_SE = "sv-se"
        TR_TR = "tr-tr"
        ZH_CN = "zh-cn"
        ZH_TW = "zh-tw"


    class azure.mgmt.consumption.models.CurrentSpend(_Model):
        amount: Optional[Decimal]
        unit: Optional[str]


    class azure.mgmt.consumption.models.Datagrain(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY_GRAIN = "daily"
        MONTHLY_GRAIN = "monthly"


    class azure.mgmt.consumption.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.consumption.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.consumption.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.EventProperties(_Model):
        adjustments: Optional[Amount]
        adjustments_in_billing_currency: Optional[AmountWithExchangeRate]
        billing_account_display_name: Optional[str]
        billing_account_id: Optional[str]
        billing_currency: Optional[str]
        billing_profile_display_name: Optional[str]
        billing_profile_id: Optional[str]
        canceled_credit: Optional[Amount]
        charges: Optional[Amount]
        charges_in_billing_currency: Optional[AmountWithExchangeRate]
        closed_balance: Optional[Amount]
        closed_balance_in_billing_currency: Optional[AmountWithExchangeRate]
        credit_currency: Optional[str]
        credit_expired: Optional[Amount]
        credit_expired_in_billing_currency: Optional[AmountWithExchangeRate]
        description: Optional[str]
        e_tag: Optional[str]
        event_type: Optional[Union[str, EventType]]
        invoice_number: Optional[str]
        is_estimated_balance: Optional[bool]
        lot_id: Optional[str]
        lot_source: Optional[str]
        new_credit: Optional[Amount]
        new_credit_in_billing_currency: Optional[AmountWithExchangeRate]
        reseller: Optional[Reseller]
        transaction_date: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                event_type: Optional[Union[str, EventType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.EventSummary(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[EventProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EventProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.consumption.models.EventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREDIT_EXPIRED = "CreditExpired"
        NEW_CREDIT = "NewCredit"
        PENDING_ADJUSTMENTS = "PendingAdjustments"
        PENDING_CHARGES = "PendingCharges"
        PENDING_EXPIRED_CREDIT = "PendingExpiredCredit"
        PENDING_NEW_CREDIT = "PendingNewCredit"
        SETTLED_CHARGES = "SettledCharges"
        UN_KNOWN = "UnKnown"


    class azure.mgmt.consumption.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.consumption.models.ForecastSpend(_Model):
        amount: Optional[Decimal]
        unit: Optional[str]


    class azure.mgmt.consumption.models.HighCasedErrorDetails(_Model):
        code: Optional[str]
        message: Optional[str]


    class azure.mgmt.consumption.models.HighCasedErrorResponse(_Model):
        error: Optional[HighCasedErrorDetails]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[HighCasedErrorDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.LegacyChargeSummary(ChargeSummary, discriminator='legacy'):
        etag: str
        id: str
        kind: Literal[ChargeSummaryKind.LEGACY]
        name: str
        properties: LegacyChargeSummaryProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: LegacyChargeSummaryProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.consumption.models.LegacyChargeSummaryProperties(_Model):
        azure_charges: Optional[Decimal]
        azure_marketplace_charges: Optional[Decimal]
        billing_period_id: Optional[str]
        charges_billed_separately: Optional[Decimal]
        currency: Optional[str]
        usage_end: Optional[str]
        usage_start: Optional[str]


    class azure.mgmt.consumption.models.LegacyReservationRecommendation(ReservationRecommendation, discriminator='legacy'):
        etag: str
        id: str
        kind: Literal[ReservationRecommendationKind.LEGACY]
        location: str
        name: str
        properties: LegacyReservationRecommendationProperties
        sku: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: LegacyReservationRecommendationProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.LegacyReservationRecommendationProperties(_Model):
        cost_with_no_reserved_instances: Optional[Decimal]
        first_usage_date: Optional[datetime]
        instance_flexibility_group: Optional[str]
        instance_flexibility_ratio: Optional[float]
        last_usage_date: Optional[datetime]
        look_back_period: Optional[str]
        meter_id: Optional[str]
        net_savings: Optional[Decimal]
        normalized_size: Optional[str]
        recommended_quantity: Optional[Decimal]
        recommended_quantity_normalized: Optional[float]
        resource_type: Optional[str]
        scope: str
        sku_properties: Optional[list[SkuProperty]]
        term: Optional[str]
        total_cost_with_reserved_instances: Optional[Decimal]
        total_hours: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                scope: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.LegacyReservationTransactionProperties(_Model):
        account_name: Optional[str]
        account_owner_email: Optional[str]
        amount: Optional[Decimal]
        arm_sku_name: Optional[str]
        billing_frequency: Optional[str]
        billing_month: Optional[int]
        cost_center: Optional[str]
        currency: Optional[str]
        current_enrollment: Optional[str]
        department_name: Optional[str]
        description: Optional[str]
        event_date: Optional[datetime]
        event_type: Optional[str]
        monetary_commitment: Optional[Decimal]
        overage: Optional[Decimal]
        purchasing_enrollment: Optional[str]
        purchasing_subscription_guid: Optional[str]
        purchasing_subscription_name: Optional[str]
        quantity: Optional[Decimal]
        region: Optional[str]
        reservation_order_id: Optional[str]
        reservation_order_name: Optional[str]
        term: Optional[str]


    class azure.mgmt.consumption.models.LegacySharedScopeReservationRecommendationProperties(LegacyReservationRecommendationProperties, discriminator='Shared'):
        cost_with_no_reserved_instances: Decimal
        first_usage_date: datetime
        instance_flexibility_group: str
        instance_flexibility_ratio: float
        last_usage_date: datetime
        look_back_period: str
        meter_id: str
        net_savings: Decimal
        normalized_size: str
        recommended_quantity: Decimal
        recommended_quantity_normalized: float
        resource_type: str
        scope: Literal["Shared"]
        sku_properties: list[SkuProperty]
        term: str
        total_cost_with_reserved_instances: Decimal
        total_hours: int

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.LegacySingleScopeReservationRecommendationProperties(LegacyReservationRecommendationProperties, discriminator='Single'):
        cost_with_no_reserved_instances: Decimal
        first_usage_date: datetime
        instance_flexibility_group: str
        instance_flexibility_ratio: float
        last_usage_date: datetime
        look_back_period: str
        meter_id: str
        net_savings: Decimal
        normalized_size: str
        recommended_quantity: Decimal
        recommended_quantity_normalized: float
        resource_type: str
        scope: Literal["Single"]
        sku_properties: list[SkuProperty]
        subscription_id: Optional[str]
        term: str
        total_cost_with_reserved_instances: Decimal
        total_hours: int

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.LegacyUsageDetail(UsageDetail, discriminator='legacy'):
        etag: str
        id: str
        kind: Literal[UsageDetailsKind.LEGACY]
        name: str
        properties: LegacyUsageDetailProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: LegacyUsageDetailProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.consumption.models.LegacyUsageDetailProperties(_Model):
        account_name: Optional[str]
        account_owner_id: Optional[str]
        additional_info: Optional[str]
        benefit_id: Optional[str]
        benefit_name: Optional[str]
        billing_account_id: Optional[str]
        billing_account_name: Optional[str]
        billing_currency: Optional[str]
        billing_period_end_date: Optional[datetime]
        billing_period_start_date: Optional[datetime]
        billing_profile_id: Optional[str]
        billing_profile_name: Optional[str]
        charge_type: Optional[str]
        consumed_service: Optional[str]
        cost: Optional[Decimal]
        cost_center: Optional[str]
        date: Optional[datetime]
        effective_price: Optional[Decimal]
        frequency: Optional[str]
        invoice_section: Optional[str]
        is_azure_credit_eligible: Optional[bool]
        meter_details: Optional[MeterDetailsResponse]
        meter_id: Optional[str]
        offer_id: Optional[str]
        part_number: Optional[str]
        pay_g_price: Optional[Decimal]
        plan_name: Optional[str]
        pricing_model: Optional[Union[str, PricingModelType]]
        product: Optional[str]
        product_order_id: Optional[str]
        product_order_name: Optional[str]
        publisher_name: Optional[str]
        publisher_type: Optional[str]
        quantity: Optional[Decimal]
        reservation_id: Optional[str]
        reservation_name: Optional[str]
        resource_group: Optional[str]
        resource_id: Optional[str]
        resource_location: Optional[str]
        resource_name: Optional[str]
        service_info1: Optional[str]
        service_info2: Optional[str]
        subscription_id: Optional[str]
        subscription_name: Optional[str]
        term: Optional[str]
        unit_price: Optional[Decimal]


    class azure.mgmt.consumption.models.LookBackPeriod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LAST07_DAYS = "Last7Days"
        LAST30_DAYS = "Last30Days"
        LAST60_DAYS = "Last60Days"


    class azure.mgmt.consumption.models.LotProperties(_Model):
        billing_currency: Optional[str]
        closed_balance: Optional[Amount]
        closed_balance_in_billing_currency: Optional[AmountWithExchangeRate]
        credit_currency: Optional[str]
        e_tag: Optional[str]
        expiration_date: Optional[datetime]
        is_estimated_balance: Optional[bool]
        organization_type: Optional[Union[str, OrganizationType]]
        original_amount: Optional[Amount]
        original_amount_in_billing_currency: Optional[AmountWithExchangeRate]
        po_number: Optional[str]
        purchased_date: Optional[datetime]
        reseller: Optional[Reseller]
        source: Optional[Union[str, LotSource]]
        start_date: Optional[datetime]
        status: Optional[Union[str, Status]]
        used_amount: Optional[Amount]


    class azure.mgmt.consumption.models.LotSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONSUMPTION_COMMITMENT = "ConsumptionCommitment"
        PROMOTIONAL_CREDIT = "PromotionalCredit"
        PURCHASED_CREDIT = "PurchasedCredit"


    class azure.mgmt.consumption.models.LotSummary(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[LotProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                properties: Optional[LotProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.consumption.models.ManagementGroupAggregatedCostProperties(_Model):
        azure_charges: Optional[Decimal]
        billing_period_id: Optional[str]
        charges_billed_separately: Optional[Decimal]
        children: Optional[list[ManagementGroupAggregatedCostResult]]
        currency: Optional[str]
        excluded_subscriptions: Optional[list[str]]
        included_subscriptions: Optional[list[str]]
        marketplace_charges: Optional[Decimal]
        usage_end: Optional[datetime]
        usage_start: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                children: Optional[list[ManagementGroupAggregatedCostResult]] = ..., 
                excluded_subscriptions: Optional[list[str]] = ..., 
                included_subscriptions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.ManagementGroupAggregatedCostResult(Resource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[ManagementGroupAggregatedCostProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ManagementGroupAggregatedCostProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.consumption.models.Marketplace(Resource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[MarketplaceProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MarketplaceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.consumption.models.MarketplaceProperties(_Model):
        account_name: Optional[str]
        additional_info: Optional[str]
        additional_properties: Optional[str]
        billing_period_id: Optional[str]
        consumed_quantity: Optional[Decimal]
        consumed_service: Optional[str]
        cost_center: Optional[str]
        currency: Optional[str]
        department_name: Optional[str]
        instance_id: Optional[str]
        instance_name: Optional[str]
        is_estimated: Optional[bool]
        is_recurring_charge: Optional[bool]
        meter_id: Optional[str]
        offer_name: Optional[str]
        order_number: Optional[str]
        plan_name: Optional[str]
        pretax_cost: Optional[Decimal]
        publisher_name: Optional[str]
        resource_group: Optional[str]
        resource_rate: Optional[Decimal]
        subscription_guid: Optional[str]
        subscription_name: Optional[str]
        unit_of_measure: Optional[str]
        usage_end: Optional[datetime]
        usage_start: Optional[datetime]


    class azure.mgmt.consumption.models.MeterDetails(_Model):
        meter_category: Optional[str]
        meter_location: Optional[str]
        meter_name: Optional[str]
        meter_sub_category: Optional[str]
        pretax_standard_rate: Optional[Decimal]
        service_name: Optional[str]
        service_tier: Optional[str]
        total_included_quantity: Optional[Decimal]
        unit: Optional[str]


    class azure.mgmt.consumption.models.MeterDetailsResponse(_Model):
        meter_category: Optional[str]
        meter_name: Optional[str]
        meter_sub_category: Optional[str]
        service_family: Optional[str]
        unit_of_measure: Optional[str]


    class azure.mgmt.consumption.models.Metrictype(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTUAL_COST_METRIC_TYPE = "actualcost"
        AMORTIZED_COST_METRIC_TYPE = "amortizedcost"
        USAGE_METRIC_TYPE = "usage"


    class azure.mgmt.consumption.models.ModernChargeSummary(ChargeSummary, discriminator='modern'):
        etag: str
        id: str
        kind: Literal[ChargeSummaryKind.MODERN]
        name: str
        properties: ModernChargeSummaryProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: ModernChargeSummaryProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.consumption.models.ModernChargeSummaryProperties(_Model):
        azure_charges: Optional[Amount]
        billing_account_id: Optional[str]
        billing_period_id: Optional[str]
        billing_profile_id: Optional[str]
        charges_billed_separately: Optional[Amount]
        customer_id: Optional[str]
        invoice_section_id: Optional[str]
        is_invoiced: Optional[bool]
        marketplace_charges: Optional[Amount]
        subscription_id: Optional[str]
        usage_end: Optional[str]
        usage_start: Optional[str]


    class azure.mgmt.consumption.models.ModernReservationRecommendation(ReservationRecommendation, discriminator='modern'):
        etag: str
        id: str
        kind: Literal[ReservationRecommendationKind.MODERN]
        location: str
        name: str
        properties: ModernReservationRecommendationProperties
        sku: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: ModernReservationRecommendationProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.ModernReservationRecommendationProperties(_Model):
        cost_with_no_reserved_instances: Optional[Amount]
        first_usage_date: Optional[datetime]
        instance_flexibility_group: Optional[str]
        instance_flexibility_ratio: Optional[float]
        last_usage_date: Optional[datetime]
        location: Optional[str]
        look_back_period: Optional[int]
        meter_id: Optional[str]
        net_savings: Optional[Amount]
        normalized_size: Optional[str]
        recommended_quantity: Optional[Decimal]
        recommended_quantity_normalized: Optional[float]
        resource_type: Optional[str]
        scope: str
        sku_name: Optional[str]
        sku_properties: Optional[list[SkuProperty]]
        term: Optional[str]
        total_cost_with_reserved_instances: Optional[Amount]
        total_hours: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                scope: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.ModernReservationTransaction(Resource):
        id: str
        name: str
        properties: ModernReservationTransactionProperties
        system_data: SystemData
        tags: Optional[list[str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: ModernReservationTransactionProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.consumption.models.ModernReservationTransactionProperties(_Model):
        amount: Optional[Decimal]
        arm_sku_name: Optional[str]
        billing_frequency: Optional[str]
        billing_profile_id: Optional[str]
        billing_profile_name: Optional[str]
        currency: Optional[str]
        description: Optional[str]
        event_date: Optional[datetime]
        event_type: Optional[str]
        invoice: Optional[str]
        invoice_id: Optional[str]
        invoice_section_id: Optional[str]
        invoice_section_name: Optional[str]
        purchasing_subscription_guid: Optional[str]
        purchasing_subscription_name: Optional[str]
        quantity: Optional[Decimal]
        region: Optional[str]
        reservation_order_id: Optional[str]
        reservation_order_name: Optional[str]
        term: Optional[str]


    class azure.mgmt.consumption.models.ModernSharedScopeReservationRecommendationProperties(ModernReservationRecommendationProperties, discriminator='Shared'):
        cost_with_no_reserved_instances: Amount
        first_usage_date: datetime
        instance_flexibility_group: str
        instance_flexibility_ratio: float
        last_usage_date: datetime
        location: str
        look_back_period: int
        meter_id: str
        net_savings: Amount
        normalized_size: str
        recommended_quantity: Decimal
        recommended_quantity_normalized: float
        resource_type: str
        scope: Literal["Shared"]
        sku_name: str
        sku_properties: list[SkuProperty]
        term: str
        total_cost_with_reserved_instances: Amount
        total_hours: int

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.ModernSingleScopeReservationRecommendationProperties(ModernReservationRecommendationProperties, discriminator='Single'):
        cost_with_no_reserved_instances: Amount
        first_usage_date: datetime
        instance_flexibility_group: str
        instance_flexibility_ratio: float
        last_usage_date: datetime
        location: str
        look_back_period: int
        meter_id: str
        net_savings: Amount
        normalized_size: str
        recommended_quantity: Decimal
        recommended_quantity_normalized: float
        resource_type: str
        scope: Literal["Single"]
        sku_name: str
        sku_properties: list[SkuProperty]
        subscription_id: Optional[str]
        term: str
        total_cost_with_reserved_instances: Amount
        total_hours: int

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.ModernUsageDetail(UsageDetail, discriminator='modern'):
        etag: str
        id: str
        kind: Literal[UsageDetailsKind.MODERN]
        name: str
        properties: ModernUsageDetailProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: ModernUsageDetailProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.consumption.models.ModernUsageDetailProperties(_Model):
        additional_info: Optional[str]
        benefit_id: Optional[str]
        benefit_name: Optional[str]
        billing_account_id: Optional[str]
        billing_account_name: Optional[str]
        billing_currency_code: Optional[str]
        billing_period_end_date: Optional[datetime]
        billing_period_start_date: Optional[datetime]
        billing_profile_id: Optional[str]
        billing_profile_name: Optional[str]
        charge_type: Optional[str]
        consumed_service: Optional[str]
        cost_allocation_rule_name: Optional[str]
        cost_center: Optional[str]
        cost_in_billing_currency: Optional[Decimal]
        cost_in_pricing_currency: Optional[Decimal]
        cost_in_usd: Optional[Decimal]
        customer_name: Optional[str]
        customer_tenant_id: Optional[str]
        date: Optional[datetime]
        effective_price: Optional[Decimal]
        exchange_rate: Optional[str]
        exchange_rate_date: Optional[datetime]
        exchange_rate_pricing_to_billing: Optional[Decimal]
        frequency: Optional[str]
        instance_name: Optional[str]
        invoice_id: Optional[str]
        invoice_section_id: Optional[str]
        invoice_section_name: Optional[str]
        is_azure_credit_eligible: Optional[bool]
        market_price: Optional[Decimal]
        meter_category: Optional[str]
        meter_id: Optional[str]
        meter_name: Optional[str]
        meter_region: Optional[str]
        meter_sub_category: Optional[str]
        partner_earned_credit_applied: Optional[str]
        partner_earned_credit_rate: Optional[Decimal]
        partner_name: Optional[str]
        partner_tenant_id: Optional[str]
        pay_g_price: Optional[Decimal]
        payg_cost_in_billing_currency: Optional[Decimal]
        payg_cost_in_usd: Optional[Decimal]
        previous_invoice_id: Optional[str]
        pricing_currency_code: Optional[str]
        pricing_model: Optional[Union[str, PricingModelType]]
        product: Optional[str]
        product_identifier: Optional[str]
        product_order_id: Optional[str]
        product_order_name: Optional[str]
        provider: Optional[str]
        publisher_id: Optional[str]
        publisher_name: Optional[str]
        publisher_type: Optional[str]
        quantity: Optional[Decimal]
        reseller_mpn_id: Optional[str]
        reseller_name: Optional[str]
        reservation_id: Optional[str]
        reservation_name: Optional[str]
        resource_group: Optional[str]
        resource_location: Optional[str]
        resource_location_normalized: Optional[str]
        service_family: Optional[str]
        service_info1: Optional[str]
        service_info2: Optional[str]
        service_period_end_date: Optional[datetime]
        service_period_start_date: Optional[datetime]
        subscription_guid: Optional[str]
        subscription_name: Optional[str]
        term: Optional[str]
        unit_of_measure: Optional[str]
        unit_price: Optional[Decimal]


    class azure.mgmt.consumption.models.Notification(_Model):
        contact_emails: list[str]
        contact_groups: Optional[list[str]]
        contact_roles: Optional[list[str]]
        enabled: bool
        locale: Optional[Union[str, CultureCode]]
        operator: Union[str, OperatorType]
        threshold: Decimal
        threshold_type: Optional[Union[str, ThresholdType]]

        @overload
        def __init__(
                self, 
                *, 
                contact_emails: list[str], 
                contact_groups: Optional[list[str]] = ..., 
                contact_roles: Optional[list[str]] = ..., 
                enabled: bool, 
                locale: Optional[Union[str, CultureCode]] = ..., 
                operator: Union[str, OperatorType], 
                threshold: Decimal, 
                threshold_type: Optional[Union[str, ThresholdType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.Operation(_Model):
        display: Optional[OperationDisplay]
        id: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.consumption.models.OperationStatus(_Model):
        properties: Optional[PricesheetDownloadProperties]
        status: Optional[Union[str, OperationStatusType]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PricesheetDownloadProperties] = ..., 
                status: Optional[Union[str, OperationStatusType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.consumption.models.OperationStatusType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        RUNNING = "Running"


    class azure.mgmt.consumption.models.OperatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUAL_TO = "EqualTo"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL_TO = "GreaterThanOrEqualTo"


    class azure.mgmt.consumption.models.OrganizationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTRIBUTOR_ORGANIZATION_TYPE = "Contributor"
        PRIMARY_ORGANIZATION_TYPE = "Primary"


    class azure.mgmt.consumption.models.PriceSheetModel(_Model):
        download: Optional[MeterDetails]
        next_link: Optional[str]
        pricesheets: Optional[list[PriceSheetProperties]]


    class azure.mgmt.consumption.models.PriceSheetProperties(_Model):
        billing_period_id: Optional[str]
        currency_code: Optional[str]
        included_quantity: Optional[Decimal]
        meter_details: Optional[MeterDetails]
        meter_id: Optional[str]
        offer_id: Optional[str]
        part_number: Optional[str]
        savings_plan: Optional[SavingsPlan]
        unit_of_measure: Optional[str]
        unit_price: Optional[Decimal]


    class azure.mgmt.consumption.models.PriceSheetResult(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[PriceSheetModel]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PriceSheetModel] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.consumption.models.PricesheetDownloadProperties(_Model):
        download_url: Optional[str]
        valid_till: Optional[datetime]


    class azure.mgmt.consumption.models.PricingModelType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ON_DEMAND = "On Demand"
        RESERVATION = "Reservation"
        SPOT = "Spot"


    class azure.mgmt.consumption.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.consumption.models.Reseller(_Model):
        reseller_description: Optional[str]
        reseller_id: Optional[str]


    class azure.mgmt.consumption.models.ReservationDetail(Resource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[ReservationDetailProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ReservationDetailProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.consumption.models.ReservationDetailProperties(_Model):
        instance_flexibility_group: Optional[str]
        instance_flexibility_ratio: Optional[str]
        instance_id: Optional[str]
        kind: Optional[str]
        reservation_id: Optional[str]
        reservation_order_id: Optional[str]
        reserved_hours: Optional[Decimal]
        sku_name: Optional[str]
        total_reserved_quantity: Optional[Decimal]
        usage_date: Optional[datetime]
        used_hours: Optional[Decimal]


    class azure.mgmt.consumption.models.ReservationRecommendation(_Model):
        etag: Optional[str]
        id: Optional[str]
        kind: str
        location: Optional[str]
        name: Optional[str]
        sku: Optional[str]
        system_data: Optional[SystemData]
        tags: Optional[dict[str, str]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.ReservationRecommendationDetailsCalculatedSavingsProperties(_Model):
        on_demand_cost: Optional[float]
        overage_cost: Optional[float]
        quantity: Optional[float]
        reservation_cost: Optional[float]
        reserved_unit_count: Optional[float]
        savings: Optional[float]
        total_reservation_cost: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                reserved_unit_count: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.ReservationRecommendationDetailsModel(Resource):
        etag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ReservationRecommendationDetailsProperties]
        sku: Optional[str]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[ReservationRecommendationDetailsProperties] = ..., 
                sku: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.consumption.models.ReservationRecommendationDetailsProperties(_Model):
        currency: Optional[str]
        resource: Optional[ReservationRecommendationDetailsResourceProperties]
        resource_group: Optional[str]
        savings: Optional[ReservationRecommendationDetailsSavingsProperties]
        scope: Optional[str]
        usage: Optional[ReservationRecommendationDetailsUsageProperties]


    class azure.mgmt.consumption.models.ReservationRecommendationDetailsResourceProperties(_Model):
        applied_scopes: Optional[list[str]]
        on_demand_rate: Optional[float]
        product: Optional[str]
        region: Optional[str]
        reservation_rate: Optional[float]
        resource_type: Optional[str]


    class azure.mgmt.consumption.models.ReservationRecommendationDetailsSavingsProperties(_Model):
        calculated_savings: Optional[list[ReservationRecommendationDetailsCalculatedSavingsProperties]]
        look_back_period: Optional[int]
        recommended_quantity: Optional[float]
        reservation_order_term: Optional[str]
        savings_type: Optional[str]
        unit_of_measure: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                calculated_savings: Optional[list[ReservationRecommendationDetailsCalculatedSavingsProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.ReservationRecommendationDetailsUsageProperties(_Model):
        first_consumption_date: Optional[str]
        last_consumption_date: Optional[str]
        look_back_unit_type: Optional[str]
        usage_data: Optional[list[float]]
        usage_grain: Optional[str]


    class azure.mgmt.consumption.models.ReservationRecommendationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LEGACY = "legacy"
        MODERN = "modern"


    class azure.mgmt.consumption.models.ReservationSummary(Resource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[ReservationSummaryProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ReservationSummaryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.consumption.models.ReservationSummaryProperties(_Model):
        avg_utilization_percentage: Optional[Decimal]
        kind: Optional[str]
        max_utilization_percentage: Optional[Decimal]
        min_utilization_percentage: Optional[Decimal]
        purchased_quantity: Optional[Decimal]
        remaining_quantity: Optional[Decimal]
        reservation_id: Optional[str]
        reservation_order_id: Optional[str]
        reserved_hours: Optional[Decimal]
        sku_name: Optional[str]
        total_reserved_quantity: Optional[Decimal]
        usage_date: Optional[datetime]
        used_hours: Optional[Decimal]
        used_quantity: Optional[Decimal]
        utilized_percentage: Optional[Decimal]


    class azure.mgmt.consumption.models.ReservationTransaction(Resource):
        id: str
        name: str
        properties: Optional[LegacyReservationTransactionProperties]
        system_data: SystemData
        tags: Optional[list[str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[LegacyReservationTransactionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.consumption.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.consumption.models.SavingsPlan(_Model):
        effective_price: Optional[Decimal]
        market_price: Optional[Decimal]
        term: Optional[str]


    class azure.mgmt.consumption.models.Scope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SHARED = "Shared"
        SINGLE = "Single"


    class azure.mgmt.consumption.models.SkuProperty(_Model):
        name: Optional[str]
        value: Optional[str]


    class azure.mgmt.consumption.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CANCELED = "Canceled"
        COMPLETE = "Complete"
        EXPIRED = "Expired"
        INACTIVE = "Inactive"
        NONE = "None"


    class azure.mgmt.consumption.models.SystemData(_Model):
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


    class azure.mgmt.consumption.models.Tag(_Model):
        key: Optional[str]
        value: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.TagProperties(_Model):
        next_link: Optional[str]
        previous_link: Optional[str]
        tags: Optional[list[Tag]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[list[Tag]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.TagsResult(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[TagProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                properties: Optional[TagProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.consumption.models.Term(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P1_M = "P1M"
        P1_Y = "P1Y"
        P3_Y = "P3Y"


    class azure.mgmt.consumption.models.ThresholdType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTUAL = "Actual"
        FORECASTED = "Forecasted"


    class azure.mgmt.consumption.models.TimeGrainType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANNUALLY = "Annually"
        BILLING_ANNUAL = "BillingAnnual"
        BILLING_MONTH = "BillingMonth"
        BILLING_QUARTER = "BillingQuarter"
        MONTHLY = "Monthly"
        QUARTERLY = "Quarterly"


    class azure.mgmt.consumption.models.UsageDetail(Resource):
        etag: Optional[str]
        id: str
        kind: str
        name: str
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.consumption.models.UsageDetailsKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LEGACY = "legacy"
        MODERN = "modern"


namespace azure.mgmt.consumption.operations

    class azure.mgmt.consumption.operations.AggregatedCostOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_by_management_group(
                self, 
                management_group_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ManagementGroupAggregatedCostResult: ...

        @distributed_trace
        def get_for_billing_period_by_management_group(
                self, 
                management_group_id: str, 
                billing_period_name: str, 
                **kwargs: Any
            ) -> ManagementGroupAggregatedCostResult: ...


    class azure.mgmt.consumption.operations.BalancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_by_billing_account(
                self, 
                billing_account_id: str, 
                **kwargs: Any
            ) -> Balance: ...

        @distributed_trace
        def get_for_billing_period_by_billing_account(
                self, 
                billing_account_id: str, 
                billing_period_name: str, 
                **kwargs: Any
            ) -> Balance: ...


    class azure.mgmt.consumption.operations.BudgetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                budget_name: str, 
                parameters: Budget, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Budget: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                budget_name: str, 
                parameters: Budget, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Budget: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                budget_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Budget: ...

        @distributed_trace
        def delete(
                self, 
                scope: str, 
                budget_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                budget_name: str, 
                **kwargs: Any
            ) -> Budget: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[Budget]: ...


    class azure.mgmt.consumption.operations.ChargesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                *, 
                apply: Optional[str] = ..., 
                end_date: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                start_date: Optional[str] = ..., 
                **kwargs: Any
            ) -> ChargesListResult: ...


    class azure.mgmt.consumption.operations.CreditsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                **kwargs: Any
            ) -> Optional[CreditSummary]: ...


    class azure.mgmt.consumption.operations.EventsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EventSummary]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                *, 
                end_date: str, 
                start_date: str, 
                **kwargs: Any
            ) -> ItemPaged[EventSummary]: ...


    class azure.mgmt.consumption.operations.LotsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[LotSummary]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                **kwargs: Any
            ) -> ItemPaged[LotSummary]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_id: str, 
                customer_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[LotSummary]: ...


    class azure.mgmt.consumption.operations.MarketplacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                skiptoken: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Marketplace]: ...


    class azure.mgmt.consumption.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.consumption.operations.PriceSheetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_download_by_billing_account_period(
                self, 
                billing_account_id: str, 
                billing_period_name: str, 
                **kwargs: Any
            ) -> LROPoller[OperationStatus]: ...

        @distributed_trace
        def get(
                self, 
                *, 
                expand: Optional[str] = ..., 
                skiptoken: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> PriceSheetResult: ...

        @distributed_trace
        def get_by_billing_period(
                self, 
                billing_period_name: str, 
                *, 
                expand: Optional[str] = ..., 
                skiptoken: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> PriceSheetResult: ...


    class azure.mgmt.consumption.operations.ReservationRecommendationDetailsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_scope: str, 
                *, 
                filter: Optional[str] = ..., 
                look_back_period: Union[str, LookBackPeriod], 
                product: str, 
                region: str, 
                scope: Union[str, Scope], 
                term: Union[str, Term], 
                **kwargs: Any
            ) -> Optional[ReservationRecommendationDetailsModel]: ...


    class azure.mgmt.consumption.operations.ReservationRecommendationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ReservationRecommendation]: ...


    class azure.mgmt.consumption.operations.ReservationTransactionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                billing_account_id: str, 
                *, 
                filter: Optional[str] = ..., 
                preview_markup_percentage: Optional[Decimal] = ..., 
                use_markup_if_partner: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ReservationTransaction]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ModernReservationTransaction]: ...


    class azure.mgmt.consumption.operations.ReservationsDetailsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_scope: str, 
                *, 
                end_date: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                reservation_id: Optional[str] = ..., 
                reservation_order_id: Optional[str] = ..., 
                start_date: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ReservationDetail]: ...

        @distributed_trace
        def list_by_reservation_order(
                self, 
                reservation_order_id: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> ItemPaged[ReservationDetail]: ...

        @distributed_trace
        def list_by_reservation_order_and_reservation(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> ItemPaged[ReservationDetail]: ...


    class azure.mgmt.consumption.operations.ReservationsSummariesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_scope: str, 
                *, 
                end_date: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                grain: Union[str, Datagrain], 
                reservation_id: Optional[str] = ..., 
                reservation_order_id: Optional[str] = ..., 
                start_date: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ReservationSummary]: ...

        @distributed_trace
        def list_by_reservation_order(
                self, 
                reservation_order_id: str, 
                *, 
                filter: Optional[str] = ..., 
                grain: Union[str, Datagrain], 
                **kwargs: Any
            ) -> ItemPaged[ReservationSummary]: ...

        @distributed_trace
        def list_by_reservation_order_and_reservation(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                *, 
                filter: Optional[str] = ..., 
                grain: Union[str, Datagrain], 
                **kwargs: Any
            ) -> ItemPaged[ReservationSummary]: ...


    class azure.mgmt.consumption.operations.TagsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> Optional[TagsResult]: ...


    class azure.mgmt.consumption.operations.UsageDetailsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                metric: Optional[Union[str, Metrictype]] = ..., 
                skiptoken: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[UsageDetail]: ...


namespace azure.mgmt.consumption.types

    class azure.mgmt.consumption.types.Budget(ExtensionResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('BudgetProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        e_tag: str
        id: str
        name: str
        properties: BudgetProperties
        system_data: SystemData
        type: str


    class azure.mgmt.consumption.types.BudgetComparisonExpression(TypedDict, total=False):
        key "name": Required[str]
        key "operator": Required[Union[str, BudgetOperatorType]]
        key "values": Required[list[str]]
        name: str
        operator: Union[str, BudgetOperatorType]
        values_property: list[str]


    class azure.mgmt.consumption.types.BudgetFilter(TypedDict):
        key "dimensions": ForwardRef('BudgetComparisonExpression', module='types')
        key "tags": ForwardRef('BudgetComparisonExpression', module='types')
        and: list[BudgetFilterProperties]
        and_property: list[BudgetFilterProperties]
        dimensions: BudgetComparisonExpression
        tags: BudgetComparisonExpression


    class azure.mgmt.consumption.types.BudgetFilterProperties(TypedDict, total=False):
        key "dimensions": ForwardRef('BudgetComparisonExpression', module='types')
        key "tags": ForwardRef('BudgetComparisonExpression', module='types')
        dimensions: BudgetComparisonExpression
        tags: BudgetComparisonExpression


    class azure.mgmt.consumption.types.BudgetProperties(TypedDict, total=False):
        key "amount": Required[float]
        key "category": Required[Union[str, CategoryType]]
        key "currentSpend": ForwardRef('CurrentSpend', module='types')
        key "filter": ForwardRef('BudgetFilter', module='types')
        key "forecastSpend": ForwardRef('ForecastSpend', module='types')
        key "timeGrain": Required[Union[str, TimeGrainType]]
        key "timePeriod": Required[BudgetTimePeriod]
        amount: float
        category: Union[str, CategoryType]
        current_spend: CurrentSpend
        filter: BudgetFilter
        forecast_spend: ForecastSpend
        notifications: dict[str, Notification]
        time_grain: Union[str, TimeGrainType]
        time_period: BudgetTimePeriod


    class azure.mgmt.consumption.types.BudgetTimePeriod(TypedDict, total=False):
        key "endDate": str
        key "startDate": Required[str]
        end_date: str
        start_date: str


    class azure.mgmt.consumption.types.CurrentSpend(TypedDict, total=False):
        key "amount": float
        key "unit": str
        amount: float
        unit: str


    class azure.mgmt.consumption.types.ExtensionResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.consumption.types.ForecastSpend(TypedDict, total=False):
        key "amount": float
        key "unit": str
        amount: float
        unit: str


    class azure.mgmt.consumption.types.Notification(TypedDict, total=False):
        key "contactEmails": Required[list[str]]
        key "enabled": Required[bool]
        key "locale": Union[str, CultureCode]
        key "operator": Required[Union[str, OperatorType]]
        key "threshold": Required[float]
        key "thresholdType": Union[str, ThresholdType]
        contactGroups: list[str]
        contactRoles: list[str]
        contact_emails: list[str]
        contact_groups: list[str]
        contact_roles: list[str]
        enabled: bool
        locale: Union[str, CultureCode]
        operator: Union[str, OperatorType]
        threshold: float
        threshold_type: Union[str, ThresholdType]


    class azure.mgmt.consumption.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.consumption.types.SystemData(TypedDict, total=False):
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