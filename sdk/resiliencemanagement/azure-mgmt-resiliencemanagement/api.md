```py
namespace azure.mgmt.resiliencemanagement

    class azure.mgmt.resiliencemanagement.ResilienceManagementClient: implements ContextManager 
        drill_resources: DrillResourcesOperations
        drill_run_resources: DrillRunResourcesOperations
        drill_runs: DrillRunsOperations
        drills: DrillsOperations
        enrollments: EnrollmentsOperations
        goal_assignments: GoalAssignmentsOperations
        goal_resources: GoalResourcesOperations
        goal_templates: GoalTemplatesOperations
        operation_status: OperationStatusOperations
        operations: Operations
        recovery_job_resources: RecoveryJobResourcesOperations
        recovery_jobs: RecoveryJobsOperations
        recovery_plan_actions: RecoveryPlanActionsOperations
        recovery_plans: RecoveryPlansOperations
        recovery_resources: RecoveryResourcesOperations
        unified_resilience_items: UnifiedResilienceItemsOperations
        usage_plans: UsagePlansOperations

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


namespace azure.mgmt.resiliencemanagement.aio

    class azure.mgmt.resiliencemanagement.aio.ResilienceManagementClient: implements AsyncContextManager 
        drill_resources: DrillResourcesOperations
        drill_run_resources: DrillRunResourcesOperations
        drill_runs: DrillRunsOperations
        drills: DrillsOperations
        enrollments: EnrollmentsOperations
        goal_assignments: GoalAssignmentsOperations
        goal_resources: GoalResourcesOperations
        goal_templates: GoalTemplatesOperations
        operation_status: OperationStatusOperations
        operations: Operations
        recovery_job_resources: RecoveryJobResourcesOperations
        recovery_jobs: RecoveryJobsOperations
        recovery_plan_actions: RecoveryPlanActionsOperations
        recovery_plans: RecoveryPlansOperations
        recovery_resources: RecoveryResourcesOperations
        unified_resilience_items: UnifiedResilienceItemsOperations
        usage_plans: UsagePlansOperations

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


namespace azure.mgmt.resiliencemanagement.aio.operations

    class azure.mgmt.resiliencemanagement.aio.operations.DrillResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_resource_name: str, 
                **kwargs: Any
            ) -> DrillResource: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                drill_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DrillResource]: ...


    class azure.mgmt.resiliencemanagement.aio.operations.DrillRunResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                drill_run_resource_name: str, 
                **kwargs: Any
            ) -> DrillRunResource: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DrillRunResource]: ...


    class azure.mgmt.resiliencemanagement.aio.operations.DrillRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_add_notes(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: DrillRunAddNotesRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_add_notes(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: DrillRunAddNotesRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_add_notes(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_fail_over(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: Optional[DrillRunFailoverRequest] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_fail_over(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: Optional[DrillRunFailoverRequest] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_fail_over(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-08-31-preview', params_added_on={'2026-08-31-preview': ['service_group_name', 'api_version', 'operation_id', 'drill_name', 'drill_run_name', 'accept']}, api_versions_list=['2026-08-31-preview'])
        async def begin_generate_report(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                *, 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_mark_as_complete(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: MarkAsCompleteRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_mark_as_complete(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: MarkAsCompleteRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_mark_as_complete(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reprotect(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: Optional[DrillRunReprotectRequest] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reprotect(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: Optional[DrillRunReprotectRequest] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reprotect(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_resume(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                *, 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                **kwargs: Any
            ) -> DrillRun: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                drill_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DrillRun]: ...

        @overload
        async def list_report_download_url(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: Optional[ListReportDownloadUrlRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListReportDownloadUrlResponse: ...

        @overload
        async def list_report_download_url(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: Optional[ListReportDownloadUrlRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListReportDownloadUrlResponse: ...

        @overload
        async def list_report_download_url(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListReportDownloadUrlResponse: ...


    class azure.mgmt.resiliencemanagement.aio.operations.DrillsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_add_or_update_resources(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: AddOrUpdateResourcesRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_add_or_update_resources(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: AddOrUpdateResourcesRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_add_or_update_resources(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create(
                self, 
                service_group_name: str, 
                drill_name: str, 
                resource: Drill, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Drill]: ...

        @overload
        async def begin_create(
                self, 
                service_group_name: str, 
                drill_name: str, 
                resource: Drill, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Drill]: ...

        @overload
        async def begin_create(
                self, 
                service_group_name: str, 
                drill_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Drill]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                service_group_name: str, 
                drill_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_end(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: DrillEndRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_end(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: DrillEndRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_end(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['service_group_name', 'api_version', 'operation_id', 'drill_name']}, api_versions_list=['2026-03-01-preview', '2026-04-01-preview', '2026-06-01-preview', '2026-08-31-preview'])
        async def begin_resync_readiness_check(
                self, 
                service_group_name: str, 
                drill_name: str, 
                *, 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_start(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: DrillStartRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_start(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: DrillStartRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_start(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                service_group_name: str, 
                drill_name: str, 
                properties: DrillUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                service_group_name: str, 
                drill_name: str, 
                properties: DrillUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                service_group_name: str, 
                drill_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_validate_for_execution(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: ValidateForExecutionRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_validate_for_execution(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: ValidateForExecutionRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_validate_for_execution(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                service_group_name: str, 
                drill_name: str, 
                **kwargs: Any
            ) -> Drill: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Drill]: ...


    class azure.mgmt.resiliencemanagement.aio.operations.EnrollmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                enrollment_name: str, 
                resource: Enrollment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Enrollment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                enrollment_name: str, 
                resource: Enrollment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Enrollment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                enrollment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Enrollment]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'usage_plan_name', 'enrollment_name']}, api_versions_list=['2026-03-01-preview', '2026-04-01-preview', '2026-06-01-preview', '2026-08-31-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                enrollment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'usage_plan_name', 'enrollment_name', 'accept']}, api_versions_list=['2026-03-01-preview', '2026-04-01-preview', '2026-06-01-preview', '2026-08-31-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                enrollment_name: str, 
                **kwargs: Any
            ) -> Enrollment: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'usage_plan_name', 'accept']}, api_versions_list=['2026-03-01-preview', '2026-04-01-preview', '2026-06-01-preview', '2026-08-31-preview'])
        def list(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Enrollment]: ...


    class azure.mgmt.resiliencemanagement.aio.operations.GoalAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                resource: GoalAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                resource: GoalAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_recommend_capacity(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                body: RecommendCapacityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_recommend_capacity(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                body: RecommendCapacityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_recommend_capacity(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_refresh_goal_resources(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                properties: GoalAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                properties: GoalAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_goal_resources(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                body: UpdateGoalResourceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_goal_resources(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                body: UpdateGoalResourceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_goal_resources(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                **kwargs: Any
            ) -> GoalAssignment: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[GoalAssignment]: ...


    class azure.mgmt.resiliencemanagement.aio.operations.GoalResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                goal_resource_name: str, 
                **kwargs: Any
            ) -> GoalResource: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[GoalResource]: ...


    class azure.mgmt.resiliencemanagement.aio.operations.GoalTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                service_group_name: str, 
                goal_template_name: str, 
                resource: GoalTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GoalTemplate]: ...

        @overload
        async def begin_create_or_update(
                self, 
                service_group_name: str, 
                goal_template_name: str, 
                resource: GoalTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GoalTemplate]: ...

        @overload
        async def begin_create_or_update(
                self, 
                service_group_name: str, 
                goal_template_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GoalTemplate]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                service_group_name: str, 
                goal_template_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                service_group_name: str, 
                goal_template_name: str, 
                properties: GoalTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                service_group_name: str, 
                goal_template_name: str, 
                properties: GoalTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                service_group_name: str, 
                goal_template_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                service_group_name: str, 
                goal_template_name: str, 
                **kwargs: Any
            ) -> GoalTemplate: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[GoalTemplate]: ...


    class azure.mgmt.resiliencemanagement.aio.operations.OperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


    class azure.mgmt.resiliencemanagement.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.resiliencemanagement.aio.operations.RecoveryJobResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                recovery_job_name: str, 
                recovery_job_resource_name: str, 
                **kwargs: Any
            ) -> RecoveryJobResource: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                recovery_job_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RecoveryJobResource]: ...


    class azure.mgmt.resiliencemanagement.aio.operations.RecoveryJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_cancel(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                recovery_job_name: str, 
                body: RecoveryActionRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ArmResponseErrorResponse]: ...

        @overload
        async def begin_cancel(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                recovery_job_name: str, 
                body: RecoveryActionRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ArmResponseErrorResponse]: ...

        @overload
        async def begin_cancel(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                recovery_job_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ArmResponseErrorResponse]: ...

        @overload
        async def begin_resume(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                recovery_job_name: str, 
                body: RecoveryActionRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ArmResponseErrorResponse]: ...

        @overload
        async def begin_resume(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                recovery_job_name: str, 
                body: RecoveryActionRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ArmResponseErrorResponse]: ...

        @overload
        async def begin_resume(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                recovery_job_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ArmResponseErrorResponse]: ...

        @distributed_trace_async
        async def begin_retry(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                recovery_job_name: str, 
                *, 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ArmResponseErrorResponse]: ...

        @distributed_trace_async
        async def get(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                recovery_job_name: str, 
                **kwargs: Any
            ) -> RecoveryJob: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RecoveryJob]: ...


    class azure.mgmt.resiliencemanagement.aio.operations.RecoveryPlanActionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_check_readiness(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                *, 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: FailoverRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlanActionBaseResponse]: ...

        @overload
        async def begin_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: FailoverRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlanActionBaseResponse]: ...

        @overload
        async def begin_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlanActionBaseResponse]: ...

        @distributed_trace_async
        async def begin_failover_commit(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                *, 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlanActionBaseResponse]: ...

        @distributed_trace_async
        async def begin_finalize(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                *, 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ArmResponseErrorResponse]: ...

        @overload
        async def begin_reprotect(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: Optional[ReprotectRequest] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlanActionBaseResponse]: ...

        @overload
        async def begin_reprotect(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: Optional[ReprotectRequest] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlanActionBaseResponse]: ...

        @overload
        async def begin_reprotect(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlanActionBaseResponse]: ...

        @overload
        async def begin_test_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: FailoverRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlanActionBaseResponse]: ...

        @overload
        async def begin_test_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: FailoverRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlanActionBaseResponse]: ...

        @overload
        async def begin_test_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlanActionBaseResponse]: ...

        @overload
        async def begin_test_failover_cleanup(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: TestFailoverCleanupRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlanActionBaseResponse]: ...

        @overload
        async def begin_test_failover_cleanup(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: TestFailoverCleanupRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlanActionBaseResponse]: ...

        @overload
        async def begin_test_failover_cleanup(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlanActionBaseResponse]: ...

        @overload
        async def begin_update_resources(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: UpdateRecoveryResourcesRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateRecoveryResourcesResponse]: ...

        @overload
        async def begin_update_resources(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: UpdateRecoveryResourcesRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateRecoveryResourcesResponse]: ...

        @overload
        async def begin_update_resources(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateRecoveryResourcesResponse]: ...

        @overload
        async def begin_validate_for_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: FailoverRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateForRecoveryOperationBaseResponse]: ...

        @overload
        async def begin_validate_for_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: FailoverRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateForRecoveryOperationBaseResponse]: ...

        @overload
        async def begin_validate_for_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateForRecoveryOperationBaseResponse]: ...

        @distributed_trace_async
        async def begin_validate_for_failover_commit(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                *, 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateForRecoveryOperationBaseResponse]: ...

        @overload
        async def begin_validate_for_operation(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: ValidateForOperationRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ArmResponseErrorResponse]: ...

        @overload
        async def begin_validate_for_operation(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: ValidateForOperationRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ArmResponseErrorResponse]: ...

        @overload
        async def begin_validate_for_operation(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ArmResponseErrorResponse]: ...

        @overload
        async def begin_validate_for_reprotect(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: Optional[ReprotectRequest] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateForRecoveryOperationBaseResponse]: ...

        @overload
        async def begin_validate_for_reprotect(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: Optional[ReprotectRequest] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateForRecoveryOperationBaseResponse]: ...

        @overload
        async def begin_validate_for_reprotect(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateForRecoveryOperationBaseResponse]: ...

        @overload
        async def begin_validate_for_test_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: FailoverRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateForRecoveryOperationBaseResponse]: ...

        @overload
        async def begin_validate_for_test_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: FailoverRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateForRecoveryOperationBaseResponse]: ...

        @overload
        async def begin_validate_for_test_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateForRecoveryOperationBaseResponse]: ...

        @distributed_trace_async
        async def begin_validate_for_test_failover_cleanup(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                *, 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateForRecoveryOperationBaseResponse]: ...


    class azure.mgmt.resiliencemanagement.aio.operations.RecoveryPlansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                resource: RecoveryPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @overload
        async def begin_create_or_update(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                resource: RecoveryPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @overload
        async def begin_create_or_update(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                properties: RecoveryPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @overload
        async def begin_update(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                properties: RecoveryPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @overload
        async def begin_update(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecoveryPlan]: ...

        @distributed_trace_async
        async def get(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                **kwargs: Any
            ) -> RecoveryPlan: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RecoveryPlan]: ...


    class azure.mgmt.resiliencemanagement.aio.operations.RecoveryResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                recovery_resource_name: str, 
                **kwargs: Any
            ) -> RecoveryResource: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RecoveryResource]: ...


    class azure.mgmt.resiliencemanagement.aio.operations.UnifiedResilienceItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                service_group_name: str, 
                unified_resilience_item_name: str, 
                **kwargs: Any
            ) -> UnifiedResilienceItem: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[UnifiedResilienceItem]: ...


    class azure.mgmt.resiliencemanagement.aio.operations.UsagePlansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                resource: UsagePlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UsagePlan]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                resource: UsagePlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UsagePlan]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UsagePlan]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'usage_plan_name']}, api_versions_list=['2026-03-01-preview', '2026-04-01-preview', '2026-06-01-preview', '2026-08-31-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                properties: UsagePlanTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UsagePlan]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                properties: UsagePlanTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UsagePlan]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[UsagePlan]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'usage_plan_name', 'accept']}, api_versions_list=['2026-03-01-preview', '2026-04-01-preview', '2026-06-01-preview', '2026-08-31-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                **kwargs: Any
            ) -> UsagePlan: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-03-01-preview', '2026-04-01-preview', '2026-06-01-preview', '2026-08-31-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[UsagePlan]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-03-01-preview', '2026-04-01-preview', '2026-06-01-preview', '2026-08-31-preview'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[UsagePlan]: ...


namespace azure.mgmt.resiliencemanagement.models

    class azure.mgmt.resiliencemanagement.models.ActionTask(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        POST_ACTION_TASK = "PostActionTask"
        PRE_ACTION_TASK = "PreActionTask"


    class azure.mgmt.resiliencemanagement.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.resiliencemanagement.models.AddOrUpdateResourcesRequest(_Model):
        fault_duration_in_min: int
        force_inclusion_and_update: Optional[Union[str, ForceInclusionAndUpdate]]
        resource_lists: Optional[ResourceLists]

        @overload
        def __init__(
                self, 
                *, 
                fault_duration_in_min: int, 
                force_inclusion_and_update: Optional[Union[str, ForceInclusionAndUpdate]] = ..., 
                resource_lists: Optional[ResourceLists] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ArmResponseErrorResponse(_Model):
        body: ErrorResponse

        @overload
        def __init__(
                self, 
                *, 
                body: ErrorResponse
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.AssetPropertiesOfDrill(_Model):
        region: str
        resource_group: Optional[str]
        subscription: str

        @overload
        def __init__(
                self, 
                *, 
                region: str, 
                resource_group: Optional[str] = ..., 
                subscription: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.AssociatedIdentity(_Model):
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.AttentionReason(_Model):
        chaos_resource: Optional[Union[str, ExtensionObjectState]]
        chaos_resource_creation_failure_reasons: Optional[list[str]]
        chaos_resource_user_msi: Optional[Union[str, ExtensionObjectState]]
        discovery_rule_exists: Optional[Union[str, ExtensionObjectState]]
        drill_monitoring_errors: Optional[list[ErrorDetails]]
        drill_monitoring_resources: Optional[Union[str, ExtensionObjectState]]
        drill_rbac_on_chaos_resource: Optional[Union[str, RBACState]]
        drill_rbac_on_health_model: Optional[Union[str, RBACState]]
        drill_rbac_on_monitoring_resources: Optional[Union[str, RBACState]]
        drill_rbac_on_recovery_plan: Optional[Union[str, RBACState]]
        drill_rbac_on_sli: Optional[Union[str, RBACState]]
        drill_user_msi: Optional[Union[str, ExtensionObjectState]]
        health_model_exists: Optional[Union[str, ExtensionObjectState]]
        included_resource_in_drill: Optional[Union[str, ExtensionObjectState]]
        missing_required_resource_providers: Optional[list[str]]
        monitoring_rbac_on_drill_resources: Optional[Union[str, RBACState]]
        monitoring_source_not_configured: Optional[bool]
        rbac_needed_for_drill_on_chaos_resource: Optional[list[str]]
        rbac_needed_for_drill_on_drill_monitoring_resources: Optional[list[str]]
        rbac_needed_for_drill_on_drill_resources: Optional[list[str]]
        rbac_needed_for_drill_on_health_model: Optional[list[str]]
        rbac_needed_for_drill_on_recovery_plan: Optional[list[str]]
        rbac_on_target_resources: Optional[Union[str, RBACState]]
        recovery_plan_and_drill_resources_state: Optional[Union[str, RelativeResourceCompositionState]]
        ro_readiness: Optional[Union[str, RecoveryPlanState]]
        runbook_fault_rbac_on_targets: Optional[Union[str, RBACState]]
        service_group_and_drill_resources_state: Optional[Union[str, RelativeResourceCompositionState]]
        sli_attention_statuses: Optional[list[SliAttentionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                chaos_resource: Optional[Union[str, ExtensionObjectState]] = ..., 
                chaos_resource_creation_failure_reasons: Optional[list[str]] = ..., 
                chaos_resource_user_msi: Optional[Union[str, ExtensionObjectState]] = ..., 
                discovery_rule_exists: Optional[Union[str, ExtensionObjectState]] = ..., 
                drill_monitoring_errors: Optional[list[ErrorDetails]] = ..., 
                drill_rbac_on_chaos_resource: Optional[Union[str, RBACState]] = ..., 
                drill_rbac_on_health_model: Optional[Union[str, RBACState]] = ..., 
                drill_rbac_on_monitoring_resources: Optional[Union[str, RBACState]] = ..., 
                drill_rbac_on_recovery_plan: Optional[Union[str, RBACState]] = ..., 
                drill_rbac_on_sli: Optional[Union[str, RBACState]] = ..., 
                drill_user_msi: Optional[Union[str, ExtensionObjectState]] = ..., 
                health_model_exists: Optional[Union[str, ExtensionObjectState]] = ..., 
                included_resource_in_drill: Optional[Union[str, ExtensionObjectState]] = ..., 
                missing_required_resource_providers: Optional[list[str]] = ..., 
                monitoring_rbac_on_drill_resources: Optional[Union[str, RBACState]] = ..., 
                monitoring_source_not_configured: Optional[bool] = ..., 
                rbac_needed_for_drill_on_chaos_resource: Optional[list[str]] = ..., 
                rbac_needed_for_drill_on_drill_monitoring_resources: Optional[list[str]] = ..., 
                rbac_needed_for_drill_on_drill_resources: Optional[list[str]] = ..., 
                rbac_needed_for_drill_on_health_model: Optional[list[str]] = ..., 
                rbac_needed_for_drill_on_recovery_plan: Optional[list[str]] = ..., 
                rbac_on_target_resources: Optional[Union[str, RBACState]] = ..., 
                recovery_plan_and_drill_resources_state: Optional[Union[str, RelativeResourceCompositionState]] = ..., 
                ro_readiness: Optional[Union[str, RecoveryPlanState]] = ..., 
                runbook_fault_rbac_on_targets: Optional[Union[str, RBACState]] = ..., 
                service_group_and_drill_resources_state: Optional[Union[str, RelativeResourceCompositionState]] = ..., 
                sli_attention_statuses: Optional[list[SliAttentionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.AttestationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANUALLY_ATTESTED = "ManuallyAttested"
        NOT_ATTESTED = "NotAttested"


    class azure.mgmt.resiliencemanagement.models.AutoFailover(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"


    class azure.mgmt.resiliencemanagement.models.ChaosResourcePropertiesOfDrill(_Model):
        chaos_resource_id: Optional[str]
        chaos_resource_identity_for_faults: AssociatedIdentity
        fault_duration_in_min: Optional[int]
        identity: AssociatedIdentity

        @overload
        def __init__(
                self, 
                *, 
                chaos_resource_identity_for_faults: AssociatedIdentity, 
                identity: AssociatedIdentity
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.CommentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DESCRIPTION = "Description"
        RESUME_REASON = "ResumeReason"


    class azure.mgmt.resiliencemanagement.models.ConfirmationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVAL_NOT_NEEDED = "ApprovalNotNeeded"
        APPROVAL_PENDING = "ApprovalPending"
        APPROVED_BY_USER = "ApprovedByUser"
        REJECTED_BY_USER = "RejectedByUser"


    class azure.mgmt.resiliencemanagement.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.resiliencemanagement.models.CustomFaultDetails(_Model):
        fault_name: str
        script_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                fault_name: str, 
                script_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.DiskReprotectInputDetails(_Model):
        disk_resource_id: Optional[str]
        staging_storage_account_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                disk_resource_id: Optional[str] = ..., 
                staging_storage_account_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.Drill(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        name: str
        properties: Optional[DrillProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[DrillProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.DrillAttestation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ATTESTED_FAILED = "Failed"
        ATTESTED_SUCCESS = "Success"


    class azure.mgmt.resiliencemanagement.models.DrillEndRequest(_Model):
        attestation: Union[str, DrillAttestation]
        attestation_notes: str

        @overload
        def __init__(
                self, 
                *, 
                attestation: Union[str, DrillAttestation], 
                attestation_notes: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.DrillMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILOVER = "Failover"


    class azure.mgmt.resiliencemanagement.models.DrillProperties(_Model):
        attention_reason: Optional[AttentionReason]
        chaos_resource_properties: Optional[ChaosResourcePropertiesOfDrill]
        drill_asset_properties: Optional[AssetPropertiesOfDrill]
        drill_type: str
        error_details: Optional[ErrorDetail]
        execution_readiness_state: Optional[Union[str, ExecutionReadinessState]]
        execution_state: Optional[Union[str, ExecutionState]]
        health_model_monitoring_properties: Optional[HealthModelMonitoringProperties]
        last_resync_readiness_check_time: Optional[datetime]
        last_run_properties: Optional[LastRunProperties]
        last_sync_time: Optional[datetime]
        monitoring_properties: Optional[MonitoringPropertiesOfDrill]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        rbac_setup_mode: Optional[Union[str, RBACSetupMode]]
        recovery_plan_properties: Optional[RecoveryPlanPropertiesOfDrill]
        service_group_id: Optional[str]
        sli_monitoring_properties: Optional[SliMonitoringProperties]
        system_metadata: Optional[SystemMetadata]

        @overload
        def __init__(
                self, 
                *, 
                chaos_resource_properties: Optional[ChaosResourcePropertiesOfDrill] = ..., 
                drill_asset_properties: Optional[AssetPropertiesOfDrill] = ..., 
                drill_type: str, 
                health_model_monitoring_properties: Optional[HealthModelMonitoringProperties] = ..., 
                monitoring_properties: Optional[MonitoringPropertiesOfDrill] = ..., 
                rbac_setup_mode: Optional[Union[str, RBACSetupMode]] = ..., 
                recovery_plan_properties: Optional[RecoveryPlanPropertiesOfDrill] = ..., 
                sli_monitoring_properties: Optional[SliMonitoringProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.DrillReportFinalizationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FINALIZED = "Finalized"
        NOT_FINALIZED = "NotFinalized"


    class azure.mgmt.resiliencemanagement.models.DrillReportFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTML = "Html"


    class azure.mgmt.resiliencemanagement.models.DrillReportGenerationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NOT_STARTED = "NotStarted"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.resiliencemanagement.models.DrillReportSummary(_Model):
        available_formats: Optional[list[Union[str, DrillReportFormat]]]
        finalization_state: Optional[Union[str, DrillReportFinalizationState]]
        generation_status: Optional[Union[str, DrillReportGenerationStatus]]
        last_error: Optional[ErrorDetails]
        last_generated_timestamp: Optional[datetime]
        schema_version: Optional[str]
        stage_statuses: Optional[list[ReportStageStatus]]


    class azure.mgmt.resiliencemanagement.models.DrillResource(ProxyResource):
        id: str
        name: str
        properties: Optional[DrillResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DrillResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.DrillResourceAttentionReason(_Model):
        fault_rbac_on_target_resource: Optional[Union[str, RBACState]]
        monitoring_rbac_on_targets: Optional[Union[str, RBACState]]
        resource_state: Optional[list[Union[str, DrillResourceState]]]
        runbook_fault_rbac_on_targets: Optional[Union[str, RBACState]]

        @overload
        def __init__(
                self, 
                *, 
                fault_rbac_on_target_resource: Optional[Union[str, RBACState]] = ..., 
                monitoring_rbac_on_targets: Optional[Union[str, RBACState]] = ..., 
                resource_state: Optional[list[Union[str, DrillResourceState]]] = ..., 
                runbook_fault_rbac_on_targets: Optional[Union[str, RBACState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.DrillResourceFaultState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_SCRIPT = "CustomScript"
        NOT_DEFINED = "NotDefined"
        SYSTEM_NATIVE = "SystemNative"


    class azure.mgmt.resiliencemanagement.models.DrillResourceInclusionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCLUDED = "Excluded"
        INCLUDED = "Included"


    class azure.mgmt.resiliencemanagement.models.DrillResourceProperties(_Model):
        active_locations: Optional[list[str]]
        active_physical_zones: Optional[list[str]]
        advisor_ha_recommendation_id: Optional[str]
        advisor_recommendation_type_id: Optional[str]
        attention_reason: Optional[DrillResourceAttentionReason]
        fault_properties: Optional[FaultProperties]
        fault_state: Optional[Union[str, DrillResourceFaultState]]
        force_inclusion_state: Optional[Union[str, ForceInclusionAndUpdate]]
        ha_status: Optional[Union[str, HAStatus]]
        inclusion_state: Optional[Union[str, DrillResourceInclusionState]]
        monitoring_rbac_assignment_error: Optional[ErrorDetails]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        rbac_assignment_error: Optional[ErrorDetails]
        readiness_state: Optional[Union[str, DrillResourceReadinessState]]
        recovery_locations: Optional[list[str]]
        recovery_physical_zones: Optional[list[str]]
        recovery_plan_exclusion_reason: Optional[Union[str, RecoveryPlanExclusionReason]]
        recovery_plan_inclusion_state: Optional[Union[str, ResourceInclusionState]]
        resource_id: str
        resource_protection_solution_type: Optional[Union[str, ResourceProtectionSolutionType]]
        resource_type: str

        @overload
        def __init__(
                self, 
                *, 
                inclusion_state: Optional[Union[str, DrillResourceInclusionState]] = ..., 
                resource_id: str, 
                resource_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.DrillResourceReadinessState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NEEDS_ATTENTION = "NeedsAttention"
        READY = "Ready"


    class azure.mgmt.resiliencemanagement.models.DrillResourceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IN_DRILL_NOT_IN_RECOVERY_PLAN = "InDrillNotInRecoveryPlan"
        IN_DRILL_NOT_IN_SERVICE_GROUP = "InDrillNotInServiceGroup"
        IN_RECOVERY_PLAN_NOT_IN_DRILL = "InRecoveryPlanNotInDrill"
        IN_SERVICE_GROUP_NOT_IN_DRILL = "InServiceGroupNotInDrill"
        RESOURCE_STATE_INCOMPATIBLE_WITH_FAULT = "ResourceStateIncompatibleWithFault"


    class azure.mgmt.resiliencemanagement.models.DrillRun(ProxyResource):
        id: str
        name: str
        properties: Optional[DrillRunProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DrillRunProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.DrillRunAddNotesRequest(_Model):
        author: Optional[str]
        notes: Optional[str]
        timestamp: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                notes: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.DrillRunFailoverRequest(_Model):
        auto_failover: Union[str, AutoFailover]
        failover_properties: FailoverRequest

        @overload
        def __init__(
                self, 
                *, 
                auto_failover: Union[str, AutoFailover], 
                failover_properties: FailoverRequest
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.DrillRunOperationVerbs(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCEL = "Cancel"
        MARK_AS_COMPLETE = "MarkAsComplete"
        RETRY = "Retry"
        START = "Start"


    class azure.mgmt.resiliencemanagement.models.DrillRunProperties(JobProperties, discriminator='DrillRun'):
        attestation: Optional[Union[str, DrillAttestation]]
        current_active_operation_id: Optional[str]
        drill_id: Optional[str]
        drill_mode: Optional[Union[str, DrillMode]]
        duration: timedelta
        end_time: datetime
        error_details: JobErrorInfo
        execution_configurations: ExecutionConfigurations
        job_extended_info: JobExtendedInfo
        job_type: Literal[JobType.DRILL_RUN]
        notes: Optional[list[str]]
        operation: str
        report: Optional[DrillReportSummary]
        resource_id: str
        retry_details: list[JobRetryDetails]
        start_time: datetime
        status: Union[str, JobStatus]
        supported_verbs_for_stage: Optional[list[SupportedVerbsForStage]]
        triggered_by: Union[str, JobTriggeredBy]
        user_comments: list[JobUserComment]

        @overload
        def __init__(
                self, 
                *, 
                error_details: Optional[JobErrorInfo] = ..., 
                job_extended_info: Optional[JobExtendedInfo] = ..., 
                retry_details: Optional[list[JobRetryDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.DrillRunReprotectRequest(_Model):
        reprotect_properties: ReprotectRequest

        @overload
        def __init__(
                self, 
                *, 
                reprotect_properties: ReprotectRequest
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.DrillRunResource(ProxyResource):
        id: str
        name: str
        properties: Optional[DrillRunResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DrillRunResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.DrillRunResourceProperties(JobResourceProperties, discriminator='DrillRun'):
        duration: timedelta
        end_time: datetime
        error_details: JobErrorInfo
        job_extended_info: JobExtendedInfo
        job_id: str
        job_resource_type: Literal[JobResourceType.DRILL_RUN]
        operation: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_id: str
        retry_details: list[JobRetryDetails]
        start_time: datetime
        status: Union[str, JobStatus]
        task_id: str
        task_name: str
        user_comments: list[JobUserComment]

        @overload
        def __init__(
                self, 
                *, 
                error_details: Optional[JobErrorInfo] = ..., 
                job_extended_info: Optional[JobExtendedInfo] = ..., 
                retry_details: Optional[list[JobRetryDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.DrillRunSubtasks(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILOVER = "Failover"
        FAILOVER_REVERSE = "FailoverReverse"
        FAULT_INJECTION = "FaultInjection"
        REPROTECT = "Reprotect"
        REPROTECT_REVERSE = "ReprotectReverse"


    class azure.mgmt.resiliencemanagement.models.DrillRunTasks(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILOVER = "Failover"
        FAILOVER_REVERSE = "FailoverReverse"
        REPROTECT = "Reprotect"
        REPROTECT_REVERSE = "ReprotectReverse"


    class azure.mgmt.resiliencemanagement.models.DrillStartRequest(_Model):
        mode: Union[str, DrillMode]

        @overload
        def __init__(
                self, 
                *, 
                mode: Union[str, DrillMode]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.DrillType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REGIONAL = "Regional"
        ZONAL = "Zonal"


    class azure.mgmt.resiliencemanagement.models.DrillUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[DrillUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[DrillUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.DrillUpdateProperties(_Model):
        chaos_resource_properties: Optional[ChaosResourcePropertiesOfDrill]
        drill_asset_properties: Optional[AssetPropertiesOfDrill]
        health_model_monitoring_properties: Optional[HealthModelMonitoringProperties]
        monitoring_properties: Optional[MonitoringPropertiesOfDrill]
        rbac_setup_mode: Optional[Union[str, RBACSetupMode]]
        recovery_plan_properties: Optional[RecoveryPlanPropertiesOfDrill]
        sli_monitoring_properties: Optional[SliMonitoringProperties]

        @overload
        def __init__(
                self, 
                *, 
                chaos_resource_properties: Optional[ChaosResourcePropertiesOfDrill] = ..., 
                drill_asset_properties: Optional[AssetPropertiesOfDrill] = ..., 
                health_model_monitoring_properties: Optional[HealthModelMonitoringProperties] = ..., 
                monitoring_properties: Optional[MonitoringPropertiesOfDrill] = ..., 
                rbac_setup_mode: Optional[Union[str, RBACSetupMode]] = ..., 
                recovery_plan_properties: Optional[RecoveryPlanPropertiesOfDrill] = ..., 
                sli_monitoring_properties: Optional[SliMonitoringProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.Enrollment(ProxyResource):
        id: str
        name: str
        properties: Optional[EnrollmentProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EnrollmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.EnrollmentProperties(_Model):
        error_details: Optional[ErrorDetail]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        service_group_id: str

        @overload
        def __init__(
                self, 
                *, 
                service_group_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.resiliencemanagement.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.resiliencemanagement.models.ErrorDetails(_Model):
        code: str
        message: str
        recommendations: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                message: str, 
                recommendations: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ExclusionReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED_OVER_RESOURCE = "FailedOverResource"
        UNSUPPORTED_RESOURCE = "UnsupportedResource"
        USER_SELECTED_EXCLUSION = "UserSelectedExclusion"


    class azure.mgmt.resiliencemanagement.models.ExclusionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCLUDED = "Excluded"
        INCLUDED = "Included"


    class azure.mgmt.resiliencemanagement.models.ExecutionConfigurations(_Model):
        user_consent: Union[str, UserConsent]

        @overload
        def __init__(
                self, 
                *, 
                user_consent: Union[str, UserConsent]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ExecutionReadinessState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NEEDS_ATTENTION = "NeedsAttention"
        READY = "Ready"


    class azure.mgmt.resiliencemanagement.models.ExecutionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_RUNNING = "NotRunning"
        PAUSED = "Paused"
        RUNNING = "Running"


    class azure.mgmt.resiliencemanagement.models.ExtensionObjectState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXISTS = "Exists"
        NOT_EXISTS = "NotExists"


    class azure.mgmt.resiliencemanagement.models.FailoverDirectionTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FROM_SPECIFIC_LOCATIONS = "FromSpecificLocations"


    class azure.mgmt.resiliencemanagement.models.FailoverRequest(_Model):
        failover_direction: Union[str, FailoverDirectionTypes]
        failover_request_properties: Optional[FailoverRequestProperties]

        @overload
        def __init__(
                self, 
                *, 
                failover_direction: Union[str, FailoverDirectionTypes], 
                failover_request_properties: Optional[FailoverRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.FailoverRequestProperties(_Model):
        execution_configurations: Optional[ExecutionConfigurations]
        selected_resource_ids: Optional[list[str]]
        source_locations: list[str]

        @overload
        def __init__(
                self, 
                *, 
                execution_configurations: Optional[ExecutionConfigurations] = ..., 
                selected_resource_ids: Optional[list[str]] = ..., 
                source_locations: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.FailoverState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED_OVER = "FailedOver"
        FAILED_OVER_COMMIT_PENDING = "FailedOverCommitPending"
        FAILED_OVER_REPROTECT_PENDING = "FailedOverReprotectPending"
        NONE = "None"


    class azure.mgmt.resiliencemanagement.models.FaultDetails(_Model):
        fault_name: str
        fault_urn: str
        target_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                fault_name: str, 
                fault_urn: str, 
                target_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.FaultProperties(_Model):
        available_faults: Optional[list[FaultDetails]]
        custom_fault: Optional[CustomFaultDetails]
        default_fault: Optional[FaultDetails]
        overridden_default_fault: Optional[FaultDetails]

        @overload
        def __init__(
                self, 
                *, 
                custom_fault: Optional[CustomFaultDetails] = ..., 
                overridden_default_fault: Optional[FaultDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ForceInclusionAndUpdate(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"


    class azure.mgmt.resiliencemanagement.models.GoalAssignment(ProxyResource):
        id: str
        name: str
        properties: Optional[GoalAssignmentProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GoalAssignmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.GoalAssignmentProperties(_Model):
        error_details: Optional[ErrorDetail]
        goal_assignment_type: Optional[Union[str, GoalAssignmentType]]
        goal_template_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        require_zonal_resiliency: Optional[bool]
        service_level_resources: Optional[list[ServiceLevelResource]]

        @overload
        def __init__(
                self, 
                *, 
                goal_assignment_type: Optional[Union[str, GoalAssignmentType]] = ..., 
                goal_template_id: Optional[str] = ..., 
                require_zonal_resiliency: Optional[bool] = ..., 
                service_level_resources: Optional[list[ServiceLevelResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.GoalAssignmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESILIENCY = "Resiliency"


    class azure.mgmt.resiliencemanagement.models.GoalResource(ProxyResource):
        id: str
        name: str
        properties: Optional[GoalResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GoalResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.GoalResourceProperties(_Model):
        disaster_recovery_attestation_status: Optional[Union[str, AttestationState]]
        disaster_recovery_goal_participation: Optional[Union[str, ExclusionState]]
        exclusion_reason_for_disaster_recovery_goals: Optional[Union[str, ExclusionReason]]
        exclusion_reason_for_high_availability_goals: Optional[Union[str, ExclusionReason]]
        high_availability_attestation_status: Optional[Union[str, AttestationState]]
        high_availability_goal_participation: Optional[Union[str, ExclusionState]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_arm_id: str
        service_group_memberships: Optional[list[ServiceGroupMembership]]
        user_confirmation_for_high_availability: Optional[list[UserConfirmationItem]]
        zonal_resiliency: Optional[ResiliencyProperties]

        @overload
        def __init__(
                self, 
                *, 
                disaster_recovery_attestation_status: Optional[Union[str, AttestationState]] = ..., 
                disaster_recovery_goal_participation: Optional[Union[str, ExclusionState]] = ..., 
                high_availability_attestation_status: Optional[Union[str, AttestationState]] = ..., 
                high_availability_goal_participation: Optional[Union[str, ExclusionState]] = ..., 
                resource_arm_id: str, 
                user_confirmation_for_high_availability: Optional[list[UserConfirmationItem]] = ..., 
                zonal_resiliency: Optional[ResiliencyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.GoalTemplate(ProxyResource):
        id: str
        name: str
        properties: Optional[GoalTemplateProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GoalTemplateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.GoalTemplateProperties(_Model):
        error_details: Optional[ErrorDetail]
        goal_type: Union[str, GoalType]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        regional_recovery_point_objective: Optional[str]
        regional_recovery_time_objective: Optional[str]
        require_disaster_recovery: Optional[Union[str, RequirementSelected]]
        require_high_availability: Optional[Union[str, RequirementSelected]]

        @overload
        def __init__(
                self, 
                *, 
                goal_type: Union[str, GoalType], 
                regional_recovery_point_objective: Optional[str] = ..., 
                regional_recovery_time_objective: Optional[str] = ..., 
                require_disaster_recovery: Optional[Union[str, RequirementSelected]] = ..., 
                require_high_availability: Optional[Union[str, RequirementSelected]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.GoalType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESILIENCY = "Resiliency"


    class azure.mgmt.resiliencemanagement.models.GoalsData(_Model):
        assignment_id: str
        regional_recovery_point_estimated_in_minutes: Optional[Union[str, IsoDuration]]
        regional_recovery_point_objective_in_minutes: Optional[Union[str, IsoDuration]]
        regional_recovery_point_objective_status: Union[str, ResilienceHealthStatus]
        regional_recovery_time_actual_in_minutes: Optional[Union[str, IsoDuration]]
        regional_recovery_time_objective_in_minutes: Optional[Union[str, IsoDuration]]
        regional_recovery_time_objective_status: Union[str, ResilienceHealthStatus]
        require_disaster_recovery: Optional[Union[str, UnifiedResilienceItemRequirementSelected]]
        require_high_availability: Optional[Union[str, UnifiedResilienceItemRequirementSelected]]
        template_id: str

        @overload
        def __init__(
                self, 
                *, 
                assignment_id: str, 
                regional_recovery_point_estimated_in_minutes: Optional[Union[str, IsoDuration]] = ..., 
                regional_recovery_point_objective_in_minutes: Optional[Union[str, IsoDuration]] = ..., 
                regional_recovery_point_objective_status: Union[str, ResilienceHealthStatus], 
                regional_recovery_time_actual_in_minutes: Optional[Union[str, IsoDuration]] = ..., 
                regional_recovery_time_objective_in_minutes: Optional[Union[str, IsoDuration]] = ..., 
                regional_recovery_time_objective_status: Union[str, ResilienceHealthStatus], 
                require_disaster_recovery: Optional[Union[str, UnifiedResilienceItemRequirementSelected]] = ..., 
                require_high_availability: Optional[Union[str, UnifiedResilienceItemRequirementSelected]] = ..., 
                template_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.HAStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENABLED = "Enabled"
        NOT_ENABLED = "NotEnabled"


    class azure.mgmt.resiliencemanagement.models.HealthModelMonitoringProperties(_Model):
        discovery_rule_id: str
        identity: AssociatedIdentity

        @overload
        def __init__(
                self, 
                *, 
                discovery_rule_id: str, 
                identity: AssociatedIdentity
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.IncludeOrUpdateResource(_Model):
        fault_properties: Optional[FaultProperties]
        id: str

        @overload
        def __init__(
                self, 
                *, 
                fault_properties: Optional[FaultProperties] = ..., 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.InitialConfig(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE = "Complete"
        PENDING = "Pending"


    class azure.mgmt.resiliencemanagement.models.IsoDuration(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PT15_M = "PT15M"
        PT1_H = "PT1H"
        PT24_H = "PT24H"
        PT4_H = "PT4H"


    class azure.mgmt.resiliencemanagement.models.JobErrorInfo(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        recommendations: Optional[list[str]]


    class azure.mgmt.resiliencemanagement.models.JobExtendedInfo(_Model):
        dynamic_error_message: Optional[str]
        tasks_list: Optional[list[JobTaskDetail]]


    class azure.mgmt.resiliencemanagement.models.JobProperties(_Model):
        duration: Optional[timedelta]
        end_time: Optional[datetime]
        error_details: Optional[JobErrorInfo]
        execution_configurations: Optional[ExecutionConfigurations]
        job_extended_info: Optional[JobExtendedInfo]
        job_type: str
        operation: Optional[str]
        resource_id: Optional[str]
        retry_details: Optional[list[JobRetryDetails]]
        start_time: Optional[datetime]
        status: Optional[Union[str, JobStatus]]
        triggered_by: Optional[Union[str, JobTriggeredBy]]
        user_comments: Optional[list[JobUserComment]]

        @overload
        def __init__(
                self, 
                *, 
                error_details: Optional[JobErrorInfo] = ..., 
                job_extended_info: Optional[JobExtendedInfo] = ..., 
                job_type: str = ..., 
                retry_details: Optional[list[JobRetryDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.JobResourceProperties(_Model):
        duration: Optional[timedelta]
        end_time: Optional[datetime]
        error_details: Optional[JobErrorInfo]
        job_extended_info: Optional[JobExtendedInfo]
        job_id: Optional[str]
        job_resource_type: str
        operation: Optional[str]
        resource_id: Optional[str]
        retry_details: Optional[list[JobRetryDetails]]
        start_time: Optional[datetime]
        status: Optional[Union[str, JobStatus]]
        task_id: Optional[str]
        task_name: Optional[str]
        user_comments: Optional[list[JobUserComment]]

        @overload
        def __init__(
                self, 
                *, 
                error_details: Optional[JobErrorInfo] = ..., 
                job_extended_info: Optional[JobExtendedInfo] = ..., 
                job_resource_type: str, 
                retry_details: Optional[list[JobRetryDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.JobResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DRILL_RUN = "DrillRun"
        INVALID = "Invalid"
        RECOVERY_PLAN = "RecoveryPlan"


    class azure.mgmt.resiliencemanagement.models.JobRetryDetails(_Model):
        duration: Optional[timedelta]
        end_time: Optional[datetime]
        error_details: Optional[JobErrorInfo]
        retry_attempt: int
        start_time: Optional[datetime]
        status: Optional[Union[str, JobStatus]]
        user_comments: Optional[list[JobUserComment]]

        @overload
        def __init__(
                self, 
                *, 
                error_details: Optional[JobErrorInfo] = ..., 
                retry_attempt: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.JobStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        CANCELLING = "Cancelling"
        COMPLETED = "Completed"
        COMPLETED_WITH_WARNINGS = "CompletedWithWarnings"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NOT_APPLICABLE = "NotApplicable"
        NOT_STARTED = "NotStarted"
        PAUSED = "Paused"
        PENDING = "Pending"
        SKIPPED = "Skipped"


    class azure.mgmt.resiliencemanagement.models.JobTaskDetail(_Model):
        duration: Optional[timedelta]
        end_time: Optional[datetime]
        error_details: Optional[JobErrorInfo]
        linked_job_ids: Optional[list[str]]
        retry_details: Optional[list[JobRetryDetails]]
        start_time: Optional[datetime]
        status: Optional[Union[str, JobStatus]]
        sub_tasks_list: Optional[list[JobTaskDetail]]
        task_id: Optional[str]
        task_name: Optional[str]
        user_comments: Optional[list[JobUserComment]]

        @overload
        def __init__(
                self, 
                *, 
                error_details: Optional[JobErrorInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.JobTriggeredBy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "System"
        USER = "User"


    class azure.mgmt.resiliencemanagement.models.JobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DRILL_RUN = "DrillRun"
        INVALID = "Invalid"
        RECOVERY_PLAN = "RecoveryPlan"


    class azure.mgmt.resiliencemanagement.models.JobUserComment(_Model):
        comment_time: Optional[datetime]
        comment_type: Optional[Union[str, CommentType]]
        comments: Optional[str]


    class azure.mgmt.resiliencemanagement.models.LastRunProperties(_Model):
        last_run_attestation: Optional[Union[str, DrillAttestation]]
        last_run_duration: Optional[timedelta]
        last_run_state: Optional[Union[str, JobStatus]]
        last_run_time: Optional[datetime]


    class azure.mgmt.resiliencemanagement.models.ListReportDownloadUrlRequest(_Model):
        format: Optional[Union[str, DrillReportFormat]]

        @overload
        def __init__(
                self, 
                *, 
                format: Optional[Union[str, DrillReportFormat]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ListReportDownloadUrlResponse(_Model):
        download_url: Optional[str]
        expiry_timestamp: Optional[datetime]
        format: Optional[Union[str, DrillReportFormat]]


    class azure.mgmt.resiliencemanagement.models.ManagedServiceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.resiliencemanagement.models.MarkAsCompleteRequest(_Model):
        drill_run_stage: Union[str, DrillRunSubtasks]

        @overload
        def __init__(
                self, 
                *, 
                drill_run_stage: Union[str, DrillRunSubtasks]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.MembershipType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIRECT = "Direct"
        THROUGH_RESOURCE_GROUP = "ThroughResourceGroup"
        THROUGH_SUBSCRIPTION = "ThroughSubscription"


    class azure.mgmt.resiliencemanagement.models.MonitoringPropertiesOfDrill(_Model):
        data_collection_endpoint_id: Optional[str]
        identity: Optional[AssociatedIdentity]
        log_analytics_workspace_id: Optional[str]
        raw_metrics_data_collection_rule_id: Optional[str]
        service_group_metrics_data_collection_rule_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[AssociatedIdentity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.Operation(_Model):
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


    class azure.mgmt.resiliencemanagement.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.resiliencemanagement.models.OperationQualificationDetails(_Model):
        not_qualified_reasons: Optional[list[str]]
        qualification_state: Union[str, QualificationState]
        resource_feasibility_reviews: Optional[list[ResourceFeasibilityReview]]

        @overload
        def __init__(
                self, 
                *, 
                not_qualified_reasons: Optional[list[str]] = ..., 
                qualification_state: Union[str, QualificationState], 
                resource_feasibility_reviews: Optional[list[ResourceFeasibilityReview]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.OperationStatusResult(_Model):
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


    class azure.mgmt.resiliencemanagement.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.resiliencemanagement.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        NEEDS_ATTENTION = "NeedsAttention"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.resiliencemanagement.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.resiliencemanagement.models.QualificationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCLUDED = "Excluded"
        NOT_QUALIFIED = "NotQualified"
        QUALIFIED = "Qualified"
        UNKNOWN = "Unknown"


    class azure.mgmt.resiliencemanagement.models.RBACSetupMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATED_BUILTIN_ROLES = "AutomatedBuiltinRoles"
        AUTOMATED_CUSTOM_ROLE = "AutomatedCustomRole"
        MANUAL = "Manual"


    class azure.mgmt.resiliencemanagement.models.RBACState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_SET = "NotSet"
        SET = "Set"


    class azure.mgmt.resiliencemanagement.models.ReasonForRequestingConfirmation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VM_IN_MULTI_ZONE_SCALE_SET_STATELESS_ONLY = "VmInMultiZoneScaleSetStatelessOnly"
        ZONE_PINNED_ZRS_DATA_DISKS_CONDITIONAL = "ZonePinnedZrsDataDisksConditional"


    class azure.mgmt.resiliencemanagement.models.RecommendCapacityRequest(_Model):
        resource_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.RecommendationsData(_Model):
        high_availability: RecommendationsHighAvailabilityData

        @overload
        def __init__(
                self, 
                *, 
                high_availability: RecommendationsHighAvailabilityData
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.RecommendationsHighAvailabilityData(_Model):
        enabled_resource_count: Optional[int]
        evaluation_date_time: Optional[datetime]
        not_enabled_resource_count: Optional[int]
        not_evaluated_resource_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                enabled_resource_count: Optional[int] = ..., 
                evaluation_date_time: Optional[datetime] = ..., 
                not_enabled_resource_count: Optional[int] = ..., 
                not_evaluated_resource_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.RecoveryActionRequest(_Model):
        description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.RecoveryGroup(ProxyResource):
        id: str
        name: str
        properties: Optional[RecoveryGroupProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RecoveryGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.RecoveryGroupActionSettings(_Model):
        action_description: Optional[str]
        action_name: Optional[str]
        action_sequence: Optional[int]
        action_task: Optional[Union[str, ActionTask]]
        recovery_group_action_type: Optional[Union[str, RecoveryGroupActionType]]


    class azure.mgmt.resiliencemanagement.models.RecoveryGroupActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_RUNBOOK = "CustomRunbook"
        MANUAL_ACTION = "ManualAction"


    class azure.mgmt.resiliencemanagement.models.RecoveryGroupBaseAction(_Model):
        description: Optional[str]
        name: str
        timeout_in_minutes: int
        type: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str, 
                timeout_in_minutes: int, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.RecoveryGroupCustomRunbookAction(RecoveryGroupBaseAction, discriminator='CustomRunbook'):
        action_resource_id: Optional[str]
        associated_identity: Optional[AssociatedIdentity]
        description: str
        name: str
        parameters: Optional[dict[str, str]]
        timeout_in_minutes: int
        type: Literal[RecoveryGroupActionType.CUSTOM_RUNBOOK]

        @overload
        def __init__(
                self, 
                *, 
                action_resource_id: Optional[str] = ..., 
                associated_identity: Optional[AssociatedIdentity] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                parameters: Optional[dict[str, str]] = ..., 
                timeout_in_minutes: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.RecoveryGroupManualAction(RecoveryGroupBaseAction, discriminator='ManualAction'):
        description: str
        name: str
        timeout_in_minutes: int
        type: Literal[RecoveryGroupActionType.MANUAL_ACTION]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str, 
                timeout_in_minutes: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.RecoveryGroupProperties(_Model):
        description: str
        group_unique_id: str
        order_id: int
        post_actions: Optional[list[RecoveryGroupBaseAction]]
        pre_actions: Optional[list[RecoveryGroupBaseAction]]

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                group_unique_id: str, 
                order_id: int, 
                post_actions: Optional[list[RecoveryGroupBaseAction]] = ..., 
                pre_actions: Optional[list[RecoveryGroupBaseAction]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.RecoveryGroupsSetting(_Model):
        additional_groups: Optional[list[RecoveryGroup]]
        default_group: RecoveryGroup

        @overload
        def __init__(
                self, 
                *, 
                additional_groups: Optional[list[RecoveryGroup]] = ..., 
                default_group: RecoveryGroup
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.RecoveryJob(ProxyResource):
        id: str
        name: str
        properties: Optional[RecoveryJobProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RecoveryJobProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.RecoveryJobProperties(JobProperties, discriminator='RecoveryPlan'):
        duration: timedelta
        end_time: datetime
        error_details: JobErrorInfo
        execution_configurations: ExecutionConfigurations
        job_extended_info: JobExtendedInfo
        job_type: Literal[JobType.RECOVERY_PLAN]
        operation: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_id: str
        retry_details: list[JobRetryDetails]
        start_time: datetime
        status: Union[str, JobStatus]
        triggered_by: Union[str, JobTriggeredBy]
        user_comments: list[JobUserComment]

        @overload
        def __init__(
                self, 
                *, 
                error_details: Optional[JobErrorInfo] = ..., 
                job_extended_info: Optional[JobExtendedInfo] = ..., 
                retry_details: Optional[list[JobRetryDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.RecoveryJobResource(ProxyResource):
        id: str
        name: str
        properties: Optional[RecoveryJobResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RecoveryJobResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.RecoveryJobResourceProperties(JobResourceProperties, discriminator='RecoveryPlan'):
        duration: timedelta
        end_time: datetime
        error_details: JobErrorInfo
        job_extended_info: JobExtendedInfo
        job_id: str
        job_resource_type: Literal[JobResourceType.RECOVERY_PLAN]
        operation: str
        protection_solution_type: Optional[Union[str, ResourceProtectionSolutionType]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        recovery_group_action_settings: Optional[RecoveryGroupActionSettings]
        resource_id: str
        retry_details: list[JobRetryDetails]
        start_time: datetime
        status: Union[str, JobStatus]
        task_id: str
        task_name: str
        user_comments: list[JobUserComment]

        @overload
        def __init__(
                self, 
                *, 
                error_details: Optional[JobErrorInfo] = ..., 
                job_extended_info: Optional[JobExtendedInfo] = ..., 
                retry_details: Optional[list[JobRetryDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.RecoveryOperationNames(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILOVER = "Failover"
        FAILOVER_COMMIT = "FailoverCommit"
        REPROTECT = "Reprotect"
        TEST_FAILOVER = "TestFailover"
        TEST_FAILOVER_CLEANUP = "TestFailoverCleanup"


    class azure.mgmt.resiliencemanagement.models.RecoveryOperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        COMPLETED_WITH_WARNING = "CompletedWithWarning"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NOT_STARTED = "NotStarted"
        SUCCEEDED = "Succeeded"
        VALIDATION_FAILED = "ValidationFailed"
        VALIDATION_IN_PROGRESS = "ValidationInProgress"


    class azure.mgmt.resiliencemanagement.models.RecoveryPlan(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        name: str
        properties: Optional[RecoveryPlanProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[RecoveryPlanProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.RecoveryPlanActionBaseResponse(_Model):
        job_id: str

        @overload
        def __init__(
                self, 
                *, 
                job_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.RecoveryPlanExclusionReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCLUDED_FROM_RECOVERY_PLAN = "ExcludedFromRecoveryPlan"
        PROTECTION_STATUS = "ProtectionStatus"


    class azure.mgmt.resiliencemanagement.models.RecoveryPlanFailoverOperationStatus(_Model):
        error_details: Optional[ErrorDetail]
        last_executed_at: Optional[datetime]
        operation_status: Optional[Union[str, RecoveryOperationStatus]]
        recovery_time_actual: Optional[timedelta]


    class azure.mgmt.resiliencemanagement.models.RecoveryPlanOperationStatus(_Model):
        error_details: Optional[ErrorDetail]
        last_executed_at: Optional[datetime]
        operation_status: Optional[Union[str, RecoveryOperationStatus]]


    class azure.mgmt.resiliencemanagement.models.RecoveryPlanProperties(_Model):
        error_details: Optional[ErrorDetail]
        latest_failover_status: Optional[RecoveryPlanFailoverOperationStatus]
        latest_validation_status: Optional[RecoveryPlanOperationStatus]
        plan_description: str
        plan_state: Optional[Union[str, RecoveryPlanState]]
        plan_type: Union[str, RecoveryPlanType]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        recovery_groups_setting: RecoveryGroupsSetting

        @overload
        def __init__(
                self, 
                *, 
                plan_description: str, 
                plan_type: Union[str, RecoveryPlanType], 
                recovery_groups_setting: RecoveryGroupsSetting
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.RecoveryPlanPropertiesOfDrill(_Model):
        identity: AssociatedIdentity
        recovery_plan_id: Optional[str]
        recovery_plan_resource_excluded_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                identity: AssociatedIdentity
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.RecoveryPlanState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        READY = "Ready"
        UNDER_EDIT = "UnderEdit"
        WARNING = "Warning"


    class azure.mgmt.resiliencemanagement.models.RecoveryPlanType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REGIONAL = "Regional"
        ZONAL = "Zonal"


    class azure.mgmt.resiliencemanagement.models.RecoveryResource(ProxyResource):
        id: str
        name: str
        properties: Optional[RecoveryResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RecoveryResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.RecoveryResourceProperties(_Model):
        associated_identity: Optional[AssociatedIdentity]
        attention_reasons: Optional[list[str]]
        error_details: Optional[ErrorDetail]
        inclusion_state: Optional[Union[str, ResourceInclusionState]]
        needs_attention: Optional[bool]
        protection_status: Optional[Union[str, ResourceProtectionStatus]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        recovery_group_id: Optional[str]
        recovery_resource_unique_id: str
        resource_id: Optional[str]
        resource_location: Optional[str]
        resource_physical_zones: Optional[list[str]]
        resource_protection_solutions: Optional[list[ResourceProtectionSolutionSettings]]
        selected_protection_solution_setting: Optional[ResourceBaseProtectionSolutionSetting]
        selected_protection_solution_type: Optional[Union[str, ResourceProtectionSolutionType]]

        @overload
        def __init__(
                self, 
                *, 
                associated_identity: Optional[AssociatedIdentity] = ..., 
                inclusion_state: Optional[Union[str, ResourceInclusionState]] = ..., 
                recovery_group_id: Optional[str] = ..., 
                recovery_resource_unique_id: str, 
                selected_protection_solution_setting: Optional[ResourceBaseProtectionSolutionSetting] = ..., 
                selected_protection_solution_type: Optional[Union[str, ResourceProtectionSolutionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.RecoveryResourceQualification(_Model):
        operation_qualification_details: OperationQualificationDetails
        recovery_resource: RecoveryResource

        @overload
        def __init__(
                self, 
                *, 
                operation_qualification_details: OperationQualificationDetails, 
                recovery_resource: RecoveryResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.RegionalDrillProperties(DrillProperties, discriminator='Regional'):
        attention_reason: AttentionReason
        chaos_resource_properties: ChaosResourcePropertiesOfDrill
        drill_asset_properties: AssetPropertiesOfDrill
        drill_type: Literal[DrillType.REGIONAL]
        error_details: ErrorDetail
        execution_readiness_state: Union[str, ExecutionReadinessState]
        execution_state: Union[str, ExecutionState]
        health_model_monitoring_properties: HealthModelMonitoringProperties
        last_resync_readiness_check_time: datetime
        last_run_properties: LastRunProperties
        last_sync_time: datetime
        monitoring_properties: MonitoringPropertiesOfDrill
        provisioning_state: Union[str, ProvisioningState]
        rbac_setup_mode: Union[str, RBACSetupMode]
        recovery_plan_properties: RecoveryPlanPropertiesOfDrill
        service_group_id: str
        sli_monitoring_properties: SliMonitoringProperties
        system_metadata: SystemMetadata

        @overload
        def __init__(
                self, 
                *, 
                chaos_resource_properties: Optional[ChaosResourcePropertiesOfDrill] = ..., 
                drill_asset_properties: Optional[AssetPropertiesOfDrill] = ..., 
                health_model_monitoring_properties: Optional[HealthModelMonitoringProperties] = ..., 
                monitoring_properties: Optional[MonitoringPropertiesOfDrill] = ..., 
                rbac_setup_mode: Optional[Union[str, RBACSetupMode]] = ..., 
                recovery_plan_properties: Optional[RecoveryPlanPropertiesOfDrill] = ..., 
                sli_monitoring_properties: Optional[SliMonitoringProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.RelativeResourceCompositionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IN_SYNC = "InSync"
        OUT_OF_SYNC = "OutOfSync"


    class azure.mgmt.resiliencemanagement.models.ReportStageStatus(_Model):
        drill_run_stage: Union[str, DrillRunSubtasks]
        generation_status: Optional[Union[str, DrillReportGenerationStatus]]
        last_attempt_timestamp: Optional[datetime]
        last_error: Optional[ErrorDetails]

        @overload
        def __init__(
                self, 
                *, 
                drill_run_stage: Union[str, DrillRunSubtasks]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ReprotectRequest(_Model):
        reprotect_request_properties: Optional[ReprotectRequestProperties]

        @overload
        def __init__(
                self, 
                *, 
                reprotect_request_properties: Optional[ReprotectRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ReprotectRequestProperties(_Model):
        selected_resource_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                selected_resource_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.RequirementSelected(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_REQUIRED = "NotRequired"
        REQUIRED = "Required"


    class azure.mgmt.resiliencemanagement.models.ResilienceHealthStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        NOT_EVALUATED = "NotEvaluated"
        UNHEALTHY = "Unhealthy"


    class azure.mgmt.resiliencemanagement.models.ResiliencyProperties(_Model):
        attestation_status: Optional[Union[str, AttestationState]]
        exclusion_reason: Optional[Union[str, ExclusionReason]]
        goal_participation: Optional[Union[str, ExclusionState]]
        user_confirmation: Optional[list[UserConfirmationItem]]

        @overload
        def __init__(
                self, 
                *, 
                attestation_status: Optional[Union[str, AttestationState]] = ..., 
                goal_participation: Optional[Union[str, ExclusionState]] = ..., 
                user_confirmation: Optional[list[UserConfirmationItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.resiliencemanagement.models.ResourceBaseProtectionSolutionSetting(_Model):
        protection_solution_type: str

        @overload
        def __init__(
                self, 
                *, 
                protection_solution_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ResourceCrossZoneVmRecoveryProtectionSetting(ResourceBaseProtectionSolutionSetting, discriminator='CrossZoneVMRecovery'):
        capacity_reservation_group_id: Optional[str]
        protection_solution_type: Literal[ResourceProtectionSolutionType.CROSS_ZONE_VM_RECOVERY]
        target_zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                capacity_reservation_group_id: Optional[str] = ..., 
                target_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ResourceCustomProtectionAction(_Model):
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ResourceCustomProtectionSetting(ResourceBaseProtectionSolutionSetting, discriminator='CustomRunbook'):
        failover_action: Optional[ResourceCustomProtectionAction]
        failover_commit_action: Optional[ResourceCustomProtectionAction]
        protection_solution_type: Literal[ResourceProtectionSolutionType.CUSTOM_RUNBOOK]
        reprotect_action: Optional[ResourceCustomProtectionAction]
        test_failover_action: Optional[ResourceCustomProtectionAction]
        test_failover_cleanup_action: Optional[ResourceCustomProtectionAction]

        @overload
        def __init__(
                self, 
                *, 
                failover_action: Optional[ResourceCustomProtectionAction] = ..., 
                failover_commit_action: Optional[ResourceCustomProtectionAction] = ..., 
                reprotect_action: Optional[ResourceCustomProtectionAction] = ..., 
                test_failover_action: Optional[ResourceCustomProtectionAction] = ..., 
                test_failover_cleanup_action: Optional[ResourceCustomProtectionAction] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ResourceFeasibilityReview(_Model):
        current_target_sku: Optional[SkuDetails]
        feasibility_type: Union[str, ResourceFeasibilityReviewType]
        recommended_target_skus: Optional[list[SkuDetails]]
        resource_type: str
        status: Union[str, ResourceFeasibilityReviewStatus]

        @overload
        def __init__(
                self, 
                *, 
                current_target_sku: Optional[SkuDetails] = ..., 
                feasibility_type: Union[str, ResourceFeasibilityReviewType], 
                recommended_target_skus: Optional[list[SkuDetails]] = ..., 
                resource_type: str, 
                status: Union[str, ResourceFeasibilityReviewStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ResourceFeasibilityReviewStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FLAGGED = "Flagged"
        NOT_APPLICABLE = "NotApplicable"
        PASSED = "Passed"
        UNAVAILABLE = "Unavailable"


    class azure.mgmt.resiliencemanagement.models.ResourceFeasibilityReviewType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SKU_CAPACITY = "SkuCapacity"


    class azure.mgmt.resiliencemanagement.models.ResourceInclusionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCLUDED = "Excluded"
        INCLUDED = "Included"


    class azure.mgmt.resiliencemanagement.models.ResourceLists(_Model):
        exclude_resources: Optional[list[str]]
        include_resources: Optional[list[IncludeOrUpdateResource]]
        update_resources: Optional[list[IncludeOrUpdateResource]]

        @overload
        def __init__(
                self, 
                *, 
                exclude_resources: Optional[list[str]] = ..., 
                include_resources: Optional[list[IncludeOrUpdateResource]] = ..., 
                update_resources: Optional[list[IncludeOrUpdateResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ResourceNativeProtectionSolutionSetting(ResourceBaseProtectionSolutionSetting, discriminator='AzureNative'):
        protection_solution_type: Literal[ResourceProtectionSolutionType.AZURE_NATIVE]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ResourceProtectionSolutionSettings(_Model):
        active_location: Optional[str]
        active_locations: Optional[list[str]]
        active_physical_zones: Optional[list[str]]
        failover_state: Optional[Union[str, FailoverState]]
        is_auto_failover: bool
        primary_resource: Optional[str]
        protection_solution_type: Optional[Union[str, ResourceProtectionSolutionType]]
        protection_status: Optional[Union[str, ResourceProtectionStatus]]
        recovery_locations: Optional[list[str]]
        replica_resources: Optional[list[str]]
        replication_role: Optional[Union[str, ResourceReplicationRole]]
        resource_id: Optional[str]
        test_failover_state: Optional[Union[str, TestFailoverState]]


    class azure.mgmt.resiliencemanagement.models.ResourceProtectionSolutionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_NATIVE = "AzureNative"
        AZURE_SITE_RECOVERY = "AzureSiteRecovery"
        CROSS_ZONE_VM_RECOVERY = "CrossZoneVMRecovery"
        CUSTOM_RUNBOOK = "CustomRunbook"
        NONE = "None"


    class azure.mgmt.resiliencemanagement.models.ResourceProtectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGHLY_AVAILABLE = "HighlyAvailable"
        NOT_PROTECTED = "NotProtected"
        PROTECTED = "Protected"
        UNKNOWN = "Unknown"


    class azure.mgmt.resiliencemanagement.models.ResourceReplicationRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        REPLICA = "Replica"
        UNKNOWN = "Unknown"


    class azure.mgmt.resiliencemanagement.models.ResourceSiteRecoveryProtectionSetting(ResourceBaseProtectionSolutionSetting, discriminator='AzureSiteRecovery'):
        protection_solution_type: Literal[ResourceProtectionSolutionType.AZURE_SITE_RECOVERY]
        reprotect_params: Optional[ResourceSiteRecoveryReprotectParams]
        test_failover_cleanup_params: Optional[ResourceSiteRecoveryTestFailoverCleanupParams]
        test_failover_params: Optional[ResourceSiteRecoveryTestFailoverParams]

        @overload
        def __init__(
                self, 
                *, 
                reprotect_params: Optional[ResourceSiteRecoveryReprotectParams] = ..., 
                test_failover_cleanup_params: Optional[ResourceSiteRecoveryTestFailoverCleanupParams] = ..., 
                test_failover_params: Optional[ResourceSiteRecoveryTestFailoverParams] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ResourceSiteRecoveryReprotectParams(_Model):
        disk_reprotect_input_details: Optional[list[DiskReprotectInputDetails]]

        @overload
        def __init__(
                self, 
                *, 
                disk_reprotect_input_details: Optional[list[DiskReprotectInputDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ResourceSiteRecoveryTestFailoverCleanupParams(_Model):
        comments: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                comments: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ResourceSiteRecoveryTestFailoverParams(_Model):
        network_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                network_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ResourceTypeCategories(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SITE_RECOVERY_VMS_PRESENT = "AzureSiteRecoveryVMsPresent"


    class azure.mgmt.resiliencemanagement.models.ServiceGroupMembership(_Model):
        membership_type: Union[str, MembershipType]
        service_group_id: str

        @overload
        def __init__(
                self, 
                *, 
                membership_type: Union[str, MembershipType], 
                service_group_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ServiceLevelResource(_Model):
        service_level_indicator_resource_id: str
        service_level_objective_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                service_level_indicator_resource_id: str, 
                service_level_objective_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.SkuDetails(_Model):
        currency: Optional[str]
        monthly_price: Optional[float]
        offering_id: Optional[str]
        ram: Optional[int]
        sku: str
        v_cpu: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                currency: Optional[str] = ..., 
                monthly_price: Optional[float] = ..., 
                offering_id: Optional[str] = ..., 
                ram: Optional[int] = ..., 
                sku: str, 
                v_cpu: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.SliAttentionStatus(_Model):
        drill_rbac_on_destination_amw: Optional[Union[str, RBACState]]
        exists: Optional[Union[str, ExtensionObjectState]]
        rbac_needed_on_destination_amws: Optional[list[str]]
        sli_id: str
        type: Union[str, SliType]
        type_match: Optional[Union[str, SliTypeMatchState]]

        @overload
        def __init__(
                self, 
                *, 
                sli_id: str, 
                type: Union[str, SliType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.SliMonitoringProperties(_Model):
        identity: AssociatedIdentity
        slis: list[SliSelection]

        @overload
        def __init__(
                self, 
                *, 
                identity: AssociatedIdentity, 
                slis: list[SliSelection]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.SliSelection(_Model):
        sli_id: str
        type: Union[str, SliType]

        @overload
        def __init__(
                self, 
                *, 
                sli_id: str, 
                type: Union[str, SliType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.SliType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABILITY = "Availability"
        LATENCY = "Latency"


    class azure.mgmt.resiliencemanagement.models.SliTypeMatchState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MATCHED = "Matched"
        MISMATCHED = "Mismatched"


    class azure.mgmt.resiliencemanagement.models.SolutionDisplayName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VM_IN_MULTI_ZONE_VMSS = "VmInMultiZoneVmss"
        ZONE_PINNED_VM_WITH_ZRS_DISK = "ZonePinnedVmWithZrsDisk"


    class azure.mgmt.resiliencemanagement.models.SupportedVerbsForStage(_Model):
        drill_run_stage: Union[str, DrillRunSubtasks]
        supported_verbs: list[Union[str, DrillRunOperationVerbs]]

        @overload
        def __init__(
                self, 
                *, 
                drill_run_stage: Union[str, DrillRunSubtasks], 
                supported_verbs: list[Union[str, DrillRunOperationVerbs]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.SystemData(_Model):
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


    class azure.mgmt.resiliencemanagement.models.SystemMetadata(_Model):
        initial_config: Union[str, InitialConfig]
        resource_type_categories: Optional[list[Union[str, ResourceTypeCategories]]]

        @overload
        def __init__(
                self, 
                *, 
                initial_config: Union[str, InitialConfig]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.TestFailoverCleanupRequest(_Model):
        comments: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                comments: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.TestFailoverState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        TEST_FAILOVER_CLEANUP_PENDING = "TestFailoverCleanupPending"


    class azure.mgmt.resiliencemanagement.models.TrackedResource(Resource):
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


    class azure.mgmt.resiliencemanagement.models.UnifiedResilienceItem(ProxyResource):
        id: str
        name: str
        properties: Optional[UnifiedResilienceItemProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[UnifiedResilienceItemProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.UnifiedResilienceItemProperties(_Model):
        goals: GoalsData
        last_modified_time: datetime
        provisioning_state: Optional[Union[str, ProvisioningState]]
        recommendations: RecommendationsData

        @overload
        def __init__(
                self, 
                *, 
                goals: GoalsData, 
                last_modified_time: datetime, 
                recommendations: RecommendationsData
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.UnifiedResilienceItemRequirementSelected(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_REQUIRED = "NotRequired"
        NOT_SELECTED = "NotSelected"
        REQUIRED = "Required"


    class azure.mgmt.resiliencemanagement.models.UpdateGoalResourceRequest(_Model):
        resources: list[GoalResource]

        @overload
        def __init__(
                self, 
                *, 
                resources: list[GoalResource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.UpdateRecoveryResourcesRequest(_Model):
        resources_to_remove: Optional[list[str]]
        resources_to_update: Optional[list[RecoveryResource]]

        @overload
        def __init__(
                self, 
                *, 
                resources_to_remove: Optional[list[str]] = ..., 
                resources_to_update: Optional[list[RecoveryResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.UpdateRecoveryResourcesResponse(_Model):
        failed_resources: Optional[list[RecoveryResource]]

        @overload
        def __init__(
                self, 
                *, 
                failed_resources: Optional[list[RecoveryResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.UsagePlan(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[UsagePlanProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[UsagePlanProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.UsagePlanProperties(_Model):
        error_details: Optional[ErrorDetail]
        plan_type: Optional[Union[str, UsagePlanType]]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                plan_type: Optional[Union[str, UsagePlanType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.UsagePlanTagsUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.UsagePlanType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        STANDARD = "Standard"


    class azure.mgmt.resiliencemanagement.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.resiliencemanagement.models.UserConfirmationItem(_Model):
        confirmation_status: Union[str, ConfirmationStatus]
        reason_for_requesting_confirmation: Optional[Union[str, ReasonForRequestingConfirmation]]
        solution_display_name: Union[str, SolutionDisplayName]

        @overload
        def __init__(
                self, 
                *, 
                confirmation_status: Union[str, ConfirmationStatus], 
                reason_for_requesting_confirmation: Optional[Union[str, ReasonForRequestingConfirmation]] = ..., 
                solution_display_name: Union[str, SolutionDisplayName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.UserConsent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED = "Allowed"
        UNSPECIFIED = "Unspecified"


    class azure.mgmt.resiliencemanagement.models.VMPresent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ABSENT = "Absent"
        PRESENT = "Present"


    class azure.mgmt.resiliencemanagement.models.ValidateForExecutionProperties(_Model):
        operation_name: Optional[Union[str, DrillRunTasks]]
        source_locations: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                operation_name: Optional[Union[str, DrillRunTasks]] = ..., 
                source_locations: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ValidateForExecutionRequest(_Model):
        validate_for_execution_properties: Optional[ValidateForExecutionProperties]

        @overload
        def __init__(
                self, 
                *, 
                validate_for_execution_properties: Optional[ValidateForExecutionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ValidateForOperationRequest(_Model):
        operation_name: Union[str, RecoveryOperationNames]

        @overload
        def __init__(
                self, 
                *, 
                operation_name: Union[str, RecoveryOperationNames]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ValidateForRecoveryOperationBaseResponse(_Model):
        recovery_resource_qualifications: list[RecoveryResourceQualification]

        @overload
        def __init__(
                self, 
                *, 
                recovery_resource_qualifications: list[RecoveryResourceQualification]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resiliencemanagement.models.ZonalDrillProperties(DrillProperties, discriminator='Zonal'):
        attention_reason: AttentionReason
        chaos_resource_properties: ChaosResourcePropertiesOfDrill
        drill_asset_properties: AssetPropertiesOfDrill
        drill_type: Literal[DrillType.ZONAL]
        error_details: ErrorDetail
        execution_readiness_state: Union[str, ExecutionReadinessState]
        execution_state: Union[str, ExecutionState]
        health_model_monitoring_properties: HealthModelMonitoringProperties
        last_resync_readiness_check_time: datetime
        last_run_properties: LastRunProperties
        last_sync_time: datetime
        monitoring_properties: MonitoringPropertiesOfDrill
        provisioning_state: Union[str, ProvisioningState]
        rbac_setup_mode: Union[str, RBACSetupMode]
        recovery_plan_properties: RecoveryPlanPropertiesOfDrill
        service_group_id: str
        sli_monitoring_properties: SliMonitoringProperties
        system_metadata: SystemMetadata
        vms_present: Optional[Union[str, VMPresent]]

        @overload
        def __init__(
                self, 
                *, 
                chaos_resource_properties: Optional[ChaosResourcePropertiesOfDrill] = ..., 
                drill_asset_properties: Optional[AssetPropertiesOfDrill] = ..., 
                health_model_monitoring_properties: Optional[HealthModelMonitoringProperties] = ..., 
                monitoring_properties: Optional[MonitoringPropertiesOfDrill] = ..., 
                rbac_setup_mode: Optional[Union[str, RBACSetupMode]] = ..., 
                recovery_plan_properties: Optional[RecoveryPlanPropertiesOfDrill] = ..., 
                sli_monitoring_properties: Optional[SliMonitoringProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.resiliencemanagement.operations

    class azure.mgmt.resiliencemanagement.operations.DrillResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_resource_name: str, 
                **kwargs: Any
            ) -> DrillResource: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                drill_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DrillResource]: ...


    class azure.mgmt.resiliencemanagement.operations.DrillRunResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                drill_run_resource_name: str, 
                **kwargs: Any
            ) -> DrillRunResource: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DrillRunResource]: ...


    class azure.mgmt.resiliencemanagement.operations.DrillRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_add_notes(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: DrillRunAddNotesRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_add_notes(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: DrillRunAddNotesRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_add_notes(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_fail_over(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: Optional[DrillRunFailoverRequest] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_fail_over(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: Optional[DrillRunFailoverRequest] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_fail_over(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-31-preview', params_added_on={'2026-08-31-preview': ['service_group_name', 'api_version', 'operation_id', 'drill_name', 'drill_run_name', 'accept']}, api_versions_list=['2026-08-31-preview'])
        def begin_generate_report(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                *, 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_mark_as_complete(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: MarkAsCompleteRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_mark_as_complete(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: MarkAsCompleteRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_mark_as_complete(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reprotect(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: Optional[DrillRunReprotectRequest] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reprotect(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: Optional[DrillRunReprotectRequest] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reprotect(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_resume(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                *, 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                **kwargs: Any
            ) -> DrillRun: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                drill_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DrillRun]: ...

        @overload
        def list_report_download_url(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: Optional[ListReportDownloadUrlRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListReportDownloadUrlResponse: ...

        @overload
        def list_report_download_url(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: Optional[ListReportDownloadUrlRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListReportDownloadUrlResponse: ...

        @overload
        def list_report_download_url(
                self, 
                service_group_name: str, 
                drill_name: str, 
                drill_run_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListReportDownloadUrlResponse: ...


    class azure.mgmt.resiliencemanagement.operations.DrillsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_add_or_update_resources(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: AddOrUpdateResourcesRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_add_or_update_resources(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: AddOrUpdateResourcesRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_add_or_update_resources(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create(
                self, 
                service_group_name: str, 
                drill_name: str, 
                resource: Drill, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Drill]: ...

        @overload
        def begin_create(
                self, 
                service_group_name: str, 
                drill_name: str, 
                resource: Drill, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Drill]: ...

        @overload
        def begin_create(
                self, 
                service_group_name: str, 
                drill_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Drill]: ...

        @distributed_trace
        def begin_delete(
                self, 
                service_group_name: str, 
                drill_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_end(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: DrillEndRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_end(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: DrillEndRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_end(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['service_group_name', 'api_version', 'operation_id', 'drill_name']}, api_versions_list=['2026-03-01-preview', '2026-04-01-preview', '2026-06-01-preview', '2026-08-31-preview'])
        def begin_resync_readiness_check(
                self, 
                service_group_name: str, 
                drill_name: str, 
                *, 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_start(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: DrillStartRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_start(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: DrillStartRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_start(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                service_group_name: str, 
                drill_name: str, 
                properties: DrillUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                service_group_name: str, 
                drill_name: str, 
                properties: DrillUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                service_group_name: str, 
                drill_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_validate_for_execution(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: ValidateForExecutionRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_validate_for_execution(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: ValidateForExecutionRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_validate_for_execution(
                self, 
                service_group_name: str, 
                drill_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                service_group_name: str, 
                drill_name: str, 
                **kwargs: Any
            ) -> Drill: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Drill]: ...


    class azure.mgmt.resiliencemanagement.operations.EnrollmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                enrollment_name: str, 
                resource: Enrollment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Enrollment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                enrollment_name: str, 
                resource: Enrollment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Enrollment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                enrollment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Enrollment]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'usage_plan_name', 'enrollment_name']}, api_versions_list=['2026-03-01-preview', '2026-04-01-preview', '2026-06-01-preview', '2026-08-31-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                enrollment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'usage_plan_name', 'enrollment_name', 'accept']}, api_versions_list=['2026-03-01-preview', '2026-04-01-preview', '2026-06-01-preview', '2026-08-31-preview'])
        def get(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                enrollment_name: str, 
                **kwargs: Any
            ) -> Enrollment: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'usage_plan_name', 'accept']}, api_versions_list=['2026-03-01-preview', '2026-04-01-preview', '2026-06-01-preview', '2026-08-31-preview'])
        def list(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Enrollment]: ...


    class azure.mgmt.resiliencemanagement.operations.GoalAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                resource: GoalAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                resource: GoalAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_recommend_capacity(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                body: RecommendCapacityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_recommend_capacity(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                body: RecommendCapacityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_recommend_capacity(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_refresh_goal_resources(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                properties: GoalAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                properties: GoalAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_goal_resources(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                body: UpdateGoalResourceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_goal_resources(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                body: UpdateGoalResourceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_goal_resources(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                **kwargs: Any
            ) -> GoalAssignment: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[GoalAssignment]: ...


    class azure.mgmt.resiliencemanagement.operations.GoalResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                goal_resource_name: str, 
                **kwargs: Any
            ) -> GoalResource: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                goal_assignment_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[GoalResource]: ...


    class azure.mgmt.resiliencemanagement.operations.GoalTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                service_group_name: str, 
                goal_template_name: str, 
                resource: GoalTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GoalTemplate]: ...

        @overload
        def begin_create_or_update(
                self, 
                service_group_name: str, 
                goal_template_name: str, 
                resource: GoalTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GoalTemplate]: ...

        @overload
        def begin_create_or_update(
                self, 
                service_group_name: str, 
                goal_template_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GoalTemplate]: ...

        @distributed_trace
        def begin_delete(
                self, 
                service_group_name: str, 
                goal_template_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                service_group_name: str, 
                goal_template_name: str, 
                properties: GoalTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                service_group_name: str, 
                goal_template_name: str, 
                properties: GoalTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                service_group_name: str, 
                goal_template_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                service_group_name: str, 
                goal_template_name: str, 
                **kwargs: Any
            ) -> GoalTemplate: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[GoalTemplate]: ...


    class azure.mgmt.resiliencemanagement.operations.OperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


    class azure.mgmt.resiliencemanagement.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.resiliencemanagement.operations.RecoveryJobResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                recovery_job_name: str, 
                recovery_job_resource_name: str, 
                **kwargs: Any
            ) -> RecoveryJobResource: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                recovery_job_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RecoveryJobResource]: ...


    class azure.mgmt.resiliencemanagement.operations.RecoveryJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_cancel(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                recovery_job_name: str, 
                body: RecoveryActionRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[ArmResponseErrorResponse]: ...

        @overload
        def begin_cancel(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                recovery_job_name: str, 
                body: RecoveryActionRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[ArmResponseErrorResponse]: ...

        @overload
        def begin_cancel(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                recovery_job_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[ArmResponseErrorResponse]: ...

        @overload
        def begin_resume(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                recovery_job_name: str, 
                body: RecoveryActionRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[ArmResponseErrorResponse]: ...

        @overload
        def begin_resume(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                recovery_job_name: str, 
                body: RecoveryActionRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[ArmResponseErrorResponse]: ...

        @overload
        def begin_resume(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                recovery_job_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[ArmResponseErrorResponse]: ...

        @distributed_trace
        def begin_retry(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                recovery_job_name: str, 
                *, 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[ArmResponseErrorResponse]: ...

        @distributed_trace
        def get(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                recovery_job_name: str, 
                **kwargs: Any
            ) -> RecoveryJob: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RecoveryJob]: ...


    class azure.mgmt.resiliencemanagement.operations.RecoveryPlanActionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_check_readiness(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                *, 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: FailoverRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlanActionBaseResponse]: ...

        @overload
        def begin_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: FailoverRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlanActionBaseResponse]: ...

        @overload
        def begin_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlanActionBaseResponse]: ...

        @distributed_trace
        def begin_failover_commit(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                *, 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlanActionBaseResponse]: ...

        @distributed_trace
        def begin_finalize(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                *, 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[ArmResponseErrorResponse]: ...

        @overload
        def begin_reprotect(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: Optional[ReprotectRequest] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlanActionBaseResponse]: ...

        @overload
        def begin_reprotect(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: Optional[ReprotectRequest] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlanActionBaseResponse]: ...

        @overload
        def begin_reprotect(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlanActionBaseResponse]: ...

        @overload
        def begin_test_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: FailoverRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlanActionBaseResponse]: ...

        @overload
        def begin_test_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: FailoverRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlanActionBaseResponse]: ...

        @overload
        def begin_test_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlanActionBaseResponse]: ...

        @overload
        def begin_test_failover_cleanup(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: TestFailoverCleanupRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlanActionBaseResponse]: ...

        @overload
        def begin_test_failover_cleanup(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: TestFailoverCleanupRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlanActionBaseResponse]: ...

        @overload
        def begin_test_failover_cleanup(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlanActionBaseResponse]: ...

        @overload
        def begin_update_resources(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: UpdateRecoveryResourcesRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[UpdateRecoveryResourcesResponse]: ...

        @overload
        def begin_update_resources(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: UpdateRecoveryResourcesRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[UpdateRecoveryResourcesResponse]: ...

        @overload
        def begin_update_resources(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[UpdateRecoveryResourcesResponse]: ...

        @overload
        def begin_validate_for_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: FailoverRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[ValidateForRecoveryOperationBaseResponse]: ...

        @overload
        def begin_validate_for_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: FailoverRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[ValidateForRecoveryOperationBaseResponse]: ...

        @overload
        def begin_validate_for_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[ValidateForRecoveryOperationBaseResponse]: ...

        @distributed_trace
        def begin_validate_for_failover_commit(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                *, 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[ValidateForRecoveryOperationBaseResponse]: ...

        @overload
        def begin_validate_for_operation(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: ValidateForOperationRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[ArmResponseErrorResponse]: ...

        @overload
        def begin_validate_for_operation(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: ValidateForOperationRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[ArmResponseErrorResponse]: ...

        @overload
        def begin_validate_for_operation(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[ArmResponseErrorResponse]: ...

        @overload
        def begin_validate_for_reprotect(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: Optional[ReprotectRequest] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[ValidateForRecoveryOperationBaseResponse]: ...

        @overload
        def begin_validate_for_reprotect(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: Optional[ReprotectRequest] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[ValidateForRecoveryOperationBaseResponse]: ...

        @overload
        def begin_validate_for_reprotect(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[ValidateForRecoveryOperationBaseResponse]: ...

        @overload
        def begin_validate_for_test_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: FailoverRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[ValidateForRecoveryOperationBaseResponse]: ...

        @overload
        def begin_validate_for_test_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: FailoverRequest, 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[ValidateForRecoveryOperationBaseResponse]: ...

        @overload
        def begin_validate_for_test_failover(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[ValidateForRecoveryOperationBaseResponse]: ...

        @distributed_trace
        def begin_validate_for_test_failover_cleanup(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                *, 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[ValidateForRecoveryOperationBaseResponse]: ...


    class azure.mgmt.resiliencemanagement.operations.RecoveryPlansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                resource: RecoveryPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @overload
        def begin_create_or_update(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                resource: RecoveryPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @overload
        def begin_create_or_update(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @distributed_trace
        def begin_delete(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                properties: RecoveryPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @overload
        def begin_update(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                properties: RecoveryPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @overload
        def begin_update(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecoveryPlan]: ...

        @distributed_trace
        def get(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                **kwargs: Any
            ) -> RecoveryPlan: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RecoveryPlan]: ...


    class azure.mgmt.resiliencemanagement.operations.RecoveryResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                recovery_resource_name: str, 
                **kwargs: Any
            ) -> RecoveryResource: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                recovery_plan_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RecoveryResource]: ...


    class azure.mgmt.resiliencemanagement.operations.UnifiedResilienceItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                service_group_name: str, 
                unified_resilience_item_name: str, 
                **kwargs: Any
            ) -> UnifiedResilienceItem: ...

        @distributed_trace
        def list(
                self, 
                service_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[UnifiedResilienceItem]: ...


    class azure.mgmt.resiliencemanagement.operations.UsagePlansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                resource: UsagePlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UsagePlan]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                resource: UsagePlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UsagePlan]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UsagePlan]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'usage_plan_name']}, api_versions_list=['2026-03-01-preview', '2026-04-01-preview', '2026-06-01-preview', '2026-08-31-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                properties: UsagePlanTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UsagePlan]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                properties: UsagePlanTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UsagePlan]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[UsagePlan]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'usage_plan_name', 'accept']}, api_versions_list=['2026-03-01-preview', '2026-04-01-preview', '2026-06-01-preview', '2026-08-31-preview'])
        def get(
                self, 
                resource_group_name: str, 
                usage_plan_name: str, 
                **kwargs: Any
            ) -> UsagePlan: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-03-01-preview', '2026-04-01-preview', '2026-06-01-preview', '2026-08-31-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[UsagePlan]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-03-01-preview', '2026-04-01-preview', '2026-06-01-preview', '2026-08-31-preview'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[UsagePlan]: ...


namespace azure.mgmt.resiliencemanagement.types

    class azure.mgmt.resiliencemanagement.types.AddOrUpdateResourcesRequest(TypedDict, total=False):
        key "faultDurationInMin": Required[int]
        key "forceInclusionAndUpdate": Union[str, ForceInclusionAndUpdate]
        key "resourceLists": ForwardRef('ResourceLists', module='types')
        faultDurationInMin: int
        forceInclusionAndUpdate: Union[str, ForceInclusionAndUpdate]
        resourceLists: ResourceLists


    class azure.mgmt.resiliencemanagement.types.AssetPropertiesOfDrill(TypedDict, total=False):
        key "region": Required[str]
        key "resourceGroup": str
        key "subscription": Required[str]
        region: str
        resourceGroup: str
        subscription: str


    class azure.mgmt.resiliencemanagement.types.AssociatedIdentity(TypedDict, total=False):
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        key "userAssignedIdentity": str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentity: str


    class azure.mgmt.resiliencemanagement.types.AttentionReason(TypedDict, total=False):
        key "chaosResource": Union[str, ExtensionObjectState]
        key "chaosResourceUserMsi": Union[str, ExtensionObjectState]
        key "discoveryRuleExists": Union[str, ExtensionObjectState]
        key "drillMonitoringResources": Union[str, ExtensionObjectState]
        key "drillRbacOnChaosResource": Union[str, RBACState]
        key "drillRbacOnHealthModel": Union[str, RBACState]
        key "drillRbacOnMonitoringResources": Union[str, RBACState]
        key "drillRbacOnRecoveryPlan": Union[str, RBACState]
        key "drillRbacOnSli": Union[str, RBACState]
        key "drillUserMsi": Union[str, ExtensionObjectState]
        key "healthModelExists": Union[str, ExtensionObjectState]
        key "includedResourceInDrill": Union[str, ExtensionObjectState]
        key "monitoringRbacOnDrillResources": Union[str, RBACState]
        key "monitoringSourceNotConfigured": bool
        key "rbacOnTargetResources": Union[str, RBACState]
        key "recoveryPlanAndDrillResourcesState": Union[str, RelativeResourceCompositionState]
        key "roReadiness": Union[str, RecoveryPlanState]
        key "runbookFaultRbacOnTargets": Union[str, RBACState]
        key "serviceGroupAndDrillResourcesState": Union[str, RelativeResourceCompositionState]
        chaosResource: Union[str, ExtensionObjectState]
        chaosResourceCreationFailureReasons: list[str]
        chaosResourceUserMsi: Union[str, ExtensionObjectState]
        discoveryRuleExists: Union[str, ExtensionObjectState]
        drillMonitoringErrors: list[ErrorDetails]
        drillMonitoringResources: Union[str, ExtensionObjectState]
        drillRbacOnChaosResource: Union[str, RBACState]
        drillRbacOnHealthModel: Union[str, RBACState]
        drillRbacOnMonitoringResources: Union[str, RBACState]
        drillRbacOnRecoveryPlan: Union[str, RBACState]
        drillRbacOnSli: Union[str, RBACState]
        drillUserMsi: Union[str, ExtensionObjectState]
        healthModelExists: Union[str, ExtensionObjectState]
        includedResourceInDrill: Union[str, ExtensionObjectState]
        missingRequiredResourceProviders: list[str]
        monitoringRbacOnDrillResources: Union[str, RBACState]
        monitoringSourceNotConfigured: bool
        rbacNeededForDrillOnChaosResource: list[str]
        rbacNeededForDrillOnDrillMonitoringResources: list[str]
        rbacNeededForDrillOnDrillResources: list[str]
        rbacNeededForDrillOnHealthModel: list[str]
        rbacNeededForDrillOnRecoveryPlan: list[str]
        rbacOnTargetResources: Union[str, RBACState]
        recoveryPlanAndDrillResourcesState: Union[str, RelativeResourceCompositionState]
        roReadiness: Union[str, RecoveryPlanState]
        runbookFaultRbacOnTargets: Union[str, RBACState]
        serviceGroupAndDrillResourcesState: Union[str, RelativeResourceCompositionState]
        sliAttentionStatuses: list[SliAttentionStatus]


    class azure.mgmt.resiliencemanagement.types.ChaosResourcePropertiesOfDrill(TypedDict, total=False):
        key "chaosResourceId": str
        key "chaosResourceIdentityForFaults": Required[AssociatedIdentity]
        key "faultDurationInMin": int
        key "identity": Required[AssociatedIdentity]
        chaosResourceId: str
        chaosResourceIdentityForFaults: AssociatedIdentity
        faultDurationInMin: int
        identity: AssociatedIdentity


    class azure.mgmt.resiliencemanagement.types.CustomFaultDetails(TypedDict, total=False):
        key "faultName": Required[str]
        key "scriptResourceId": Required[str]
        faultName: str
        scriptResourceId: str


    class azure.mgmt.resiliencemanagement.types.DiskReprotectInputDetails(TypedDict, total=False):
        key "diskResourceId": str
        key "stagingStorageAccountResourceId": str
        diskResourceId: str
        stagingStorageAccountResourceId: str


    class azure.mgmt.resiliencemanagement.types.Drill(ProxyResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "name": str
        key "properties": ForwardRef('DrillProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        name: str
        properties: DrillProperties
        systemData: SystemData
        type: str


    class azure.mgmt.resiliencemanagement.types.DrillEndRequest(TypedDict, total=False):
        key "attestation": Required[Union[str, DrillAttestation]]
        key "attestationNotes": Required[str]
        attestation: Union[str, DrillAttestation]
        attestationNotes: str


    class azure.mgmt.resiliencemanagement.types.DrillRunAddNotesRequest(TypedDict, total=False):
        key "author": str
        key "notes": str
        key "timestamp": str
        author: str
        notes: str
        timestamp: str


    class azure.mgmt.resiliencemanagement.types.DrillRunFailoverRequest(TypedDict, total=False):
        key "autoFailover": Required[Union[str, AutoFailover]]
        key "failoverProperties": Required[FailoverRequest]
        autoFailover: Union[str, AutoFailover]
        failoverProperties: FailoverRequest


    class azure.mgmt.resiliencemanagement.types.DrillRunReprotectRequest(TypedDict, total=False):
        key "reprotectProperties": Required[ReprotectRequest]
        reprotectProperties: ReprotectRequest


    class azure.mgmt.resiliencemanagement.types.DrillStartRequest(TypedDict, total=False):
        key "mode": Required[Union[str, DrillMode]]
        mode: Union[str, DrillMode]


    class azure.mgmt.resiliencemanagement.types.DrillType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REGIONAL = "Regional"
        ZONAL = "Zonal"


    class azure.mgmt.resiliencemanagement.types.DrillUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('DrillUpdateProperties', module='types')
        identity: ManagedServiceIdentity
        properties: DrillUpdateProperties


    class azure.mgmt.resiliencemanagement.types.DrillUpdateProperties(TypedDict, total=False):
        key "chaosResourceProperties": ForwardRef('ChaosResourcePropertiesOfDrill', module='types')
        key "drillAssetProperties": ForwardRef('AssetPropertiesOfDrill', module='types')
        key "healthModelMonitoringProperties": Optional[HealthModelMonitoringProperties]
        key "monitoringProperties": ForwardRef('MonitoringPropertiesOfDrill', module='types')
        key "rbacSetupMode": Union[str, RBACSetupMode]
        key "recoveryPlanProperties": ForwardRef('RecoveryPlanPropertiesOfDrill', module='types')
        key "sliMonitoringProperties": Optional[SliMonitoringProperties]
        chaosResourceProperties: ChaosResourcePropertiesOfDrill
        drillAssetProperties: AssetPropertiesOfDrill
        healthModelMonitoringProperties: HealthModelMonitoringProperties
        monitoringProperties: MonitoringPropertiesOfDrill
        rbacSetupMode: Union[str, RBACSetupMode]
        recoveryPlanProperties: RecoveryPlanPropertiesOfDrill
        sliMonitoringProperties: SliMonitoringProperties


    class azure.mgmt.resiliencemanagement.types.Enrollment(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('EnrollmentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: EnrollmentProperties
        systemData: SystemData
        type: str


    class azure.mgmt.resiliencemanagement.types.EnrollmentProperties(TypedDict, total=False):
        key "errorDetails": ForwardRef('ErrorDetail', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "serviceGroupId": Required[str]
        errorDetails: ErrorDetail
        provisioningState: Union[str, ProvisioningState]
        serviceGroupId: str


    class azure.mgmt.resiliencemanagement.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.resiliencemanagement.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.resiliencemanagement.types.ErrorDetails(TypedDict, total=False):
        key "code": Required[str]
        key "message": Required[str]
        code: str
        message: str
        recommendations: list[str]


    class azure.mgmt.resiliencemanagement.types.ExecutionConfigurations(TypedDict, total=False):
        key "userConsent": Required[Union[str, UserConsent]]
        userConsent: Union[str, UserConsent]


    class azure.mgmt.resiliencemanagement.types.FailoverRequest(TypedDict, total=False):
        key "failoverDirection": Required[Union[str, FailoverDirectionTypes]]
        key "failoverRequestProperties": ForwardRef('FailoverRequestProperties', module='types')
        failoverDirection: Union[str, FailoverDirectionTypes]
        failoverRequestProperties: FailoverRequestProperties


    class azure.mgmt.resiliencemanagement.types.FailoverRequestProperties(TypedDict, total=False):
        key "executionConfigurations": ForwardRef('ExecutionConfigurations', module='types')
        key "sourceLocations": Required[list[str]]
        executionConfigurations: ExecutionConfigurations
        selectedResourceIds: list[str]
        sourceLocations: list[str]


    class azure.mgmt.resiliencemanagement.types.FaultDetails(TypedDict, total=False):
        key "faultName": Required[str]
        key "faultUrn": Required[str]
        key "targetResourceId": Required[str]
        faultName: str
        faultUrn: str
        targetResourceId: str


    class azure.mgmt.resiliencemanagement.types.FaultProperties(TypedDict, total=False):
        key "customFault": ForwardRef('CustomFaultDetails', module='types')
        key "defaultFault": ForwardRef('FaultDetails', module='types')
        key "overriddenDefaultFault": ForwardRef('FaultDetails', module='types')
        availableFaults: list[FaultDetails]
        customFault: CustomFaultDetails
        defaultFault: FaultDetails
        overriddenDefaultFault: FaultDetails


    class azure.mgmt.resiliencemanagement.types.GoalAssignment(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('GoalAssignmentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: GoalAssignmentProperties
        systemData: SystemData
        type: str


    class azure.mgmt.resiliencemanagement.types.GoalAssignmentProperties(TypedDict, total=False):
        key "errorDetails": ForwardRef('ErrorDetail', module='types')
        key "goalAssignmentType": Union[str, GoalAssignmentType]
        key "goalTemplateId": str
        key "provisioningState": Union[str, ProvisioningState]
        key "requireZonalResiliency": bool
        errorDetails: ErrorDetail
        goalAssignmentType: Union[str, GoalAssignmentType]
        goalTemplateId: str
        provisioningState: Union[str, ProvisioningState]
        requireZonalResiliency: bool
        serviceLevelResources: list[ServiceLevelResource]


    class azure.mgmt.resiliencemanagement.types.GoalResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('GoalResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: GoalResourceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.resiliencemanagement.types.GoalResourceProperties(TypedDict, total=False):
        key "disasterRecoveryAttestationStatus": Union[str, AttestationState]
        key "disasterRecoveryGoalParticipation": Union[str, ExclusionState]
        key "exclusionReasonForDisasterRecoveryGoals": Union[str, ExclusionReason]
        key "exclusionReasonForHighAvailabilityGoals": Union[str, ExclusionReason]
        key "highAvailabilityAttestationStatus": Union[str, AttestationState]
        key "highAvailabilityGoalParticipation": Union[str, ExclusionState]
        key "provisioningState": Union[str, ProvisioningState]
        key "resourceArmId": Required[str]
        key "zonalResiliency": ForwardRef('ResiliencyProperties', module='types')
        disasterRecoveryAttestationStatus: Union[str, AttestationState]
        disasterRecoveryGoalParticipation: Union[str, ExclusionState]
        exclusionReasonForDisasterRecoveryGoals: Union[str, ExclusionReason]
        exclusionReasonForHighAvailabilityGoals: Union[str, ExclusionReason]
        highAvailabilityAttestationStatus: Union[str, AttestationState]
        highAvailabilityGoalParticipation: Union[str, ExclusionState]
        provisioningState: Union[str, ProvisioningState]
        resourceArmId: str
        serviceGroupMemberships: list[ServiceGroupMembership]
        userConfirmationForHighAvailability: list[UserConfirmationItem]
        zonalResiliency: ResiliencyProperties


    class azure.mgmt.resiliencemanagement.types.GoalTemplate(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('GoalTemplateProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: GoalTemplateProperties
        systemData: SystemData
        type: str


    class azure.mgmt.resiliencemanagement.types.GoalTemplateProperties(TypedDict, total=False):
        key "errorDetails": ForwardRef('ErrorDetail', module='types')
        key "goalType": Required[Union[str, GoalType]]
        key "provisioningState": Union[str, ProvisioningState]
        key "regionalRecoveryPointObjective": str
        key "regionalRecoveryTimeObjective": str
        key "requireDisasterRecovery": Union[str, RequirementSelected]
        key "requireHighAvailability": Union[str, RequirementSelected]
        errorDetails: ErrorDetail
        goalType: Union[str, GoalType]
        provisioningState: Union[str, ProvisioningState]
        regionalRecoveryPointObjective: str
        regionalRecoveryTimeObjective: str
        requireDisasterRecovery: Union[str, RequirementSelected]
        requireHighAvailability: Union[str, RequirementSelected]


    class azure.mgmt.resiliencemanagement.types.HealthModelMonitoringProperties(TypedDict, total=False):
        key "discoveryRuleId": Required[str]
        key "identity": Required[AssociatedIdentity]
        discoveryRuleId: str
        identity: AssociatedIdentity


    class azure.mgmt.resiliencemanagement.types.IncludeOrUpdateResource(TypedDict, total=False):
        key "faultProperties": ForwardRef('FaultProperties', module='types')
        key "id": Required[str]
        faultProperties: FaultProperties
        id: str


    class azure.mgmt.resiliencemanagement.types.LastRunProperties(TypedDict, total=False):
        key "lastRunAttestation": Union[str, DrillAttestation]
        key "lastRunDuration": str
        key "lastRunState": Union[str, JobStatus]
        key "lastRunTime": str
        lastRunAttestation: Union[str, DrillAttestation]
        lastRunDuration: str
        lastRunState: Union[str, JobStatus]
        lastRunTime: str


    class azure.mgmt.resiliencemanagement.types.ListReportDownloadUrlRequest(TypedDict, total=False):
        key "format": Union[str, DrillReportFormat]
        format: Union[str, DrillReportFormat]


    class azure.mgmt.resiliencemanagement.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.resiliencemanagement.types.MarkAsCompleteRequest(TypedDict, total=False):
        key "drillRunStage": Required[Union[str, DrillRunSubtasks]]
        drillRunStage: Union[str, DrillRunSubtasks]


    class azure.mgmt.resiliencemanagement.types.MonitoringPropertiesOfDrill(TypedDict, total=False):
        key "dataCollectionEndpointId": str
        key "identity": ForwardRef('AssociatedIdentity', module='types')
        key "logAnalyticsWorkspaceId": str
        key "rawMetricsDataCollectionRuleId": str
        key "serviceGroupMetricsDataCollectionRuleId": str
        dataCollectionEndpointId: str
        identity: AssociatedIdentity
        logAnalyticsWorkspaceId: str
        rawMetricsDataCollectionRuleId: str
        serviceGroupMetricsDataCollectionRuleId: str


    class azure.mgmt.resiliencemanagement.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.resiliencemanagement.types.RecommendCapacityRequest(TypedDict, total=False):
        key "resourceIds": Required[list[str]]
        resourceIds: list[str]


    class azure.mgmt.resiliencemanagement.types.RecoveryActionRequest(TypedDict, total=False):
        key "description": str
        description: str


    class azure.mgmt.resiliencemanagement.types.RecoveryGroup(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('RecoveryGroupProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: RecoveryGroupProperties
        systemData: SystemData
        type: str


    class azure.mgmt.resiliencemanagement.types.RecoveryGroupActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_RUNBOOK = "CustomRunbook"
        MANUAL_ACTION = "ManualAction"


    class azure.mgmt.resiliencemanagement.types.RecoveryGroupCustomRunbookAction(TypedDict, total=False):
        key "actionResourceId": str
        key "associatedIdentity": ForwardRef('AssociatedIdentity', module='types')
        key "description": str
        key "name": Required[str]
        key "timeoutInMinutes": Required[int]
        key "type": Required[Literal[RecoveryGroupActionType.CUSTOM_RUNBOOK]]
        actionResourceId: str
        associatedIdentity: AssociatedIdentity
        description: str
        name: str
        parameters: dict[str, str]
        timeoutInMinutes: int
        type: Literal[RecoveryGroupActionType.CUSTOM_RUNBOOK]


    class azure.mgmt.resiliencemanagement.types.RecoveryGroupManualAction(TypedDict, total=False):
        key "description": str
        key "name": Required[str]
        key "timeoutInMinutes": Required[int]
        key "type": Required[Literal[RecoveryGroupActionType.MANUAL_ACTION]]
        description: str
        name: str
        timeoutInMinutes: int
        type: Literal[RecoveryGroupActionType.MANUAL_ACTION]


    class azure.mgmt.resiliencemanagement.types.RecoveryGroupProperties(TypedDict, total=False):
        key "description": Required[str]
        key "groupUniqueId": Required[str]
        key "orderId": Required[int]
        description: str
        groupUniqueId: str
        orderId: int
        postActions: list[RecoveryGroupBaseAction]
        preActions: list[RecoveryGroupBaseAction]


    class azure.mgmt.resiliencemanagement.types.RecoveryGroupsSetting(TypedDict, total=False):
        key "defaultGroup": Required[RecoveryGroup]
        additionalGroups: list[RecoveryGroup]
        defaultGroup: RecoveryGroup


    class azure.mgmt.resiliencemanagement.types.RecoveryPlan(ProxyResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "name": str
        key "properties": ForwardRef('RecoveryPlanProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        name: str
        properties: RecoveryPlanProperties
        systemData: SystemData
        type: str


    class azure.mgmt.resiliencemanagement.types.RecoveryPlanFailoverOperationStatus(TypedDict, total=False):
        key "errorDetails": ForwardRef('ErrorDetail', module='types')
        key "lastExecutedAt": str
        key "operationStatus": Union[str, RecoveryOperationStatus]
        key "recoveryTimeActual": str
        errorDetails: ErrorDetail
        lastExecutedAt: str
        operationStatus: Union[str, RecoveryOperationStatus]
        recoveryTimeActual: str


    class azure.mgmt.resiliencemanagement.types.RecoveryPlanOperationStatus(TypedDict, total=False):
        key "errorDetails": ForwardRef('ErrorDetail', module='types')
        key "lastExecutedAt": str
        key "operationStatus": Union[str, RecoveryOperationStatus]
        errorDetails: ErrorDetail
        lastExecutedAt: str
        operationStatus: Union[str, RecoveryOperationStatus]


    class azure.mgmt.resiliencemanagement.types.RecoveryPlanProperties(TypedDict, total=False):
        key "errorDetails": ForwardRef('ErrorDetail', module='types')
        key "latestFailoverStatus": ForwardRef('RecoveryPlanFailoverOperationStatus', module='types')
        key "latestValidationStatus": ForwardRef('RecoveryPlanOperationStatus', module='types')
        key "planDescription": Required[str]
        key "planState": Union[str, RecoveryPlanState]
        key "planType": Required[Union[str, RecoveryPlanType]]
        key "provisioningState": Union[str, ProvisioningState]
        key "recoveryGroupsSetting": Required[RecoveryGroupsSetting]
        errorDetails: ErrorDetail
        latestFailoverStatus: RecoveryPlanFailoverOperationStatus
        latestValidationStatus: RecoveryPlanOperationStatus
        planDescription: str
        planState: Union[str, RecoveryPlanState]
        planType: Union[str, RecoveryPlanType]
        provisioningState: Union[str, ProvisioningState]
        recoveryGroupsSetting: RecoveryGroupsSetting


    class azure.mgmt.resiliencemanagement.types.RecoveryPlanPropertiesOfDrill(TypedDict, total=False):
        key "identity": Required[AssociatedIdentity]
        key "recoveryPlanId": str
        key "recoveryPlanResourceExcludedCount": int
        identity: AssociatedIdentity
        recoveryPlanId: str
        recoveryPlanResourceExcludedCount: int


    class azure.mgmt.resiliencemanagement.types.RecoveryResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('RecoveryResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: RecoveryResourceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.resiliencemanagement.types.RecoveryResourceProperties(TypedDict, total=False):
        key "associatedIdentity": ForwardRef('AssociatedIdentity', module='types')
        key "errorDetails": ForwardRef('ErrorDetail', module='types')
        key "inclusionState": Union[str, ResourceInclusionState]
        key "needsAttention": bool
        key "protectionStatus": Union[str, ResourceProtectionStatus]
        key "provisioningState": Union[str, ProvisioningState]
        key "recoveryGroupId": str
        key "recoveryResourceUniqueId": Required[str]
        key "resourceId": str
        key "resourceLocation": str
        key "selectedProtectionSolutionSetting": ForwardRef('ResourceBaseProtectionSolutionSetting', module='types')
        key "selectedProtectionSolutionType": Union[str, ResourceProtectionSolutionType]
        associatedIdentity: AssociatedIdentity
        attentionReasons: list[str]
        errorDetails: ErrorDetail
        inclusionState: Union[str, ResourceInclusionState]
        needsAttention: bool
        protectionStatus: Union[str, ResourceProtectionStatus]
        provisioningState: Union[str, ProvisioningState]
        recoveryGroupId: str
        recoveryResourceUniqueId: str
        resourceId: str
        resourceLocation: str
        resourcePhysicalZones: list[str]
        resourceProtectionSolutions: list[ResourceProtectionSolutionSettings]
        selectedProtectionSolutionSetting: ResourceBaseProtectionSolutionSetting
        selectedProtectionSolutionType: Union[str, ResourceProtectionSolutionType]


    class azure.mgmt.resiliencemanagement.types.RegionalDrillProperties(TypedDict, total=False):
        key "attentionReason": ForwardRef('AttentionReason', module='types')
        key "chaosResourceProperties": ForwardRef('ChaosResourcePropertiesOfDrill', module='types')
        key "drillAssetProperties": ForwardRef('AssetPropertiesOfDrill', module='types')
        key "drillType": Required[Literal[DrillType.REGIONAL]]
        key "errorDetails": ForwardRef('ErrorDetail', module='types')
        key "executionReadinessState": Union[str, ExecutionReadinessState]
        key "executionState": Union[str, ExecutionState]
        key "healthModelMonitoringProperties": ForwardRef('HealthModelMonitoringProperties', module='types')
        key "lastResyncReadinessCheckTime": str
        key "lastRunProperties": ForwardRef('LastRunProperties', module='types')
        key "lastSyncTime": str
        key "monitoringProperties": ForwardRef('MonitoringPropertiesOfDrill', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "rbacSetupMode": Union[str, RBACSetupMode]
        key "recoveryPlanProperties": ForwardRef('RecoveryPlanPropertiesOfDrill', module='types')
        key "serviceGroupId": str
        key "sliMonitoringProperties": ForwardRef('SliMonitoringProperties', module='types')
        key "systemMetadata": ForwardRef('SystemMetadata', module='types')
        attentionReason: AttentionReason
        chaosResourceProperties: ChaosResourcePropertiesOfDrill
        drillAssetProperties: AssetPropertiesOfDrill
        drillType: Literal[DrillType.REGIONAL]
        errorDetails: ErrorDetail
        executionReadinessState: Union[str, ExecutionReadinessState]
        executionState: Union[str, ExecutionState]
        healthModelMonitoringProperties: HealthModelMonitoringProperties
        lastResyncReadinessCheckTime: str
        lastRunProperties: LastRunProperties
        lastSyncTime: str
        monitoringProperties: MonitoringPropertiesOfDrill
        provisioningState: Union[str, ProvisioningState]
        rbacSetupMode: Union[str, RBACSetupMode]
        recoveryPlanProperties: RecoveryPlanPropertiesOfDrill
        serviceGroupId: str
        sliMonitoringProperties: SliMonitoringProperties
        systemMetadata: SystemMetadata


    class azure.mgmt.resiliencemanagement.types.ReprotectRequest(TypedDict, total=False):
        key "reprotectRequestProperties": ForwardRef('ReprotectRequestProperties', module='types')
        reprotectRequestProperties: ReprotectRequestProperties


    class azure.mgmt.resiliencemanagement.types.ReprotectRequestProperties(TypedDict, total=False):
        selectedResourceIds: list[str]


    class azure.mgmt.resiliencemanagement.types.ResiliencyProperties(TypedDict, total=False):
        key "attestationStatus": Union[str, AttestationState]
        key "exclusionReason": Union[str, ExclusionReason]
        key "goalParticipation": Union[str, ExclusionState]
        attestationStatus: Union[str, AttestationState]
        exclusionReason: Union[str, ExclusionReason]
        goalParticipation: Union[str, ExclusionState]
        userConfirmation: list[UserConfirmationItem]


    class azure.mgmt.resiliencemanagement.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.resiliencemanagement.types.ResourceCrossZoneVmRecoveryProtectionSetting(TypedDict, total=False):
        key "capacityReservationGroupId": str
        key "protectionSolutionType": Required[Literal[ResourceProtectionSolutionType.CROSS_ZONE_VM_RECOVERY]]
        key "targetZone": str
        capacityReservationGroupId: str
        protectionSolutionType: Literal[ResourceProtectionSolutionType.CROSS_ZONE_VM_RECOVERY]
        targetZone: str


    class azure.mgmt.resiliencemanagement.types.ResourceCustomProtectionAction(TypedDict, total=False):
        key "resourceId": Required[str]
        resourceId: str


    class azure.mgmt.resiliencemanagement.types.ResourceCustomProtectionSetting(TypedDict, total=False):
        key "failoverAction": ForwardRef('ResourceCustomProtectionAction', module='types')
        key "failoverCommitAction": ForwardRef('ResourceCustomProtectionAction', module='types')
        key "protectionSolutionType": Required[Literal[ResourceProtectionSolutionType.CUSTOM_RUNBOOK]]
        key "reprotectAction": ForwardRef('ResourceCustomProtectionAction', module='types')
        key "testFailoverAction": ForwardRef('ResourceCustomProtectionAction', module='types')
        key "testFailoverCleanupAction": ForwardRef('ResourceCustomProtectionAction', module='types')
        failoverAction: ResourceCustomProtectionAction
        failoverCommitAction: ResourceCustomProtectionAction
        protectionSolutionType: Literal[ResourceProtectionSolutionType.CUSTOM_RUNBOOK]
        reprotectAction: ResourceCustomProtectionAction
        testFailoverAction: ResourceCustomProtectionAction
        testFailoverCleanupAction: ResourceCustomProtectionAction


    class azure.mgmt.resiliencemanagement.types.ResourceLists(TypedDict, total=False):
        excludeResources: list[str]
        includeResources: list[IncludeOrUpdateResource]
        updateResources: list[IncludeOrUpdateResource]


    class azure.mgmt.resiliencemanagement.types.ResourceNativeProtectionSolutionSetting(TypedDict, total=False):
        key "protectionSolutionType": Required[Literal[ResourceProtectionSolutionType.AZURE_NATIVE]]
        protectionSolutionType: Literal[ResourceProtectionSolutionType.AZURE_NATIVE]


    class azure.mgmt.resiliencemanagement.types.ResourceProtectionSolutionSettings(TypedDict, total=False):
        key "activeLocation": str
        key "failoverState": Union[str, FailoverState]
        key "isAutoFailover": Required[bool]
        key "primaryResource": str
        key "protectionSolutionType": Union[str, ResourceProtectionSolutionType]
        key "protectionStatus": Union[str, ResourceProtectionStatus]
        key "replicationRole": Union[str, ResourceReplicationRole]
        key "resourceId": str
        key "testFailoverState": Union[str, TestFailoverState]
        activeLocation: str
        activeLocations: list[str]
        activePhysicalZones: list[str]
        failoverState: Union[str, FailoverState]
        isAutoFailover: bool
        primaryResource: str
        protectionSolutionType: Union[str, ResourceProtectionSolutionType]
        protectionStatus: Union[str, ResourceProtectionStatus]
        recoveryLocations: list[str]
        replicaResources: list[str]
        replicationRole: Union[str, ResourceReplicationRole]
        resourceId: str
        testFailoverState: Union[str, TestFailoverState]


    class azure.mgmt.resiliencemanagement.types.ResourceProtectionSolutionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_NATIVE = "AzureNative"
        AZURE_SITE_RECOVERY = "AzureSiteRecovery"
        CROSS_ZONE_VM_RECOVERY = "CrossZoneVMRecovery"
        CUSTOM_RUNBOOK = "CustomRunbook"
        NONE = "None"


    class azure.mgmt.resiliencemanagement.types.ResourceSiteRecoveryProtectionSetting(TypedDict, total=False):
        key "protectionSolutionType": Required[Literal[ResourceProtectionSolutionType.AZURE_SITE_RECOVERY]]
        key "reprotectParams": ForwardRef('ResourceSiteRecoveryReprotectParams', module='types')
        key "testFailoverCleanupParams": ForwardRef('ResourceSiteRecoveryTestFailoverCleanupParams', module='types')
        key "testFailoverParams": ForwardRef('ResourceSiteRecoveryTestFailoverParams', module='types')
        protectionSolutionType: Literal[ResourceProtectionSolutionType.AZURE_SITE_RECOVERY]
        reprotectParams: ResourceSiteRecoveryReprotectParams
        testFailoverCleanupParams: ResourceSiteRecoveryTestFailoverCleanupParams
        testFailoverParams: ResourceSiteRecoveryTestFailoverParams


    class azure.mgmt.resiliencemanagement.types.ResourceSiteRecoveryReprotectParams(TypedDict, total=False):
        diskReprotectInputDetails: list[DiskReprotectInputDetails]


    class azure.mgmt.resiliencemanagement.types.ResourceSiteRecoveryTestFailoverCleanupParams(TypedDict, total=False):
        key "comments": str
        comments: str


    class azure.mgmt.resiliencemanagement.types.ResourceSiteRecoveryTestFailoverParams(TypedDict, total=False):
        key "networkResourceId": str
        networkResourceId: str


    class azure.mgmt.resiliencemanagement.types.ServiceGroupMembership(TypedDict, total=False):
        key "membershipType": Required[Union[str, MembershipType]]
        key "serviceGroupId": Required[str]
        membershipType: Union[str, MembershipType]
        serviceGroupId: str


    class azure.mgmt.resiliencemanagement.types.ServiceLevelResource(TypedDict, total=False):
        key "serviceLevelIndicatorResourceId": Required[str]
        key "serviceLevelObjectiveResourceId": str
        serviceLevelIndicatorResourceId: str
        serviceLevelObjectiveResourceId: str


    class azure.mgmt.resiliencemanagement.types.SliAttentionStatus(TypedDict, total=False):
        key "drillRbacOnDestinationAmw": Union[str, RBACState]
        key "exists": Union[str, ExtensionObjectState]
        key "sliId": Required[str]
        key "type": Required[Union[str, SliType]]
        key "typeMatch": Union[str, SliTypeMatchState]
        drillRbacOnDestinationAmw: Union[str, RBACState]
        exists: Union[str, ExtensionObjectState]
        rbacNeededOnDestinationAmws: list[str]
        sliId: str
        type: Union[str, SliType]
        typeMatch: Union[str, SliTypeMatchState]


    class azure.mgmt.resiliencemanagement.types.SliMonitoringProperties(TypedDict, total=False):
        key "identity": Required[AssociatedIdentity]
        key "slis": Required[list[SliSelection]]
        identity: AssociatedIdentity
        slis: list[SliSelection]


    class azure.mgmt.resiliencemanagement.types.SliSelection(TypedDict, total=False):
        key "sliId": Required[str]
        key "type": Required[Union[str, SliType]]
        sliId: str
        type: Union[str, SliType]


    class azure.mgmt.resiliencemanagement.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.resiliencemanagement.types.SystemMetadata(TypedDict, total=False):
        key "initialConfig": Required[Union[str, InitialConfig]]
        initialConfig: Union[str, InitialConfig]
        resourceTypeCategories: list[Union[str, ResourceTypeCategories]]


    class azure.mgmt.resiliencemanagement.types.TestFailoverCleanupRequest(TypedDict, total=False):
        key "comments": str
        comments: str


    class azure.mgmt.resiliencemanagement.types.TrackedResource(Resource):
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


    class azure.mgmt.resiliencemanagement.types.UpdateGoalResourceRequest(TypedDict, total=False):
        key "resources": Required[list[GoalResource]]
        resources: list[GoalResource]


    class azure.mgmt.resiliencemanagement.types.UpdateRecoveryResourcesRequest(TypedDict, total=False):
        resourcesToRemove: list[str]
        resourcesToUpdate: list[RecoveryResource]


    class azure.mgmt.resiliencemanagement.types.UsagePlan(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('UsagePlanProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: UsagePlanProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.resiliencemanagement.types.UsagePlanProperties(TypedDict, total=False):
        key "errorDetails": ForwardRef('ErrorDetail', module='types')
        key "planType": Union[str, UsagePlanType]
        key "provisioningState": Union[str, ProvisioningState]
        errorDetails: ErrorDetail
        planType: Union[str, UsagePlanType]
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.resiliencemanagement.types.UsagePlanTagsUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.resiliencemanagement.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.resiliencemanagement.types.UserConfirmationItem(TypedDict, total=False):
        key "confirmationStatus": Required[Union[str, ConfirmationStatus]]
        key "reasonForRequestingConfirmation": Union[str, ReasonForRequestingConfirmation]
        key "solutionDisplayName": Required[Union[str, SolutionDisplayName]]
        confirmationStatus: Union[str, ConfirmationStatus]
        reasonForRequestingConfirmation: Union[str, ReasonForRequestingConfirmation]
        solutionDisplayName: Union[str, SolutionDisplayName]


    class azure.mgmt.resiliencemanagement.types.ValidateForExecutionProperties(TypedDict, total=False):
        key "operationName": Union[str, DrillRunTasks]
        operationName: Union[str, DrillRunTasks]
        sourceLocations: list[str]


    class azure.mgmt.resiliencemanagement.types.ValidateForExecutionRequest(TypedDict, total=False):
        key "validateForExecutionProperties": ForwardRef('ValidateForExecutionProperties', module='types')
        validateForExecutionProperties: ValidateForExecutionProperties


    class azure.mgmt.resiliencemanagement.types.ValidateForOperationRequest(TypedDict, total=False):
        key "operationName": Required[Union[str, RecoveryOperationNames]]
        operationName: Union[str, RecoveryOperationNames]


    class azure.mgmt.resiliencemanagement.types.ZonalDrillProperties(TypedDict, total=False):
        key "attentionReason": ForwardRef('AttentionReason', module='types')
        key "chaosResourceProperties": ForwardRef('ChaosResourcePropertiesOfDrill', module='types')
        key "drillAssetProperties": ForwardRef('AssetPropertiesOfDrill', module='types')
        key "drillType": Required[Literal[DrillType.ZONAL]]
        key "errorDetails": ForwardRef('ErrorDetail', module='types')
        key "executionReadinessState": Union[str, ExecutionReadinessState]
        key "executionState": Union[str, ExecutionState]
        key "healthModelMonitoringProperties": ForwardRef('HealthModelMonitoringProperties', module='types')
        key "lastResyncReadinessCheckTime": str
        key "lastRunProperties": ForwardRef('LastRunProperties', module='types')
        key "lastSyncTime": str
        key "monitoringProperties": ForwardRef('MonitoringPropertiesOfDrill', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "rbacSetupMode": Union[str, RBACSetupMode]
        key "recoveryPlanProperties": ForwardRef('RecoveryPlanPropertiesOfDrill', module='types')
        key "serviceGroupId": str
        key "sliMonitoringProperties": ForwardRef('SliMonitoringProperties', module='types')
        key "systemMetadata": ForwardRef('SystemMetadata', module='types')
        key "vmsPresent": Union[str, VMPresent]
        attentionReason: AttentionReason
        chaosResourceProperties: ChaosResourcePropertiesOfDrill
        drillAssetProperties: AssetPropertiesOfDrill
        drillType: Literal[DrillType.ZONAL]
        errorDetails: ErrorDetail
        executionReadinessState: Union[str, ExecutionReadinessState]
        executionState: Union[str, ExecutionState]
        healthModelMonitoringProperties: HealthModelMonitoringProperties
        lastResyncReadinessCheckTime: str
        lastRunProperties: LastRunProperties
        lastSyncTime: str
        monitoringProperties: MonitoringPropertiesOfDrill
        provisioningState: Union[str, ProvisioningState]
        rbacSetupMode: Union[str, RBACSetupMode]
        recoveryPlanProperties: RecoveryPlanPropertiesOfDrill
        serviceGroupId: str
        sliMonitoringProperties: SliMonitoringProperties
        systemMetadata: SystemMetadata
        vmsPresent: Union[str, VMPresent]


```