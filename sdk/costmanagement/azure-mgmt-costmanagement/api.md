```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.costmanagement

    class azure.mgmt.costmanagement.CostManagementClient: implements ContextManager 
        alerts: AlertsOperations
        benefit_recommendations: BenefitRecommendationsOperations
        benefit_utilization_summaries: BenefitUtilizationSummariesOperations
        dimensions: DimensionsOperations
        exports: ExportsOperations
        forecast: ForecastOperations
        generate_cost_details_report: GenerateCostDetailsReportOperations
        generate_detailed_cost_report: GenerateDetailedCostReportOperations
        generate_detailed_cost_report_operation_results: GenerateDetailedCostReportOperationResultsOperations
        generate_detailed_cost_report_operation_status: GenerateDetailedCostReportOperationStatusOperations
        generate_reservation_details_report: GenerateReservationDetailsReportOperations
        operations: Operations
        price_sheet: PriceSheetOperations
        query: QueryOperations
        scheduled_actions: ScheduledActionsOperations
        views: ViewsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.costmanagement.aio

    class azure.mgmt.costmanagement.aio.CostManagementClient: implements AsyncContextManager 
        alerts: AlertsOperations
        benefit_recommendations: BenefitRecommendationsOperations
        benefit_utilization_summaries: BenefitUtilizationSummariesOperations
        dimensions: DimensionsOperations
        exports: ExportsOperations
        forecast: ForecastOperations
        generate_cost_details_report: GenerateCostDetailsReportOperations
        generate_detailed_cost_report: GenerateDetailedCostReportOperations
        generate_detailed_cost_report_operation_results: GenerateDetailedCostReportOperationResultsOperations
        generate_detailed_cost_report_operation_status: GenerateDetailedCostReportOperationStatusOperations
        generate_reservation_details_report: GenerateReservationDetailsReportOperations
        operations: Operations
        price_sheet: PriceSheetOperations
        query: QueryOperations
        scheduled_actions: ScheduledActionsOperations
        views: ViewsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


namespace azure.mgmt.costmanagement.aio.operations

    class azure.mgmt.costmanagement.aio.operations.AlertsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def dismiss(
                self, 
                scope: str, 
                alert_id: str, 
                parameters: DismissAlertPayload, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Alert: ...

        @overload
        async def dismiss(
                self, 
                scope: str, 
                alert_id: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                alert_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace_async
        async def list(
                self, 
                scope: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AlertsResult: ...

        @distributed_trace_async
        async def list_external(
                self, 
                external_cloud_provider_type: Union[str, ExternalCloudProviderType], 
                external_cloud_provider_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AlertsResult: ...


    class azure.mgmt.costmanagement.aio.operations.BenefitRecommendationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                billing_scope: str, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                expand: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[BenefitRecommendationModel]: ...


    class azure.mgmt.costmanagement.aio.operations.BenefitUtilizationSummariesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_billing_account_id(
                self, 
                billing_account_id: str, 
                grain_parameter: Optional[Union[str, GrainParameter]] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[BenefitUtilizationSummary]: ...

        @distributed_trace
        def list_by_billing_profile_id(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                grain_parameter: Optional[Union[str, GrainParameter]] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[BenefitUtilizationSummary]: ...

        @distributed_trace
        def list_by_savings_plan_id(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                filter: Optional[str] = None, 
                grain_parameter: Optional[Union[str, GrainParameter]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[BenefitUtilizationSummary]: ...

        @distributed_trace
        def list_by_savings_plan_order(
                self, 
                savings_plan_order_id: str, 
                filter: Optional[str] = None, 
                grain_parameter: Optional[Union[str, GrainParameter]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[BenefitUtilizationSummary]: ...


    class azure.mgmt.costmanagement.aio.operations.DimensionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def by_external_cloud_provider_type(
                self, 
                external_cloud_provider_type: Union[str, ExternalCloudProviderType], 
                external_cloud_provider_id: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                skiptoken: Optional[str] = None, 
                top: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Dimension]: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                skiptoken: Optional[str] = None, 
                top: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Dimension]: ...


    class azure.mgmt.costmanagement.aio.operations.ExportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                export_name: str, 
                parameters: Export, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Export: ...

        @overload
        async def create_or_update(
                self, 
                scope: str, 
                export_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Export: ...

        @distributed_trace_async
        async def delete(
                self, 
                scope: str, 
                export_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def execute(
                self, 
                scope: str, 
                export_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                export_name: str, 
                expand: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Export: ...

        @distributed_trace_async
        async def get_execution_history(
                self, 
                scope: str, 
                export_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ExportExecutionListResult: ...

        @distributed_trace_async
        async def list(
                self, 
                scope: str, 
                expand: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ExportListResult: ...


    class azure.mgmt.costmanagement.aio.operations.ForecastOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def external_cloud_provider_usage(
                self, 
                external_cloud_provider_type: Union[str, ExternalCloudProviderType], 
                external_cloud_provider_id: str, 
                parameters: ForecastDefinition, 
                filter: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ForecastResult: ...

        @overload
        async def external_cloud_provider_usage(
                self, 
                external_cloud_provider_type: Union[str, ExternalCloudProviderType], 
                external_cloud_provider_id: str, 
                parameters: IO, 
                filter: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ForecastResult: ...

        @overload
        async def usage(
                self, 
                scope: str, 
                parameters: ForecastDefinition, 
                filter: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[ForecastResult]: ...

        @overload
        async def usage(
                self, 
                scope: str, 
                parameters: IO, 
                filter: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[ForecastResult]: ...


    class azure.mgmt.costmanagement.aio.operations.GenerateCostDetailsReportOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_operation(
                self, 
                scope: str, 
                parameters: GenerateCostDetailsReportRequestDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CostDetailsOperationResults]: ...

        @overload
        async def begin_create_operation(
                self, 
                scope: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CostDetailsOperationResults]: ...

        @distributed_trace_async
        async def begin_get_operation_results(
                self, 
                scope: str, 
                operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[CostDetailsOperationResults]: ...


    class azure.mgmt.costmanagement.aio.operations.GenerateDetailedCostReportOperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_get(
                self, 
                operation_id: str, 
                scope: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[GenerateDetailedCostReportOperationResult]: ...


    class azure.mgmt.costmanagement.aio.operations.GenerateDetailedCostReportOperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                operation_id: str, 
                scope: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GenerateDetailedCostReportOperationStatuses: ...


    class azure.mgmt.costmanagement.aio.operations.GenerateDetailedCostReportOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_operation(
                self, 
                scope: str, 
                parameters: GenerateDetailedCostReportDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GenerateDetailedCostReportOperationResult]: ...

        @overload
        async def begin_create_operation(
                self, 
                scope: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GenerateDetailedCostReportOperationResult]: ...


    class azure.mgmt.costmanagement.aio.operations.GenerateReservationDetailsReportOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_by_billing_account_id(
                self, 
                billing_account_id: str, 
                start_date: str, 
                end_date: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatus]: ...

        @distributed_trace_async
        async def begin_by_billing_profile_id(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                start_date: str, 
                end_date: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatus]: ...


    class azure.mgmt.costmanagement.aio.operations.Operations:

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
            ) -> AsyncIterable[CostManagementOperation]: ...


    class azure.mgmt.costmanagement.aio.operations.PriceSheetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_download(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DownloadURL]: ...

        @distributed_trace_async
        async def begin_download_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DownloadURL]: ...


    class azure.mgmt.costmanagement.aio.operations.QueryOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def usage(
                self, 
                scope: str, 
                parameters: QueryDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[QueryResult]: ...

        @overload
        async def usage(
                self, 
                scope: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[QueryResult]: ...

        @overload
        async def usage_by_external_cloud_provider_type(
                self, 
                external_cloud_provider_type: Union[str, ExternalCloudProviderType], 
                external_cloud_provider_id: str, 
                parameters: QueryDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryResult: ...

        @overload
        async def usage_by_external_cloud_provider_type(
                self, 
                external_cloud_provider_type: Union[str, ExternalCloudProviderType], 
                external_cloud_provider_id: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryResult: ...


    class azure.mgmt.costmanagement.aio.operations.ScheduledActionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def check_name_availability(
                self, 
                check_name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                check_name_availability_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability_by_scope(
                self, 
                scope: str, 
                check_name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability_by_scope(
                self, 
                scope: str, 
                check_name_availability_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def create_or_update(
                self, 
                name: str, 
                scheduled_action: ScheduledAction, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @overload
        async def create_or_update(
                self, 
                name: str, 
                scheduled_action: IO, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @overload
        async def create_or_update_by_scope(
                self, 
                scope: str, 
                name: str, 
                scheduled_action: ScheduledAction, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @overload
        async def create_or_update_by_scope(
                self, 
                scope: str, 
                name: str, 
                scheduled_action: IO, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @distributed_trace_async
        async def delete(
                self, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_by_scope(
                self, 
                scope: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @distributed_trace_async
        async def get_by_scope(
                self, 
                scope: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ScheduledAction]: ...

        @distributed_trace
        def list_by_scope(
                self, 
                scope: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ScheduledAction]: ...

        @distributed_trace_async
        async def run(
                self, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def run_by_scope(
                self, 
                scope: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.costmanagement.aio.operations.ViewsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                view_name: str, 
                parameters: View, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> View: ...

        @overload
        async def create_or_update(
                self, 
                view_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> View: ...

        @overload
        async def create_or_update_by_scope(
                self, 
                scope: str, 
                view_name: str, 
                parameters: View, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> View: ...

        @overload
        async def create_or_update_by_scope(
                self, 
                scope: str, 
                view_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> View: ...

        @distributed_trace_async
        async def delete(
                self, 
                view_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_by_scope(
                self, 
                scope: str, 
                view_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                view_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> View: ...

        @distributed_trace_async
        async def get_by_scope(
                self, 
                scope: str, 
                view_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> View: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[View]: ...

        @distributed_trace
        def list_by_scope(
                self, 
                scope: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[View]: ...


namespace azure.mgmt.costmanagement.models

    class azure.mgmt.costmanagement.models.AccumulatedType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "false"
        TRUE = "true"


    class azure.mgmt.costmanagement.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.costmanagement.models.Alert(CostManagementProxyResource):
        close_time: str
        cost_entity_id: str
        creation_time: str
        definition: AlertPropertiesDefinition
        description: str
        details: AlertPropertiesDetails
        e_tag: str
        id: str
        modification_time: str
        name: str
        source: Union[str, AlertSource]
        status: Union[str, AlertStatus]
        status_modification_time: str
        status_modification_user_name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                close_time: Optional[str] = ..., 
                cost_entity_id: Optional[str] = ..., 
                creation_time: Optional[str] = ..., 
                definition: Optional[AlertPropertiesDefinition] = ..., 
                description: Optional[str] = ..., 
                details: Optional[AlertPropertiesDetails] = ..., 
                e_tag: Optional[str] = ..., 
                modification_time: Optional[str] = ..., 
                source: Optional[Union[str, AlertSource]] = ..., 
                status: Optional[Union[str, AlertStatus]] = ..., 
                status_modification_time: Optional[str] = ..., 
                status_modification_user_name: Optional[str] = ..., 
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


    class azure.mgmt.costmanagement.models.AlertCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BILLING = "Billing"
        COST = "Cost"
        SYSTEM = "System"
        USAGE = "Usage"


    class azure.mgmt.costmanagement.models.AlertCriteria(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COST_THRESHOLD_EXCEEDED = "CostThresholdExceeded"
        CREDIT_THRESHOLD_APPROACHING = "CreditThresholdApproaching"
        CREDIT_THRESHOLD_REACHED = "CreditThresholdReached"
        CROSS_CLOUD_COLLECTION_ERROR = "CrossCloudCollectionError"
        CROSS_CLOUD_NEW_DATA_AVAILABLE = "CrossCloudNewDataAvailable"
        FORECAST_COST_THRESHOLD_EXCEEDED = "ForecastCostThresholdExceeded"
        FORECAST_USAGE_THRESHOLD_EXCEEDED = "ForecastUsageThresholdExceeded"
        GENERAL_THRESHOLD_ERROR = "GeneralThresholdError"
        INVOICE_DUE_DATE_APPROACHING = "InvoiceDueDateApproaching"
        INVOICE_DUE_DATE_REACHED = "InvoiceDueDateReached"
        MULTI_CURRENCY = "MultiCurrency"
        QUOTA_THRESHOLD_APPROACHING = "QuotaThresholdApproaching"
        QUOTA_THRESHOLD_REACHED = "QuotaThresholdReached"
        USAGE_THRESHOLD_EXCEEDED = "UsageThresholdExceeded"


    class azure.mgmt.costmanagement.models.AlertOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUAL_TO = "EqualTo"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL_TO = "GreaterThanOrEqualTo"
        LESS_THAN = "LessThan"
        LESS_THAN_OR_EQUAL_TO = "LessThanOrEqualTo"
        NONE = "None"


    class azure.mgmt.costmanagement.models.AlertPropertiesDefinition(Model):
        category: Union[str, AlertCategory]
        criteria: Union[str, AlertCriteria]
        type: Union[str, AlertType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                category: Optional[Union[str, AlertCategory]] = ..., 
                criteria: Optional[Union[str, AlertCriteria]] = ..., 
                type: Optional[Union[str, AlertType]] = ..., 
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


    class azure.mgmt.costmanagement.models.AlertPropertiesDetails(Model):
        amount: float
        company_name: str
        contact_emails: list[str]
        contact_groups: list[str]
        contact_roles: list[str]
        current_spend: float
        department_name: str
        enrollment_end_date: str
        enrollment_number: str
        enrollment_start_date: str
        invoicing_threshold: float
        meter_filter: list[any]
        operator: Union[str, AlertOperator]
        overriding_alert: str
        period_start_date: str
        resource_filter: list[any]
        resource_group_filter: list[any]
        tag_filter: JSON
        threshold: float
        time_grain_type: Union[str, AlertTimeGrainType]
        triggered_by: str
        unit: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                amount: Optional[float] = ..., 
                company_name: Optional[str] = ..., 
                contact_emails: Optional[List[str]] = ..., 
                contact_groups: Optional[List[str]] = ..., 
                contact_roles: Optional[List[str]] = ..., 
                current_spend: Optional[float] = ..., 
                department_name: Optional[str] = ..., 
                enrollment_end_date: Optional[str] = ..., 
                enrollment_number: Optional[str] = ..., 
                enrollment_start_date: Optional[str] = ..., 
                invoicing_threshold: Optional[float] = ..., 
                meter_filter: Optional[List[Any]] = ..., 
                operator: Optional[Union[str, AlertOperator]] = ..., 
                overriding_alert: Optional[str] = ..., 
                period_start_date: Optional[str] = ..., 
                resource_filter: Optional[List[Any]] = ..., 
                resource_group_filter: Optional[List[Any]] = ..., 
                tag_filter: Optional[JSON] = ..., 
                threshold: Optional[float] = ..., 
                time_grain_type: Optional[Union[str, AlertTimeGrainType]] = ..., 
                triggered_by: Optional[str] = ..., 
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


    class azure.mgmt.costmanagement.models.AlertSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRESET = "Preset"
        USER = "User"


    class azure.mgmt.costmanagement.models.AlertStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DISMISSED = "Dismissed"
        NONE = "None"
        OVERRIDDEN = "Overridden"
        RESOLVED = "Resolved"


    class azure.mgmt.costmanagement.models.AlertTimeGrainType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANNUALLY = "Annually"
        BILLING_ANNUAL = "BillingAnnual"
        BILLING_MONTH = "BillingMonth"
        BILLING_QUARTER = "BillingQuarter"
        MONTHLY = "Monthly"
        NONE = "None"
        QUARTERLY = "Quarterly"


    class azure.mgmt.costmanagement.models.AlertType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUDGET = "Budget"
        BUDGET_FORECAST = "BudgetForecast"
        CREDIT = "Credit"
        GENERAL = "General"
        INVOICE = "Invoice"
        QUOTA = "Quota"
        X_CLOUD = "xCloud"


    class azure.mgmt.costmanagement.models.AlertsResult(Model):
        next_link: str
        value: list[Alert]

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


    class azure.mgmt.costmanagement.models.AllSavingsBenefitDetails(Model):
        average_utilization_percentage: float
        benefit_cost: float
        commitment_amount: float
        coverage_percentage: float
        overage_cost: float
        savings_amount: float
        savings_percentage: float
        total_cost: float
        wastage_cost: float

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


    class azure.mgmt.costmanagement.models.AllSavingsList(Model):
        next_link: str
        value: list[AllSavingsBenefitDetails]

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


    class azure.mgmt.costmanagement.models.BenefitKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INCLUDED_QUANTITY = "IncludedQuantity"
        RESERVATION = "Reservation"
        SAVINGS_PLAN = "SavingsPlan"


    class azure.mgmt.costmanagement.models.BenefitRecommendationModel(BenefitResource):
        id: str
        kind: Union[str, BenefitKind]
        name: str
        properties: BenefitRecommendationProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, BenefitKind]] = ..., 
                properties: Optional[BenefitRecommendationProperties] = ..., 
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


    class azure.mgmt.costmanagement.models.BenefitRecommendationProperties(Model):
        all_recommendation_details: AllSavingsList
        arm_sku_name: str
        commitment_granularity: Union[str, Grain]
        cost_without_benefit: float
        currency_code: str
        first_consumption_date: datetime
        last_consumption_date: datetime
        look_back_period: Union[str, LookBackPeriod]
        recommendation_details: AllSavingsBenefitDetails
        scope: Union[str, Scope]
        term: Union[str, Term]
        total_hours: int
        usage: RecommendationUsageDetails

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                commitment_granularity: Optional[Union[str, Grain]] = ..., 
                look_back_period: Optional[Union[str, LookBackPeriod]] = ..., 
                recommendation_details: Optional[AllSavingsBenefitDetails] = ..., 
                term: Optional[Union[str, Term]] = ..., 
                usage: Optional[RecommendationUsageDetails] = ..., 
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


    class azure.mgmt.costmanagement.models.BenefitRecommendationsListResult(Model):
        next_link: str
        value: list[BenefitRecommendationModel]

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


    class azure.mgmt.costmanagement.models.BenefitResource(Resource):
        id: str
        kind: Union[str, BenefitKind]
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, BenefitKind]] = ..., 
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


    class azure.mgmt.costmanagement.models.BenefitUtilizationSummariesListResult(Model):
        next_link: str
        value: list[BenefitUtilizationSummary]

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


    class azure.mgmt.costmanagement.models.BenefitUtilizationSummary(Resource):
        id: str
        kind: Union[str, BenefitKind]
        name: str
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


    class azure.mgmt.costmanagement.models.BenefitUtilizationSummaryProperties(Model):
        arm_sku_name: str
        benefit_id: str
        benefit_order_id: str
        benefit_type: Union[str, BenefitKind]
        usage_date: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                benefit_type: Optional[Union[str, BenefitKind]] = ..., 
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


    class azure.mgmt.costmanagement.models.BlobInfo(Model):
        blob_link: str
        byte_count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob_link: Optional[str] = ..., 
                byte_count: Optional[int] = ..., 
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


    class azure.mgmt.costmanagement.models.ChartType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AREA = "Area"
        GROUPED_COLUMN = "GroupedColumn"
        LINE = "Line"
        STACKED_COLUMN = "StackedColumn"
        TABLE = "Table"


    class azure.mgmt.costmanagement.models.CheckNameAvailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.costmanagement.models.CheckNameAvailabilityRequest(Model):
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ..., 
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


    class azure.mgmt.costmanagement.models.CheckNameAvailabilityResponse(Model):
        message: str
        name_available: bool
        reason: Union[str, CheckNameAvailabilityReason]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[Union[str, CheckNameAvailabilityReason]] = ..., 
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


    class azure.mgmt.costmanagement.models.CommonExportProperties(Model):
        definition: ExportDefinition
        delivery_info: ExportDeliveryInfo
        format: Union[str, FormatType]
        next_run_time_estimate: datetime
        partition_data: bool
        run_history: ExportExecutionListResult

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                definition: ExportDefinition, 
                delivery_info: ExportDeliveryInfo, 
                format: Optional[Union[str, FormatType]] = ..., 
                partition_data: Optional[bool] = ..., 
                run_history: Optional[ExportExecutionListResult] = ..., 
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


    class azure.mgmt.costmanagement.models.CostDetailsDataFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CSV_COST_DETAILS_DATA_FORMAT = "Csv"


    class azure.mgmt.costmanagement.models.CostDetailsMetricType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTUAL_COST_COST_DETAILS_METRIC_TYPE = "ActualCost"
        AMORTIZED_COST_COST_DETAILS_METRIC_TYPE = "AmortizedCost"


    class azure.mgmt.costmanagement.models.CostDetailsOperationResults(Model):
        blob_count: int
        blobs: list[BlobInfo]
        byte_count: int
        compress_data: bool
        data_format: Union[str, CostDetailsDataFormat]
        error: ErrorDetails
        id: str
        manifest_version: str
        name: str
        request_body: GenerateCostDetailsReportRequestDefinition
        request_scope: str
        status: Union[str, CostDetailsStatusType]
        type: str
        valid_till: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob_count: Optional[int] = ..., 
                blobs: Optional[List[BlobInfo]] = ..., 
                byte_count: Optional[int] = ..., 
                compress_data: Optional[bool] = ..., 
                data_format: Optional[Union[str, CostDetailsDataFormat]] = ..., 
                error: Optional[ErrorDetails] = ..., 
                id: Optional[str] = ..., 
                manifest_version: Optional[str] = ..., 
                name: Optional[str] = ..., 
                request_body: Optional[GenerateCostDetailsReportRequestDefinition] = ..., 
                request_scope: Optional[str] = ..., 
                status: Optional[Union[str, CostDetailsStatusType]] = ..., 
                type: Optional[str] = ..., 
                valid_till: Optional[datetime] = ..., 
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


    class azure.mgmt.costmanagement.models.CostDetailsStatusType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED_COST_DETAILS_STATUS_TYPE = "Completed"
        FAILED_COST_DETAILS_STATUS_TYPE = "Failed"
        NO_DATA_FOUND_COST_DETAILS_STATUS_TYPE = "NoDataFound"


    class azure.mgmt.costmanagement.models.CostDetailsTimePeriod(Model):
        end: str
        start: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end: str, 
                start: str, 
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


    class azure.mgmt.costmanagement.models.CostManagementOperation(Operation):
        action_type: Union[str, ActionType]
        display: OperationDisplay
        id: str
        is_data_action: bool
        name: str
        origin: Union[str, Origin]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
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


    class azure.mgmt.costmanagement.models.CostManagementProxyResource(Model):
        e_tag: str
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
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


    class azure.mgmt.costmanagement.models.CostManagementResource(Model):
        e_tag: str
        id: str
        location: str
        name: str
        sku: str
        tags: dict[str, str]
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


    class azure.mgmt.costmanagement.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.costmanagement.models.DaysOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.costmanagement.models.Dimension(CostManagementResource):
        category: str
        data: list[str]
        description: str
        e_tag: str
        filter_enabled: bool
        grouping_enabled: bool
        id: str
        location: str
        name: str
        next_link: str
        sku: str
        tags: dict[str, str]
        total: int
        type: str
        usage_end: datetime
        usage_start: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data: Optional[List[str]] = ..., 
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


    class azure.mgmt.costmanagement.models.DimensionsListResult(Model):
        value: list[Dimension]

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


    class azure.mgmt.costmanagement.models.DismissAlertPayload(Model):
        close_time: str
        cost_entity_id: str
        creation_time: str
        definition: AlertPropertiesDefinition
        description: str
        details: AlertPropertiesDetails
        modification_time: str
        source: Union[str, AlertSource]
        status: Union[str, AlertStatus]
        status_modification_time: str
        status_modification_user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                close_time: Optional[str] = ..., 
                cost_entity_id: Optional[str] = ..., 
                creation_time: Optional[str] = ..., 
                definition: Optional[AlertPropertiesDefinition] = ..., 
                description: Optional[str] = ..., 
                details: Optional[AlertPropertiesDetails] = ..., 
                modification_time: Optional[str] = ..., 
                source: Optional[Union[str, AlertSource]] = ..., 
                status: Optional[Union[str, AlertStatus]] = ..., 
                status_modification_time: Optional[str] = ..., 
                status_modification_user_name: Optional[str] = ..., 
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


    class azure.mgmt.costmanagement.models.DownloadURL(Model):
        download_url: str
        expiry_time: datetime
        valid_till: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                download_url: Optional[str] = ..., 
                valid_till: Optional[datetime] = ..., 
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


    class azure.mgmt.costmanagement.models.ErrorDetails(Model):
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


    class azure.mgmt.costmanagement.models.ErrorDetailsWithNestedDetails(ErrorDetails):
        code: str
        details: list[ErrorDetailsWithNestedDetails]
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


    class azure.mgmt.costmanagement.models.ErrorResponse(Model):
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


    class azure.mgmt.costmanagement.models.ErrorResponseWithNestedDetails(Model):
        error: ErrorDetailsWithNestedDetails

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetailsWithNestedDetails] = ..., 
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


    class azure.mgmt.costmanagement.models.ExecutionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        DATA_NOT_AVAILABLE = "DataNotAvailable"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NEW_DATA_NOT_AVAILABLE = "NewDataNotAvailable"
        QUEUED = "Queued"
        TIMEOUT = "Timeout"


    class azure.mgmt.costmanagement.models.ExecutionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ON_DEMAND = "OnDemand"
        SCHEDULED = "Scheduled"


    class azure.mgmt.costmanagement.models.Export(CostManagementProxyResource):
        definition: ExportDefinition
        delivery_info: ExportDeliveryInfo
        e_tag: str
        format: Union[str, FormatType]
        id: str
        name: str
        next_run_time_estimate: datetime
        partition_data: bool
        run_history: ExportExecutionListResult
        schedule: ExportSchedule
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                definition: Optional[ExportDefinition] = ..., 
                delivery_info: Optional[ExportDeliveryInfo] = ..., 
                e_tag: Optional[str] = ..., 
                format: Optional[Union[str, FormatType]] = ..., 
                partition_data: Optional[bool] = ..., 
                run_history: Optional[ExportExecutionListResult] = ..., 
                schedule: Optional[ExportSchedule] = ..., 
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


    class azure.mgmt.costmanagement.models.ExportDataset(Model):
        configuration: ExportDatasetConfiguration
        granularity: Union[str, GranularityType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration: Optional[ExportDatasetConfiguration] = ..., 
                granularity: Optional[Union[str, GranularityType]] = ..., 
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


    class azure.mgmt.costmanagement.models.ExportDatasetConfiguration(Model):
        columns: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                columns: Optional[List[str]] = ..., 
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


    class azure.mgmt.costmanagement.models.ExportDefinition(Model):
        data_set: ExportDataset
        time_period: ExportTimePeriod
        timeframe: Union[str, TimeframeType]
        type: Union[str, ExportType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_set: Optional[ExportDataset] = ..., 
                time_period: Optional[ExportTimePeriod] = ..., 
                timeframe: Union[str, TimeframeType], 
                type: Union[str, ExportType], 
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


    class azure.mgmt.costmanagement.models.ExportDeliveryDestination(Model):
        container: str
        resource_id: str
        root_folder_path: str
        sas_token: str
        storage_account: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                container: str, 
                resource_id: Optional[str] = ..., 
                root_folder_path: Optional[str] = ..., 
                sas_token: Optional[str] = ..., 
                storage_account: Optional[str] = ..., 
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


    class azure.mgmt.costmanagement.models.ExportDeliveryInfo(Model):
        destination: ExportDeliveryDestination

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                destination: ExportDeliveryDestination, 
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


    class azure.mgmt.costmanagement.models.ExportExecutionListResult(Model):
        value: list[ExportRun]

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


    class azure.mgmt.costmanagement.models.ExportListResult(Model):
        value: list[Export]

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


    class azure.mgmt.costmanagement.models.ExportProperties(CommonExportProperties):
        definition: ExportDefinition
        delivery_info: ExportDeliveryInfo
        format: Union[str, FormatType]
        next_run_time_estimate: datetime
        partition_data: bool
        run_history: ExportExecutionListResult
        schedule: ExportSchedule

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                definition: ExportDefinition, 
                delivery_info: ExportDeliveryInfo, 
                format: Optional[Union[str, FormatType]] = ..., 
                partition_data: Optional[bool] = ..., 
                run_history: Optional[ExportExecutionListResult] = ..., 
                schedule: Optional[ExportSchedule] = ..., 
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


    class azure.mgmt.costmanagement.models.ExportRecurrencePeriod(Model):
        from_property: datetime
        to: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                from_property: datetime, 
                to: Optional[datetime] = ..., 
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


    class azure.mgmt.costmanagement.models.ExportRun(CostManagementProxyResource):
        e_tag: str
        error: ErrorDetails
        execution_type: Union[str, ExecutionType]
        file_name: str
        id: str
        name: str
        processing_end_time: datetime
        processing_start_time: datetime
        run_settings: CommonExportProperties
        status: Union[str, ExecutionStatus]
        submitted_by: str
        submitted_time: datetime
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                error: Optional[ErrorDetails] = ..., 
                execution_type: Optional[Union[str, ExecutionType]] = ..., 
                file_name: Optional[str] = ..., 
                processing_end_time: Optional[datetime] = ..., 
                processing_start_time: Optional[datetime] = ..., 
                run_settings: Optional[CommonExportProperties] = ..., 
                status: Optional[Union[str, ExecutionStatus]] = ..., 
                submitted_by: Optional[str] = ..., 
                submitted_time: Optional[datetime] = ..., 
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


    class azure.mgmt.costmanagement.models.ExportSchedule(Model):
        recurrence: Union[str, RecurrenceType]
        recurrence_period: ExportRecurrencePeriod
        status: Union[str, StatusType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                recurrence: Optional[Union[str, RecurrenceType]] = ..., 
                recurrence_period: Optional[ExportRecurrencePeriod] = ..., 
                status: Optional[Union[str, StatusType]] = ..., 
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


    class azure.mgmt.costmanagement.models.ExportTimePeriod(Model):
        from_property: datetime
        to: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                from_property: datetime, 
                to: datetime, 
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


    class azure.mgmt.costmanagement.models.ExportType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTUAL_COST = "ActualCost"
        AMORTIZED_COST = "AmortizedCost"
        USAGE = "Usage"


    class azure.mgmt.costmanagement.models.ExternalCloudProviderType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTERNAL_BILLING_ACCOUNTS = "externalBillingAccounts"
        EXTERNAL_SUBSCRIPTIONS = "externalSubscriptions"


    class azure.mgmt.costmanagement.models.FileDestination(Model):
        file_formats: Union[list[str, FileFormat]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                file_formats: Optional[List[Union[str, FileFormat]]] = ..., 
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


    class azure.mgmt.costmanagement.models.FileFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CSV = "Csv"


    class azure.mgmt.costmanagement.models.ForecastAggregation(Model):
        function: Union[str, FunctionType]
        name: Union[str, FunctionName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                function: Union[str, FunctionType], 
                name: Union[str, FunctionName], 
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


    class azure.mgmt.costmanagement.models.ForecastColumn(Model):
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ..., 
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


    class azure.mgmt.costmanagement.models.ForecastComparisonExpression(Model):
        name: str
        operator: Union[str, ForecastOperatorType]
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                operator: Union[str, ForecastOperatorType], 
                values: List[str], 
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


    class azure.mgmt.costmanagement.models.ForecastDataset(Model):
        aggregation: dict[str, ForecastAggregation]
        configuration: ForecastDatasetConfiguration
        filter: ForecastFilter
        granularity: Union[str, GranularityType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                aggregation: Dict[str, ForecastAggregation], 
                configuration: Optional[ForecastDatasetConfiguration] = ..., 
                filter: Optional[ForecastFilter] = ..., 
                granularity: Optional[Union[str, GranularityType]] = ..., 
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


    class azure.mgmt.costmanagement.models.ForecastDatasetConfiguration(Model):
        columns: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                columns: Optional[List[str]] = ..., 
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


    class azure.mgmt.costmanagement.models.ForecastDefinition(Model):
        dataset: ForecastDataset
        include_actual_cost: bool
        include_fresh_partial_cost: bool
        time_period: ForecastTimePeriod
        timeframe: Union[str, ForecastTimeframe]
        type: Union[str, ForecastType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dataset: ForecastDataset, 
                include_actual_cost: Optional[bool] = ..., 
                include_fresh_partial_cost: Optional[bool] = ..., 
                time_period: Optional[ForecastTimePeriod] = ..., 
                timeframe: Union[str, ForecastTimeframe], 
                type: Union[str, ForecastType], 
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


    class azure.mgmt.costmanagement.models.ForecastFilter(Model):
        and_property: list[ForecastFilter]
        dimensions: ForecastComparisonExpression
        or_property: list[ForecastFilter]
        tags: ForecastComparisonExpression

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                and_property: Optional[List[ForecastFilter]] = ..., 
                dimensions: Optional[ForecastComparisonExpression] = ..., 
                or_property: Optional[List[ForecastFilter]] = ..., 
                tags: Optional[ForecastComparisonExpression] = ..., 
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


    class azure.mgmt.costmanagement.models.ForecastOperatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IN = "In"
        IN_ENUM = "In"


    class azure.mgmt.costmanagement.models.ForecastResult(CostManagementResource):
        columns: list[ForecastColumn]
        e_tag: str
        id: str
        location: str
        name: str
        next_link: str
        rows: list[list[any]]
        sku: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                columns: Optional[List[ForecastColumn]] = ..., 
                next_link: Optional[str] = ..., 
                rows: Optional[List[List[Any]]] = ..., 
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


    class azure.mgmt.costmanagement.models.ForecastTimePeriod(Model):
        from_property: datetime
        to: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                from_property: datetime, 
                to: datetime, 
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


    class azure.mgmt.costmanagement.models.ForecastTimeframe(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"


    class azure.mgmt.costmanagement.models.ForecastType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTUAL_COST = "ActualCost"
        AMORTIZED_COST = "AmortizedCost"
        USAGE = "Usage"


    class azure.mgmt.costmanagement.models.FormatType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CSV = "Csv"


    class azure.mgmt.costmanagement.models.FunctionName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COST = "Cost"
        COST_USD = "CostUSD"
        PRE_TAX_COST = "PreTaxCost"
        PRE_TAX_COST_USD = "PreTaxCostUSD"


    class azure.mgmt.costmanagement.models.FunctionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SUM = "Sum"


    class azure.mgmt.costmanagement.models.GenerateCostDetailsReportErrorResponse(Model):
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


    class azure.mgmt.costmanagement.models.GenerateCostDetailsReportRequestDefinition(Model):
        billing_period: str
        invoice_id: str
        metric: Union[str, CostDetailsMetricType]
        time_period: CostDetailsTimePeriod

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_period: Optional[str] = ..., 
                invoice_id: Optional[str] = ..., 
                metric: Optional[Union[str, CostDetailsMetricType]] = ..., 
                time_period: Optional[CostDetailsTimePeriod] = ..., 
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


    class azure.mgmt.costmanagement.models.GenerateDetailedCostReportDefinition(Model):
        billing_period: str
        customer_id: str
        invoice_id: str
        metric: Union[str, GenerateDetailedCostReportMetricType]
        time_period: GenerateDetailedCostReportTimePeriod

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_period: Optional[str] = ..., 
                customer_id: Optional[str] = ..., 
                invoice_id: Optional[str] = ..., 
                metric: Optional[Union[str, GenerateDetailedCostReportMetricType]] = ..., 
                time_period: Optional[GenerateDetailedCostReportTimePeriod] = ..., 
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


    class azure.mgmt.costmanagement.models.GenerateDetailedCostReportErrorResponse(Model):
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


    class azure.mgmt.costmanagement.models.GenerateDetailedCostReportMetricType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTUAL_COST = "ActualCost"
        AMORTIZED_COST = "AmortizedCost"


    class azure.mgmt.costmanagement.models.GenerateDetailedCostReportOperationResult(Model):
        download_url: str
        expiry_time: datetime
        id: str
        name: str
        type: str
        valid_till: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                download_url: Optional[str] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                type: Optional[str] = ..., 
                valid_till: Optional[datetime] = ..., 
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


    class azure.mgmt.costmanagement.models.GenerateDetailedCostReportOperationStatuses(Model):
        download_url: str
        end_time: str
        error: ErrorDetails
        expiry_time: datetime
        id: str
        name: str
        start_time: str
        status: Status
        type: str
        valid_till: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                download_url: Optional[str] = ..., 
                end_time: Optional[str] = ..., 
                error: Optional[ErrorDetails] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
                status: Optional[Status] = ..., 
                type: Optional[str] = ..., 
                valid_till: Optional[datetime] = ..., 
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


    class azure.mgmt.costmanagement.models.GenerateDetailedCostReportTimePeriod(Model):
        end: str
        start: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end: str, 
                start: str, 
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


    class azure.mgmt.costmanagement.models.Grain(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        HOURLY = "Hourly"
        MONTHLY = "Monthly"


    class azure.mgmt.costmanagement.models.GrainParameter(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        HOURLY = "Hourly"
        MONTHLY = "Monthly"


    class azure.mgmt.costmanagement.models.GranularityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"


    class azure.mgmt.costmanagement.models.IncludedQuantityUtilizationSummary(BenefitUtilizationSummary):
        arm_sku_name: str
        benefit_id: str
        benefit_order_id: str
        benefit_type: Union[str, BenefitKind]
        id: str
        kind: Union[str, BenefitKind]
        name: str
        type: str
        usage_date: datetime
        utilization_percentage: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                benefit_type: Optional[Union[str, BenefitKind]] = ..., 
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


    class azure.mgmt.costmanagement.models.IncludedQuantityUtilizationSummaryProperties(BenefitUtilizationSummaryProperties):
        arm_sku_name: str
        benefit_id: str
        benefit_order_id: str
        benefit_type: Union[str, BenefitKind]
        usage_date: datetime
        utilization_percentage: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                benefit_type: Optional[Union[str, BenefitKind]] = ..., 
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


    class azure.mgmt.costmanagement.models.KpiProperties(Model):
        enabled: bool
        id: str
        type: Union[str, KpiType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                id: Optional[str] = ..., 
                type: Optional[Union[str, KpiType]] = ..., 
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


    class azure.mgmt.costmanagement.models.KpiType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUDGET = "Budget"
        FORECAST = "Forecast"


    class azure.mgmt.costmanagement.models.LookBackPeriod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LAST30_DAYS = "Last30Days"
        LAST60_DAYS = "Last60Days"
        LAST7_DAYS = "Last7Days"


    class azure.mgmt.costmanagement.models.MetricType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTUAL_COST = "ActualCost"
        AHUB = "AHUB"
        AMORTIZED_COST = "AmortizedCost"


    class azure.mgmt.costmanagement.models.NotificationProperties(Model):
        language: str
        message: str
        regional_format: str
        subject: str
        to: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                language: Optional[str] = ..., 
                message: Optional[str] = ..., 
                regional_format: Optional[str] = ..., 
                subject: str, 
                to: List[str], 
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


    class azure.mgmt.costmanagement.models.Operation(Model):
        action_type: Union[str, ActionType]
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, Origin]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
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


    class azure.mgmt.costmanagement.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

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


    class azure.mgmt.costmanagement.models.OperationListResult(Model):
        next_link: str
        value: list[CostManagementOperation]

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


    class azure.mgmt.costmanagement.models.OperationStatus(Model):
        report_url: Union[str, ReservationReportSchema]
        status: Union[str, OperationStatusType]
        valid_until: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                report_url: Optional[Union[str, ReservationReportSchema]] = ..., 
                status: Optional[Union[str, OperationStatusType]] = ..., 
                valid_until: Optional[datetime] = ..., 
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


    class azure.mgmt.costmanagement.models.OperationStatusType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        RUNNING = "Running"


    class azure.mgmt.costmanagement.models.OperatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINS = "Contains"
        IN = "In"
        IN_ENUM = "In"


    class azure.mgmt.costmanagement.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.costmanagement.models.PivotProperties(Model):
        name: str
        type: Union[str, PivotType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[Union[str, PivotType]] = ..., 
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


    class azure.mgmt.costmanagement.models.PivotType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIMENSION = "Dimension"
        TAG_KEY = "TagKey"


    class azure.mgmt.costmanagement.models.ProxyResource(Resource):
        id: str
        name: str
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


    class azure.mgmt.costmanagement.models.QueryAggregation(Model):
        function: Union[str, FunctionType]
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                function: Union[str, FunctionType], 
                name: str, 
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


    class azure.mgmt.costmanagement.models.QueryColumn(Model):
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ..., 
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


    class azure.mgmt.costmanagement.models.QueryColumnType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIMENSION = "Dimension"
        TAG_KEY = "TagKey"


    class azure.mgmt.costmanagement.models.QueryComparisonExpression(Model):
        name: str
        operator: Union[str, QueryOperatorType]
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                operator: Union[str, QueryOperatorType], 
                values: List[str], 
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


    class azure.mgmt.costmanagement.models.QueryDataset(Model):
        aggregation: dict[str, QueryAggregation]
        configuration: QueryDatasetConfiguration
        filter: QueryFilter
        granularity: Union[str, GranularityType]
        grouping: list[QueryGrouping]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                aggregation: Optional[Dict[str, QueryAggregation]] = ..., 
                configuration: Optional[QueryDatasetConfiguration] = ..., 
                filter: Optional[QueryFilter] = ..., 
                granularity: Optional[Union[str, GranularityType]] = ..., 
                grouping: Optional[List[QueryGrouping]] = ..., 
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


    class azure.mgmt.costmanagement.models.QueryDatasetConfiguration(Model):
        columns: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                columns: Optional[List[str]] = ..., 
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


    class azure.mgmt.costmanagement.models.QueryDefinition(Model):
        dataset: QueryDataset
        time_period: QueryTimePeriod
        timeframe: Union[str, TimeframeType]
        type: Union[str, ExportType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dataset: QueryDataset, 
                time_period: Optional[QueryTimePeriod] = ..., 
                timeframe: Union[str, TimeframeType], 
                type: Union[str, ExportType], 
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


    class azure.mgmt.costmanagement.models.QueryFilter(Model):
        and_property: list[QueryFilter]
        dimensions: QueryComparisonExpression
        or_property: list[QueryFilter]
        tags: QueryComparisonExpression

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                and_property: Optional[List[QueryFilter]] = ..., 
                dimensions: Optional[QueryComparisonExpression] = ..., 
                or_property: Optional[List[QueryFilter]] = ..., 
                tags: Optional[QueryComparisonExpression] = ..., 
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


    class azure.mgmt.costmanagement.models.QueryGrouping(Model):
        name: str
        type: Union[str, QueryColumnType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                type: Union[str, QueryColumnType], 
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


    class azure.mgmt.costmanagement.models.QueryOperatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IN = "In"
        IN_ENUM = "In"


    class azure.mgmt.costmanagement.models.QueryResult(CostManagementResource):
        columns: list[QueryColumn]
        e_tag: str
        id: str
        location: str
        name: str
        next_link: str
        rows: list[list[any]]
        sku: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                columns: Optional[List[QueryColumn]] = ..., 
                next_link: Optional[str] = ..., 
                rows: Optional[List[List[Any]]] = ..., 
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


    class azure.mgmt.costmanagement.models.QueryTimePeriod(Model):
        from_property: datetime
        to: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                from_property: datetime, 
                to: datetime, 
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


    class azure.mgmt.costmanagement.models.RecommendationUsageDetails(Model):
        charges: list[float]
        usage_grain: Union[str, Grain]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                usage_grain: Optional[Union[str, Grain]] = ..., 
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


    class azure.mgmt.costmanagement.models.RecurrenceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANNUALLY = "Annually"
        DAILY = "Daily"
        MONTHLY = "Monthly"
        WEEKLY = "Weekly"


    class azure.mgmt.costmanagement.models.ReportConfigAggregation(Model):
        function: Union[str, FunctionType]
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                function: Union[str, FunctionType], 
                name: str, 
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


    class azure.mgmt.costmanagement.models.ReportConfigComparisonExpression(Model):
        name: str
        operator: Union[str, OperatorType]
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                operator: Union[str, OperatorType], 
                values: List[str], 
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


    class azure.mgmt.costmanagement.models.ReportConfigDataset(Model):
        aggregation: dict[str, ReportConfigAggregation]
        configuration: ReportConfigDatasetConfiguration
        filter: ReportConfigFilter
        granularity: Union[str, ReportGranularityType]
        grouping: list[ReportConfigGrouping]
        sorting: list[ReportConfigSorting]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                aggregation: Optional[Dict[str, ReportConfigAggregation]] = ..., 
                configuration: Optional[ReportConfigDatasetConfiguration] = ..., 
                filter: Optional[ReportConfigFilter] = ..., 
                granularity: Optional[Union[str, ReportGranularityType]] = ..., 
                grouping: Optional[List[ReportConfigGrouping]] = ..., 
                sorting: Optional[List[ReportConfigSorting]] = ..., 
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


    class azure.mgmt.costmanagement.models.ReportConfigDatasetConfiguration(Model):
        columns: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                columns: Optional[List[str]] = ..., 
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


    class azure.mgmt.costmanagement.models.ReportConfigFilter(Model):
        and_property: list[ReportConfigFilter]
        dimensions: ReportConfigComparisonExpression
        or_property: list[ReportConfigFilter]
        tags: ReportConfigComparisonExpression

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                and_property: Optional[List[ReportConfigFilter]] = ..., 
                dimensions: Optional[ReportConfigComparisonExpression] = ..., 
                or_property: Optional[List[ReportConfigFilter]] = ..., 
                tags: Optional[ReportConfigComparisonExpression] = ..., 
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


    class azure.mgmt.costmanagement.models.ReportConfigGrouping(Model):
        name: str
        type: Union[str, QueryColumnType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                type: Union[str, QueryColumnType], 
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


    class azure.mgmt.costmanagement.models.ReportConfigSorting(Model):
        direction: Union[str, ReportConfigSortingType]
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                direction: Optional[Union[str, ReportConfigSortingType]] = ..., 
                name: str, 
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


    class azure.mgmt.costmanagement.models.ReportConfigSortingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASCENDING = "Ascending"
        DESCENDING = "Descending"


    class azure.mgmt.costmanagement.models.ReportConfigTimePeriod(Model):
        from_property: datetime
        to: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                from_property: datetime, 
                to: datetime, 
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


    class azure.mgmt.costmanagement.models.ReportGranularityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        MONTHLY = "Monthly"


    class azure.mgmt.costmanagement.models.ReportOperationStatusType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NO_DATA_FOUND = "NoDataFound"
        QUEUED = "Queued"
        READY_TO_DOWNLOAD = "ReadyToDownload"
        TIMED_OUT = "TimedOut"


    class azure.mgmt.costmanagement.models.ReportTimeframeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"
        MONTH_TO_DATE = "MonthToDate"
        WEEK_TO_DATE = "WeekToDate"
        YEAR_TO_DATE = "YearToDate"


    class azure.mgmt.costmanagement.models.ReportType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        USAGE = "Usage"


    class azure.mgmt.costmanagement.models.ReservationReportSchema(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INSTANCE_FLEXIBILITY_GROUP = "InstanceFlexibilityGroup"
        INSTANCE_FLEXIBILITY_RATIO = "InstanceFlexibilityRatio"
        INSTANCE_ID = "InstanceId"
        KIND = "Kind"
        RESERVATION_ID = "ReservationId"
        RESERVATION_ORDER_ID = "ReservationOrderId"
        RESERVED_HOURS = "ReservedHours"
        SKU_NAME = "SkuName"
        TOTAL_RESERVED_QUANTITY = "TotalReservedQuantity"
        USAGE_DATE = "UsageDate"
        USED_HOURS = "UsedHours"


    class azure.mgmt.costmanagement.models.Resource(Model):
        id: str
        name: str
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


    class azure.mgmt.costmanagement.models.SavingsPlanUtilizationSummary(BenefitUtilizationSummary):
        arm_sku_name: str
        avg_utilization_percentage: float
        benefit_id: str
        benefit_order_id: str
        benefit_type: Union[str, BenefitKind]
        id: str
        kind: Union[str, BenefitKind]
        max_utilization_percentage: float
        min_utilization_percentage: float
        name: str
        type: str
        usage_date: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                benefit_type: Optional[Union[str, BenefitKind]] = ..., 
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


    class azure.mgmt.costmanagement.models.SavingsPlanUtilizationSummaryProperties(BenefitUtilizationSummaryProperties):
        arm_sku_name: str
        avg_utilization_percentage: float
        benefit_id: str
        benefit_order_id: str
        benefit_type: Union[str, BenefitKind]
        max_utilization_percentage: float
        min_utilization_percentage: float
        usage_date: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                benefit_type: Optional[Union[str, BenefitKind]] = ..., 
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


    class azure.mgmt.costmanagement.models.ScheduleFrequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        MONTHLY = "Monthly"
        WEEKLY = "Weekly"


    class azure.mgmt.costmanagement.models.ScheduleProperties(Model):
        day_of_month: int
        days_of_week: Union[list[str, DaysOfWeek]]
        end_date: datetime
        frequency: Union[str, ScheduleFrequency]
        hour_of_day: int
        start_date: datetime
        weeks_of_month: Union[list[str, WeeksOfMonth]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                day_of_month: Optional[int] = ..., 
                days_of_week: Optional[List[Union[str, DaysOfWeek]]] = ..., 
                end_date: datetime, 
                frequency: Union[str, ScheduleFrequency], 
                hour_of_day: Optional[int] = ..., 
                start_date: datetime, 
                weeks_of_month: Optional[List[Union[str, WeeksOfMonth]]] = ..., 
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


    class azure.mgmt.costmanagement.models.ScheduledAction(ScheduledActionProxyResource):
        display_name: str
        e_tag: str
        file_destination: FileDestination
        id: str
        kind: Union[str, ScheduledActionKind]
        name: str
        notification: NotificationProperties
        notification_email: str
        schedule: ScheduleProperties
        scope: str
        status: Union[str, ScheduledActionStatus]
        system_data: SystemData
        type: str
        view_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                file_destination: Optional[FileDestination] = ..., 
                kind: Optional[Union[str, ScheduledActionKind]] = ..., 
                notification: Optional[NotificationProperties] = ..., 
                notification_email: Optional[str] = ..., 
                schedule: Optional[ScheduleProperties] = ..., 
                scope: Optional[str] = ..., 
                status: Optional[Union[str, ScheduledActionStatus]] = ..., 
                view_id: Optional[str] = ..., 
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


    class azure.mgmt.costmanagement.models.ScheduledActionKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EMAIL = "Email"
        INSIGHT_ALERT = "InsightAlert"


    class azure.mgmt.costmanagement.models.ScheduledActionListResult(Model):
        next_link: str
        value: list[ScheduledAction]

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


    class azure.mgmt.costmanagement.models.ScheduledActionProxyResource(ProxyResource):
        e_tag: str
        id: str
        kind: Union[str, ScheduledActionKind]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, ScheduledActionKind]] = ..., 
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


    class azure.mgmt.costmanagement.models.ScheduledActionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        EXPIRED = "Expired"


    class azure.mgmt.costmanagement.models.Scope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SHARED = "Shared"
        SINGLE = "Single"


    class azure.mgmt.costmanagement.models.SharedScopeBenefitRecommendationProperties(BenefitRecommendationProperties):
        all_recommendation_details: AllSavingsList
        arm_sku_name: str
        commitment_granularity: Union[str, Grain]
        cost_without_benefit: float
        currency_code: str
        first_consumption_date: datetime
        last_consumption_date: datetime
        look_back_period: Union[str, LookBackPeriod]
        recommendation_details: AllSavingsBenefitDetails
        scope: Union[str, Scope]
        term: Union[str, Term]
        total_hours: int
        usage: RecommendationUsageDetails

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                commitment_granularity: Optional[Union[str, Grain]] = ..., 
                look_back_period: Optional[Union[str, LookBackPeriod]] = ..., 
                recommendation_details: Optional[AllSavingsBenefitDetails] = ..., 
                term: Optional[Union[str, Term]] = ..., 
                usage: Optional[RecommendationUsageDetails] = ..., 
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


    class azure.mgmt.costmanagement.models.SingleScopeBenefitRecommendationProperties(BenefitRecommendationProperties):
        all_recommendation_details: AllSavingsList
        arm_sku_name: str
        commitment_granularity: Union[str, Grain]
        cost_without_benefit: float
        currency_code: str
        first_consumption_date: datetime
        last_consumption_date: datetime
        look_back_period: Union[str, LookBackPeriod]
        recommendation_details: AllSavingsBenefitDetails
        resource_group: str
        scope: Union[str, Scope]
        subscription_id: str
        term: Union[str, Term]
        total_hours: int
        usage: RecommendationUsageDetails

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                commitment_granularity: Optional[Union[str, Grain]] = ..., 
                look_back_period: Optional[Union[str, LookBackPeriod]] = ..., 
                recommendation_details: Optional[AllSavingsBenefitDetails] = ..., 
                term: Optional[Union[str, Term]] = ..., 
                usage: Optional[RecommendationUsageDetails] = ..., 
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


    class azure.mgmt.costmanagement.models.Status(Model):
        status: Union[str, ReportOperationStatusType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                status: Optional[Union[str, ReportOperationStatusType]] = ..., 
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


    class azure.mgmt.costmanagement.models.StatusType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        INACTIVE = "Inactive"


    class azure.mgmt.costmanagement.models.SystemData(Model):
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


    class azure.mgmt.costmanagement.models.Term(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P1_Y = "P1Y"
        P3_Y = "P3Y"


    class azure.mgmt.costmanagement.models.TimeframeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BILLING_MONTH_TO_DATE = "BillingMonthToDate"
        CUSTOM = "Custom"
        MONTH_TO_DATE = "MonthToDate"
        THE_LAST_BILLING_MONTH = "TheLastBillingMonth"
        THE_LAST_MONTH = "TheLastMonth"
        WEEK_TO_DATE = "WeekToDate"


    class azure.mgmt.costmanagement.models.View(CostManagementProxyResource):
        accumulated: Union[str, AccumulatedType]
        chart: Union[str, ChartType]
        created_on: datetime
        currency: str
        data_set: ReportConfigDataset
        date_range: str
        display_name: str
        e_tag: str
        id: str
        include_monetary_commitment: bool
        kpis: list[KpiProperties]
        metric: Union[str, MetricType]
        modified_on: datetime
        name: str
        pivots: list[PivotProperties]
        scope: str
        time_period: ReportConfigTimePeriod
        timeframe: Union[str, ReportTimeframeType]
        type: str
        type_properties_query_type: Union[str, ReportType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                accumulated: Optional[Union[str, AccumulatedType]] = ..., 
                chart: Optional[Union[str, ChartType]] = ..., 
                data_set: Optional[ReportConfigDataset] = ..., 
                date_range: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                e_tag: Optional[str] = ..., 
                include_monetary_commitment: Optional[bool] = ..., 
                kpis: Optional[List[KpiProperties]] = ..., 
                metric: Optional[Union[str, MetricType]] = ..., 
                pivots: Optional[List[PivotProperties]] = ..., 
                scope: Optional[str] = ..., 
                time_period: Optional[ReportConfigTimePeriod] = ..., 
                timeframe: Optional[Union[str, ReportTimeframeType]] = ..., 
                type_properties_query_type: Optional[Union[str, ReportType]] = ..., 
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


    class azure.mgmt.costmanagement.models.ViewListResult(Model):
        next_link: str
        value: list[View]

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


    class azure.mgmt.costmanagement.models.WeeksOfMonth(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIRST = "First"
        FOURTH = "Fourth"
        LAST = "Last"
        SECOND = "Second"
        THIRD = "Third"


namespace azure.mgmt.costmanagement.operations

    class azure.mgmt.costmanagement.operations.AlertsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def dismiss(
                self, 
                scope: str, 
                alert_id: str, 
                parameters: DismissAlertPayload, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Alert: ...

        @overload
        def dismiss(
                self, 
                scope: str, 
                alert_id: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                alert_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AlertsResult: ...

        @distributed_trace
        def list_external(
                self, 
                external_cloud_provider_type: Union[str, ExternalCloudProviderType], 
                external_cloud_provider_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AlertsResult: ...


    class azure.mgmt.costmanagement.operations.BenefitRecommendationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                billing_scope: str, 
                filter: Optional[str] = None, 
                orderby: Optional[str] = None, 
                expand: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[BenefitRecommendationModel]: ...


    class azure.mgmt.costmanagement.operations.BenefitUtilizationSummariesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_billing_account_id(
                self, 
                billing_account_id: str, 
                grain_parameter: Optional[Union[str, GrainParameter]] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[BenefitUtilizationSummary]: ...

        @distributed_trace
        def list_by_billing_profile_id(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                grain_parameter: Optional[Union[str, GrainParameter]] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[BenefitUtilizationSummary]: ...

        @distributed_trace
        def list_by_savings_plan_id(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                filter: Optional[str] = None, 
                grain_parameter: Optional[Union[str, GrainParameter]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[BenefitUtilizationSummary]: ...

        @distributed_trace
        def list_by_savings_plan_order(
                self, 
                savings_plan_order_id: str, 
                filter: Optional[str] = None, 
                grain_parameter: Optional[Union[str, GrainParameter]] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[BenefitUtilizationSummary]: ...


    class azure.mgmt.costmanagement.operations.DimensionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def by_external_cloud_provider_type(
                self, 
                external_cloud_provider_type: Union[str, ExternalCloudProviderType], 
                external_cloud_provider_id: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                skiptoken: Optional[str] = None, 
                top: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Dimension]: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                filter: Optional[str] = None, 
                expand: Optional[str] = None, 
                skiptoken: Optional[str] = None, 
                top: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Dimension]: ...


    class azure.mgmt.costmanagement.operations.ExportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                export_name: str, 
                parameters: Export, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Export: ...

        @overload
        def create_or_update(
                self, 
                scope: str, 
                export_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Export: ...

        @distributed_trace
        def delete(
                self, 
                scope: str, 
                export_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def execute(
                self, 
                scope: str, 
                export_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                export_name: str, 
                expand: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Export: ...

        @distributed_trace
        def get_execution_history(
                self, 
                scope: str, 
                export_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ExportExecutionListResult: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                expand: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ExportListResult: ...


    class azure.mgmt.costmanagement.operations.ForecastOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def external_cloud_provider_usage(
                self, 
                external_cloud_provider_type: Union[str, ExternalCloudProviderType], 
                external_cloud_provider_id: str, 
                parameters: ForecastDefinition, 
                filter: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ForecastResult: ...

        @overload
        def external_cloud_provider_usage(
                self, 
                external_cloud_provider_type: Union[str, ExternalCloudProviderType], 
                external_cloud_provider_id: str, 
                parameters: IO, 
                filter: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ForecastResult: ...

        @overload
        def usage(
                self, 
                scope: str, 
                parameters: ForecastDefinition, 
                filter: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[ForecastResult]: ...

        @overload
        def usage(
                self, 
                scope: str, 
                parameters: IO, 
                filter: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[ForecastResult]: ...


    class azure.mgmt.costmanagement.operations.GenerateCostDetailsReportOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_operation(
                self, 
                scope: str, 
                parameters: GenerateCostDetailsReportRequestDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CostDetailsOperationResults]: ...

        @overload
        def begin_create_operation(
                self, 
                scope: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CostDetailsOperationResults]: ...

        @distributed_trace
        def begin_get_operation_results(
                self, 
                scope: str, 
                operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[CostDetailsOperationResults]: ...


    class azure.mgmt.costmanagement.operations.GenerateDetailedCostReportOperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_get(
                self, 
                operation_id: str, 
                scope: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[GenerateDetailedCostReportOperationResult]: ...


    class azure.mgmt.costmanagement.operations.GenerateDetailedCostReportOperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                operation_id: str, 
                scope: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GenerateDetailedCostReportOperationStatuses: ...


    class azure.mgmt.costmanagement.operations.GenerateDetailedCostReportOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_operation(
                self, 
                scope: str, 
                parameters: GenerateDetailedCostReportDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GenerateDetailedCostReportOperationResult]: ...

        @overload
        def begin_create_operation(
                self, 
                scope: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GenerateDetailedCostReportOperationResult]: ...


    class azure.mgmt.costmanagement.operations.GenerateReservationDetailsReportOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_by_billing_account_id(
                self, 
                billing_account_id: str, 
                start_date: str, 
                end_date: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatus]: ...

        @distributed_trace
        def begin_by_billing_profile_id(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                start_date: str, 
                end_date: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatus]: ...


    class azure.mgmt.costmanagement.operations.Operations:

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
            ) -> Iterable[CostManagementOperation]: ...


    class azure.mgmt.costmanagement.operations.PriceSheetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_download(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[DownloadURL]: ...

        @distributed_trace
        def begin_download_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[DownloadURL]: ...


    class azure.mgmt.costmanagement.operations.QueryOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def usage(
                self, 
                scope: str, 
                parameters: QueryDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[QueryResult]: ...

        @overload
        def usage(
                self, 
                scope: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[QueryResult]: ...

        @overload
        def usage_by_external_cloud_provider_type(
                self, 
                external_cloud_provider_type: Union[str, ExternalCloudProviderType], 
                external_cloud_provider_id: str, 
                parameters: QueryDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryResult: ...

        @overload
        def usage_by_external_cloud_provider_type(
                self, 
                external_cloud_provider_type: Union[str, ExternalCloudProviderType], 
                external_cloud_provider_id: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryResult: ...


    class azure.mgmt.costmanagement.operations.ScheduledActionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def check_name_availability(
                self, 
                check_name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                check_name_availability_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability_by_scope(
                self, 
                scope: str, 
                check_name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability_by_scope(
                self, 
                scope: str, 
                check_name_availability_request: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def create_or_update(
                self, 
                name: str, 
                scheduled_action: ScheduledAction, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @overload
        def create_or_update(
                self, 
                name: str, 
                scheduled_action: IO, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @overload
        def create_or_update_by_scope(
                self, 
                scope: str, 
                name: str, 
                scheduled_action: ScheduledAction, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @overload
        def create_or_update_by_scope(
                self, 
                scope: str, 
                name: str, 
                scheduled_action: IO, 
                if_match: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @distributed_trace
        def delete(
                self, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_by_scope(
                self, 
                scope: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @distributed_trace
        def get_by_scope(
                self, 
                scope: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ScheduledAction]: ...

        @distributed_trace
        def list_by_scope(
                self, 
                scope: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ScheduledAction]: ...

        @distributed_trace
        def run(
                self, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def run_by_scope(
                self, 
                scope: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.costmanagement.operations.ViewsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                view_name: str, 
                parameters: View, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> View: ...

        @overload
        def create_or_update(
                self, 
                view_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> View: ...

        @overload
        def create_or_update_by_scope(
                self, 
                scope: str, 
                view_name: str, 
                parameters: View, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> View: ...

        @overload
        def create_or_update_by_scope(
                self, 
                scope: str, 
                view_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> View: ...

        @distributed_trace
        def delete(
                self, 
                view_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_by_scope(
                self, 
                scope: str, 
                view_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                view_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> View: ...

        @distributed_trace
        def get_by_scope(
                self, 
                scope: str, 
                view_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> View: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[View]: ...

        @distributed_trace
        def list_by_scope(
                self, 
                scope: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[View]: ...


```