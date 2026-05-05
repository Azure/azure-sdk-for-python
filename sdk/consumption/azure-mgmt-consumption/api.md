```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


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
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


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
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


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
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ManagementGroupAggregatedCostResult: ...

        @distributed_trace_async
        async def get_for_billing_period_by_management_group(
                self, 
                management_group_id: str, 
                billing_period_name: str, 
                *, 
                cls: Optional[callable] = ..., 
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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Balance: ...

        @distributed_trace_async
        async def get_for_billing_period_by_billing_account(
                self, 
                billing_account_id: str, 
                billing_period_name: str, 
                *, 
                cls: Optional[callable] = ..., 
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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Budget: ...

        @distributed_trace_async
        async def delete(
                self, 
                scope: str, 
                budget_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                budget_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Budget: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Budget]: ...


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
                start_date: Optional[str] = None, 
                end_date: Optional[str] = None, 
                filter: Optional[str] = None, 
                apply: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
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
                *, 
                cls: Optional[callable] = ..., 
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
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[EventSummary]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                start_date: str, 
                end_date: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[EventSummary]: ...


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
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[LotSummary]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[LotSummary]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_id: str, 
                customer_id: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[LotSummary]: ...


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
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skiptoken: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Marketplace]: ...


    class azure.mgmt.consumption.aio.operations.Operations:

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
            ) -> AsyncIterable[Operation]: ...


    class azure.mgmt.consumption.aio.operations.PriceSheetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                expand: Optional[str] = None, 
                skiptoken: Optional[str] = None, 
                top: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PriceSheetResult: ...

        @distributed_trace_async
        async def get_by_billing_period(
                self, 
                billing_period_name: str, 
                expand: Optional[str] = None, 
                skiptoken: Optional[str] = None, 
                top: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
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
                scope: Union[str, Scope], 
                region: str, 
                term: Union[str, Term], 
                look_back_period: Union[str, LookBackPeriod], 
                product: str, 
                *, 
                cls: Optional[callable] = ..., 
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
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ReservationRecommendation]: ...


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
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ReservationTransaction]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ModernReservationTransaction]: ...


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
                start_date: Optional[str] = None, 
                end_date: Optional[str] = None, 
                filter: Optional[str] = None, 
                reservation_id: Optional[str] = None, 
                reservation_order_id: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ReservationDetail]: ...

        @distributed_trace
        def list_by_reservation_order(
                self, 
                reservation_order_id: str, 
                filter: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ReservationDetail]: ...

        @distributed_trace
        def list_by_reservation_order_and_reservation(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                filter: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ReservationDetail]: ...


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
                grain: Union[str, Datagrain], 
                start_date: Optional[str] = None, 
                end_date: Optional[str] = None, 
                filter: Optional[str] = None, 
                reservation_id: Optional[str] = None, 
                reservation_order_id: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ReservationSummary]: ...

        @distributed_trace
        def list_by_reservation_order(
                self, 
                reservation_order_id: str, 
                grain: Union[str, Datagrain], 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ReservationSummary]: ...

        @distributed_trace
        def list_by_reservation_order_and_reservation(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                grain: Union[str, Datagrain], 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ReservationSummary]: ...


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
                *, 
                cls: Optional[callable] = ..., 
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
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                skiptoken: Optional[str] = None, 
                top: Optional[int] = None, 
                metric: Optional[Union[str, Metrictype]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[UsageDetail]: ...


namespace azure.mgmt.consumption.models

    class azure.mgmt.consumption.models.Amount(Model):
        currency: str
        value: float

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.AmountWithExchangeRate(Amount):
        currency: str
        exchange_rate: float
        exchange_rate_month: int
        value: float

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.Balance(Resource):
        adjustment_details: list[BalancePropertiesAdjustmentDetailsItem]
        adjustments: float
        azure_marketplace_service_charges: float
        beginning_balance: float
        billing_frequency: Union[str, BillingFrequency]
        charges_billed_separately: float
        currency: str
        ending_balance: float
        etag: str
        id: str
        name: str
        new_purchases: float
        new_purchases_details: list[BalancePropertiesNewPurchasesDetailsItem]
        price_hidden: bool
        service_overage: float
        tags: dict[str, str]
        total_overage: float
        total_usage: float
        type: str
        utilized: float

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                billing_frequency: Optional[Union[str, BillingFrequency]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.BalancePropertiesAdjustmentDetailsItem(Model):
        name: str
        value: float

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.BalancePropertiesNewPurchasesDetailsItem(Model):
        name: str
        value: float

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.BillingFrequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONTH = "Month"
        QUARTER = "Quarter"
        YEAR = "Year"


    class azure.mgmt.consumption.models.Budget(ProxyResource):
        amount: float
        category: Union[str, CategoryType]
        current_spend: CurrentSpend
        e_tag: str
        filter: BudgetFilter
        forecast_spend: ForecastSpend
        id: str
        name: str
        notifications: dict[str, Notification]
        time_grain: Union[str, TimeGrainType]
        time_period: BudgetTimePeriod
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                amount: Optional[float] = ..., 
                category: Optional[Union[str, CategoryType]] = ..., 
                e_tag: Optional[str] = ..., 
                filter: Optional[BudgetFilter] = ..., 
                notifications: Optional[Dict[str, Notification]] = ..., 
                time_grain: Optional[Union[str, TimeGrainType]] = ..., 
                time_period: Optional[BudgetTimePeriod] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.BudgetComparisonExpression(Model):
        name: str
        operator: Union[str, BudgetOperatorType]
        values: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                name: str, 
                operator: Union[str, BudgetOperatorType], 
                values: List[str], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.BudgetFilter(Model):
        and_property: list[BudgetFilterProperties]
        dimensions: BudgetComparisonExpression
        tags: BudgetComparisonExpression

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                and_property: Optional[List[BudgetFilterProperties]] = ..., 
                dimensions: Optional[BudgetComparisonExpression] = ..., 
                tags: Optional[BudgetComparisonExpression] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.BudgetFilterProperties(Model):
        dimensions: BudgetComparisonExpression
        tags: BudgetComparisonExpression

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                dimensions: Optional[BudgetComparisonExpression] = ..., 
                tags: Optional[BudgetComparisonExpression] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.BudgetOperatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IN = "In"


    class azure.mgmt.consumption.models.BudgetTimePeriod(Model):
        end_date: datetime
        start_date: datetime

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                end_date: Optional[datetime] = ..., 
                start_date: datetime, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.BudgetsListResult(Model):
        next_link: str
        value: list[Budget]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.CategoryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COST = "Cost"


    class azure.mgmt.consumption.models.ChargeSummary(Resource):
        etag: str
        id: str
        kind: Union[str, ChargeSummaryKind]
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ChargeSummaryKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LEGACY = "legacy"
        MODERN = "modern"


    class azure.mgmt.consumption.models.ChargesListResult(Model):
        value: list[ChargeSummary]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.CreditBalanceSummary(Model):
        current_balance: Amount
        estimated_balance: Amount
        estimated_balance_in_billing_currency: AmountWithExchangeRate

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.CreditSummary(ProxyResource):
        balance_summary: CreditBalanceSummary
        billing_currency: str
        credit_currency: str
        e_tag: str
        e_tag_properties_e_tag: str
        expired_credit: Amount
        id: str
        name: str
        pending_credit_adjustments: Amount
        pending_eligible_charges: Amount
        reseller: Reseller
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


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


    class azure.mgmt.consumption.models.CurrentSpend(Model):
        amount: float
        unit: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.Datagrain(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY_GRAIN = "daily"
        MONTHLY_GRAIN = "monthly"


    class azure.mgmt.consumption.models.DownloadProperties(Model):
        download_url: str
        valid_till: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ErrorDetails(Model):
        code: str
        message: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ErrorResponse(Model):
        error: ErrorDetails

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetails] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.EventSummary(ProxyResource):
        adjustments: Amount
        adjustments_in_billing_currency: AmountWithExchangeRate
        billing_currency: str
        billing_profile_display_name: str
        billing_profile_id: str
        canceled_credit: Amount
        charges: Amount
        charges_in_billing_currency: AmountWithExchangeRate
        closed_balance: Amount
        closed_balance_in_billing_currency: AmountWithExchangeRate
        credit_currency: str
        credit_expired: Amount
        credit_expired_in_billing_currency: AmountWithExchangeRate
        description: str
        e_tag: str
        e_tag_properties_e_tag: str
        event_type: Union[str, EventType]
        id: str
        invoice_number: str
        lot_id: str
        lot_source: str
        name: str
        new_credit: Amount
        new_credit_in_billing_currency: AmountWithExchangeRate
        reseller: Reseller
        transaction_date: datetime
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                event_type: Optional[Union[str, EventType]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.EventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREDIT_EXPIRED = "CreditExpired"
        NEW_CREDIT = "NewCredit"
        PENDING_ADJUSTMENTS = "PendingAdjustments"
        PENDING_CHARGES = "PendingCharges"
        PENDING_EXPIRED_CREDIT = "PendingExpiredCredit"
        PENDING_NEW_CREDIT = "PendingNewCredit"
        SETTLED_CHARGES = "SettledCharges"
        UN_KNOWN = "UnKnown"


    class azure.mgmt.consumption.models.Events(Model):
        next_link: str
        value: list[EventSummary]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ForecastSpend(Model):
        amount: float
        unit: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.HighCasedErrorDetails(Model):
        code: str
        message: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.HighCasedErrorResponse(Model):
        error: HighCasedErrorDetails

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[HighCasedErrorDetails] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.LegacyChargeSummary(ChargeSummary):
        azure_charges: float
        azure_marketplace_charges: float
        billing_period_id: str
        charges_billed_separately: float
        currency: str
        etag: str
        id: str
        kind: Union[str, ChargeSummaryKind]
        name: str
        tags: dict[str, str]
        type: str
        usage_end: str
        usage_start: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.LegacyReservationRecommendation(ReservationRecommendation):
        cost_with_no_reserved_instances: float
        etag: str
        first_usage_date: datetime
        id: str
        instance_flexibility_group: str
        instance_flexibility_ratio: float
        kind: Union[str, ReservationRecommendationKind]
        location: str
        look_back_period: str
        meter_id: str
        name: str
        net_savings: float
        normalized_size: str
        recommended_quantity: float
        recommended_quantity_normalized: float
        resource_type: str
        scope: str
        sku: str
        sku_properties: list[SkuProperty]
        tags: dict[str, str]
        term: str
        total_cost_with_reserved_instances: float
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.LegacyReservationRecommendationProperties(Model):
        cost_with_no_reserved_instances: float
        first_usage_date: datetime
        instance_flexibility_group: str
        instance_flexibility_ratio: float
        look_back_period: str
        meter_id: str
        net_savings: float
        normalized_size: str
        recommended_quantity: float
        recommended_quantity_normalized: float
        resource_type: str
        scope: str
        sku_properties: list[SkuProperty]
        term: str
        total_cost_with_reserved_instances: float

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.LegacyReservationTransaction(ReservationTransaction):
        account_name: str
        account_owner_email: str
        amount: float
        arm_sku_name: str
        billing_frequency: str
        billing_month: int
        cost_center: str
        currency: str
        current_enrollment: str
        department_name: str
        description: str
        event_date: datetime
        event_type: str
        id: str
        monetary_commitment: float
        name: str
        overage: float
        purchasing_enrollment: str
        purchasing_subscription_guid: str
        purchasing_subscription_name: str
        quantity: float
        region: str
        reservation_order_id: str
        reservation_order_name: str
        tags: list[str]
        term: str
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.LegacySharedScopeReservationRecommendationProperties(LegacyReservationRecommendationProperties):
        cost_with_no_reserved_instances: float
        first_usage_date: datetime
        instance_flexibility_group: str
        instance_flexibility_ratio: float
        look_back_period: str
        meter_id: str
        net_savings: float
        normalized_size: str
        recommended_quantity: float
        recommended_quantity_normalized: float
        resource_type: str
        scope: str
        sku_properties: list[SkuProperty]
        term: str
        total_cost_with_reserved_instances: float

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.LegacySingleScopeReservationRecommendationProperties(LegacyReservationRecommendationProperties):
        cost_with_no_reserved_instances: float
        first_usage_date: datetime
        instance_flexibility_group: str
        instance_flexibility_ratio: float
        look_back_period: str
        meter_id: str
        net_savings: float
        normalized_size: str
        recommended_quantity: float
        recommended_quantity_normalized: float
        resource_type: str
        scope: str
        sku_properties: list[SkuProperty]
        subscription_id: str
        term: str
        total_cost_with_reserved_instances: float

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.LegacyUsageDetail(UsageDetail):
        account_name: str
        account_owner_id: str
        additional_info: str
        benefit_id: str
        benefit_name: str
        billing_account_id: str
        billing_account_name: str
        billing_currency: str
        billing_period_end_date: datetime
        billing_period_start_date: datetime
        billing_profile_id: str
        billing_profile_name: str
        charge_type: str
        consumed_service: str
        cost: float
        cost_center: str
        date: datetime
        effective_price: float
        etag: str
        frequency: str
        id: str
        invoice_section: str
        is_azure_credit_eligible: bool
        kind: Union[str, UsageDetailsKind]
        meter_details: MeterDetailsResponse
        meter_id: str
        name: str
        offer_id: str
        part_number: str
        pay_g_price: float
        plan_name: str
        pricing_model: Union[str, PricingModelType]
        product: str
        product_order_id: str
        product_order_name: str
        publisher_name: str
        publisher_type: str
        quantity: float
        reservation_id: str
        reservation_name: str
        resource_group: str
        resource_id: str
        resource_location: str
        resource_name: str
        service_info1: str
        service_info2: str
        subscription_id: str
        subscription_name: str
        tags: dict[str, str]
        term: str
        type: str
        unit_price: float

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.LookBackPeriod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LAST07_DAYS = "Last7Days"
        LAST30_DAYS = "Last30Days"
        LAST60_DAYS = "Last60Days"


    class azure.mgmt.consumption.models.LotSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONSUMPTION_COMMITMENT = "ConsumptionCommitment"
        PROMOTIONAL_CREDIT = "PromotionalCredit"
        PURCHASED_CREDIT = "PurchasedCredit"


    class azure.mgmt.consumption.models.LotSummary(ProxyResource):
        billing_currency: str
        closed_balance: Amount
        closed_balance_in_billing_currency: AmountWithExchangeRate
        credit_currency: str
        e_tag: str
        e_tag_properties_e_tag: str
        expiration_date: datetime
        id: str
        name: str
        original_amount: Amount
        original_amount_in_billing_currency: AmountWithExchangeRate
        po_number: str
        purchased_date: datetime
        reseller: Reseller
        source: Union[str, LotSource]
        start_date: datetime
        status: Union[str, Status]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.Lots(Model):
        next_link: str
        value: list[LotSummary]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ManagementGroupAggregatedCostResult(Resource):
        azure_charges: float
        billing_period_id: str
        charges_billed_separately: float
        children: list[ManagementGroupAggregatedCostResult]
        currency: str
        etag: str
        excluded_subscriptions: list[str]
        id: str
        included_subscriptions: list[str]
        marketplace_charges: float
        name: str
        tags: dict[str, str]
        type: str
        usage_end: datetime
        usage_start: datetime

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                children: Optional[List[ManagementGroupAggregatedCostResult]] = ..., 
                excluded_subscriptions: Optional[List[str]] = ..., 
                included_subscriptions: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.Marketplace(Resource):
        account_name: str
        additional_info: str
        additional_properties: str
        billing_period_id: str
        consumed_quantity: float
        consumed_service: str
        cost_center: str
        currency: str
        department_name: str
        etag: str
        id: str
        instance_id: str
        instance_name: str
        is_estimated: bool
        is_recurring_charge: bool
        meter_id: str
        name: str
        offer_name: str
        order_number: str
        plan_name: str
        pretax_cost: float
        publisher_name: str
        resource_group: str
        resource_rate: float
        subscription_guid: str
        subscription_name: str
        tags: dict[str, str]
        type: str
        unit_of_measure: str
        usage_end: datetime
        usage_start: datetime

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.MarketplacesListResult(Model):
        next_link: str
        value: list[Marketplace]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.MeterDetails(Model):
        meter_category: str
        meter_location: str
        meter_name: str
        meter_sub_category: str
        pretax_standard_rate: float
        service_name: str
        service_tier: str
        total_included_quantity: float
        unit: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.MeterDetailsResponse(Model):
        meter_category: str
        meter_name: str
        meter_sub_category: str
        service_family: str
        unit_of_measure: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.Metrictype(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTUAL_COST_METRIC_TYPE = "actualcost"
        AMORTIZED_COST_METRIC_TYPE = "amortizedcost"
        USAGE_METRIC_TYPE = "usage"


    class azure.mgmt.consumption.models.ModernChargeSummary(ChargeSummary):
        azure_charges: Amount
        billing_account_id: str
        billing_period_id: str
        billing_profile_id: str
        charges_billed_separately: Amount
        customer_id: str
        etag: str
        id: str
        invoice_section_id: str
        is_invoiced: bool
        kind: Union[str, ChargeSummaryKind]
        marketplace_charges: Amount
        name: str
        tags: dict[str, str]
        type: str
        usage_end: str
        usage_start: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ModernReservationRecommendation(ReservationRecommendation):
        cost_with_no_reserved_instances: Amount
        etag: str
        first_usage_date: datetime
        id: str
        instance_flexibility_group: str
        instance_flexibility_ratio: float
        kind: Union[str, ReservationRecommendationKind]
        location: str
        location_properties_location: str
        look_back_period: int
        meter_id: str
        name: str
        net_savings: Amount
        normalized_size: str
        recommended_quantity: float
        recommended_quantity_normalized: float
        resource_type: str
        scope: str
        sku: str
        sku_name: str
        sku_properties: list[SkuProperty]
        tags: dict[str, str]
        term: str
        total_cost_with_reserved_instances: Amount
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ModernReservationRecommendationProperties(Model):
        cost_with_no_reserved_instances: Amount
        first_usage_date: datetime
        instance_flexibility_group: str
        instance_flexibility_ratio: float
        location: str
        look_back_period: int
        meter_id: str
        net_savings: Amount
        normalized_size: str
        recommended_quantity: float
        recommended_quantity_normalized: float
        resource_type: str
        scope: str
        sku_name: str
        sku_properties: list[SkuProperty]
        term: str
        total_cost_with_reserved_instances: Amount

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ModernReservationTransaction(ReservationTransactionResource):
        amount: float
        arm_sku_name: str
        billing_frequency: str
        billing_profile_id: str
        billing_profile_name: str
        currency: str
        description: str
        event_date: datetime
        event_type: str
        id: str
        invoice: str
        invoice_id: str
        invoice_section_id: str
        invoice_section_name: str
        name: str
        purchasing_subscription_guid: str
        purchasing_subscription_name: str
        quantity: float
        region: str
        reservation_order_id: str
        reservation_order_name: str
        tags: list[str]
        term: str
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ModernReservationTransactionsListResult(Model):
        next_link: str
        value: list[ModernReservationTransaction]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ModernSharedScopeReservationRecommendationProperties(ModernReservationRecommendationProperties):
        cost_with_no_reserved_instances: Amount
        first_usage_date: datetime
        instance_flexibility_group: str
        instance_flexibility_ratio: float
        location: str
        look_back_period: int
        meter_id: str
        net_savings: Amount
        normalized_size: str
        recommended_quantity: float
        recommended_quantity_normalized: float
        resource_type: str
        scope: str
        sku_name: str
        sku_properties: list[SkuProperty]
        term: str
        total_cost_with_reserved_instances: Amount

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ModernSingleScopeReservationRecommendationProperties(ModernReservationRecommendationProperties):
        cost_with_no_reserved_instances: Amount
        first_usage_date: datetime
        instance_flexibility_group: str
        instance_flexibility_ratio: float
        location: str
        look_back_period: int
        meter_id: str
        net_savings: Amount
        normalized_size: str
        recommended_quantity: float
        recommended_quantity_normalized: float
        resource_type: str
        scope: str
        sku_name: str
        sku_properties: list[SkuProperty]
        subscription_id: str
        term: str
        total_cost_with_reserved_instances: Amount

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ModernUsageDetail(UsageDetail):
        additional_info: str
        benefit_id: str
        benefit_name: str
        billing_account_id: str
        billing_account_name: str
        billing_currency_code: str
        billing_period_end_date: datetime
        billing_period_start_date: datetime
        billing_profile_id: str
        billing_profile_name: str
        charge_type: str
        consumed_service: str
        cost_allocation_rule_name: str
        cost_center: str
        cost_in_billing_currency: float
        cost_in_pricing_currency: float
        cost_in_usd: float
        customer_name: str
        customer_tenant_id: str
        date: datetime
        effective_price: float
        etag: str
        exchange_rate: str
        exchange_rate_date: datetime
        exchange_rate_pricing_to_billing: float
        frequency: str
        id: str
        instance_name: str
        invoice_id: str
        invoice_section_id: str
        invoice_section_name: str
        is_azure_credit_eligible: bool
        kind: Union[str, UsageDetailsKind]
        market_price: float
        meter_category: str
        meter_id: str
        meter_name: str
        meter_region: str
        meter_sub_category: str
        name: str
        partner_earned_credit_applied: str
        partner_earned_credit_rate: float
        partner_name: str
        partner_tenant_id: str
        pay_g_price: float
        payg_cost_in_billing_currency: float
        payg_cost_in_usd: float
        previous_invoice_id: str
        pricing_currency_code: str
        pricing_model: Union[str, PricingModelType]
        product: str
        product_identifier: str
        product_order_id: str
        product_order_name: str
        provider: str
        publisher_id: str
        publisher_name: str
        publisher_type: str
        quantity: float
        reseller_mpn_id: str
        reseller_name: str
        reservation_id: str
        reservation_name: str
        resource_group: str
        resource_location: str
        resource_location_normalized: str
        service_family: str
        service_info1: str
        service_info2: str
        service_period_end_date: datetime
        service_period_start_date: datetime
        subscription_guid: str
        subscription_name: str
        tags: dict[str, str]
        term: str
        type: str
        unit_of_measure: str
        unit_price: float

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.Notification(Model):
        contact_emails: list[str]
        contact_groups: list[str]
        contact_roles: list[str]
        enabled: bool
        locale: Union[str, CultureCode]
        operator: Union[str, OperatorType]
        threshold: float
        threshold_type: Union[str, ThresholdType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                contact_emails: List[str], 
                contact_groups: Optional[List[str]] = ..., 
                contact_roles: Optional[List[str]] = ..., 
                enabled: bool, 
                locale: Optional[Union[str, CultureCode]] = ..., 
                operator: Union[str, OperatorType], 
                threshold: float, 
                threshold_type: Union[str, ThresholdType] = "Actual", 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.Operation(Model):
        display: OperationDisplay
        id: str
        name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.OperatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUAL_TO = "EqualTo"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL_TO = "GreaterThanOrEqualTo"


    class azure.mgmt.consumption.models.PriceSheetProperties(Model):
        billing_period_id: str
        currency_code: str
        included_quantity: float
        meter_details: MeterDetails
        meter_id: str
        offer_id: str
        part_number: str
        unit_of_measure: str
        unit_price: float

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.PriceSheetResult(Resource):
        download: MeterDetails
        etag: str
        id: str
        name: str
        next_link: str
        pricesheets: list[PriceSheetProperties]
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.PricingModelType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ON_DEMAND = "On Demand"
        RESERVATION = "Reservation"
        SPOT = "Spot"


    class azure.mgmt.consumption.models.ProxyResource(Model):
        e_tag: str
        id: str
        name: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.Reseller(Model):
        reseller_description: str
        reseller_id: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ReservationDetail(Resource):
        etag: str
        id: str
        instance_flexibility_group: str
        instance_flexibility_ratio: str
        instance_id: str
        kind: str
        name: str
        reservation_id: str
        reservation_order_id: str
        reserved_hours: float
        sku_name: str
        tags: dict[str, str]
        total_reserved_quantity: float
        type: str
        usage_date: datetime
        used_hours: float

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ReservationDetailsListResult(Model):
        next_link: str
        value: list[ReservationDetail]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ReservationRecommendation(Resource, ResourceAttributes):
        etag: str
        id: str
        kind: Union[str, ReservationRecommendationKind]
        location: str
        name: str
        sku: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ReservationRecommendationDetailsCalculatedSavingsProperties(Model):
        on_demand_cost: float
        overage_cost: float
        quantity: float
        reservation_cost: float
        reserved_unit_count: float
        savings: float
        total_reservation_cost: float

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                reserved_unit_count: Optional[float] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ReservationRecommendationDetailsModel(Resource):
        currency: str
        etag: str
        id: str
        location: str
        name: str
        resource: ReservationRecommendationDetailsResourceProperties
        resource_group: str
        savings: ReservationRecommendationDetailsSavingsProperties
        scope: str
        sku: str
        tags: dict[str, str]
        type: str
        usage: ReservationRecommendationDetailsUsageProperties

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                sku: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ReservationRecommendationDetailsResourceProperties(Model):
        applied_scopes: list[str]
        on_demand_rate: float
        product: str
        region: str
        reservation_rate: float
        resource_type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ReservationRecommendationDetailsSavingsProperties(Model):
        calculated_savings: list[ReservationRecommendationDetailsCalculatedSavingsProperties]
        look_back_period: int
        recommended_quantity: float
        reservation_order_term: str
        savings_type: str
        unit_of_measure: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                calculated_savings: Optional[List[ReservationRecommendationDetailsCalculatedSavingsProperties]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ReservationRecommendationDetailsUsageProperties(Model):
        first_consumption_date: str
        last_consumption_date: str
        look_back_unit_type: str
        usage_data: list[float]
        usage_grain: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ReservationRecommendationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LEGACY = "legacy"
        MODERN = "modern"


    class azure.mgmt.consumption.models.ReservationRecommendationsListResult(Model):
        next_link: str
        previous_link: str
        value: list[ReservationRecommendation]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ReservationSummariesListResult(Model):
        next_link: str
        value: list[ReservationSummary]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ReservationSummary(Resource):
        avg_utilization_percentage: float
        etag: str
        id: str
        kind: str
        max_utilization_percentage: float
        min_utilization_percentage: float
        name: str
        purchased_quantity: float
        remaining_quantity: float
        reservation_id: str
        reservation_order_id: str
        reserved_hours: float
        sku_name: str
        tags: dict[str, str]
        total_reserved_quantity: float
        type: str
        usage_date: datetime
        used_hours: float
        used_quantity: float
        utilized_percentage: float

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ReservationTransaction(ReservationTransactionResource):
        account_name: str
        account_owner_email: str
        amount: float
        arm_sku_name: str
        billing_frequency: str
        billing_month: int
        cost_center: str
        currency: str
        current_enrollment: str
        department_name: str
        description: str
        event_date: datetime
        event_type: str
        id: str
        monetary_commitment: float
        name: str
        overage: float
        purchasing_enrollment: str
        purchasing_subscription_guid: str
        purchasing_subscription_name: str
        quantity: float
        region: str
        reservation_order_id: str
        reservation_order_name: str
        tags: list[str]
        term: str
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ReservationTransactionResource(Model):
        id: str
        name: str
        tags: list[str]
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ReservationTransactionsListResult(Model):
        next_link: str
        value: list[ReservationTransaction]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.Resource(Model):
        etag: str
        id: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.ResourceAttributes(Model):
        location: str
        sku: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.Scope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SHARED = "Shared"
        SINGLE = "Single"


    class azure.mgmt.consumption.models.SkuProperty(Model):
        name: str
        value: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CANCELED = "Canceled"
        COMPLETE = "Complete"
        EXPIRED = "Expired"
        INACTIVE = "Inactive"
        NONE = "None"


    class azure.mgmt.consumption.models.Tag(Model):
        key: str
        value: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.TagsResult(ProxyResource):
        e_tag: str
        id: str
        name: str
        next_link: str
        previous_link: str
        tags: list[Tag]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                tags: Optional[List[Tag]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.Term(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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
        etag: str
        id: str
        kind: Union[str, UsageDetailsKind]
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.consumption.models.UsageDetailsKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LEGACY = "legacy"
        MODERN = "modern"


    class azure.mgmt.consumption.models.UsageDetailsListResult(Model):
        next_link: str
        value: list[UsageDetail]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


namespace azure.mgmt.consumption.operations

    class azure.mgmt.consumption.operations.AggregatedCostOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get_by_management_group(
                self, 
                management_group_id: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ManagementGroupAggregatedCostResult: ...

        @distributed_trace
        def get_for_billing_period_by_management_group(
                self, 
                management_group_id: str, 
                billing_period_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ManagementGroupAggregatedCostResult: ...


    class azure.mgmt.consumption.operations.BalancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get_by_billing_account(
                self, 
                billing_account_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Balance: ...

        @distributed_trace
        def get_for_billing_period_by_billing_account(
                self, 
                billing_account_id: str, 
                billing_period_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Balance: ...


    class azure.mgmt.consumption.operations.BudgetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Budget: ...

        @distributed_trace
        def delete(
                self, 
                scope: str, 
                budget_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                budget_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Budget: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Budget]: ...


    class azure.mgmt.consumption.operations.ChargesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                start_date: Optional[str] = None, 
                end_date: Optional[str] = None, 
                filter: Optional[str] = None, 
                apply: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ChargesListResult: ...


    class azure.mgmt.consumption.operations.CreditsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Optional[CreditSummary]: ...


    class azure.mgmt.consumption.operations.EventsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_id: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[EventSummary]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                start_date: str, 
                end_date: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[EventSummary]: ...


    class azure.mgmt.consumption.operations.LotsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_billing_account(
                self, 
                billing_account_id: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[LotSummary]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[LotSummary]: ...

        @distributed_trace
        def list_by_customer(
                self, 
                billing_account_id: str, 
                customer_id: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[LotSummary]: ...


    class azure.mgmt.consumption.operations.MarketplacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                filter: Optional[str] = None, 
                top: Optional[int] = None, 
                skiptoken: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Marketplace]: ...


    class azure.mgmt.consumption.operations.Operations:

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
            ) -> Iterable[Operation]: ...


    class azure.mgmt.consumption.operations.PriceSheetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                expand: Optional[str] = None, 
                skiptoken: Optional[str] = None, 
                top: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PriceSheetResult: ...

        @distributed_trace
        def get_by_billing_period(
                self, 
                billing_period_name: str, 
                expand: Optional[str] = None, 
                skiptoken: Optional[str] = None, 
                top: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> PriceSheetResult: ...


    class azure.mgmt.consumption.operations.ReservationRecommendationDetailsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_scope: str, 
                scope: Union[str, Scope], 
                region: str, 
                term: Union[str, Term], 
                look_back_period: Union[str, LookBackPeriod], 
                product: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Optional[ReservationRecommendationDetailsModel]: ...


    class azure.mgmt.consumption.operations.ReservationRecommendationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                resource_scope: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ReservationRecommendation]: ...


    class azure.mgmt.consumption.operations.ReservationTransactionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                billing_account_id: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ReservationTransaction]: ...

        @distributed_trace
        def list_by_billing_profile(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ModernReservationTransaction]: ...


    class azure.mgmt.consumption.operations.ReservationsDetailsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                resource_scope: str, 
                start_date: Optional[str] = None, 
                end_date: Optional[str] = None, 
                filter: Optional[str] = None, 
                reservation_id: Optional[str] = None, 
                reservation_order_id: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ReservationDetail]: ...

        @distributed_trace
        def list_by_reservation_order(
                self, 
                reservation_order_id: str, 
                filter: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ReservationDetail]: ...

        @distributed_trace
        def list_by_reservation_order_and_reservation(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                filter: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ReservationDetail]: ...


    class azure.mgmt.consumption.operations.ReservationsSummariesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                resource_scope: str, 
                grain: Union[str, Datagrain], 
                start_date: Optional[str] = None, 
                end_date: Optional[str] = None, 
                filter: Optional[str] = None, 
                reservation_id: Optional[str] = None, 
                reservation_order_id: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ReservationSummary]: ...

        @distributed_trace
        def list_by_reservation_order(
                self, 
                reservation_order_id: str, 
                grain: Union[str, Datagrain], 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ReservationSummary]: ...

        @distributed_trace
        def list_by_reservation_order_and_reservation(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                grain: Union[str, Datagrain], 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ReservationSummary]: ...


    class azure.mgmt.consumption.operations.TagsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Optional[TagsResult]: ...


    class azure.mgmt.consumption.operations.UsageDetailsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                expand: Optional[str] = None, 
                filter: Optional[str] = None, 
                skiptoken: Optional[str] = None, 
                top: Optional[int] = None, 
                metric: Optional[Union[str, Metrictype]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[UsageDetail]: ...


```