```py
namespace azure.mgmt.carbonoptimization

    class azure.mgmt.carbonoptimization.CarbonOptimizationMgmtClient: implements ContextManager 
        carbon_service: CarbonServiceOperations
        operations: Operations

        def __init__(
                self, 
                credential: TokenCredential, 
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


namespace azure.mgmt.carbonoptimization.aio

    class azure.mgmt.carbonoptimization.aio.CarbonOptimizationMgmtClient: implements AsyncContextManager 
        carbon_service: CarbonServiceOperations
        operations: Operations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
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


namespace azure.mgmt.carbonoptimization.aio.operations

    class azure.mgmt.carbonoptimization.aio.operations.CarbonServiceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def query_carbon_emission_data_available_date_range(self, **kwargs: Any) -> CarbonEmissionDataAvailableDateRange: ...

        @overload
        def query_carbon_emission_reports(
                self, 
                query_parameters: QueryFilter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[CarbonEmissionData]: ...

        @overload
        def query_carbon_emission_reports(
                self, 
                query_parameters: QueryFilter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[CarbonEmissionData]: ...

        @overload
        def query_carbon_emission_reports(
                self, 
                query_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[CarbonEmissionData]: ...

        @overload
        def query_carbon_emission_reports_by_billing_account(
                self, 
                scope: str, 
                query_parameters: BillingAccountQueryFilter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[CarbonEmissionData]: ...

        @overload
        def query_carbon_emission_reports_by_billing_account(
                self, 
                scope: str, 
                query_parameters: BillingAccountQueryFilter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[CarbonEmissionData]: ...

        @overload
        def query_carbon_emission_reports_by_billing_account(
                self, 
                scope: str, 
                query_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[CarbonEmissionData]: ...


    class azure.mgmt.carbonoptimization.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.carbonoptimization.models

    class azure.mgmt.carbonoptimization.models.AccessDecisionEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED = "Allowed"
        DENIED = "Denied"


    class azure.mgmt.carbonoptimization.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.carbonoptimization.models.BillingAccountCategoryTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCATION = "Location"
        RESOURCE_TYPE = "ResourceType"
        SUBSCRIPTION = "Subscription"


    class azure.mgmt.carbonoptimization.models.BillingAccountItemDetailsReportQueryFilter(BillingAccountQueryFilter, discriminator='ItemDetailsReport'):
        carbon_scope_list: Union[list[str, EmissionScopeEnum]]
        category_type: Union[str, BillingAccountCategoryTypeEnum]
        date_range: DateRange
        location_list: list[str]
        order_by: Optional[Union[str, BillingAccountOrderByColumnEnum]]
        page_size: int
        report_type: Literal[ReportTypeEnum.ITEM_DETAILS_REPORT]
        resource_type_list: list[str]
        skip_token: Optional[str]
        sort_direction: Optional[Union[str, SortDirectionEnum]]
        subscription_list: list[str]

        @overload
        def __init__(
                self, 
                *, 
                carbon_scope_list: list[Union[str, EmissionScopeEnum]], 
                category_type: Union[str, BillingAccountCategoryTypeEnum], 
                date_range: DateRange, 
                location_list: Optional[list[str]] = ..., 
                order_by: Optional[Union[str, BillingAccountOrderByColumnEnum]] = ..., 
                page_size: int, 
                resource_type_list: Optional[list[str]] = ..., 
                skip_token: Optional[str] = ..., 
                sort_direction: Optional[Union[str, SortDirectionEnum]] = ..., 
                subscription_list: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.BillingAccountMonthlySummaryReportQueryFilter(BillingAccountQueryFilter, discriminator='MonthlySummaryReport'):
        carbon_scope_list: Union[list[str, EmissionScopeEnum]]
        date_range: DateRange
        location_list: list[str]
        report_type: Literal[ReportTypeEnum.MONTHLY_SUMMARY_REPORT]
        resource_type_list: list[str]
        subscription_list: list[str]

        @overload
        def __init__(
                self, 
                *, 
                carbon_scope_list: list[Union[str, EmissionScopeEnum]], 
                date_range: DateRange, 
                location_list: Optional[list[str]] = ..., 
                resource_type_list: Optional[list[str]] = ..., 
                subscription_list: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.BillingAccountOrderByColumnEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ITEM_NAME = "ItemName"
        LATEST_MONTH_EMISSIONS = "LatestMonthEmissions"
        MONTHLY_EMISSIONS_CHANGE_VALUE = "MonthlyEmissionsChangeValue"
        MONTH_OVER_MONTH_EMISSIONS_CHANGE_RATIO = "MonthOverMonthEmissionsChangeRatio"
        PREVIOUS_MONTH_EMISSIONS = "PreviousMonthEmissions"


    class azure.mgmt.carbonoptimization.models.BillingAccountOverallSummaryReportQueryFilter(BillingAccountQueryFilter, discriminator='OverallSummaryReport'):
        carbon_scope_list: Union[list[str, EmissionScopeEnum]]
        date_range: DateRange
        location_list: list[str]
        report_type: Literal[ReportTypeEnum.OVERALL_SUMMARY_REPORT]
        resource_type_list: list[str]
        subscription_list: list[str]

        @overload
        def __init__(
                self, 
                *, 
                carbon_scope_list: list[Union[str, EmissionScopeEnum]], 
                date_range: DateRange, 
                location_list: Optional[list[str]] = ..., 
                resource_type_list: Optional[list[str]] = ..., 
                subscription_list: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.BillingAccountQueryFilter(_Model):
        carbon_scope_list: list[Union[str, EmissionScopeEnum]]
        date_range: DateRange
        location_list: Optional[list[str]]
        report_type: str
        resource_type_list: Optional[list[str]]
        subscription_list: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                carbon_scope_list: list[Union[str, EmissionScopeEnum]], 
                date_range: DateRange, 
                location_list: Optional[list[str]] = ..., 
                report_type: str, 
                resource_type_list: Optional[list[str]] = ..., 
                subscription_list: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.BillingAccountTopItemsMonthlySummaryReportQueryFilter(BillingAccountQueryFilter, discriminator='TopItemsMonthlySummaryReport'):
        carbon_scope_list: Union[list[str, EmissionScopeEnum]]
        category_type: Union[str, BillingAccountCategoryTypeEnum]
        date_range: DateRange
        location_list: list[str]
        report_type: Literal[ReportTypeEnum.TOP_ITEMS_MONTHLY_SUMMARY_REPORT]
        resource_type_list: list[str]
        subscription_list: list[str]
        top_items: int

        @overload
        def __init__(
                self, 
                *, 
                carbon_scope_list: list[Union[str, EmissionScopeEnum]], 
                category_type: Union[str, BillingAccountCategoryTypeEnum], 
                date_range: DateRange, 
                location_list: Optional[list[str]] = ..., 
                resource_type_list: Optional[list[str]] = ..., 
                subscription_list: Optional[list[str]] = ..., 
                top_items: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.BillingAccountTopItemsSummaryReportQueryFilter(BillingAccountQueryFilter, discriminator='TopItemsSummaryReport'):
        carbon_scope_list: Union[list[str, EmissionScopeEnum]]
        category_type: Union[str, BillingAccountCategoryTypeEnum]
        date_range: DateRange
        location_list: list[str]
        report_type: Literal[ReportTypeEnum.TOP_ITEMS_SUMMARY_REPORT]
        resource_type_list: list[str]
        subscription_list: list[str]
        top_items: int

        @overload
        def __init__(
                self, 
                *, 
                carbon_scope_list: list[Union[str, EmissionScopeEnum]], 
                category_type: Union[str, BillingAccountCategoryTypeEnum], 
                date_range: DateRange, 
                location_list: Optional[list[str]] = ..., 
                resource_type_list: Optional[list[str]] = ..., 
                subscription_list: Optional[list[str]] = ..., 
                top_items: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.CarbonEmissionData(_Model):
        data_type: str
        latest_month_emissions: float
        month_over_month_emissions_change_ratio: Optional[float]
        monthly_emissions_change_value: Optional[float]
        previous_month_emissions: float

        @overload
        def __init__(
                self, 
                *, 
                data_type: str, 
                latest_month_emissions: float, 
                month_over_month_emissions_change_ratio: Optional[float] = ..., 
                monthly_emissions_change_value: Optional[float] = ..., 
                previous_month_emissions: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.CarbonEmissionDataAvailableDateRange(_Model):
        end_date: str
        start_date: str

        @overload
        def __init__(
                self, 
                *, 
                end_date: str, 
                start_date: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.CarbonEmissionItemDetailData(CarbonEmissionData, discriminator='ItemDetailsData'):
        category_type: Union[str, CategoryTypeEnum]
        data_type: Literal[ResponseDataTypeEnum.ITEM_DETAILS_DATA]
        item_name: str
        latest_month_emissions: float
        month_over_month_emissions_change_ratio: float
        monthly_emissions_change_value: float
        previous_month_emissions: float

        @overload
        def __init__(
                self, 
                *, 
                category_type: Union[str, CategoryTypeEnum], 
                item_name: str, 
                latest_month_emissions: float, 
                month_over_month_emissions_change_ratio: Optional[float] = ..., 
                monthly_emissions_change_value: Optional[float] = ..., 
                previous_month_emissions: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.CarbonEmissionMonthlySummaryData(CarbonEmissionData, discriminator='MonthlySummaryData'):
        carbon_intensity: float
        data_type: Literal[ResponseDataTypeEnum.MONTHLY_SUMMARY_DATA]
        date: str
        latest_month_emissions: float
        month_over_month_emissions_change_ratio: float
        monthly_emissions_change_value: float
        previous_month_emissions: float

        @overload
        def __init__(
                self, 
                *, 
                carbon_intensity: float, 
                date: str, 
                latest_month_emissions: float, 
                month_over_month_emissions_change_ratio: Optional[float] = ..., 
                monthly_emissions_change_value: Optional[float] = ..., 
                previous_month_emissions: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.CarbonEmissionOverallSummaryData(CarbonEmissionData, discriminator='OverallSummaryData'):
        data_type: Literal[ResponseDataTypeEnum.OVERALL_SUMMARY_DATA]
        latest_month_emissions: float
        month_over_month_emissions_change_ratio: float
        monthly_emissions_change_value: float
        previous_month_emissions: float

        @overload
        def __init__(
                self, 
                *, 
                latest_month_emissions: float, 
                month_over_month_emissions_change_ratio: Optional[float] = ..., 
                monthly_emissions_change_value: Optional[float] = ..., 
                previous_month_emissions: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.CarbonEmissionTopItemMonthlySummaryData(CarbonEmissionData, discriminator='TopItemsMonthlySummaryData'):
        category_type: Union[str, CategoryTypeEnum]
        data_type: Literal[ResponseDataTypeEnum.TOP_ITEMS_MONTHLY_SUMMARY_DATA]
        date: str
        item_name: str
        latest_month_emissions: float
        month_over_month_emissions_change_ratio: float
        monthly_emissions_change_value: float
        previous_month_emissions: float

        @overload
        def __init__(
                self, 
                *, 
                category_type: Union[str, CategoryTypeEnum], 
                date: str, 
                item_name: str, 
                latest_month_emissions: float, 
                month_over_month_emissions_change_ratio: Optional[float] = ..., 
                monthly_emissions_change_value: Optional[float] = ..., 
                previous_month_emissions: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.CarbonEmissionTopItemsSummaryData(CarbonEmissionData, discriminator='TopItemsSummaryData'):
        category_type: Union[str, CategoryTypeEnum]
        data_type: Literal[ResponseDataTypeEnum.TOP_ITEMS_SUMMARY_DATA]
        item_name: str
        latest_month_emissions: float
        month_over_month_emissions_change_ratio: float
        monthly_emissions_change_value: float
        previous_month_emissions: float

        @overload
        def __init__(
                self, 
                *, 
                category_type: Union[str, CategoryTypeEnum], 
                item_name: str, 
                latest_month_emissions: float, 
                month_over_month_emissions_change_ratio: Optional[float] = ..., 
                monthly_emissions_change_value: Optional[float] = ..., 
                previous_month_emissions: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.CategoryTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCATION = "Location"
        RESOURCE = "Resource"
        RESOURCE_GROUP = "ResourceGroup"
        RESOURCE_TYPE = "ResourceType"
        SUBSCRIPTION = "Subscription"


    class azure.mgmt.carbonoptimization.models.DateRange(_Model):
        end: date
        start: date

        @overload
        def __init__(
                self, 
                *, 
                end: date, 
                start: date
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.EmissionScopeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SCOPE1 = "Scope1"
        SCOPE2 = "Scope2"
        SCOPE3 = "Scope3"


    class azure.mgmt.carbonoptimization.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.carbonoptimization.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.carbonoptimization.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.ItemDetailsQueryFilter(QueryFilter, discriminator='ItemDetailsReport'):
        carbon_scope_list: Union[list[str, EmissionScopeEnum]]
        category_type: Union[str, CategoryTypeEnum]
        date_range: DateRange
        location_list: list[str]
        order_by: Union[str, OrderByColumnEnum]
        page_size: int
        report_type: Literal[ReportTypeEnum.ITEM_DETAILS_REPORT]
        resource_group_url_list: list[str]
        resource_type_list: list[str]
        skip_token: Optional[str]
        sort_direction: Union[str, SortDirectionEnum]
        subscription_list: list[str]

        @overload
        def __init__(
                self, 
                *, 
                carbon_scope_list: list[Union[str, EmissionScopeEnum]], 
                category_type: Union[str, CategoryTypeEnum], 
                date_range: DateRange, 
                location_list: Optional[list[str]] = ..., 
                order_by: Union[str, OrderByColumnEnum], 
                page_size: int, 
                resource_group_url_list: Optional[list[str]] = ..., 
                resource_type_list: Optional[list[str]] = ..., 
                skip_token: Optional[str] = ..., 
                sort_direction: Union[str, SortDirectionEnum], 
                subscription_list: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.MonthlySummaryReportQueryFilter(QueryFilter, discriminator='MonthlySummaryReport'):
        carbon_scope_list: Union[list[str, EmissionScopeEnum]]
        date_range: DateRange
        location_list: list[str]
        report_type: Literal[ReportTypeEnum.MONTHLY_SUMMARY_REPORT]
        resource_group_url_list: list[str]
        resource_type_list: list[str]
        subscription_list: list[str]

        @overload
        def __init__(
                self, 
                *, 
                carbon_scope_list: list[Union[str, EmissionScopeEnum]], 
                date_range: DateRange, 
                location_list: Optional[list[str]] = ..., 
                resource_group_url_list: Optional[list[str]] = ..., 
                resource_type_list: Optional[list[str]] = ..., 
                subscription_list: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.Operation(_Model):
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


    class azure.mgmt.carbonoptimization.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.carbonoptimization.models.OrderByColumnEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ITEM_NAME = "ItemName"
        LATEST_MONTH_EMISSIONS = "LatestMonthEmissions"
        MONTHLY_EMISSIONS_CHANGE_VALUE = "MonthlyEmissionsChangeValue"
        MONTH_OVER_MONTH_EMISSIONS_CHANGE_RATIO = "MonthOverMonthEmissionsChangeRatio"
        PREVIOUS_MONTH_EMISSIONS = "PreviousMonthEmissions"
        RESOURCE_GROUP = "ResourceGroup"


    class azure.mgmt.carbonoptimization.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.carbonoptimization.models.OverallSummaryReportQueryFilter(QueryFilter, discriminator='OverallSummaryReport'):
        carbon_scope_list: Union[list[str, EmissionScopeEnum]]
        date_range: DateRange
        location_list: list[str]
        report_type: Literal[ReportTypeEnum.OVERALL_SUMMARY_REPORT]
        resource_group_url_list: list[str]
        resource_type_list: list[str]
        subscription_list: list[str]

        @overload
        def __init__(
                self, 
                *, 
                carbon_scope_list: list[Union[str, EmissionScopeEnum]], 
                date_range: DateRange, 
                location_list: Optional[list[str]] = ..., 
                resource_group_url_list: Optional[list[str]] = ..., 
                resource_type_list: Optional[list[str]] = ..., 
                subscription_list: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.QueryFilter(_Model):
        carbon_scope_list: list[Union[str, EmissionScopeEnum]]
        date_range: DateRange
        location_list: Optional[list[str]]
        report_type: str
        resource_group_url_list: Optional[list[str]]
        resource_type_list: Optional[list[str]]
        subscription_list: list[str]

        @overload
        def __init__(
                self, 
                *, 
                carbon_scope_list: list[Union[str, EmissionScopeEnum]], 
                date_range: DateRange, 
                location_list: Optional[list[str]] = ..., 
                report_type: str, 
                resource_group_url_list: Optional[list[str]] = ..., 
                resource_type_list: Optional[list[str]] = ..., 
                subscription_list: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.ReportTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ITEM_DETAILS_REPORT = "ItemDetailsReport"
        MONTHLY_SUMMARY_REPORT = "MonthlySummaryReport"
        OVERALL_SUMMARY_REPORT = "OverallSummaryReport"
        TOP_ITEMS_MONTHLY_SUMMARY_REPORT = "TopItemsMonthlySummaryReport"
        TOP_ITEMS_SUMMARY_REPORT = "TopItemsSummaryReport"


    class azure.mgmt.carbonoptimization.models.ResourceCarbonEmissionItemDetailData(CarbonEmissionData, discriminator='ResourceItemDetailsData'):
        category_type: Union[str, CategoryTypeEnum]
        data_type: Literal[ResponseDataTypeEnum.RESOURCE_ITEM_DETAILS_DATA]
        item_name: str
        latest_month_emissions: float
        location: Optional[str]
        month_over_month_emissions_change_ratio: float
        monthly_emissions_change_value: float
        previous_month_emissions: float
        resource_group: str
        resource_id: str
        resource_type: Optional[str]
        subscription_id: str

        @overload
        def __init__(
                self, 
                *, 
                category_type: Union[str, CategoryTypeEnum], 
                item_name: str, 
                latest_month_emissions: float, 
                location: Optional[str] = ..., 
                month_over_month_emissions_change_ratio: Optional[float] = ..., 
                monthly_emissions_change_value: Optional[float] = ..., 
                previous_month_emissions: float, 
                resource_group: str, 
                resource_id: str, 
                resource_type: Optional[str] = ..., 
                subscription_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.ResourceCarbonEmissionTopItemMonthlySummaryData(CarbonEmissionData, discriminator='ResourceTopItemsMonthlySummaryData'):
        category_type: Union[str, CategoryTypeEnum]
        data_type: Literal[ResponseDataTypeEnum.RESOURCE_TOP_ITEMS_MONTHLY_SUMMARY_DATA]
        date: str
        item_name: str
        latest_month_emissions: float
        month_over_month_emissions_change_ratio: float
        monthly_emissions_change_value: float
        previous_month_emissions: float
        resource_group: str
        resource_id: str
        subscription_id: str

        @overload
        def __init__(
                self, 
                *, 
                category_type: Union[str, CategoryTypeEnum], 
                date: str, 
                item_name: str, 
                latest_month_emissions: float, 
                month_over_month_emissions_change_ratio: Optional[float] = ..., 
                monthly_emissions_change_value: Optional[float] = ..., 
                previous_month_emissions: float, 
                resource_group: str, 
                resource_id: str, 
                subscription_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.ResourceCarbonEmissionTopItemsSummaryData(CarbonEmissionData, discriminator='ResourceTopItemsSummaryData'):
        category_type: Union[str, CategoryTypeEnum]
        data_type: Literal[ResponseDataTypeEnum.RESOURCE_TOP_ITEMS_SUMMARY_DATA]
        item_name: str
        latest_month_emissions: float
        month_over_month_emissions_change_ratio: float
        monthly_emissions_change_value: float
        previous_month_emissions: float
        resource_group: str
        resource_id: str
        subscription_id: str

        @overload
        def __init__(
                self, 
                *, 
                category_type: Union[str, CategoryTypeEnum], 
                item_name: str, 
                latest_month_emissions: float, 
                month_over_month_emissions_change_ratio: Optional[float] = ..., 
                monthly_emissions_change_value: Optional[float] = ..., 
                previous_month_emissions: float, 
                resource_group: str, 
                resource_id: str, 
                subscription_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.ResourceGroupCarbonEmissionItemDetailData(CarbonEmissionData, discriminator='ResourceGroupItemDetailsData'):
        category_type: Union[str, CategoryTypeEnum]
        data_type: Literal[ResponseDataTypeEnum.RESOURCE_GROUP_ITEM_DETAILS_DATA]
        item_name: str
        latest_month_emissions: float
        month_over_month_emissions_change_ratio: float
        monthly_emissions_change_value: float
        previous_month_emissions: float
        resource_group_url: str
        subscription_id: str

        @overload
        def __init__(
                self, 
                *, 
                category_type: Union[str, CategoryTypeEnum], 
                item_name: str, 
                latest_month_emissions: float, 
                month_over_month_emissions_change_ratio: Optional[float] = ..., 
                monthly_emissions_change_value: Optional[float] = ..., 
                previous_month_emissions: float, 
                resource_group_url: str, 
                subscription_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.ResourceGroupCarbonEmissionTopItemMonthlySummaryData(CarbonEmissionData, discriminator='ResourceGroupTopItemsMonthlySummaryData'):
        category_type: Union[str, CategoryTypeEnum]
        data_type: Literal[ResponseDataTypeEnum.RESOURCE_GROUP_TOP_ITEMS_MONTHLY_SUMMARY_DATA]
        date: str
        item_name: str
        latest_month_emissions: float
        month_over_month_emissions_change_ratio: float
        monthly_emissions_change_value: float
        previous_month_emissions: float
        resource_group_url: str
        subscription_id: str

        @overload
        def __init__(
                self, 
                *, 
                category_type: Union[str, CategoryTypeEnum], 
                date: str, 
                item_name: str, 
                latest_month_emissions: float, 
                month_over_month_emissions_change_ratio: Optional[float] = ..., 
                monthly_emissions_change_value: Optional[float] = ..., 
                previous_month_emissions: float, 
                resource_group_url: str, 
                subscription_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.ResourceGroupCarbonEmissionTopItemsSummaryData(CarbonEmissionData, discriminator='ResourceGroupTopItemsSummaryData'):
        category_type: Union[str, CategoryTypeEnum]
        data_type: Literal[ResponseDataTypeEnum.RESOURCE_GROUP_TOP_ITEMS_SUMMARY_DATA]
        item_name: str
        latest_month_emissions: float
        month_over_month_emissions_change_ratio: float
        monthly_emissions_change_value: float
        previous_month_emissions: float
        resource_group_url: str
        subscription_id: str

        @overload
        def __init__(
                self, 
                *, 
                category_type: Union[str, CategoryTypeEnum], 
                item_name: str, 
                latest_month_emissions: float, 
                month_over_month_emissions_change_ratio: Optional[float] = ..., 
                monthly_emissions_change_value: Optional[float] = ..., 
                previous_month_emissions: float, 
                resource_group_url: str, 
                subscription_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.ResponseDataTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ITEM_DETAILS_DATA = "ItemDetailsData"
        MONTHLY_SUMMARY_DATA = "MonthlySummaryData"
        OVERALL_SUMMARY_DATA = "OverallSummaryData"
        RESOURCE_GROUP_ITEM_DETAILS_DATA = "ResourceGroupItemDetailsData"
        RESOURCE_GROUP_TOP_ITEMS_MONTHLY_SUMMARY_DATA = "ResourceGroupTopItemsMonthlySummaryData"
        RESOURCE_GROUP_TOP_ITEMS_SUMMARY_DATA = "ResourceGroupTopItemsSummaryData"
        RESOURCE_ITEM_DETAILS_DATA = "ResourceItemDetailsData"
        RESOURCE_TOP_ITEMS_MONTHLY_SUMMARY_DATA = "ResourceTopItemsMonthlySummaryData"
        RESOURCE_TOP_ITEMS_SUMMARY_DATA = "ResourceTopItemsSummaryData"
        TOP_ITEMS_MONTHLY_SUMMARY_DATA = "TopItemsMonthlySummaryData"
        TOP_ITEMS_SUMMARY_DATA = "TopItemsSummaryData"


    class azure.mgmt.carbonoptimization.models.SortDirectionEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASC = "Asc"
        DESC = "Desc"


    class azure.mgmt.carbonoptimization.models.SubscriptionAccessDecision(_Model):
        decision: Union[str, AccessDecisionEnum]
        denial_reason: Optional[str]
        subscription_id: str

        @overload
        def __init__(
                self, 
                *, 
                decision: Union[str, AccessDecisionEnum], 
                denial_reason: Optional[str] = ..., 
                subscription_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.TopItemsMonthlySummaryReportQueryFilter(QueryFilter, discriminator='TopItemsMonthlySummaryReport'):
        carbon_scope_list: Union[list[str, EmissionScopeEnum]]
        category_type: Union[str, CategoryTypeEnum]
        date_range: DateRange
        location_list: list[str]
        report_type: Literal[ReportTypeEnum.TOP_ITEMS_MONTHLY_SUMMARY_REPORT]
        resource_group_url_list: list[str]
        resource_type_list: list[str]
        subscription_list: list[str]
        top_items: int

        @overload
        def __init__(
                self, 
                *, 
                carbon_scope_list: list[Union[str, EmissionScopeEnum]], 
                category_type: Union[str, CategoryTypeEnum], 
                date_range: DateRange, 
                location_list: Optional[list[str]] = ..., 
                resource_group_url_list: Optional[list[str]] = ..., 
                resource_type_list: Optional[list[str]] = ..., 
                subscription_list: list[str], 
                top_items: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.carbonoptimization.models.TopItemsSummaryReportQueryFilter(QueryFilter, discriminator='TopItemsSummaryReport'):
        carbon_scope_list: Union[list[str, EmissionScopeEnum]]
        category_type: Union[str, CategoryTypeEnum]
        date_range: DateRange
        location_list: list[str]
        report_type: Literal[ReportTypeEnum.TOP_ITEMS_SUMMARY_REPORT]
        resource_group_url_list: list[str]
        resource_type_list: list[str]
        subscription_list: list[str]
        top_items: int

        @overload
        def __init__(
                self, 
                *, 
                carbon_scope_list: list[Union[str, EmissionScopeEnum]], 
                category_type: Union[str, CategoryTypeEnum], 
                date_range: DateRange, 
                location_list: Optional[list[str]] = ..., 
                resource_group_url_list: Optional[list[str]] = ..., 
                resource_type_list: Optional[list[str]] = ..., 
                subscription_list: list[str], 
                top_items: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.carbonoptimization.operations

    class azure.mgmt.carbonoptimization.operations.CarbonServiceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def query_carbon_emission_data_available_date_range(self, **kwargs: Any) -> CarbonEmissionDataAvailableDateRange: ...

        @overload
        def query_carbon_emission_reports(
                self, 
                query_parameters: QueryFilter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[CarbonEmissionData]: ...

        @overload
        def query_carbon_emission_reports(
                self, 
                query_parameters: QueryFilter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[CarbonEmissionData]: ...

        @overload
        def query_carbon_emission_reports(
                self, 
                query_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[CarbonEmissionData]: ...

        @overload
        def query_carbon_emission_reports_by_billing_account(
                self, 
                scope: str, 
                query_parameters: BillingAccountQueryFilter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[CarbonEmissionData]: ...

        @overload
        def query_carbon_emission_reports_by_billing_account(
                self, 
                scope: str, 
                query_parameters: BillingAccountQueryFilter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[CarbonEmissionData]: ...

        @overload
        def query_carbon_emission_reports_by_billing_account(
                self, 
                scope: str, 
                query_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[CarbonEmissionData]: ...


    class azure.mgmt.carbonoptimization.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


namespace azure.mgmt.carbonoptimization.types

    class azure.mgmt.carbonoptimization.types.BillingAccountItemDetailsReportQueryFilter(TypedDict, total=False):
        key "carbonScopeList": Required[list[Union[str, EmissionScopeEnum]]]
        key "categoryType": Required[Union[str, BillingAccountCategoryTypeEnum]]
        key "dateRange": Required[DateRange]
        key "orderBy": Union[str, BillingAccountOrderByColumnEnum]
        key "pageSize": Required[int]
        key "reportType": Required[Literal[ReportTypeEnum.ITEM_DETAILS_REPORT]]
        key "skipToken": str
        key "sortDirection": Union[str, SortDirectionEnum]
        carbonScopeList: list[Union[str, EmissionScopeEnum]]
        categoryType: Union[str, BillingAccountCategoryTypeEnum]
        dateRange: DateRange
        locationList: list[str]
        orderBy: Union[str, BillingAccountOrderByColumnEnum]
        pageSize: int
        reportType: Literal[ReportTypeEnum.ITEM_DETAILS_REPORT]
        resourceTypeList: list[str]
        skipToken: str
        sortDirection: Union[str, SortDirectionEnum]
        subscriptionList: list[str]


    class azure.mgmt.carbonoptimization.types.BillingAccountMonthlySummaryReportQueryFilter(TypedDict, total=False):
        key "carbonScopeList": Required[list[Union[str, EmissionScopeEnum]]]
        key "dateRange": Required[DateRange]
        key "reportType": Required[Literal[ReportTypeEnum.MONTHLY_SUMMARY_REPORT]]
        carbonScopeList: list[Union[str, EmissionScopeEnum]]
        dateRange: DateRange
        locationList: list[str]
        reportType: Literal[ReportTypeEnum.MONTHLY_SUMMARY_REPORT]
        resourceTypeList: list[str]
        subscriptionList: list[str]


    class azure.mgmt.carbonoptimization.types.BillingAccountOverallSummaryReportQueryFilter(TypedDict, total=False):
        key "carbonScopeList": Required[list[Union[str, EmissionScopeEnum]]]
        key "dateRange": Required[DateRange]
        key "reportType": Required[Literal[ReportTypeEnum.OVERALL_SUMMARY_REPORT]]
        carbonScopeList: list[Union[str, EmissionScopeEnum]]
        dateRange: DateRange
        locationList: list[str]
        reportType: Literal[ReportTypeEnum.OVERALL_SUMMARY_REPORT]
        resourceTypeList: list[str]
        subscriptionList: list[str]


    class azure.mgmt.carbonoptimization.types.BillingAccountTopItemsMonthlySummaryReportQueryFilter(TypedDict, total=False):
        key "carbonScopeList": Required[list[Union[str, EmissionScopeEnum]]]
        key "categoryType": Required[Union[str, BillingAccountCategoryTypeEnum]]
        key "dateRange": Required[DateRange]
        key "reportType": Required[Literal[ReportTypeEnum.TOP_ITEMS_MONTHLY_SUMMARY_REPORT]]
        key "topItems": Required[int]
        carbonScopeList: list[Union[str, EmissionScopeEnum]]
        categoryType: Union[str, BillingAccountCategoryTypeEnum]
        dateRange: DateRange
        locationList: list[str]
        reportType: Literal[ReportTypeEnum.TOP_ITEMS_MONTHLY_SUMMARY_REPORT]
        resourceTypeList: list[str]
        subscriptionList: list[str]
        topItems: int


    class azure.mgmt.carbonoptimization.types.BillingAccountTopItemsSummaryReportQueryFilter(TypedDict, total=False):
        key "carbonScopeList": Required[list[Union[str, EmissionScopeEnum]]]
        key "categoryType": Required[Union[str, BillingAccountCategoryTypeEnum]]
        key "dateRange": Required[DateRange]
        key "reportType": Required[Literal[ReportTypeEnum.TOP_ITEMS_SUMMARY_REPORT]]
        key "topItems": Required[int]
        carbonScopeList: list[Union[str, EmissionScopeEnum]]
        categoryType: Union[str, BillingAccountCategoryTypeEnum]
        dateRange: DateRange
        locationList: list[str]
        reportType: Literal[ReportTypeEnum.TOP_ITEMS_SUMMARY_REPORT]
        resourceTypeList: list[str]
        subscriptionList: list[str]
        topItems: int


    class azure.mgmt.carbonoptimization.types.DateRange(TypedDict, total=False):
        key "end": Required[str]
        key "start": Required[str]
        end: str
        start: str


    class azure.mgmt.carbonoptimization.types.ItemDetailsQueryFilter(TypedDict, total=False):
        key "carbonScopeList": Required[list[Union[str, EmissionScopeEnum]]]
        key "categoryType": Required[Union[str, CategoryTypeEnum]]
        key "dateRange": Required[DateRange]
        key "orderBy": Required[Union[str, OrderByColumnEnum]]
        key "pageSize": Required[int]
        key "reportType": Required[Literal[ReportTypeEnum.ITEM_DETAILS_REPORT]]
        key "skipToken": str
        key "sortDirection": Required[Union[str, SortDirectionEnum]]
        key "subscriptionList": Required[list[str]]
        carbonScopeList: list[Union[str, EmissionScopeEnum]]
        categoryType: Union[str, CategoryTypeEnum]
        dateRange: DateRange
        locationList: list[str]
        orderBy: Union[str, OrderByColumnEnum]
        pageSize: int
        reportType: Literal[ReportTypeEnum.ITEM_DETAILS_REPORT]
        resourceGroupUrlList: list[str]
        resourceTypeList: list[str]
        skipToken: str
        sortDirection: Union[str, SortDirectionEnum]
        subscriptionList: list[str]


    class azure.mgmt.carbonoptimization.types.MonthlySummaryReportQueryFilter(TypedDict, total=False):
        key "carbonScopeList": Required[list[Union[str, EmissionScopeEnum]]]
        key "dateRange": Required[DateRange]
        key "reportType": Required[Literal[ReportTypeEnum.MONTHLY_SUMMARY_REPORT]]
        key "subscriptionList": Required[list[str]]
        carbonScopeList: list[Union[str, EmissionScopeEnum]]
        dateRange: DateRange
        locationList: list[str]
        reportType: Literal[ReportTypeEnum.MONTHLY_SUMMARY_REPORT]
        resourceGroupUrlList: list[str]
        resourceTypeList: list[str]
        subscriptionList: list[str]


    class azure.mgmt.carbonoptimization.types.OverallSummaryReportQueryFilter(TypedDict, total=False):
        key "carbonScopeList": Required[list[Union[str, EmissionScopeEnum]]]
        key "dateRange": Required[DateRange]
        key "reportType": Required[Literal[ReportTypeEnum.OVERALL_SUMMARY_REPORT]]
        key "subscriptionList": Required[list[str]]
        carbonScopeList: list[Union[str, EmissionScopeEnum]]
        dateRange: DateRange
        locationList: list[str]
        reportType: Literal[ReportTypeEnum.OVERALL_SUMMARY_REPORT]
        resourceGroupUrlList: list[str]
        resourceTypeList: list[str]
        subscriptionList: list[str]


    class azure.mgmt.carbonoptimization.types.ReportTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ITEM_DETAILS_REPORT = "ItemDetailsReport"
        MONTHLY_SUMMARY_REPORT = "MonthlySummaryReport"
        OVERALL_SUMMARY_REPORT = "OverallSummaryReport"
        TOP_ITEMS_MONTHLY_SUMMARY_REPORT = "TopItemsMonthlySummaryReport"
        TOP_ITEMS_SUMMARY_REPORT = "TopItemsSummaryReport"


    class azure.mgmt.carbonoptimization.types.TopItemsMonthlySummaryReportQueryFilter(TypedDict, total=False):
        key "carbonScopeList": Required[list[Union[str, EmissionScopeEnum]]]
        key "categoryType": Required[Union[str, CategoryTypeEnum]]
        key "dateRange": Required[DateRange]
        key "reportType": Required[Literal[ReportTypeEnum.TOP_ITEMS_MONTHLY_SUMMARY_REPORT]]
        key "subscriptionList": Required[list[str]]
        key "topItems": Required[int]
        carbonScopeList: list[Union[str, EmissionScopeEnum]]
        categoryType: Union[str, CategoryTypeEnum]
        dateRange: DateRange
        locationList: list[str]
        reportType: Literal[ReportTypeEnum.TOP_ITEMS_MONTHLY_SUMMARY_REPORT]
        resourceGroupUrlList: list[str]
        resourceTypeList: list[str]
        subscriptionList: list[str]
        topItems: int


    class azure.mgmt.carbonoptimization.types.TopItemsSummaryReportQueryFilter(TypedDict, total=False):
        key "carbonScopeList": Required[list[Union[str, EmissionScopeEnum]]]
        key "categoryType": Required[Union[str, CategoryTypeEnum]]
        key "dateRange": Required[DateRange]
        key "reportType": Required[Literal[ReportTypeEnum.TOP_ITEMS_SUMMARY_REPORT]]
        key "subscriptionList": Required[list[str]]
        key "topItems": Required[int]
        carbonScopeList: list[Union[str, EmissionScopeEnum]]
        categoryType: Union[str, CategoryTypeEnum]
        dateRange: DateRange
        locationList: list[str]
        reportType: Literal[ReportTypeEnum.TOP_ITEMS_SUMMARY_REPORT]
        resourceGroupUrlList: list[str]
        resourceTypeList: list[str]
        subscriptionList: list[str]
        topItems: int


```