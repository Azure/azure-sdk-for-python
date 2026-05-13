```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.commerce

    class azure.mgmt.commerce.UsageManagementClient: implements ContextManager 
        rate_card: RateCardOperations
        usage_aggregates: UsageAggregatesOperations

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


namespace azure.mgmt.commerce.aio

    class azure.mgmt.commerce.aio.UsageManagementClient: implements AsyncContextManager 
        rate_card: RateCardOperations
        usage_aggregates: UsageAggregatesOperations

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


namespace azure.mgmt.commerce.aio.operations

    class azure.mgmt.commerce.aio.operations.RateCardOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> ResourceRateCardInfo: ...


    class azure.mgmt.commerce.aio.operations.UsageAggregatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                aggregation_granularity: Union[str, AggregationGranularity] = "Daily", 
                continuation_token_parameter: Optional[str] = ..., 
                reported_end_time: datetime, 
                reported_start_time: datetime, 
                show_details: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[UsageAggregation]: ...


namespace azure.mgmt.commerce.models

    class azure.mgmt.commerce.models.AggregationGranularity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        HOURLY = "Hourly"


    class azure.mgmt.commerce.models.ErrorObjectResponse(_Model):
        error: Optional[ErrorResponse]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponse] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commerce.models.ErrorResponse(_Model):
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


    class azure.mgmt.commerce.models.MeterInfo(_Model):
        effective_date: Optional[datetime]
        included_quantity: Optional[float]
        meter_category: Optional[str]
        meter_id: Optional[str]
        meter_name: Optional[str]
        meter_rates: Optional[dict[str, float]]
        meter_region: Optional[str]
        meter_sub_category: Optional[str]
        meter_tags: Optional[list[str]]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                effective_date: Optional[datetime] = ..., 
                included_quantity: Optional[float] = ..., 
                meter_category: Optional[str] = ..., 
                meter_id: Optional[str] = ..., 
                meter_name: Optional[str] = ..., 
                meter_rates: Optional[dict[str, float]] = ..., 
                meter_region: Optional[str] = ..., 
                meter_sub_category: Optional[str] = ..., 
                meter_tags: Optional[list[str]] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commerce.models.MonetaryCommitment(OfferTermInfo, discriminator='Monetary Commitment'):
        effective_date: datetime
        excluded_meter_ids: Optional[list[str]]
        name: Literal[OfferTermInfoName.MONETARY_COMMITMENT]
        tiered_discount: Optional[dict[str, Decimal]]

        @overload
        def __init__(
                self, 
                *, 
                effective_date: Optional[datetime] = ..., 
                excluded_meter_ids: Optional[list[str]] = ..., 
                tiered_discount: Optional[dict[str, Decimal]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commerce.models.MonetaryCredit(OfferTermInfo, discriminator='Monetary Credit'):
        credit: Optional[Decimal]
        effective_date: datetime
        excluded_meter_ids: Optional[list[str]]
        name: Literal[OfferTermInfoName.MONETARY_CREDIT]

        @overload
        def __init__(
                self, 
                *, 
                credit: Optional[Decimal] = ..., 
                effective_date: Optional[datetime] = ..., 
                excluded_meter_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commerce.models.OfferTermInfo(_Model):
        effective_date: Optional[datetime]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                effective_date: Optional[datetime] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commerce.models.OfferTermInfoName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONETARY_COMMITMENT = "Monetary Commitment"
        MONETARY_CREDIT = "Monetary Credit"
        RECURRING_CHARGE = "Recurring Charge"


    class azure.mgmt.commerce.models.RecurringCharge(OfferTermInfo, discriminator='Recurring Charge'):
        effective_date: datetime
        name: Literal[OfferTermInfoName.RECURRING_CHARGE]
        recurring_charge: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                effective_date: Optional[datetime] = ..., 
                recurring_charge: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commerce.models.ResourceRateCardInfo(_Model):
        currency: Optional[str]
        is_tax_included: Optional[bool]
        locale: Optional[str]
        meters: Optional[list[MeterInfo]]
        offer_terms: Optional[list[OfferTermInfo]]

        @overload
        def __init__(
                self, 
                *, 
                currency: Optional[str] = ..., 
                is_tax_included: Optional[bool] = ..., 
                locale: Optional[str] = ..., 
                meters: Optional[list[MeterInfo]] = ..., 
                offer_terms: Optional[list[OfferTermInfo]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commerce.models.UsageAggregation(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[UsageSample]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[UsageSample] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.commerce.models.UsageSample(_Model):
        info_fields: Optional[Any]
        instance_data: Optional[str]
        meter_category: Optional[str]
        meter_id: Optional[str]
        meter_name: Optional[str]
        meter_region: Optional[str]
        meter_sub_category: Optional[str]
        quantity: Optional[float]
        subscription_id: Optional[str]
        unit: Optional[str]
        usage_end_time: Optional[datetime]
        usage_start_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                info_fields: Optional[Any] = ..., 
                instance_data: Optional[str] = ..., 
                meter_category: Optional[str] = ..., 
                meter_id: Optional[str] = ..., 
                meter_name: Optional[str] = ..., 
                meter_region: Optional[str] = ..., 
                meter_sub_category: Optional[str] = ..., 
                quantity: Optional[float] = ..., 
                subscription_id: Optional[str] = ..., 
                unit: Optional[str] = ..., 
                usage_end_time: Optional[datetime] = ..., 
                usage_start_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.commerce.operations

    class azure.mgmt.commerce.operations.RateCardOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                *, 
                filter: str, 
                **kwargs: Any
            ) -> ResourceRateCardInfo: ...


    class azure.mgmt.commerce.operations.UsageAggregatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                aggregation_granularity: Union[str, AggregationGranularity] = "Daily", 
                continuation_token_parameter: Optional[str] = ..., 
                reported_end_time: datetime, 
                reported_start_time: datetime, 
                show_details: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ItemPaged[UsageAggregation]: ...


```