```py
namespace azure.mgmt.costmanagement

    class azure.mgmt.costmanagement.CostManagementClient: implements ContextManager 
        alerts: AlertsOperations
        benefit_recommendations: BenefitRecommendationsOperations
        benefit_utilization_summaries: BenefitUtilizationSummariesOperations
        budgets: BudgetsOperations
        cost_allocation_rules: CostAllocationRulesOperations
        dimensions: DimensionsOperations
        exports: ExportsOperations
        forecast: ForecastOperations
        generate_benefit_utilization_summaries_report: GenerateBenefitUtilizationSummariesReportOperations
        generate_cost_details_report: GenerateCostDetailsReportOperations
        generate_detailed_cost_report: GenerateDetailedCostReportOperations
        generate_detailed_cost_report_operation_results: GenerateDetailedCostReportOperationResultsOperations
        generate_detailed_cost_report_operation_status: GenerateDetailedCostReportOperationStatusOperations
        generate_reservation_details_report: GenerateReservationDetailsReportOperations
        operations: Operations
        price_sheet: PriceSheetOperations
        query: QueryOperations
        scheduled_actions: ScheduledActionsOperations
        settings: SettingsOperations
        views: ViewsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
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


namespace azure.mgmt.costmanagement.aio

    class azure.mgmt.costmanagement.aio.CostManagementClient: implements AsyncContextManager 
        alerts: AlertsOperations
        benefit_recommendations: BenefitRecommendationsOperations
        benefit_utilization_summaries: BenefitUtilizationSummariesOperations
        budgets: BudgetsOperations
        cost_allocation_rules: CostAllocationRulesOperations
        dimensions: DimensionsOperations
        exports: ExportsOperations
        forecast: ForecastOperations
        generate_benefit_utilization_summaries_report: GenerateBenefitUtilizationSummariesReportOperations
        generate_cost_details_report: GenerateCostDetailsReportOperations
        generate_detailed_cost_report: GenerateDetailedCostReportOperations
        generate_detailed_cost_report_operation_results: GenerateDetailedCostReportOperationResultsOperations
        generate_detailed_cost_report_operation_status: GenerateDetailedCostReportOperationStatusOperations
        generate_reservation_details_report: GenerateReservationDetailsReportOperations
        operations: Operations
        price_sheet: PriceSheetOperations
        query: QueryOperations
        scheduled_actions: ScheduledActionsOperations
        settings: SettingsOperations
        views: ViewsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                alert_id: str, 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace_async
        async def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AlertsResult: ...

        @distributed_trace_async
        async def list_external(
                self, 
                external_cloud_provider_type: Union[str, ExternalCloudProviderType], 
                external_cloud_provider_id: str, 
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
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BenefitRecommendationModel]: ...


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
                *, 
                filter: Optional[str] = ..., 
                grain_parameter: Optional[Union[str, GrainParameter]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BenefitUtilizationSummary]: ...

        @distributed_trace
        def list_by_billing_profile_id(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                *, 
                filter: Optional[str] = ..., 
                grain_parameter: Optional[Union[str, GrainParameter]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BenefitUtilizationSummary]: ...

        @distributed_trace
        def list_by_savings_plan_id(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                *, 
                filter: Optional[str] = ..., 
                grain_parameter: Optional[Union[str, GrainParameter]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BenefitUtilizationSummary]: ...

        @distributed_trace
        def list_by_savings_plan_order(
                self, 
                savings_plan_order_id: str, 
                *, 
                filter: Optional[str] = ..., 
                grain_parameter: Optional[Union[str, GrainParameter]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BenefitUtilizationSummary]: ...


    class azure.mgmt.costmanagement.aio.operations.BudgetsOperations:

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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Budget]: ...


    class azure.mgmt.costmanagement.aio.operations.CostAllocationRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def check_name_availability(
                self, 
                billing_account_id: str, 
                cost_allocation_rule_check_name_availability_request: CostAllocationRuleCheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CostAllocationRuleCheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                billing_account_id: str, 
                cost_allocation_rule_check_name_availability_request: CostAllocationRuleCheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CostAllocationRuleCheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                billing_account_id: str, 
                cost_allocation_rule_check_name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CostAllocationRuleCheckNameAvailabilityResponse: ...

        @overload
        async def create_or_update(
                self, 
                billing_account_id: str, 
                rule_name: str, 
                cost_allocation_rule: CostAllocationRuleDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CostAllocationRuleDefinition: ...

        @overload
        async def create_or_update(
                self, 
                billing_account_id: str, 
                rule_name: str, 
                cost_allocation_rule: CostAllocationRuleDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CostAllocationRuleDefinition: ...

        @overload
        async def create_or_update(
                self, 
                billing_account_id: str, 
                rule_name: str, 
                cost_allocation_rule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CostAllocationRuleDefinition: ...

        @distributed_trace_async
        async def delete(
                self, 
                billing_account_id: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                billing_account_id: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> CostAllocationRuleDefinition: ...

        @distributed_trace
        def list(
                self, 
                billing_account_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CostAllocationRuleDefinition]: ...


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
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                skiptoken: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Dimension]: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                skiptoken: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Dimension]: ...


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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Export: ...

        @distributed_trace_async
        async def delete(
                self, 
                scope: str, 
                export_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def execute(
                self, 
                scope: str, 
                export_name: str, 
                parameters: Optional[ExportRunRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def execute(
                self, 
                scope: str, 
                export_name: str, 
                parameters: Optional[ExportRunRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def execute(
                self, 
                scope: str, 
                export_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                export_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> Export: ...

        @distributed_trace_async
        async def get_execution_history(
                self, 
                scope: str, 
                export_name: str, 
                **kwargs: Any
            ) -> ExportExecutionListResult: ...

        @distributed_trace_async
        async def list(
                self, 
                scope: str, 
                *, 
                expand: Optional[str] = ..., 
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
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ForecastResult: ...

        @overload
        async def external_cloud_provider_usage(
                self, 
                external_cloud_provider_type: Union[str, ExternalCloudProviderType], 
                external_cloud_provider_id: str, 
                parameters: ForecastDefinition, 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ForecastResult: ...

        @overload
        async def external_cloud_provider_usage(
                self, 
                external_cloud_provider_type: Union[str, ExternalCloudProviderType], 
                external_cloud_provider_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ForecastResult: ...

        @overload
        async def usage(
                self, 
                scope: str, 
                parameters: ForecastDefinition, 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> Optional[ForecastResult]: ...

        @overload
        async def usage(
                self, 
                scope: str, 
                parameters: ForecastDefinition, 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> Optional[ForecastResult]: ...

        @overload
        async def usage(
                self, 
                scope: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> Optional[ForecastResult]: ...


    class azure.mgmt.costmanagement.aio.operations.GenerateBenefitUtilizationSummariesReportOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_generate_by_billing_account(
                self, 
                billing_account_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        async def begin_generate_by_billing_account(
                self, 
                billing_account_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        async def begin_generate_by_billing_account(
                self, 
                billing_account_id: str, 
                benefit_utilization_summaries_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        async def begin_generate_by_billing_profile(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        async def begin_generate_by_billing_profile(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        async def begin_generate_by_billing_profile(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                benefit_utilization_summaries_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        async def begin_generate_by_reservation_id(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        async def begin_generate_by_reservation_id(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        async def begin_generate_by_reservation_id(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                benefit_utilization_summaries_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        async def begin_generate_by_reservation_order_id(
                self, 
                reservation_order_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        async def begin_generate_by_reservation_order_id(
                self, 
                reservation_order_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        async def begin_generate_by_reservation_order_id(
                self, 
                reservation_order_id: str, 
                benefit_utilization_summaries_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        async def begin_generate_by_savings_plan_id(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        async def begin_generate_by_savings_plan_id(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        async def begin_generate_by_savings_plan_id(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                benefit_utilization_summaries_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        async def begin_generate_by_savings_plan_order_id(
                self, 
                savings_plan_order_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        async def begin_generate_by_savings_plan_order_id(
                self, 
                savings_plan_order_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        async def begin_generate_by_savings_plan_order_id(
                self, 
                savings_plan_order_id: str, 
                benefit_utilization_summaries_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BenefitUtilizationSummariesOperationStatus]: ...


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
                parameters: GenerateCostDetailsReportRequestDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CostDetailsOperationResults]: ...

        @overload
        async def begin_create_operation(
                self, 
                scope: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CostDetailsOperationResults]: ...

        @distributed_trace_async
        async def begin_get_operation_results(
                self, 
                scope: str, 
                operation_id: str, 
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
                parameters: GenerateDetailedCostReportDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GenerateDetailedCostReportOperationResult]: ...

        @overload
        async def begin_create_operation(
                self, 
                scope: str, 
                parameters: IO[bytes], 
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
                *, 
                end_date: str, 
                start_date: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatus]: ...

        @distributed_trace_async
        async def begin_by_billing_profile_id(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                *, 
                end_date: str, 
                start_date: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatus]: ...


    class azure.mgmt.costmanagement.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[CostManagementOperation]: ...


    class azure.mgmt.costmanagement.aio.operations.PriceSheetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_download_by_billing_account(
                self, 
                billing_account_id: str, 
                billing_period_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatus]: ...

        @distributed_trace_async
        async def begin_download_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[PricesheetDownloadProperties]: ...

        @distributed_trace_async
        async def begin_download_by_invoice(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_name: str, 
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
                parameters: QueryDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[QueryResult]: ...

        @overload
        async def usage(
                self, 
                scope: str, 
                parameters: IO[bytes], 
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
                parameters: IO[bytes], 
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
                check_name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                check_name_availability_request: IO[bytes], 
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
                check_name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability_by_scope(
                self, 
                scope: str, 
                check_name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def create_or_update(
                self, 
                name: str, 
                scheduled_action: ScheduledAction, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @overload
        async def create_or_update(
                self, 
                name: str, 
                scheduled_action: ScheduledAction, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @overload
        async def create_or_update(
                self, 
                name: str, 
                scheduled_action: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @overload
        async def create_or_update_by_scope(
                self, 
                scope: str, 
                name: str, 
                scheduled_action: ScheduledAction, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @overload
        async def create_or_update_by_scope(
                self, 
                scope: str, 
                name: str, 
                scheduled_action: ScheduledAction, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @overload
        async def create_or_update_by_scope(
                self, 
                scope: str, 
                name: str, 
                scheduled_action: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @distributed_trace_async
        async def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_by_scope(
                self, 
                scope: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @distributed_trace_async
        async def get_by_scope(
                self, 
                scope: str, 
                name: str, 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ScheduledAction]: ...

        @distributed_trace
        def list_by_scope(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ScheduledAction]: ...

        @distributed_trace_async
        async def run(
                self, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def run_by_scope(
                self, 
                scope: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.costmanagement.aio.operations.SettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update_by_scope(
                self, 
                scope: str, 
                type: Union[str, SettingType], 
                setting: Setting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Setting: ...

        @overload
        async def create_or_update_by_scope(
                self, 
                scope: str, 
                type: Union[str, SettingType], 
                setting: Setting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Setting: ...

        @overload
        async def create_or_update_by_scope(
                self, 
                scope: str, 
                type: Union[str, SettingType], 
                setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Setting: ...

        @distributed_trace_async
        async def delete_by_scope(
                self, 
                scope: str, 
                type: Union[str, SettingType], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_by_scope(
                self, 
                scope: str, 
                type: Union[str, SettingType], 
                **kwargs: Any
            ) -> Setting: ...

        @distributed_trace_async
        async def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> SettingsListResult: ...


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
                parameters: View, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> View: ...

        @overload
        async def create_or_update(
                self, 
                view_name: str, 
                parameters: IO[bytes], 
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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> View: ...

        @distributed_trace_async
        async def delete(
                self, 
                view_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_by_scope(
                self, 
                scope: str, 
                view_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                view_name: str, 
                **kwargs: Any
            ) -> View: ...

        @distributed_trace_async
        async def get_by_scope(
                self, 
                scope: str, 
                view_name: str, 
                **kwargs: Any
            ) -> View: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[View]: ...

        @distributed_trace
        def list_by_scope(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[View]: ...


namespace azure.mgmt.costmanagement.models

    class azure.mgmt.costmanagement.models.AccumulatedType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "false"
        TRUE = "true"


    class azure.mgmt.costmanagement.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.costmanagement.models.Alert(ExtensionResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[AlertProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                properties: Optional[AlertProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


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


    class azure.mgmt.costmanagement.models.AlertProperties(_Model):
        close_time: Optional[str]
        cost_entity_id: Optional[str]
        creation_time: Optional[str]
        definition: Optional[AlertPropertiesDefinition]
        description: Optional[str]
        details: Optional[AlertPropertiesDetails]
        modification_time: Optional[str]
        source: Optional[Union[str, AlertSource]]
        status: Optional[Union[str, AlertStatus]]
        status_modification_time: Optional[str]
        status_modification_user_name: Optional[str]

        @overload
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
                status_modification_user_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.AlertPropertiesDefinition(_Model):
        category: Optional[Union[str, AlertCategory]]
        criteria: Optional[Union[str, AlertCriteria]]
        type: Optional[Union[str, AlertType]]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[Union[str, AlertCategory]] = ..., 
                criteria: Optional[Union[str, AlertCriteria]] = ..., 
                type: Optional[Union[str, AlertType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.AlertPropertiesDetails(_Model):
        amount: Optional[Decimal]
        company_name: Optional[str]
        contact_emails: Optional[list[str]]
        contact_groups: Optional[list[str]]
        contact_roles: Optional[list[str]]
        current_spend: Optional[Decimal]
        department_name: Optional[str]
        enrollment_end_date: Optional[str]
        enrollment_number: Optional[str]
        enrollment_start_date: Optional[str]
        invoicing_threshold: Optional[Decimal]
        meter_filter: Optional[list[Any]]
        operator: Optional[Union[str, AlertOperator]]
        overriding_alert: Optional[str]
        period_start_date: Optional[str]
        resource_filter: Optional[list[Any]]
        resource_group_filter: Optional[list[Any]]
        tag_filter: Optional[Any]
        threshold: Optional[Decimal]
        time_grain_type: Optional[Union[str, AlertTimeGrainType]]
        triggered_by: Optional[str]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                amount: Optional[Decimal] = ..., 
                company_name: Optional[str] = ..., 
                contact_emails: Optional[list[str]] = ..., 
                contact_groups: Optional[list[str]] = ..., 
                contact_roles: Optional[list[str]] = ..., 
                current_spend: Optional[Decimal] = ..., 
                department_name: Optional[str] = ..., 
                enrollment_end_date: Optional[str] = ..., 
                enrollment_number: Optional[str] = ..., 
                enrollment_start_date: Optional[str] = ..., 
                invoicing_threshold: Optional[Decimal] = ..., 
                meter_filter: Optional[list[Any]] = ..., 
                operator: Optional[Union[str, AlertOperator]] = ..., 
                overriding_alert: Optional[str] = ..., 
                period_start_date: Optional[str] = ..., 
                resource_filter: Optional[list[Any]] = ..., 
                resource_group_filter: Optional[list[Any]] = ..., 
                tag_filter: Optional[Any] = ..., 
                threshold: Optional[Decimal] = ..., 
                time_grain_type: Optional[Union[str, AlertTimeGrainType]] = ..., 
                triggered_by: Optional[str] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.costmanagement.models.AlertsResult(_Model):
        next_link: Optional[str]
        value: Optional[list[Alert]]


    class azure.mgmt.costmanagement.models.AllSavingsBenefitDetails(_Model):
        average_utilization_percentage: Optional[Decimal]
        benefit_cost: Optional[Decimal]
        commitment_amount: Optional[Decimal]
        coverage_percentage: Optional[Decimal]
        overage_cost: Optional[Decimal]
        savings_amount: Optional[Decimal]
        savings_percentage: Optional[Decimal]
        total_cost: Optional[Decimal]
        wastage_cost: Optional[Decimal]


    class azure.mgmt.costmanagement.models.AllSavingsList(_Model):
        next_link: Optional[str]
        value: Optional[list[AllSavingsBenefitDetails]]


    class azure.mgmt.costmanagement.models.ArmErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.AsyncOperationStatusProperties(_Model):
        report_url: Optional[Union[str, BenefitUtilizationSummaryReportSchema]]
        secondary_report_url: Optional[Union[str, BenefitUtilizationSummaryReportSchema]]
        valid_until: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                report_url: Optional[Union[str, BenefitUtilizationSummaryReportSchema]] = ..., 
                secondary_report_url: Optional[Union[str, BenefitUtilizationSummaryReportSchema]] = ..., 
                valid_until: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.BenefitKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INCLUDED_QUANTITY = "IncludedQuantity"
        RESERVATION = "Reservation"
        SAVINGS_PLAN = "SavingsPlan"


    class azure.mgmt.costmanagement.models.BenefitRecommendationModel(BenefitResource):
        id: str
        kind: Union[str, BenefitKind]
        name: str
        properties: Optional[BenefitRecommendationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, BenefitKind]] = ..., 
                properties: Optional[BenefitRecommendationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.BenefitRecommendationProperties(_Model):
        all_recommendation_details: Optional[AllSavingsList]
        arm_sku_name: Optional[str]
        commitment_granularity: Optional[Union[str, Grain]]
        cost_without_benefit: Optional[Decimal]
        currency_code: Optional[str]
        first_consumption_date: Optional[datetime]
        last_consumption_date: Optional[datetime]
        look_back_period: Optional[Union[str, LookBackPeriod]]
        recommendation_details: Optional[AllSavingsBenefitDetails]
        scope: str
        term: Optional[Union[str, Term]]
        total_hours: Optional[int]
        usage: Optional[RecommendationUsageDetails]

        @overload
        def __init__(
                self, 
                *, 
                commitment_granularity: Optional[Union[str, Grain]] = ..., 
                look_back_period: Optional[Union[str, LookBackPeriod]] = ..., 
                recommendation_details: Optional[AllSavingsBenefitDetails] = ..., 
                scope: str, 
                term: Optional[Union[str, Term]] = ..., 
                usage: Optional[RecommendationUsageDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.BenefitResource(Resource):
        id: str
        kind: Optional[Union[str, BenefitKind]]
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, BenefitKind]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.BenefitUtilizationSummariesOperationStatus(_Model):
        input: Optional[BenefitUtilizationSummariesRequest]
        properties: Optional[AsyncOperationStatusProperties]
        status: Optional[Union[str, OperationStatusType]]

        @overload
        def __init__(
                self, 
                *, 
                input: Optional[BenefitUtilizationSummariesRequest] = ..., 
                properties: Optional[AsyncOperationStatusProperties] = ..., 
                status: Optional[Union[str, OperationStatusType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.BenefitUtilizationSummariesRequest(_Model):
        benefit_id: Optional[str]
        benefit_order_id: Optional[str]
        billing_account_id: Optional[str]
        billing_profile_id: Optional[str]
        end_date: datetime
        grain: Union[str, Grain]
        kind: Optional[Union[str, BenefitKind]]
        start_date: datetime

        @overload
        def __init__(
                self, 
                *, 
                benefit_id: Optional[str] = ..., 
                benefit_order_id: Optional[str] = ..., 
                billing_account_id: Optional[str] = ..., 
                billing_profile_id: Optional[str] = ..., 
                end_date: datetime, 
                grain: Union[str, Grain], 
                kind: Optional[Union[str, BenefitKind]] = ..., 
                start_date: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.BenefitUtilizationSummary(Resource):
        id: str
        kind: str
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.BenefitUtilizationSummaryProperties(_Model):
        arm_sku_name: Optional[str]
        benefit_id: Optional[str]
        benefit_order_id: Optional[str]
        benefit_type: Optional[Union[str, BenefitKind]]
        usage_date: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                benefit_type: Optional[Union[str, BenefitKind]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.BenefitUtilizationSummaryReportSchema(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVG_UTILIZATION_PERCENTAGE = "AvgUtilizationPercentage"
        BENEFIT_ID = "BenefitId"
        BENEFIT_ORDER_ID = "BenefitOrderId"
        BENEFIT_TYPE = "BenefitType"
        KIND = "Kind"
        MAX_UTILIZATION_PERCENTAGE = "MaxUtilizationPercentage"
        MIN_UTILIZATION_PERCENTAGE = "MinUtilizationPercentage"
        USAGE_DATE = "UsageDate"
        UTILIZED_PERCENTAGE = "UtilizedPercentage"


    class azure.mgmt.costmanagement.models.BlobInfo(_Model):
        blob_link: Optional[str]
        byte_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                blob_link: Optional[str] = ..., 
                byte_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.Budget(ExtensionResource):
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


    class azure.mgmt.costmanagement.models.BudgetComparisonExpression(_Model):
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


    class azure.mgmt.costmanagement.models.BudgetFilter(_Model):
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


    class azure.mgmt.costmanagement.models.BudgetFilterProperties(_Model):
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


    class azure.mgmt.costmanagement.models.BudgetNotificationOperatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUAL_TO = "EqualTo"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL_TO = "GreaterThanOrEqualTo"
        LESS_THAN = "LessThan"


    class azure.mgmt.costmanagement.models.BudgetOperatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IN = "In"


    class azure.mgmt.costmanagement.models.BudgetProperties(_Model):
        amount: Optional[float]
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
                amount: Optional[float] = ..., 
                category: Union[str, CategoryType], 
                filter: Optional[BudgetFilter] = ..., 
                notifications: Optional[dict[str, Notification]] = ..., 
                time_grain: Union[str, TimeGrainType], 
                time_period: BudgetTimePeriod
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.BudgetTimePeriod(_Model):
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


    class azure.mgmt.costmanagement.models.CategoryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COST = "Cost"
        RESERVATION_UTILIZATION = "ReservationUtilization"


    class azure.mgmt.costmanagement.models.ChartType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AREA = "Area"
        GROUPED_COLUMN = "GroupedColumn"
        LINE = "Line"
        STACKED_COLUMN = "StackedColumn"
        TABLE = "Table"


    class azure.mgmt.costmanagement.models.CheckNameAvailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.costmanagement.models.CheckNameAvailabilityRequest(_Model):
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


    class azure.mgmt.costmanagement.models.CheckNameAvailabilityResponse(_Model):
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


    class azure.mgmt.costmanagement.models.CommonExportProperties(_Model):
        compression_mode: Optional[Union[str, CompressionModeType]]
        data_overwrite_behavior: Optional[Union[str, DataOverwriteBehaviorType]]
        definition: ExportDefinition
        delivery_info: ExportDeliveryInfo
        export_description: Optional[str]
        format: Optional[Union[str, FormatType]]
        next_run_time_estimate: Optional[datetime]
        partition_data: Optional[bool]
        run_history: Optional[ExportExecutionListResult]
        system_suspension_context: Optional[ExportSuspensionContext]

        @overload
        def __init__(
                self, 
                *, 
                compression_mode: Optional[Union[str, CompressionModeType]] = ..., 
                data_overwrite_behavior: Optional[Union[str, DataOverwriteBehaviorType]] = ..., 
                definition: ExportDefinition, 
                delivery_info: ExportDeliveryInfo, 
                export_description: Optional[str] = ..., 
                format: Optional[Union[str, FormatType]] = ..., 
                partition_data: Optional[bool] = ..., 
                run_history: Optional[ExportExecutionListResult] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.CompressionModeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GZIP = "gzip"
        NONE = "none"
        SNAPPY = "snappy"


    class azure.mgmt.costmanagement.models.CostAllocationPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIXED_PROPORTION = "FixedProportion"


    class azure.mgmt.costmanagement.models.CostAllocationProportion(_Model):
        name: str
        percentage: float

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                percentage: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.CostAllocationResource(_Model):
        name: str
        resource_type: Union[str, CostAllocationResourceType]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                resource_type: Union[str, CostAllocationResourceType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.CostAllocationResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIMENSION = "Dimension"
        TAG = "Tag"


    class azure.mgmt.costmanagement.models.CostAllocationRuleCheckNameAvailabilityRequest(_Model):
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


    class azure.mgmt.costmanagement.models.CostAllocationRuleCheckNameAvailabilityResponse(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[Union[str, Reason]]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[Union[str, Reason]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.CostAllocationRuleDefinition(ProxyResource):
        id: str
        name: str
        properties: Optional[CostAllocationRuleProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CostAllocationRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.CostAllocationRuleDetails(_Model):
        source_resources: Optional[list[SourceCostAllocationResource]]
        target_resources: Optional[list[TargetCostAllocationResource]]

        @overload
        def __init__(
                self, 
                *, 
                source_resources: Optional[list[SourceCostAllocationResource]] = ..., 
                target_resources: Optional[list[TargetCostAllocationResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.CostAllocationRuleProperties(_Model):
        created_date: Optional[datetime]
        description: Optional[str]
        details: CostAllocationRuleDetails
        status: Union[str, RuleStatus]
        updated_date: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                details: CostAllocationRuleDetails, 
                status: Union[str, RuleStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.CostDetailsDataFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CSV_COST_DETAILS_DATA_FORMAT = "Csv"


    class azure.mgmt.costmanagement.models.CostDetailsMetricType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTUAL_COST_COST_DETAILS_METRIC_TYPE = "ActualCost"
        AMORTIZED_COST_COST_DETAILS_METRIC_TYPE = "AmortizedCost"


    class azure.mgmt.costmanagement.models.CostDetailsOperationResults(_Model):
        error: Optional[ErrorDetails]
        id: Optional[str]
        manifest: Optional[ReportManifest]
        name: Optional[str]
        status: Optional[Union[str, CostDetailsStatusType]]
        type: Optional[str]
        valid_till: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetails] = ..., 
                id: Optional[str] = ..., 
                manifest: Optional[ReportManifest] = ..., 
                name: Optional[str] = ..., 
                status: Optional[Union[str, CostDetailsStatusType]] = ..., 
                type: Optional[str] = ..., 
                valid_till: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.CostDetailsStatusType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED_COST_DETAILS_STATUS_TYPE = "Completed"
        FAILED_COST_DETAILS_STATUS_TYPE = "Failed"
        NO_DATA_FOUND_COST_DETAILS_STATUS_TYPE = "NoDataFound"


    class azure.mgmt.costmanagement.models.CostDetailsTimePeriod(_Model):
        end: str
        start: str

        @overload
        def __init__(
                self, 
                *, 
                end: str, 
                start: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.CostManagementOperation(Operation):
        action_type: Union[str, ActionType]
        display: OperationDisplay
        id: Optional[str]
        is_data_action: bool
        name: str
        origin: Union[str, Origin]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.CostManagementProxyResource(_Model):
        e_tag: Optional[str]
        id: Optional[str]
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.CostManagementResource(_Model):
        e_tag: Optional[str]
        id: Optional[str]
        location: Optional[str]
        name: Optional[str]
        sku: Optional[str]
        tags: Optional[dict[str, str]]
        type: Optional[str]


    class azure.mgmt.costmanagement.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.costmanagement.models.CultureCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


    class azure.mgmt.costmanagement.models.CurrentSpend(_Model):
        amount: Optional[float]
        unit: Optional[str]


    class azure.mgmt.costmanagement.models.DataOverwriteBehaviorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE_NEW_REPORT = "CreateNewReport"
        OVERWRITE_PREVIOUS_REPORT = "OverwritePreviousReport"


    class azure.mgmt.costmanagement.models.DaysOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.costmanagement.models.DestinationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BLOB = "AzureBlob"


    class azure.mgmt.costmanagement.models.Dimension(CostManagementResource):
        e_tag: str
        id: str
        location: str
        name: str
        properties: Optional[DimensionProperties]
        sku: str
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DimensionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.costmanagement.models.DimensionProperties(_Model):
        category: Optional[str]
        data: Optional[list[str]]
        description: Optional[str]
        filter_enabled: Optional[bool]
        grouping_enabled: Optional[bool]
        next_link: Optional[str]
        total: Optional[int]
        usage_end: Optional[datetime]
        usage_start: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                data: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.DismissAlertPayload(_Model):
        properties: Optional[AlertProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AlertProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.costmanagement.models.DownloadURL(_Model):
        download_url: Optional[str]
        expiry_time: Optional[datetime]
        valid_till: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                download_url: Optional[str] = ..., 
                valid_till: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.costmanagement.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.costmanagement.models.ErrorDetails(_Model):
        code: Optional[str]
        message: Optional[str]


    class azure.mgmt.costmanagement.models.ErrorDetailsWithNestedDetails(ErrorDetails):
        code: str
        details: Optional[list[ErrorDetailsWithNestedDetails]]
        message: str


    class azure.mgmt.costmanagement.models.ErrorResponse(_Model):
        error: Optional[ErrorDetails]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ErrorResponseWithNestedDetails(_Model):
        error: Optional[ErrorDetailsWithNestedDetails]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetailsWithNestedDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.costmanagement.models.Export(ExtensionResource):
        e_tag: Optional[str]
        id: str
        identity: Optional[SystemAssignedServiceIdentity]
        location: Optional[str]
        name: str
        properties: Optional[ExportProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                identity: Optional[SystemAssignedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ExportProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.costmanagement.models.ExportDataset(_Model):
        configuration: Optional[ExportDatasetConfiguration]
        granularity: Optional[Union[str, GranularityType]]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[ExportDatasetConfiguration] = ..., 
                granularity: Optional[Union[str, GranularityType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ExportDatasetConfiguration(_Model):
        columns: Optional[list[str]]
        data_version: Optional[str]
        filters: Optional[list[FilterItems]]

        @overload
        def __init__(
                self, 
                *, 
                columns: Optional[list[str]] = ..., 
                data_version: Optional[str] = ..., 
                filters: Optional[list[FilterItems]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ExportDefinition(_Model):
        data_set: Optional[ExportDataset]
        time_period: Optional[ExportTimePeriod]
        timeframe: Union[str, TimeframeType]
        type: Union[str, ExportType]

        @overload
        def __init__(
                self, 
                *, 
                data_set: Optional[ExportDataset] = ..., 
                time_period: Optional[ExportTimePeriod] = ..., 
                timeframe: Union[str, TimeframeType], 
                type: Union[str, ExportType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ExportDeliveryDestination(_Model):
        container: str
        resource_id: Optional[str]
        root_folder_path: Optional[str]
        sas_token: Optional[str]
        storage_account: Optional[str]
        type: Optional[Union[str, DestinationType]]

        @overload
        def __init__(
                self, 
                *, 
                container: str, 
                resource_id: Optional[str] = ..., 
                root_folder_path: Optional[str] = ..., 
                sas_token: Optional[str] = ..., 
                storage_account: Optional[str] = ..., 
                type: Optional[Union[str, DestinationType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ExportDeliveryInfo(_Model):
        destination: ExportDeliveryDestination

        @overload
        def __init__(
                self, 
                *, 
                destination: ExportDeliveryDestination
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ExportExecutionListResult(_Model):
        value: Optional[list[ExportRun]]


    class azure.mgmt.costmanagement.models.ExportListResult(_Model):
        value: Optional[list[Export]]


    class azure.mgmt.costmanagement.models.ExportProperties(CommonExportProperties):
        compression_mode: Union[str, CompressionModeType]
        data_overwrite_behavior: Union[str, DataOverwriteBehaviorType]
        definition: ExportDefinition
        delivery_info: ExportDeliveryInfo
        export_description: str
        format: Union[str, FormatType]
        next_run_time_estimate: datetime
        partition_data: bool
        run_history: ExportExecutionListResult
        schedule: Optional[ExportSchedule]
        system_suspension_context: ExportSuspensionContext

        @overload
        def __init__(
                self, 
                *, 
                compression_mode: Optional[Union[str, CompressionModeType]] = ..., 
                data_overwrite_behavior: Optional[Union[str, DataOverwriteBehaviorType]] = ..., 
                definition: ExportDefinition, 
                delivery_info: ExportDeliveryInfo, 
                export_description: Optional[str] = ..., 
                format: Optional[Union[str, FormatType]] = ..., 
                partition_data: Optional[bool] = ..., 
                run_history: Optional[ExportExecutionListResult] = ..., 
                schedule: Optional[ExportSchedule] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ExportRecurrencePeriod(_Model):
        from_property: datetime
        to: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                from_property: datetime, 
                to: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ExportRun(CostManagementProxyResource):
        e_tag: str
        id: str
        name: str
        properties: Optional[ExportRunProperties]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                properties: Optional[ExportRunProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.costmanagement.models.ExportRunProperties(_Model):
        end_date: Optional[datetime]
        error: Optional[ErrorDetails]
        execution_type: Optional[Union[str, ExecutionType]]
        file_name: Optional[str]
        manifest_file: Optional[str]
        processing_end_time: Optional[datetime]
        processing_start_time: Optional[datetime]
        run_settings: Optional[CommonExportProperties]
        start_date: Optional[datetime]
        status: Optional[Union[str, ExecutionStatus]]
        submitted_by: Optional[str]
        submitted_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                end_date: Optional[datetime] = ..., 
                error: Optional[ErrorDetails] = ..., 
                execution_type: Optional[Union[str, ExecutionType]] = ..., 
                file_name: Optional[str] = ..., 
                manifest_file: Optional[str] = ..., 
                processing_end_time: Optional[datetime] = ..., 
                processing_start_time: Optional[datetime] = ..., 
                run_settings: Optional[CommonExportProperties] = ..., 
                start_date: Optional[datetime] = ..., 
                status: Optional[Union[str, ExecutionStatus]] = ..., 
                submitted_by: Optional[str] = ..., 
                submitted_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ExportRunRequest(_Model):
        time_period: Optional[ExportTimePeriod]

        @overload
        def __init__(
                self, 
                *, 
                time_period: Optional[ExportTimePeriod] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ExportSchedule(_Model):
        recurrence: Optional[Union[str, RecurrenceType]]
        recurrence_period: Optional[ExportRecurrencePeriod]
        status: Optional[Union[str, StatusType]]

        @overload
        def __init__(
                self, 
                *, 
                recurrence: Optional[Union[str, RecurrenceType]] = ..., 
                recurrence_period: Optional[ExportRecurrencePeriod] = ..., 
                status: Optional[Union[str, StatusType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ExportSuspensionContext(_Model):
        suspension_code: Optional[str]
        suspension_reason: Optional[str]
        suspension_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                suspension_code: Optional[str] = ..., 
                suspension_reason: Optional[str] = ..., 
                suspension_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ExportTimePeriod(_Model):
        from_property: datetime
        to: datetime

        @overload
        def __init__(
                self, 
                *, 
                from_property: datetime, 
                to: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ExportType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTUAL_COST = "ActualCost"
        AMORTIZED_COST = "AmortizedCost"
        FOCUS_COST = "FocusCost"
        PRICE_SHEET = "PriceSheet"
        RESERVATION_DETAILS = "ReservationDetails"
        RESERVATION_RECOMMENDATIONS = "ReservationRecommendations"
        RESERVATION_TRANSACTIONS = "ReservationTransactions"
        USAGE = "Usage"


    class azure.mgmt.costmanagement.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.costmanagement.models.ExternalCloudProviderType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTERNAL_BILLING_ACCOUNTS = "externalBillingAccounts"
        EXTERNAL_SUBSCRIPTIONS = "externalSubscriptions"


    class azure.mgmt.costmanagement.models.FileDestination(_Model):
        file_formats: Optional[list[Union[str, FileFormat]]]

        @overload
        def __init__(
                self, 
                *, 
                file_formats: Optional[list[Union[str, FileFormat]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.FileFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CSV = "Csv"


    class azure.mgmt.costmanagement.models.FilterItemNames(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOOK_BACK_PERIOD = "LookBackPeriod"
        RESERVATION_SCOPE = "ReservationScope"
        RESOURCE_TYPE = "ResourceType"


    class azure.mgmt.costmanagement.models.FilterItems(_Model):
        name: Optional[Union[str, FilterItemNames]]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[Union[str, FilterItemNames]] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ForecastAggregation(_Model):
        function: Union[str, FunctionType]
        name: Union[str, FunctionName]

        @overload
        def __init__(
                self, 
                *, 
                function: Union[str, FunctionType], 
                name: Union[str, FunctionName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ForecastColumn(_Model):
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


    class azure.mgmt.costmanagement.models.ForecastComparisonExpression(_Model):
        name: str
        operator: Union[str, ForecastOperatorType]
        values_property: list[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                operator: Union[str, ForecastOperatorType], 
                values_property: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ForecastDataset(_Model):
        aggregation: dict[str, ForecastAggregation]
        configuration: Optional[ForecastDatasetConfiguration]
        filter: Optional[ForecastFilter]
        granularity: Optional[Union[str, GranularityType]]

        @overload
        def __init__(
                self, 
                *, 
                aggregation: dict[str, ForecastAggregation], 
                configuration: Optional[ForecastDatasetConfiguration] = ..., 
                filter: Optional[ForecastFilter] = ..., 
                granularity: Optional[Union[str, GranularityType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ForecastDatasetConfiguration(_Model):
        columns: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                columns: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ForecastDefinition(_Model):
        dataset: ForecastDataset
        include_actual_cost: Optional[bool]
        include_fresh_partial_cost: Optional[bool]
        time_period: Optional[ForecastTimePeriod]
        timeframe: Union[str, ForecastTimeframe]
        type: Union[str, ForecastType]

        @overload
        def __init__(
                self, 
                *, 
                dataset: ForecastDataset, 
                include_actual_cost: Optional[bool] = ..., 
                include_fresh_partial_cost: Optional[bool] = ..., 
                time_period: Optional[ForecastTimePeriod] = ..., 
                timeframe: Union[str, ForecastTimeframe], 
                type: Union[str, ForecastType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ForecastFilter(_Model):
        and_property: Optional[list[ForecastFilter]]
        dimensions: Optional[ForecastComparisonExpression]
        or_property: Optional[list[ForecastFilter]]
        tags: Optional[ForecastComparisonExpression]

        @overload
        def __init__(
                self, 
                *, 
                and_property: Optional[list[ForecastFilter]] = ..., 
                dimensions: Optional[ForecastComparisonExpression] = ..., 
                or_property: Optional[list[ForecastFilter]] = ..., 
                tags: Optional[ForecastComparisonExpression] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ForecastOperatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IN = "In"


    class azure.mgmt.costmanagement.models.ForecastProperties(_Model):
        columns: Optional[list[ForecastColumn]]
        next_link: Optional[str]
        rows: Optional[list[list[Any]]]

        @overload
        def __init__(
                self, 
                *, 
                columns: Optional[list[ForecastColumn]] = ..., 
                next_link: Optional[str] = ..., 
                rows: Optional[list[list[Any]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ForecastResult(CostManagementResource):
        e_tag: str
        id: str
        location: str
        name: str
        properties: Optional[ForecastProperties]
        sku: str
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ForecastProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.costmanagement.models.ForecastSpend(_Model):
        amount: Optional[float]
        unit: Optional[str]


    class azure.mgmt.costmanagement.models.ForecastTimePeriod(_Model):
        from_property: datetime
        to: datetime

        @overload
        def __init__(
                self, 
                *, 
                from_property: datetime, 
                to: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ForecastTimeframe(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"


    class azure.mgmt.costmanagement.models.ForecastType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTUAL_COST = "ActualCost"
        AMORTIZED_COST = "AmortizedCost"
        USAGE = "Usage"


    class azure.mgmt.costmanagement.models.FormatType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CSV = "Csv"
        PARQUET = "Parquet"


    class azure.mgmt.costmanagement.models.Frequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        MONTHLY = "Monthly"
        WEEKLY = "Weekly"


    class azure.mgmt.costmanagement.models.FunctionName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COST = "Cost"
        COST_USD = "CostUSD"
        PRE_TAX_COST = "PreTaxCost"
        PRE_TAX_COST_USD = "PreTaxCostUSD"


    class azure.mgmt.costmanagement.models.FunctionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SUM = "Sum"


    class azure.mgmt.costmanagement.models.GenerateCostDetailsReportErrorResponse(_Model):
        error: Optional[ErrorDetails]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.GenerateCostDetailsReportRequestDefinition(_Model):
        billing_period: Optional[str]
        invoice_id: Optional[str]
        metric: Optional[Union[str, CostDetailsMetricType]]
        time_period: Optional[CostDetailsTimePeriod]

        @overload
        def __init__(
                self, 
                *, 
                billing_period: Optional[str] = ..., 
                invoice_id: Optional[str] = ..., 
                metric: Optional[Union[str, CostDetailsMetricType]] = ..., 
                time_period: Optional[CostDetailsTimePeriod] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.GenerateDetailedCostReportDefinition(_Model):
        billing_period: Optional[str]
        customer_id: Optional[str]
        invoice_id: Optional[str]
        metric: Optional[Union[str, GenerateDetailedCostReportMetricType]]
        time_period: Optional[GenerateDetailedCostReportTimePeriod]

        @overload
        def __init__(
                self, 
                *, 
                billing_period: Optional[str] = ..., 
                customer_id: Optional[str] = ..., 
                invoice_id: Optional[str] = ..., 
                metric: Optional[Union[str, GenerateDetailedCostReportMetricType]] = ..., 
                time_period: Optional[GenerateDetailedCostReportTimePeriod] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.GenerateDetailedCostReportErrorResponse(_Model):
        error: Optional[ErrorDetails]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.GenerateDetailedCostReportMetricType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTUAL_COST = "ActualCost"
        AMORTIZED_COST = "AmortizedCost"


    class azure.mgmt.costmanagement.models.GenerateDetailedCostReportOperationResult(ExtensionResource):
        id: str
        name: str
        properties: Optional[DownloadURL]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DownloadURL] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.costmanagement.models.GenerateDetailedCostReportOperationStatuses(ExtensionResource):
        end_time: Optional[str]
        error: Optional[ErrorDetails]
        id: str
        name: str
        properties: Optional[DownloadURL]
        start_time: Optional[str]
        status: Optional[Status]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[str] = ..., 
                error: Optional[ErrorDetails] = ..., 
                properties: Optional[DownloadURL] = ..., 
                start_time: Optional[str] = ..., 
                status: Optional[Status] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.costmanagement.models.GenerateDetailedCostReportTimePeriod(_Model):
        end: str
        start: str

        @overload
        def __init__(
                self, 
                *, 
                end: str, 
                start: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        MONTHLY = "Monthly"


    class azure.mgmt.costmanagement.models.IncludedQuantityUtilizationSummary(BenefitUtilizationSummary, discriminator='IncludedQuantity'):
        id: str
        kind: Literal[BenefitKind.INCLUDED_QUANTITY]
        name: str
        properties: Optional[IncludedQuantityUtilizationSummaryProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[IncludedQuantityUtilizationSummaryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.costmanagement.models.IncludedQuantityUtilizationSummaryProperties(BenefitUtilizationSummaryProperties):
        arm_sku_name: str
        benefit_id: str
        benefit_order_id: str
        benefit_type: Union[str, BenefitKind]
        usage_date: datetime
        utilization_percentage: Optional[Decimal]

        @overload
        def __init__(
                self, 
                *, 
                benefit_type: Optional[Union[str, BenefitKind]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.KpiProperties(_Model):
        enabled: Optional[bool]
        id: Optional[str]
        type: Optional[Union[str, KpiType]]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                id: Optional[str] = ..., 
                type: Optional[Union[str, KpiType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.KpiType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUDGET = "Budget"
        FORECAST = "Forecast"


    class azure.mgmt.costmanagement.models.LookBackPeriod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LAST30_DAYS = "Last30Days"
        LAST60_DAYS = "Last60Days"
        LAST7_DAYS = "Last7Days"


    class azure.mgmt.costmanagement.models.MCAPriceSheetProperties(_Model):
        base_price: Optional[str]
        billing_account_id: Optional[str]
        billing_account_name: Optional[str]
        billing_currency: Optional[str]
        billing_profile_id: Optional[str]
        billing_profile_name: Optional[str]
        currency: Optional[str]
        effective_end_date: Optional[datetime]
        effective_start_date: Optional[datetime]
        market_price: Optional[str]
        meter_category: Optional[str]
        meter_id: Optional[str]
        meter_name: Optional[str]
        meter_region: Optional[str]
        meter_sub_category: Optional[str]
        meter_type: Optional[str]
        price_type: Optional[str]
        product: Optional[str]
        product_id: Optional[str]
        product_order_name: Optional[str]
        service_family: Optional[float]
        sku_id: Optional[str]
        term: Optional[str]
        tier_minimum_units: Optional[str]
        unit_of_measure: Optional[str]
        unit_price: Optional[str]


    class azure.mgmt.costmanagement.models.MetricType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTUAL_COST = "ActualCost"
        AHUB = "AHUB"
        AMORTIZED_COST = "AmortizedCost"


    class azure.mgmt.costmanagement.models.Notification(_Model):
        contact_emails: list[str]
        contact_groups: Optional[list[str]]
        contact_roles: Optional[list[str]]
        enabled: bool
        frequency: Optional[Union[str, Frequency]]
        locale: Optional[Union[str, CultureCode]]
        operator: Union[str, BudgetNotificationOperatorType]
        threshold: float
        threshold_type: Optional[Union[str, ThresholdType]]

        @overload
        def __init__(
                self, 
                *, 
                contact_emails: list[str], 
                contact_groups: Optional[list[str]] = ..., 
                contact_roles: Optional[list[str]] = ..., 
                enabled: bool, 
                frequency: Optional[Union[str, Frequency]] = ..., 
                locale: Optional[Union[str, CultureCode]] = ..., 
                operator: Union[str, BudgetNotificationOperatorType], 
                threshold: float, 
                threshold_type: Optional[Union[str, ThresholdType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.NotificationProperties(_Model):
        language: Optional[str]
        message: Optional[str]
        regional_format: Optional[str]
        subject: str
        to: list[str]

        @overload
        def __init__(
                self, 
                *, 
                language: Optional[str] = ..., 
                message: Optional[str] = ..., 
                regional_format: Optional[str] = ..., 
                subject: str, 
                to: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.Operation(_Model):
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


    class azure.mgmt.costmanagement.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.costmanagement.models.OperationStatus(_Model):
        properties: Optional[ReportURL]
        status: Optional[Union[str, OperationStatusType]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ReportURL] = ..., 
                status: Optional[Union[str, OperationStatusType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.costmanagement.models.OperationStatusType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        RUNNING = "Running"


    class azure.mgmt.costmanagement.models.OperatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINS = "Contains"
        IN = "In"


    class azure.mgmt.costmanagement.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.costmanagement.models.PivotProperties(_Model):
        name: Optional[str]
        type: Optional[Union[str, PivotType]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[Union[str, PivotType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.PivotType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIMENSION = "Dimension"
        TAG_KEY = "TagKey"


    class azure.mgmt.costmanagement.models.PricesheetDownloadProperties(_Model):
        download_file_properties: Optional[MCAPriceSheetProperties]
        download_url: Optional[str]
        expiry_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                download_file_properties: Optional[MCAPriceSheetProperties] = ..., 
                download_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.costmanagement.models.QueryAggregation(_Model):
        function: Union[str, FunctionType]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                function: Union[str, FunctionType], 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.QueryColumn(_Model):
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


    class azure.mgmt.costmanagement.models.QueryColumnType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIMENSION = "Dimension"
        TAG_KEY = "TagKey"


    class azure.mgmt.costmanagement.models.QueryComparisonExpression(_Model):
        name: str
        operator: Union[str, QueryOperatorType]
        values_property: list[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                operator: Union[str, QueryOperatorType], 
                values_property: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.QueryDataset(_Model):
        aggregation: Optional[dict[str, QueryAggregation]]
        configuration: Optional[QueryDatasetConfiguration]
        filter: Optional[QueryFilter]
        granularity: Optional[Union[str, GranularityType]]
        grouping: Optional[list[QueryGrouping]]

        @overload
        def __init__(
                self, 
                *, 
                aggregation: Optional[dict[str, QueryAggregation]] = ..., 
                configuration: Optional[QueryDatasetConfiguration] = ..., 
                filter: Optional[QueryFilter] = ..., 
                granularity: Optional[Union[str, GranularityType]] = ..., 
                grouping: Optional[list[QueryGrouping]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.QueryDatasetConfiguration(_Model):
        columns: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                columns: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.QueryDefinition(_Model):
        dataset: QueryDataset
        time_period: Optional[QueryTimePeriod]
        timeframe: Union[str, TimeframeType]
        type: Union[str, ExportType]

        @overload
        def __init__(
                self, 
                *, 
                dataset: QueryDataset, 
                time_period: Optional[QueryTimePeriod] = ..., 
                timeframe: Union[str, TimeframeType], 
                type: Union[str, ExportType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.QueryFilter(_Model):
        and_property: Optional[list[QueryFilter]]
        dimensions: Optional[QueryComparisonExpression]
        or_property: Optional[list[QueryFilter]]
        tags: Optional[QueryComparisonExpression]

        @overload
        def __init__(
                self, 
                *, 
                and_property: Optional[list[QueryFilter]] = ..., 
                dimensions: Optional[QueryComparisonExpression] = ..., 
                or_property: Optional[list[QueryFilter]] = ..., 
                tags: Optional[QueryComparisonExpression] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.QueryGrouping(_Model):
        name: str
        type: Union[str, QueryColumnType]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                type: Union[str, QueryColumnType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.QueryOperatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IN = "In"


    class azure.mgmt.costmanagement.models.QueryProperties(_Model):
        columns: Optional[list[QueryColumn]]
        next_link: Optional[str]
        rows: Optional[list[list[Any]]]

        @overload
        def __init__(
                self, 
                *, 
                columns: Optional[list[QueryColumn]] = ..., 
                next_link: Optional[str] = ..., 
                rows: Optional[list[list[Any]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.QueryResult(CostManagementResource):
        e_tag: str
        id: str
        location: str
        name: str
        properties: Optional[QueryProperties]
        sku: str
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[QueryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.costmanagement.models.QueryTimePeriod(_Model):
        from_property: datetime
        to: datetime

        @overload
        def __init__(
                self, 
                *, 
                from_property: datetime, 
                to: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.Reason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"
        VALID = "Valid"


    class azure.mgmt.costmanagement.models.RecommendationUsageDetails(_Model):
        charges: Optional[list[Decimal]]
        usage_grain: Optional[Union[str, Grain]]

        @overload
        def __init__(
                self, 
                *, 
                usage_grain: Optional[Union[str, Grain]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.RecurrenceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANNUALLY = "Annually"
        DAILY = "Daily"
        MONTHLY = "Monthly"
        WEEKLY = "Weekly"


    class azure.mgmt.costmanagement.models.ReportConfigAggregation(_Model):
        function: Union[str, FunctionType]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                function: Union[str, FunctionType], 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ReportConfigComparisonExpression(_Model):
        name: str
        operator: Union[str, OperatorType]
        values_property: list[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                operator: Union[str, OperatorType], 
                values_property: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ReportConfigDataset(_Model):
        aggregation: Optional[dict[str, ReportConfigAggregation]]
        configuration: Optional[ReportConfigDatasetConfiguration]
        filter: Optional[ReportConfigFilter]
        granularity: Optional[Union[str, ReportGranularityType]]
        grouping: Optional[list[ReportConfigGrouping]]
        sorting: Optional[list[ReportConfigSorting]]

        @overload
        def __init__(
                self, 
                *, 
                aggregation: Optional[dict[str, ReportConfigAggregation]] = ..., 
                configuration: Optional[ReportConfigDatasetConfiguration] = ..., 
                filter: Optional[ReportConfigFilter] = ..., 
                granularity: Optional[Union[str, ReportGranularityType]] = ..., 
                grouping: Optional[list[ReportConfigGrouping]] = ..., 
                sorting: Optional[list[ReportConfigSorting]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ReportConfigDatasetConfiguration(_Model):
        columns: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                columns: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ReportConfigDefinition(_Model):
        data_set: Optional[ReportConfigDataset]
        include_monetary_commitment: Optional[bool]
        time_period: Optional[ReportConfigTimePeriod]
        timeframe: Union[str, ReportTimeframeType]
        type: Union[str, ReportType]

        @overload
        def __init__(
                self, 
                *, 
                data_set: Optional[ReportConfigDataset] = ..., 
                include_monetary_commitment: Optional[bool] = ..., 
                time_period: Optional[ReportConfigTimePeriod] = ..., 
                timeframe: Union[str, ReportTimeframeType], 
                type: Union[str, ReportType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ReportConfigFilter(_Model):
        and_property: Optional[list[ReportConfigFilter]]
        dimensions: Optional[ReportConfigComparisonExpression]
        or_property: Optional[list[ReportConfigFilter]]
        tags: Optional[ReportConfigComparisonExpression]

        @overload
        def __init__(
                self, 
                *, 
                and_property: Optional[list[ReportConfigFilter]] = ..., 
                dimensions: Optional[ReportConfigComparisonExpression] = ..., 
                or_property: Optional[list[ReportConfigFilter]] = ..., 
                tags: Optional[ReportConfigComparisonExpression] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ReportConfigGrouping(_Model):
        name: str
        type: Union[str, QueryColumnType]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                type: Union[str, QueryColumnType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ReportConfigSorting(_Model):
        direction: Optional[Union[str, ReportConfigSortingType]]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                direction: Optional[Union[str, ReportConfigSortingType]] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ReportConfigSortingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASCENDING = "Ascending"
        DESCENDING = "Descending"


    class azure.mgmt.costmanagement.models.ReportConfigTimePeriod(_Model):
        from_property: datetime
        to: datetime

        @overload
        def __init__(
                self, 
                *, 
                from_property: datetime, 
                to: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ReportGranularityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        MONTHLY = "Monthly"


    class azure.mgmt.costmanagement.models.ReportManifest(_Model):
        blob_count: Optional[int]
        blobs: Optional[list[BlobInfo]]
        byte_count: Optional[int]
        compress_data: Optional[bool]
        data_format: Optional[Union[str, CostDetailsDataFormat]]
        manifest_version: Optional[str]
        request_context: Optional[RequestContext]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                blob_count: Optional[int] = ..., 
                blobs: Optional[list[BlobInfo]] = ..., 
                byte_count: Optional[int] = ..., 
                compress_data: Optional[bool] = ..., 
                data_format: Optional[Union[str, CostDetailsDataFormat]] = ..., 
                manifest_version: Optional[str] = ..., 
                request_context: Optional[RequestContext] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


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


    class azure.mgmt.costmanagement.models.ReportURL(_Model):
        report_url: Optional[Union[str, ReservationReportSchema]]
        valid_until: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                report_url: Optional[Union[str, ReservationReportSchema]] = ..., 
                valid_until: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.RequestContext(_Model):
        request_body: Optional[GenerateCostDetailsReportRequestDefinition]
        request_scope: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                request_body: Optional[GenerateCostDetailsReportRequestDefinition] = ..., 
                request_scope: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.costmanagement.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.costmanagement.models.RuleStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        NOT_ACTIVE = "NotActive"
        PROCESSING = "Processing"


    class azure.mgmt.costmanagement.models.SavingsPlanUtilizationSummary(BenefitUtilizationSummary, discriminator='SavingsPlan'):
        id: str
        kind: Literal[BenefitKind.SAVINGS_PLAN]
        name: str
        properties: Optional[SavingsPlanUtilizationSummaryProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SavingsPlanUtilizationSummaryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.costmanagement.models.SavingsPlanUtilizationSummaryProperties(BenefitUtilizationSummaryProperties):
        arm_sku_name: str
        avg_utilization_percentage: Optional[Decimal]
        benefit_id: str
        benefit_order_id: str
        benefit_type: Union[str, BenefitKind]
        max_utilization_percentage: Optional[Decimal]
        min_utilization_percentage: Optional[Decimal]
        usage_date: datetime

        @overload
        def __init__(
                self, 
                *, 
                benefit_type: Optional[Union[str, BenefitKind]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ScheduleFrequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        MONTHLY = "Monthly"
        WEEKLY = "Weekly"


    class azure.mgmt.costmanagement.models.ScheduleProperties(_Model):
        day_of_month: Optional[int]
        days_of_week: Optional[list[Union[str, DaysOfWeek]]]
        end_date: datetime
        frequency: Union[str, ScheduleFrequency]
        hour_of_day: Optional[int]
        start_date: datetime
        weeks_of_month: Optional[list[Union[str, WeeksOfMonth]]]

        @overload
        def __init__(
                self, 
                *, 
                day_of_month: Optional[int] = ..., 
                days_of_week: Optional[list[Union[str, DaysOfWeek]]] = ..., 
                end_date: datetime, 
                frequency: Union[str, ScheduleFrequency], 
                hour_of_day: Optional[int] = ..., 
                start_date: datetime, 
                weeks_of_month: Optional[list[Union[str, WeeksOfMonth]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ScheduledAction(ProxyResource):
        e_tag: Optional[str]
        id: str
        kind: Optional[Union[str, ScheduledActionKind]]
        name: str
        properties: Optional[ScheduledActionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                kind: Optional[Union[str, ScheduledActionKind]] = ..., 
                properties: Optional[ScheduledActionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.costmanagement.models.ScheduledActionKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EMAIL = "Email"
        INSIGHT_ALERT = "InsightAlert"


    class azure.mgmt.costmanagement.models.ScheduledActionProperties(_Model):
        display_name: str
        file_destination: Optional[FileDestination]
        notification: NotificationProperties
        notification_email: Optional[str]
        schedule: ScheduleProperties
        scope: Optional[str]
        status: Union[str, ScheduledActionStatus]
        view_id: str

        @overload
        def __init__(
                self, 
                *, 
                display_name: str, 
                file_destination: Optional[FileDestination] = ..., 
                notification: NotificationProperties, 
                notification_email: Optional[str] = ..., 
                schedule: ScheduleProperties, 
                scope: Optional[str] = ..., 
                status: Union[str, ScheduledActionStatus], 
                view_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ScheduledActionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        EXPIRED = "Expired"


    class azure.mgmt.costmanagement.models.Scope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SHARED = "Shared"
        SINGLE = "Single"


    class azure.mgmt.costmanagement.models.Setting(ProxyResource):
        id: str
        kind: str
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.SettingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TAGINHERITANCE = "taginheritance"


    class azure.mgmt.costmanagement.models.SettingsKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TAGINHERITANCE = "taginheritance"


    class azure.mgmt.costmanagement.models.SettingsListResult(_Model):
        value: Optional[list[Setting]]


    class azure.mgmt.costmanagement.models.SharedScopeBenefitRecommendationProperties(BenefitRecommendationProperties, discriminator='Shared'):
        all_recommendation_details: AllSavingsList
        arm_sku_name: str
        commitment_granularity: Union[str, Grain]
        cost_without_benefit: Decimal
        currency_code: str
        first_consumption_date: datetime
        last_consumption_date: datetime
        look_back_period: Union[str, LookBackPeriod]
        recommendation_details: AllSavingsBenefitDetails
        scope: Literal[Scope.SHARED]
        term: Union[str, Term]
        total_hours: int
        usage: RecommendationUsageDetails

        @overload
        def __init__(
                self, 
                *, 
                commitment_granularity: Optional[Union[str, Grain]] = ..., 
                look_back_period: Optional[Union[str, LookBackPeriod]] = ..., 
                recommendation_details: Optional[AllSavingsBenefitDetails] = ..., 
                term: Optional[Union[str, Term]] = ..., 
                usage: Optional[RecommendationUsageDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.SingleScopeBenefitRecommendationProperties(BenefitRecommendationProperties, discriminator='Single'):
        all_recommendation_details: AllSavingsList
        arm_sku_name: str
        commitment_granularity: Union[str, Grain]
        cost_without_benefit: Decimal
        currency_code: str
        first_consumption_date: datetime
        last_consumption_date: datetime
        look_back_period: Union[str, LookBackPeriod]
        recommendation_details: AllSavingsBenefitDetails
        resource_group: Optional[str]
        scope: Literal[Scope.SINGLE]
        subscription_id: Optional[str]
        term: Union[str, Term]
        total_hours: int
        usage: RecommendationUsageDetails

        @overload
        def __init__(
                self, 
                *, 
                commitment_granularity: Optional[Union[str, Grain]] = ..., 
                look_back_period: Optional[Union[str, LookBackPeriod]] = ..., 
                recommendation_details: Optional[AllSavingsBenefitDetails] = ..., 
                term: Optional[Union[str, Term]] = ..., 
                usage: Optional[RecommendationUsageDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.SourceCostAllocationResource(CostAllocationResource):
        name: str
        resource_type: Union[str, CostAllocationResourceType]
        values_property: list[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                resource_type: Union[str, CostAllocationResourceType], 
                values_property: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.Status(_Model):
        status: Optional[Union[str, ReportOperationStatusType]]

        @overload
        def __init__(
                self, 
                *, 
                status: Optional[Union[str, ReportOperationStatusType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.StatusType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        INACTIVE = "Inactive"


    class azure.mgmt.costmanagement.models.SystemAssignedServiceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, SystemAssignedServiceIdentityType]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, SystemAssignedServiceIdentityType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.SystemAssignedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"


    class azure.mgmt.costmanagement.models.SystemData(_Model):
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


    class azure.mgmt.costmanagement.models.TagInheritanceProperties(_Model):
        prefer_container_tags: bool

        @overload
        def __init__(
                self, 
                *, 
                prefer_container_tags: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.TagInheritanceSetting(Setting, discriminator='taginheritance'):
        id: str
        kind: Literal[SettingsKind.TAGINHERITANCE]
        name: str
        properties: Optional[TagInheritanceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TagInheritanceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.TargetCostAllocationResource(CostAllocationResource):
        name: str
        policy_type: Union[str, CostAllocationPolicyType]
        resource_type: Union[str, CostAllocationResourceType]
        values_property: list[CostAllocationProportion]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                policy_type: Union[str, CostAllocationPolicyType], 
                resource_type: Union[str, CostAllocationResourceType], 
                values_property: list[CostAllocationProportion]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.Term(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P1_Y = "P1Y"
        P3_Y = "P3Y"


    class azure.mgmt.costmanagement.models.ThresholdType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTUAL = "Actual"
        FORECASTED = "Forecasted"


    class azure.mgmt.costmanagement.models.TimeGrainType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANNUALLY = "Annually"
        BILLING_ANNUAL = "BillingAnnual"
        BILLING_MONTH = "BillingMonth"
        BILLING_QUARTER = "BillingQuarter"
        LAST30_DAYS = "Last30Days"
        LAST7_DAYS = "Last7Days"
        MONTHLY = "Monthly"
        QUARTERLY = "Quarterly"


    class azure.mgmt.costmanagement.models.TimeframeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BILLING_MONTH_TO_DATE = "BillingMonthToDate"
        CUSTOM = "Custom"
        MONTH_TO_DATE = "MonthToDate"
        THE_CURRENT_MONTH = "TheCurrentMonth"
        THE_LAST_BILLING_MONTH = "TheLastBillingMonth"
        THE_LAST_MONTH = "TheLastMonth"
        WEEK_TO_DATE = "WeekToDate"


    class azure.mgmt.costmanagement.models.View(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[ViewProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                properties: Optional[ViewProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.costmanagement.models.ViewProperties(_Model):
        accumulated: Optional[Union[str, AccumulatedType]]
        chart: Optional[Union[str, ChartType]]
        created_on: Optional[datetime]
        currency: Optional[str]
        date_range: Optional[str]
        display_name: Optional[str]
        kpis: Optional[list[KpiProperties]]
        metric: Optional[Union[str, MetricType]]
        modified_on: Optional[datetime]
        pivots: Optional[list[PivotProperties]]
        query: Optional[ReportConfigDefinition]
        scope: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                accumulated: Optional[Union[str, AccumulatedType]] = ..., 
                chart: Optional[Union[str, ChartType]] = ..., 
                date_range: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                kpis: Optional[list[KpiProperties]] = ..., 
                metric: Optional[Union[str, MetricType]] = ..., 
                modified_on: Optional[datetime] = ..., 
                pivots: Optional[list[PivotProperties]] = ..., 
                query: Optional[ReportConfigDefinition] = ..., 
                scope: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


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
            ) -> None: ...

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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                alert_id: str, 
                **kwargs: Any
            ) -> Alert: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> AlertsResult: ...

        @distributed_trace
        def list_external(
                self, 
                external_cloud_provider_type: Union[str, ExternalCloudProviderType], 
                external_cloud_provider_id: str, 
                **kwargs: Any
            ) -> AlertsResult: ...


    class azure.mgmt.costmanagement.operations.BenefitRecommendationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                billing_scope: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BenefitRecommendationModel]: ...


    class azure.mgmt.costmanagement.operations.BenefitUtilizationSummariesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_billing_account_id(
                self, 
                billing_account_id: str, 
                *, 
                filter: Optional[str] = ..., 
                grain_parameter: Optional[Union[str, GrainParameter]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BenefitUtilizationSummary]: ...

        @distributed_trace
        def list_by_billing_profile_id(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                *, 
                filter: Optional[str] = ..., 
                grain_parameter: Optional[Union[str, GrainParameter]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BenefitUtilizationSummary]: ...

        @distributed_trace
        def list_by_savings_plan_id(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                *, 
                filter: Optional[str] = ..., 
                grain_parameter: Optional[Union[str, GrainParameter]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BenefitUtilizationSummary]: ...

        @distributed_trace
        def list_by_savings_plan_order(
                self, 
                savings_plan_order_id: str, 
                *, 
                filter: Optional[str] = ..., 
                grain_parameter: Optional[Union[str, GrainParameter]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BenefitUtilizationSummary]: ...


    class azure.mgmt.costmanagement.operations.BudgetsOperations:

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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Budget]: ...


    class azure.mgmt.costmanagement.operations.CostAllocationRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def check_name_availability(
                self, 
                billing_account_id: str, 
                cost_allocation_rule_check_name_availability_request: CostAllocationRuleCheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CostAllocationRuleCheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                billing_account_id: str, 
                cost_allocation_rule_check_name_availability_request: CostAllocationRuleCheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CostAllocationRuleCheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                billing_account_id: str, 
                cost_allocation_rule_check_name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CostAllocationRuleCheckNameAvailabilityResponse: ...

        @overload
        def create_or_update(
                self, 
                billing_account_id: str, 
                rule_name: str, 
                cost_allocation_rule: CostAllocationRuleDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CostAllocationRuleDefinition: ...

        @overload
        def create_or_update(
                self, 
                billing_account_id: str, 
                rule_name: str, 
                cost_allocation_rule: CostAllocationRuleDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CostAllocationRuleDefinition: ...

        @overload
        def create_or_update(
                self, 
                billing_account_id: str, 
                rule_name: str, 
                cost_allocation_rule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CostAllocationRuleDefinition: ...

        @distributed_trace
        def delete(
                self, 
                billing_account_id: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                billing_account_id: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> CostAllocationRuleDefinition: ...

        @distributed_trace
        def list(
                self, 
                billing_account_id: str, 
                **kwargs: Any
            ) -> ItemPaged[CostAllocationRuleDefinition]: ...


    class azure.mgmt.costmanagement.operations.DimensionsOperations:

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
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                skiptoken: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Dimension]: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                skiptoken: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Dimension]: ...


    class azure.mgmt.costmanagement.operations.ExportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Export: ...

        @distributed_trace
        def delete(
                self, 
                scope: str, 
                export_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def execute(
                self, 
                scope: str, 
                export_name: str, 
                parameters: Optional[ExportRunRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def execute(
                self, 
                scope: str, 
                export_name: str, 
                parameters: Optional[ExportRunRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def execute(
                self, 
                scope: str, 
                export_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                export_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> Export: ...

        @distributed_trace
        def get_execution_history(
                self, 
                scope: str, 
                export_name: str, 
                **kwargs: Any
            ) -> ExportExecutionListResult: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> ExportListResult: ...


    class azure.mgmt.costmanagement.operations.ForecastOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def external_cloud_provider_usage(
                self, 
                external_cloud_provider_type: Union[str, ExternalCloudProviderType], 
                external_cloud_provider_id: str, 
                parameters: ForecastDefinition, 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ForecastResult: ...

        @overload
        def external_cloud_provider_usage(
                self, 
                external_cloud_provider_type: Union[str, ExternalCloudProviderType], 
                external_cloud_provider_id: str, 
                parameters: ForecastDefinition, 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ForecastResult: ...

        @overload
        def external_cloud_provider_usage(
                self, 
                external_cloud_provider_type: Union[str, ExternalCloudProviderType], 
                external_cloud_provider_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ForecastResult: ...

        @overload
        def usage(
                self, 
                scope: str, 
                parameters: ForecastDefinition, 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> Optional[ForecastResult]: ...

        @overload
        def usage(
                self, 
                scope: str, 
                parameters: ForecastDefinition, 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> Optional[ForecastResult]: ...

        @overload
        def usage(
                self, 
                scope: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> Optional[ForecastResult]: ...


    class azure.mgmt.costmanagement.operations.GenerateBenefitUtilizationSummariesReportOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_generate_by_billing_account(
                self, 
                billing_account_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        def begin_generate_by_billing_account(
                self, 
                billing_account_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        def begin_generate_by_billing_account(
                self, 
                billing_account_id: str, 
                benefit_utilization_summaries_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        def begin_generate_by_billing_profile(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        def begin_generate_by_billing_profile(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        def begin_generate_by_billing_profile(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                benefit_utilization_summaries_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        def begin_generate_by_reservation_id(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        def begin_generate_by_reservation_id(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        def begin_generate_by_reservation_id(
                self, 
                reservation_order_id: str, 
                reservation_id: str, 
                benefit_utilization_summaries_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        def begin_generate_by_reservation_order_id(
                self, 
                reservation_order_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        def begin_generate_by_reservation_order_id(
                self, 
                reservation_order_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        def begin_generate_by_reservation_order_id(
                self, 
                reservation_order_id: str, 
                benefit_utilization_summaries_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        def begin_generate_by_savings_plan_id(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        def begin_generate_by_savings_plan_id(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        def begin_generate_by_savings_plan_id(
                self, 
                savings_plan_order_id: str, 
                savings_plan_id: str, 
                benefit_utilization_summaries_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        def begin_generate_by_savings_plan_order_id(
                self, 
                savings_plan_order_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        def begin_generate_by_savings_plan_order_id(
                self, 
                savings_plan_order_id: str, 
                benefit_utilization_summaries_request: BenefitUtilizationSummariesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BenefitUtilizationSummariesOperationStatus]: ...

        @overload
        def begin_generate_by_savings_plan_order_id(
                self, 
                savings_plan_order_id: str, 
                benefit_utilization_summaries_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BenefitUtilizationSummariesOperationStatus]: ...


    class azure.mgmt.costmanagement.operations.GenerateCostDetailsReportOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                parameters: GenerateCostDetailsReportRequestDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CostDetailsOperationResults]: ...

        @overload
        def begin_create_operation(
                self, 
                scope: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CostDetailsOperationResults]: ...

        @distributed_trace
        def begin_get_operation_results(
                self, 
                scope: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[CostDetailsOperationResults]: ...


    class azure.mgmt.costmanagement.operations.GenerateDetailedCostReportOperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_get(
                self, 
                operation_id: str, 
                scope: str, 
                **kwargs: Any
            ) -> LROPoller[GenerateDetailedCostReportOperationResult]: ...


    class azure.mgmt.costmanagement.operations.GenerateDetailedCostReportOperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                operation_id: str, 
                scope: str, 
                **kwargs: Any
            ) -> GenerateDetailedCostReportOperationStatuses: ...


    class azure.mgmt.costmanagement.operations.GenerateDetailedCostReportOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                parameters: GenerateDetailedCostReportDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GenerateDetailedCostReportOperationResult]: ...

        @overload
        def begin_create_operation(
                self, 
                scope: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GenerateDetailedCostReportOperationResult]: ...


    class azure.mgmt.costmanagement.operations.GenerateReservationDetailsReportOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_by_billing_account_id(
                self, 
                billing_account_id: str, 
                *, 
                end_date: str, 
                start_date: str, 
                **kwargs: Any
            ) -> LROPoller[OperationStatus]: ...

        @distributed_trace
        def begin_by_billing_profile_id(
                self, 
                billing_account_id: str, 
                billing_profile_id: str, 
                *, 
                end_date: str, 
                start_date: str, 
                **kwargs: Any
            ) -> LROPoller[OperationStatus]: ...


    class azure.mgmt.costmanagement.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[CostManagementOperation]: ...


    class azure.mgmt.costmanagement.operations.PriceSheetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_download_by_billing_account(
                self, 
                billing_account_id: str, 
                billing_period_name: str, 
                **kwargs: Any
            ) -> LROPoller[OperationStatus]: ...

        @distributed_trace
        def begin_download_by_billing_profile(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                **kwargs: Any
            ) -> LROPoller[PricesheetDownloadProperties]: ...

        @distributed_trace
        def begin_download_by_invoice(
                self, 
                billing_account_name: str, 
                billing_profile_name: str, 
                invoice_name: str, 
                **kwargs: Any
            ) -> LROPoller[DownloadURL]: ...


    class azure.mgmt.costmanagement.operations.QueryOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                parameters: QueryDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[QueryResult]: ...

        @overload
        def usage(
                self, 
                scope: str, 
                parameters: IO[bytes], 
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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QueryResult: ...


    class azure.mgmt.costmanagement.operations.ScheduledActionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                check_name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                check_name_availability_request: IO[bytes], 
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
                check_name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability_by_scope(
                self, 
                scope: str, 
                check_name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def create_or_update(
                self, 
                name: str, 
                scheduled_action: ScheduledAction, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @overload
        def create_or_update(
                self, 
                name: str, 
                scheduled_action: ScheduledAction, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @overload
        def create_or_update(
                self, 
                name: str, 
                scheduled_action: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @overload
        def create_or_update_by_scope(
                self, 
                scope: str, 
                name: str, 
                scheduled_action: ScheduledAction, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @overload
        def create_or_update_by_scope(
                self, 
                scope: str, 
                name: str, 
                scheduled_action: ScheduledAction, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @overload
        def create_or_update_by_scope(
                self, 
                scope: str, 
                name: str, 
                scheduled_action: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @distributed_trace
        def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_by_scope(
                self, 
                scope: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @distributed_trace
        def get_by_scope(
                self, 
                scope: str, 
                name: str, 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ScheduledAction]: ...

        @distributed_trace
        def list_by_scope(
                self, 
                scope: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ScheduledAction]: ...

        @distributed_trace
        def run(
                self, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def run_by_scope(
                self, 
                scope: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.costmanagement.operations.SettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update_by_scope(
                self, 
                scope: str, 
                type: Union[str, SettingType], 
                setting: Setting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Setting: ...

        @overload
        def create_or_update_by_scope(
                self, 
                scope: str, 
                type: Union[str, SettingType], 
                setting: Setting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Setting: ...

        @overload
        def create_or_update_by_scope(
                self, 
                scope: str, 
                type: Union[str, SettingType], 
                setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Setting: ...

        @distributed_trace
        def delete_by_scope(
                self, 
                scope: str, 
                type: Union[str, SettingType], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_by_scope(
                self, 
                scope: str, 
                type: Union[str, SettingType], 
                **kwargs: Any
            ) -> Setting: ...

        @distributed_trace
        def list(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> SettingsListResult: ...


    class azure.mgmt.costmanagement.operations.ViewsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                parameters: View, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> View: ...

        @overload
        def create_or_update(
                self, 
                view_name: str, 
                parameters: IO[bytes], 
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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> View: ...

        @distributed_trace
        def delete(
                self, 
                view_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_by_scope(
                self, 
                scope: str, 
                view_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                view_name: str, 
                **kwargs: Any
            ) -> View: ...

        @distributed_trace
        def get_by_scope(
                self, 
                scope: str, 
                view_name: str, 
                **kwargs: Any
            ) -> View: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[View]: ...

        @distributed_trace
        def list_by_scope(
                self, 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[View]: ...


namespace azure.mgmt.costmanagement.types

    class azure.mgmt.costmanagement.types.AlertProperties(TypedDict, total=False):
        key "closeTime": str
        key "costEntityId": str
        key "creationTime": str
        key "definition": ForwardRef('AlertPropertiesDefinition', module='types')
        key "description": str
        key "details": ForwardRef('AlertPropertiesDetails', module='types')
        key "modificationTime": str
        key "source": Union[str, AlertSource]
        key "status": Union[str, AlertStatus]
        key "statusModificationTime": str
        key "statusModificationUserName": str
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


    class azure.mgmt.costmanagement.types.AlertPropertiesDefinition(TypedDict, total=False):
        key "category": Union[str, AlertCategory]
        key "criteria": Union[str, AlertCriteria]
        key "type": Union[str, AlertType]
        category: Union[str, AlertCategory]
        criteria: Union[str, AlertCriteria]
        type: Union[str, AlertType]


    class azure.mgmt.costmanagement.types.AlertPropertiesDetails(TypedDict, total=False):
        key "amount": float
        key "companyName": str
        key "currentSpend": float
        key "departmentName": str
        key "enrollmentEndDate": str
        key "enrollmentNumber": str
        key "enrollmentStartDate": str
        key "invoicingThreshold": float
        key "operator": Union[str, AlertOperator]
        key "overridingAlert": str
        key "periodStartDate": str
        key "tagFilter": Any
        key "threshold": float
        key "timeGrainType": Union[str, AlertTimeGrainType]
        key "triggeredBy": str
        key "unit": str
        amount: float
        company_name: str
        contactEmails: list[str]
        contactGroups: list[str]
        contactRoles: list[str]
        contact_emails: list[str]
        contact_groups: list[str]
        contact_roles: list[str]
        current_spend: float
        department_name: str
        enrollment_end_date: str
        enrollment_number: str
        enrollment_start_date: str
        invoicing_threshold: float
        meterFilter: list[Any]
        meter_filter: list[Any]
        operator: Union[str, AlertOperator]
        overriding_alert: str
        period_start_date: str
        resourceFilter: list[Any]
        resourceGroupFilter: list[Any]
        resource_filter: list[Any]
        resource_group_filter: list[Any]
        tag_filter: Any
        threshold: float
        time_grain_type: Union[str, AlertTimeGrainType]
        triggered_by: str
        unit: str


    class azure.mgmt.costmanagement.types.BenefitUtilizationSummariesRequest(TypedDict, total=False):
        key "benefitId": str
        key "benefitOrderId": str
        key "billingAccountId": str
        key "billingProfileId": str
        key "endDate": Required[str]
        key "grain": Required[Union[str, Grain]]
        key "kind": Union[str, BenefitKind]
        key "startDate": Required[str]
        benefit_id: str
        benefit_order_id: str
        billing_account_id: str
        billing_profile_id: str
        end_date: str
        grain: Union[str, Grain]
        kind: Union[str, BenefitKind]
        start_date: str


    class azure.mgmt.costmanagement.types.Budget(ExtensionResource):
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


    class azure.mgmt.costmanagement.types.BudgetComparisonExpression(TypedDict, total=False):
        key "name": Required[str]
        key "operator": Required[Union[str, BudgetOperatorType]]
        key "values": Required[list[str]]
        name: str
        operator: Union[str, BudgetOperatorType]
        values_property: list[str]


    class azure.mgmt.costmanagement.types.BudgetFilter(TypedDict):
        key "dimensions": ForwardRef('BudgetComparisonExpression', module='types')
        key "tags": ForwardRef('BudgetComparisonExpression', module='types')
        and: list[BudgetFilterProperties]
        and_property: list[BudgetFilterProperties]
        dimensions: BudgetComparisonExpression
        tags: BudgetComparisonExpression


    class azure.mgmt.costmanagement.types.BudgetFilterProperties(TypedDict, total=False):
        key "dimensions": ForwardRef('BudgetComparisonExpression', module='types')
        key "tags": ForwardRef('BudgetComparisonExpression', module='types')
        dimensions: BudgetComparisonExpression
        tags: BudgetComparisonExpression


    class azure.mgmt.costmanagement.types.BudgetProperties(TypedDict, total=False):
        key "amount": float
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


    class azure.mgmt.costmanagement.types.BudgetTimePeriod(TypedDict, total=False):
        key "endDate": str
        key "startDate": Required[str]
        end_date: str
        start_date: str


    class azure.mgmt.costmanagement.types.CheckNameAvailabilityRequest(TypedDict, total=False):
        key "name": str
        key "type": str
        name: str
        type: str


    class azure.mgmt.costmanagement.types.CommonExportProperties(TypedDict, total=False):
        key "compressionMode": Union[str, CompressionModeType]
        key "dataOverwriteBehavior": Union[str, DataOverwriteBehaviorType]
        key "definition": Required[ExportDefinition]
        key "deliveryInfo": Required[ExportDeliveryInfo]
        key "exportDescription": str
        key "format": Union[str, FormatType]
        key "nextRunTimeEstimate": str
        key "partitionData": bool
        key "runHistory": ForwardRef('ExportExecutionListResult', module='types')
        key "systemSuspensionContext": ForwardRef('ExportSuspensionContext', module='types')
        compression_mode: Union[str, CompressionModeType]
        data_overwrite_behavior: Union[str, DataOverwriteBehaviorType]
        definition: ExportDefinition
        delivery_info: ExportDeliveryInfo
        export_description: str
        format: Union[str, FormatType]
        next_run_time_estimate: str
        partition_data: bool
        run_history: ExportExecutionListResult
        system_suspension_context: ExportSuspensionContext


    class azure.mgmt.costmanagement.types.CostAllocationProportion(TypedDict, total=False):
        key "name": Required[str]
        key "percentage": Required[float]
        name: str
        percentage: float


    class azure.mgmt.costmanagement.types.CostAllocationResource(TypedDict, total=False):
        key "name": Required[str]
        key "resourceType": Required[Union[str, CostAllocationResourceType]]
        name: str
        resource_type: Union[str, CostAllocationResourceType]


    class azure.mgmt.costmanagement.types.CostAllocationRuleCheckNameAvailabilityRequest(TypedDict, total=False):
        key "name": str
        key "type": str
        name: str
        type: str


    class azure.mgmt.costmanagement.types.CostAllocationRuleDefinition(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('CostAllocationRuleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: CostAllocationRuleProperties
        system_data: SystemData
        type: str


    class azure.mgmt.costmanagement.types.CostAllocationRuleDetails(TypedDict, total=False):
        sourceResources: list[SourceCostAllocationResource]
        source_resources: list[SourceCostAllocationResource]
        targetResources: list[TargetCostAllocationResource]
        target_resources: list[TargetCostAllocationResource]


    class azure.mgmt.costmanagement.types.CostAllocationRuleProperties(TypedDict, total=False):
        key "createdDate": str
        key "description": str
        key "details": Required[CostAllocationRuleDetails]
        key "status": Required[Union[str, RuleStatus]]
        key "updatedDate": str
        created_date: str
        description: str
        details: CostAllocationRuleDetails
        status: Union[str, RuleStatus]
        updated_date: str


    class azure.mgmt.costmanagement.types.CostDetailsTimePeriod(TypedDict, total=False):
        key "end": Required[str]
        key "start": Required[str]
        end: str
        start: str


    class azure.mgmt.costmanagement.types.CostManagementProxyResource(TypedDict, total=False):
        key "eTag": str
        key "id": str
        key "name": str
        key "type": str
        e_tag: str
        id: str
        name: str
        type: str


    class azure.mgmt.costmanagement.types.CurrentSpend(TypedDict, total=False):
        key "amount": float
        key "unit": str
        amount: float
        unit: str


    class azure.mgmt.costmanagement.types.DismissAlertPayload(TypedDict, total=False):
        key "properties": ForwardRef('AlertProperties', module='types')
        properties: AlertProperties


    class azure.mgmt.costmanagement.types.ErrorDetails(TypedDict, total=False):
        key "code": str
        key "message": str
        code: str
        message: str


    class azure.mgmt.costmanagement.types.Export(ExtensionResource):
        key "eTag": str
        key "id": str
        key "identity": ForwardRef('SystemAssignedServiceIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": ForwardRef('ExportProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        e_tag: str
        id: str
        identity: SystemAssignedServiceIdentity
        location: str
        name: str
        properties: ExportProperties
        system_data: SystemData
        type: str


    class azure.mgmt.costmanagement.types.ExportDataset(TypedDict, total=False):
        key "configuration": ForwardRef('ExportDatasetConfiguration', module='types')
        key "granularity": Union[str, GranularityType]
        configuration: ExportDatasetConfiguration
        granularity: Union[str, GranularityType]


    class azure.mgmt.costmanagement.types.ExportDatasetConfiguration(TypedDict, total=False):
        key "dataVersion": str
        columns: list[str]
        data_version: str
        filters: list[FilterItems]


    class azure.mgmt.costmanagement.types.ExportDefinition(TypedDict, total=False):
        key "dataSet": ForwardRef('ExportDataset', module='types')
        key "timePeriod": ForwardRef('ExportTimePeriod', module='types')
        key "timeframe": Required[Union[str, TimeframeType]]
        key "type": Required[Union[str, ExportType]]
        data_set: ExportDataset
        time_period: ExportTimePeriod
        timeframe: Union[str, TimeframeType]
        type: Union[str, ExportType]


    class azure.mgmt.costmanagement.types.ExportDeliveryDestination(TypedDict, total=False):
        key "container": Required[str]
        key "resourceId": str
        key "rootFolderPath": str
        key "sasToken": str
        key "storageAccount": str
        key "type": Union[str, DestinationType]
        container: str
        resource_id: str
        root_folder_path: str
        sas_token: str
        storage_account: str
        type: Union[str, DestinationType]


    class azure.mgmt.costmanagement.types.ExportDeliveryInfo(TypedDict, total=False):
        key "destination": Required[ExportDeliveryDestination]
        destination: ExportDeliveryDestination


    class azure.mgmt.costmanagement.types.ExportExecutionListResult(TypedDict, total=False):
        value: list[ExportRun]


    class azure.mgmt.costmanagement.types.ExportProperties(CommonExportProperties):
        key "compressionMode": Union[str, CompressionModeType]
        key "dataOverwriteBehavior": Union[str, DataOverwriteBehaviorType]
        key "definition": Required[ExportDefinition]
        key "deliveryInfo": Required[ExportDeliveryInfo]
        key "exportDescription": str
        key "format": Union[str, FormatType]
        key "nextRunTimeEstimate": str
        key "partitionData": bool
        key "runHistory": ForwardRef('ExportExecutionListResult', module='types')
        key "schedule": ForwardRef('ExportSchedule', module='types')
        key "systemSuspensionContext": ForwardRef('ExportSuspensionContext', module='types')
        compression_mode: Union[str, CompressionModeType]
        data_overwrite_behavior: Union[str, DataOverwriteBehaviorType]
        definition: ExportDefinition
        delivery_info: ExportDeliveryInfo
        export_description: str
        format: Union[str, FormatType]
        next_run_time_estimate: str
        partition_data: bool
        run_history: ExportExecutionListResult
        schedule: ExportSchedule
        system_suspension_context: ExportSuspensionContext


    class azure.mgmt.costmanagement.types.ExportRecurrencePeriod(TypedDict):
        key "from": Required[str]
        key "to": str
        from_property: str
        to: str


    class azure.mgmt.costmanagement.types.ExportRun(CostManagementProxyResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('ExportRunProperties', module='types')
        key "type": str
        e_tag: str
        id: str
        name: str
        properties: ExportRunProperties
        type: str


    class azure.mgmt.costmanagement.types.ExportRunProperties(TypedDict, total=False):
        key "endDate": str
        key "error": ForwardRef('ErrorDetails', module='types')
        key "executionType": Union[str, ExecutionType]
        key "fileName": str
        key "manifestFile": str
        key "processingEndTime": str
        key "processingStartTime": str
        key "runSettings": ForwardRef('CommonExportProperties', module='types')
        key "startDate": str
        key "status": Union[str, ExecutionStatus]
        key "submittedBy": str
        key "submittedTime": str
        end_date: str
        error: ErrorDetails
        execution_type: Union[str, ExecutionType]
        file_name: str
        manifest_file: str
        processing_end_time: str
        processing_start_time: str
        run_settings: CommonExportProperties
        start_date: str
        status: Union[str, ExecutionStatus]
        submitted_by: str
        submitted_time: str


    class azure.mgmt.costmanagement.types.ExportRunRequest(TypedDict, total=False):
        key "timePeriod": ForwardRef('ExportTimePeriod', module='types')
        time_period: ExportTimePeriod


    class azure.mgmt.costmanagement.types.ExportSchedule(TypedDict, total=False):
        key "recurrence": Union[str, RecurrenceType]
        key "recurrencePeriod": ForwardRef('ExportRecurrencePeriod', module='types')
        key "status": Union[str, StatusType]
        recurrence: Union[str, RecurrenceType]
        recurrence_period: ExportRecurrencePeriod
        status: Union[str, StatusType]


    class azure.mgmt.costmanagement.types.ExportSuspensionContext(TypedDict, total=False):
        key "suspensionCode": str
        key "suspensionReason": str
        key "suspensionTime": str
        suspension_code: str
        suspension_reason: str
        suspension_time: str


    class azure.mgmt.costmanagement.types.ExportTimePeriod(TypedDict):
        key "from": Required[str]
        key "to": Required[str]
        from_property: str
        to: str


    class azure.mgmt.costmanagement.types.ExtensionResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.costmanagement.types.FileDestination(TypedDict, total=False):
        fileFormats: list[Union[str, FileFormat]]
        file_formats: list[Union[str, FileFormat]]


    class azure.mgmt.costmanagement.types.FilterItems(TypedDict, total=False):
        key "name": Union[str, FilterItemNames]
        key "value": str
        name: Union[str, FilterItemNames]
        value: str


    class azure.mgmt.costmanagement.types.ForecastAggregation(TypedDict, total=False):
        key "function": Required[Union[str, FunctionType]]
        key "name": Required[Union[str, FunctionName]]
        function: Union[str, FunctionType]
        name: Union[str, FunctionName]


    class azure.mgmt.costmanagement.types.ForecastComparisonExpression(TypedDict, total=False):
        key "name": Required[str]
        key "operator": Required[Union[str, ForecastOperatorType]]
        key "values": Required[list[str]]
        name: str
        operator: Union[str, ForecastOperatorType]
        values_property: list[str]


    class azure.mgmt.costmanagement.types.ForecastDataset(TypedDict, total=False):
        key "aggregation": Required[dict[str, ForecastAggregation]]
        key "configuration": ForwardRef('ForecastDatasetConfiguration', module='types')
        key "filter": ForwardRef('ForecastFilter', module='types')
        key "granularity": Union[str, GranularityType]
        aggregation: dict[str, ForecastAggregation]
        configuration: ForecastDatasetConfiguration
        filter: ForecastFilter
        granularity: Union[str, GranularityType]


    class azure.mgmt.costmanagement.types.ForecastDatasetConfiguration(TypedDict, total=False):
        columns: list[str]


    class azure.mgmt.costmanagement.types.ForecastDefinition(TypedDict, total=False):
        key "dataset": Required[ForecastDataset]
        key "includeActualCost": bool
        key "includeFreshPartialCost": bool
        key "timePeriod": ForwardRef('ForecastTimePeriod', module='types')
        key "timeframe": Required[Union[str, ForecastTimeframe]]
        key "type": Required[Union[str, ForecastType]]
        dataset: ForecastDataset
        include_actual_cost: bool
        include_fresh_partial_cost: bool
        time_period: ForecastTimePeriod
        timeframe: Union[str, ForecastTimeframe]
        type: Union[str, ForecastType]


    class azure.mgmt.costmanagement.types.ForecastFilter(TypedDict):
        key "dimensions": ForwardRef('ForecastComparisonExpression', module='types')
        key "tags": ForwardRef('ForecastComparisonExpression', module='types')
        and: list[ForecastFilter]
        and_property: list[ForecastFilter]
        dimensions: ForecastComparisonExpression
        or: list[ForecastFilter]
        or_property: list[ForecastFilter]
        tags: ForecastComparisonExpression


    class azure.mgmt.costmanagement.types.ForecastSpend(TypedDict, total=False):
        key "amount": float
        key "unit": str
        amount: float
        unit: str


    class azure.mgmt.costmanagement.types.ForecastTimePeriod(TypedDict):
        key "from": Required[str]
        key "to": Required[str]
        from_property: str
        to: str


    class azure.mgmt.costmanagement.types.GenerateCostDetailsReportRequestDefinition(TypedDict, total=False):
        key "billingPeriod": str
        key "invoiceId": str
        key "metric": Union[str, CostDetailsMetricType]
        key "timePeriod": ForwardRef('CostDetailsTimePeriod', module='types')
        billing_period: str
        invoice_id: str
        metric: Union[str, CostDetailsMetricType]
        time_period: CostDetailsTimePeriod


    class azure.mgmt.costmanagement.types.GenerateDetailedCostReportDefinition(TypedDict, total=False):
        key "billingPeriod": str
        key "customerId": str
        key "invoiceId": str
        key "metric": Union[str, GenerateDetailedCostReportMetricType]
        key "timePeriod": ForwardRef('GenerateDetailedCostReportTimePeriod', module='types')
        billing_period: str
        customer_id: str
        invoice_id: str
        metric: Union[str, GenerateDetailedCostReportMetricType]
        time_period: GenerateDetailedCostReportTimePeriod


    class azure.mgmt.costmanagement.types.GenerateDetailedCostReportTimePeriod(TypedDict, total=False):
        key "end": Required[str]
        key "start": Required[str]
        end: str
        start: str


    class azure.mgmt.costmanagement.types.KpiProperties(TypedDict, total=False):
        key "enabled": bool
        key "id": str
        key "type": Union[str, KpiType]
        enabled: bool
        id: str
        type: Union[str, KpiType]


    class azure.mgmt.costmanagement.types.Notification(TypedDict, total=False):
        key "contactEmails": Required[list[str]]
        key "enabled": Required[bool]
        key "frequency": Union[str, Frequency]
        key "locale": Union[str, CultureCode]
        key "operator": Required[Union[str, BudgetNotificationOperatorType]]
        key "threshold": Required[float]
        key "thresholdType": Union[str, ThresholdType]
        contactGroups: list[str]
        contactRoles: list[str]
        contact_emails: list[str]
        contact_groups: list[str]
        contact_roles: list[str]
        enabled: bool
        frequency: Union[str, Frequency]
        locale: Union[str, CultureCode]
        operator: Union[str, BudgetNotificationOperatorType]
        threshold: float
        threshold_type: Union[str, ThresholdType]


    class azure.mgmt.costmanagement.types.NotificationProperties(TypedDict, total=False):
        key "language": str
        key "message": str
        key "regionalFormat": str
        key "subject": Required[str]
        key "to": Required[list[str]]
        language: str
        message: str
        regional_format: str
        subject: str
        to: list[str]


    class azure.mgmt.costmanagement.types.PivotProperties(TypedDict, total=False):
        key "name": str
        key "type": Union[str, PivotType]
        name: str
        type: Union[str, PivotType]


    class azure.mgmt.costmanagement.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.costmanagement.types.QueryAggregation(TypedDict, total=False):
        key "function": Required[Union[str, FunctionType]]
        key "name": Required[str]
        function: Union[str, FunctionType]
        name: str


    class azure.mgmt.costmanagement.types.QueryComparisonExpression(TypedDict, total=False):
        key "name": Required[str]
        key "operator": Required[Union[str, QueryOperatorType]]
        key "values": Required[list[str]]
        name: str
        operator: Union[str, QueryOperatorType]
        values_property: list[str]


    class azure.mgmt.costmanagement.types.QueryDataset(TypedDict, total=False):
        key "configuration": ForwardRef('QueryDatasetConfiguration', module='types')
        key "filter": ForwardRef('QueryFilter', module='types')
        key "granularity": Union[str, GranularityType]
        aggregation: dict[str, QueryAggregation]
        configuration: QueryDatasetConfiguration
        filter: QueryFilter
        granularity: Union[str, GranularityType]
        grouping: list[QueryGrouping]


    class azure.mgmt.costmanagement.types.QueryDatasetConfiguration(TypedDict, total=False):
        columns: list[str]


    class azure.mgmt.costmanagement.types.QueryDefinition(TypedDict, total=False):
        key "dataset": Required[QueryDataset]
        key "timePeriod": ForwardRef('QueryTimePeriod', module='types')
        key "timeframe": Required[Union[str, TimeframeType]]
        key "type": Required[Union[str, ExportType]]
        dataset: QueryDataset
        time_period: QueryTimePeriod
        timeframe: Union[str, TimeframeType]
        type: Union[str, ExportType]


    class azure.mgmt.costmanagement.types.QueryFilter(TypedDict):
        key "dimensions": ForwardRef('QueryComparisonExpression', module='types')
        key "tags": ForwardRef('QueryComparisonExpression', module='types')
        and: list[QueryFilter]
        and_property: list[QueryFilter]
        dimensions: QueryComparisonExpression
        or: list[QueryFilter]
        or_property: list[QueryFilter]
        tags: QueryComparisonExpression


    class azure.mgmt.costmanagement.types.QueryGrouping(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Union[str, QueryColumnType]]
        name: str
        type: Union[str, QueryColumnType]


    class azure.mgmt.costmanagement.types.QueryTimePeriod(TypedDict):
        key "from": Required[str]
        key "to": Required[str]
        from_property: str
        to: str


    class azure.mgmt.costmanagement.types.ReportConfigAggregation(TypedDict, total=False):
        key "function": Required[Union[str, FunctionType]]
        key "name": Required[str]
        function: Union[str, FunctionType]
        name: str


    class azure.mgmt.costmanagement.types.ReportConfigComparisonExpression(TypedDict, total=False):
        key "name": Required[str]
        key "operator": Required[Union[str, OperatorType]]
        key "values": Required[list[str]]
        name: str
        operator: Union[str, OperatorType]
        values_property: list[str]


    class azure.mgmt.costmanagement.types.ReportConfigDataset(TypedDict, total=False):
        key "configuration": ForwardRef('ReportConfigDatasetConfiguration', module='types')
        key "filter": ForwardRef('ReportConfigFilter', module='types')
        key "granularity": Union[str, ReportGranularityType]
        aggregation: dict[str, ReportConfigAggregation]
        configuration: ReportConfigDatasetConfiguration
        filter: ReportConfigFilter
        granularity: Union[str, ReportGranularityType]
        grouping: list[ReportConfigGrouping]
        sorting: list[ReportConfigSorting]


    class azure.mgmt.costmanagement.types.ReportConfigDatasetConfiguration(TypedDict, total=False):
        columns: list[str]


    class azure.mgmt.costmanagement.types.ReportConfigDefinition(TypedDict, total=False):
        key "dataSet": ForwardRef('ReportConfigDataset', module='types')
        key "includeMonetaryCommitment": bool
        key "timePeriod": ForwardRef('ReportConfigTimePeriod', module='types')
        key "timeframe": Required[Union[str, ReportTimeframeType]]
        key "type": Required[Union[str, ReportType]]
        data_set: ReportConfigDataset
        include_monetary_commitment: bool
        time_period: ReportConfigTimePeriod
        timeframe: Union[str, ReportTimeframeType]
        type: Union[str, ReportType]


    class azure.mgmt.costmanagement.types.ReportConfigFilter(TypedDict):
        key "dimensions": ForwardRef('ReportConfigComparisonExpression', module='types')
        key "tags": ForwardRef('ReportConfigComparisonExpression', module='types')
        and: list[ReportConfigFilter]
        and_property: list[ReportConfigFilter]
        dimensions: ReportConfigComparisonExpression
        or: list[ReportConfigFilter]
        or_property: list[ReportConfigFilter]
        tags: ReportConfigComparisonExpression


    class azure.mgmt.costmanagement.types.ReportConfigGrouping(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Union[str, QueryColumnType]]
        name: str
        type: Union[str, QueryColumnType]


    class azure.mgmt.costmanagement.types.ReportConfigSorting(TypedDict, total=False):
        key "direction": Union[str, ReportConfigSortingType]
        key "name": Required[str]
        direction: Union[str, ReportConfigSortingType]
        name: str


    class azure.mgmt.costmanagement.types.ReportConfigTimePeriod(TypedDict):
        key "from": Required[str]
        key "to": Required[str]
        from_property: str
        to: str


    class azure.mgmt.costmanagement.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.costmanagement.types.ScheduleProperties(TypedDict, total=False):
        key "dayOfMonth": int
        key "endDate": Required[str]
        key "frequency": Required[Union[str, ScheduleFrequency]]
        key "hourOfDay": int
        key "startDate": Required[str]
        day_of_month: int
        daysOfWeek: list[Union[str, DaysOfWeek]]
        days_of_week: list[Union[str, DaysOfWeek]]
        end_date: str
        frequency: Union[str, ScheduleFrequency]
        hour_of_day: int
        start_date: str
        weeksOfMonth: list[Union[str, WeeksOfMonth]]
        weeks_of_month: list[Union[str, WeeksOfMonth]]


    class azure.mgmt.costmanagement.types.ScheduledAction(ProxyResource):
        key "eTag": str
        key "id": str
        key "kind": Union[str, ScheduledActionKind]
        key "name": str
        key "properties": ForwardRef('ScheduledActionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        e_tag: str
        id: str
        kind: Union[str, ScheduledActionKind]
        name: str
        properties: ScheduledActionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.costmanagement.types.ScheduledActionProperties(TypedDict, total=False):
        key "displayName": Required[str]
        key "fileDestination": ForwardRef('FileDestination', module='types')
        key "notification": Required[NotificationProperties]
        key "notificationEmail": str
        key "schedule": Required[ScheduleProperties]
        key "scope": str
        key "status": Required[Union[str, ScheduledActionStatus]]
        key "viewId": Required[str]
        display_name: str
        file_destination: FileDestination
        notification: NotificationProperties
        notification_email: str
        schedule: ScheduleProperties
        scope: str
        status: Union[str, ScheduledActionStatus]
        view_id: str


    class azure.mgmt.costmanagement.types.Setting(TypedDict, total=False):
        key "id": str
        key "kind": Required[Literal[SettingsKind.TAGINHERITANCE]]
        key "name": str
        key "properties": ForwardRef('TagInheritanceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Literal[SettingsKind.TAGINHERITANCE]
        name: str
        properties: TagInheritanceProperties
        system_data: SystemData
        type: str


    class azure.mgmt.costmanagement.types.SettingsKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TAGINHERITANCE = "taginheritance"


    class azure.mgmt.costmanagement.types.SourceCostAllocationResource(CostAllocationResource):
        key "name": Required[str]
        key "resourceType": Required[Union[str, CostAllocationResourceType]]
        key "values": Required[list[str]]
        name: str
        resource_type: Union[str, CostAllocationResourceType]
        values_property: list[str]


    class azure.mgmt.costmanagement.types.SystemAssignedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, SystemAssignedServiceIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, SystemAssignedServiceIdentityType]


    class azure.mgmt.costmanagement.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.costmanagement.types.TagInheritanceProperties(TypedDict, total=False):
        key "preferContainerTags": Required[bool]
        prefer_container_tags: bool


    class azure.mgmt.costmanagement.types.TagInheritanceSetting(TypedDict, total=False):
        key "id": str
        key "kind": Required[Literal[SettingsKind.TAGINHERITANCE]]
        key "name": str
        key "properties": ForwardRef('TagInheritanceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Literal[SettingsKind.TAGINHERITANCE]
        name: str
        properties: TagInheritanceProperties
        system_data: SystemData
        type: str


    class azure.mgmt.costmanagement.types.TargetCostAllocationResource(CostAllocationResource):
        key "name": Required[str]
        key "policyType": Required[Union[str, CostAllocationPolicyType]]
        key "resourceType": Required[Union[str, CostAllocationResourceType]]
        key "values": Required[list[CostAllocationProportion]]
        name: str
        policy_type: Union[str, CostAllocationPolicyType]
        resource_type: Union[str, CostAllocationResourceType]
        values_property: list[CostAllocationProportion]


    class azure.mgmt.costmanagement.types.View(ProxyResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('ViewProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        e_tag: str
        id: str
        name: str
        properties: ViewProperties
        system_data: SystemData
        type: str


    class azure.mgmt.costmanagement.types.ViewProperties(TypedDict, total=False):
        key "accumulated": Union[str, AccumulatedType]
        key "chart": Union[str, ChartType]
        key "createdOn": str
        key "currency": str
        key "dateRange": str
        key "displayName": str
        key "metric": Union[str, MetricType]
        key "modifiedOn": str
        key "query": ForwardRef('ReportConfigDefinition', module='types')
        key "scope": str
        accumulated: Union[str, AccumulatedType]
        chart: Union[str, ChartType]
        created_on: str
        currency: str
        date_range: str
        display_name: str
        kpis: list[KpiProperties]
        metric: Union[str, MetricType]
        modified_on: str
        pivots: list[PivotProperties]
        query: ReportConfigDefinition
        scope: str


```