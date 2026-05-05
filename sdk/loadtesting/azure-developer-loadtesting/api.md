```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.developer.loadtesting

    class azure.developer.loadtesting.LoadTestAdministrationClient(LoadTestAdministrationClientOperationsMixin): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: TokenCredential, 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def begin_clone_test(
                self, 
                test_id: str, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                new_test_id: str, 
                **kwargs: Any
            ) -> LROPoller[Test]: ...

        @overload
        def begin_clone_test(
                self, 
                test_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Test]: ...

        @overload
        def begin_clone_test(
                self, 
                test_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Test]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-11-01-preview', params_added_on={'2025-11-01-preview': ['api_version', 'test_id', 'accept']}, api_versions_list=['2025-11-01-preview'])
        def begin_generate_test_plan_recommendations(
                self, 
                test_id: str, 
                **kwargs: Any
            ) -> LROPoller[Test]: ...

        @overload
        def begin_upload_test_file(
                self, 
                test_id: str, 
                file_name: str, 
                body: bytes, 
                *, 
                file_type: Optional[Union[str, FileType]] = ..., 
                **kwargs: Any
            ) -> LROPoller[TestFileInfo]: ...

        @overload
        def begin_upload_test_file(
                self, 
                test_id: str, 
                file_name: str, 
                body: IO, 
                *, 
                file_type: Optional[Union[str, FileType]] = ..., 
                **kwargs: Any
            ) -> LROPoller[TestFileInfo]: ...

        def close(self) -> None: ...

        @overload
        def create_or_update_app_components(
                self, 
                test_id: str, 
                body: TestAppComponents, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestAppComponents: ...

        @overload
        def create_or_update_app_components(
                self, 
                test_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestAppComponents: ...

        @overload
        def create_or_update_app_components(
                self, 
                test_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestAppComponents: ...

        @overload
        def create_or_update_notification_rule(
                self, 
                notification_rule_id: str, 
                body: NotificationRule, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> NotificationRule: ...

        @overload
        def create_or_update_notification_rule(
                self, 
                notification_rule_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> NotificationRule: ...

        @overload
        def create_or_update_notification_rule(
                self, 
                notification_rule_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> NotificationRule: ...

        @overload
        def create_or_update_server_metrics_config(
                self, 
                test_id: str, 
                body: TestServerMetricsConfiguration, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestServerMetricsConfiguration: ...

        @overload
        def create_or_update_server_metrics_config(
                self, 
                test_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestServerMetricsConfiguration: ...

        @overload
        def create_or_update_server_metrics_config(
                self, 
                test_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestServerMetricsConfiguration: ...

        @overload
        def create_or_update_test(
                self, 
                test_id: str, 
                body: Test, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Test: ...

        @overload
        def create_or_update_test(
                self, 
                test_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Test: ...

        @overload
        def create_or_update_test(
                self, 
                test_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Test: ...

        @overload
        def create_or_update_test_profile(
                self, 
                test_profile_id: str, 
                body: TestProfile, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestProfile: ...

        @overload
        def create_or_update_test_profile(
                self, 
                test_profile_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestProfile: ...

        @overload
        def create_or_update_test_profile(
                self, 
                test_profile_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestProfile: ...

        @overload
        def create_or_update_trigger(
                self, 
                trigger_id: str, 
                body: Trigger, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Trigger: ...

        @overload
        def create_or_update_trigger(
                self, 
                trigger_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Trigger: ...

        @overload
        def create_or_update_trigger(
                self, 
                trigger_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Trigger: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'notification_rule_id']}, api_versions_list=['2024-12-01-preview', '2025-03-01-preview', '2025-11-01-preview'])
        def delete_notification_rule(
                self, 
                notification_rule_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_test(
                self, 
                test_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_test_file(
                self, 
                test_id: str, 
                file_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'test_profile_id']}, api_versions_list=['2024-05-01-preview', '2024-07-01-preview', '2024-12-01-preview', '2025-03-01-preview', '2025-11-01-preview'])
        def delete_test_profile(
                self, 
                test_profile_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_trigger(
                self, 
                trigger_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_app_components(
                self, 
                test_id: str, 
                **kwargs: Any
            ) -> TestAppComponents: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'notification_rule_id', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-03-01-preview', '2025-11-01-preview'])
        def get_notification_rule(
                self, 
                notification_rule_id: str, 
                **kwargs: Any
            ) -> NotificationRule: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-03-01-preview', params_added_on={'2025-03-01-preview': ['api_version', 'operation_id', 'accept']}, api_versions_list=['2025-03-01-preview', '2025-11-01-preview'])
        def get_operation_status(
                self, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...

        @distributed_trace
        def get_server_metrics_config(
                self, 
                test_id: str, 
                **kwargs: Any
            ) -> TestServerMetricsConfiguration: ...

        @distributed_trace
        def get_test(
                self, 
                test_id: str, 
                **kwargs: Any
            ) -> Test: ...

        @distributed_trace
        def get_test_file(
                self, 
                test_id: str, 
                file_name: str, 
                **kwargs: Any
            ) -> TestFileInfo: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'test_profile_id', 'accept']}, api_versions_list=['2024-05-01-preview', '2024-07-01-preview', '2024-12-01-preview', '2025-03-01-preview', '2025-11-01-preview'])
        def get_test_profile(
                self, 
                test_profile_id: str, 
                **kwargs: Any
            ) -> TestProfile: ...

        @distributed_trace
        def get_trigger(
                self, 
                trigger_id: str, 
                **kwargs: Any
            ) -> Trigger: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'test_ids', 'scopes', 'last_modified_start_time', 'last_modified_end_time', 'maxpagesize', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-03-01-preview', '2025-11-01-preview'])
        def list_notification_rules(
                self, 
                *, 
                last_modified_end_time: Optional[datetime] = ..., 
                last_modified_start_time: Optional[datetime] = ..., 
                scopes: Optional[str] = ..., 
                test_ids: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[NotificationRule]: ...

        @distributed_trace
        def list_test_files(
                self, 
                test_id: str, 
                **kwargs: Any
            ) -> ItemPaged[TestFileInfo]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'maxpagesize', 'last_modified_start_time', 'last_modified_end_time', 'test_profile_ids', 'test_ids', 'accept']}, api_versions_list=['2024-05-01-preview', '2024-07-01-preview', '2024-12-01-preview', '2025-03-01-preview', '2025-11-01-preview'])
        def list_test_profiles(
                self, 
                *, 
                last_modified_end_time: Optional[datetime] = ..., 
                last_modified_start_time: Optional[datetime] = ..., 
                test_ids: Optional[list[str]] = ..., 
                test_profile_ids: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[TestProfile]: ...

        @distributed_trace
        def list_tests(
                self, 
                *, 
                last_modified_end_time: Optional[datetime] = ..., 
                last_modified_start_time: Optional[datetime] = ..., 
                orderby: Optional[str] = ..., 
                search: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Test]: ...

        @distributed_trace
        def list_triggers(
                self, 
                *, 
                last_modified_end_time: Optional[datetime] = ..., 
                last_modified_start_time: Optional[datetime] = ..., 
                states: Optional[Union[str, TriggerState]] = ..., 
                test_ids: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Trigger]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


    class azure.developer.loadtesting.LoadTestRunClient(LoadTestRunClientOperationsMixin): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: TokenCredential, 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-03-01-preview', params_added_on={'2025-03-01-preview': ['api_version', 'test_run_id', 'accept']}, api_versions_list=['2025-03-01-preview', '2025-11-01-preview'])
        def begin_generate_test_run_insights(
                self, 
                test_run_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_test_profile_run(
                self, 
                test_profile_run_id: str, 
                body: TestProfileRun, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> LROPoller[TestProfileRun]: ...

        @overload
        def begin_test_profile_run(
                self, 
                test_profile_run_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> LROPoller[TestProfileRun]: ...

        @overload
        def begin_test_profile_run(
                self, 
                test_profile_run_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> LROPoller[TestProfileRun]: ...

        @overload
        def begin_test_run(
                self, 
                test_run_id: str, 
                body: TestRun, 
                *, 
                content_type: str = "application/merge-patch+json", 
                old_test_run_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[TestRun]: ...

        @overload
        def begin_test_run(
                self, 
                test_run_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                old_test_run_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[TestRun]: ...

        @overload
        def begin_test_run(
                self, 
                test_run_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                old_test_run_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[TestRun]: ...

        def close(self) -> None: ...

        @overload
        def create_or_update_app_components(
                self, 
                test_run_id: str, 
                body: TestRunAppComponents, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestRunAppComponents: ...

        @overload
        def create_or_update_app_components(
                self, 
                test_run_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestRunAppComponents: ...

        @overload
        def create_or_update_app_components(
                self, 
                test_run_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestRunAppComponents: ...

        @overload
        def create_or_update_server_metrics_config(
                self, 
                test_run_id: str, 
                body: TestRunServerMetricsConfiguration, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestRunServerMetricsConfiguration: ...

        @overload
        def create_or_update_server_metrics_config(
                self, 
                test_run_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestRunServerMetricsConfiguration: ...

        @overload
        def create_or_update_server_metrics_config(
                self, 
                test_run_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestRunServerMetricsConfiguration: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'test_profile_run_id']}, api_versions_list=['2024-05-01-preview', '2024-07-01-preview', '2024-12-01-preview', '2025-03-01-preview', '2025-11-01-preview'])
        def delete_test_profile_run(
                self, 
                test_profile_run_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_test_run(
                self, 
                test_run_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_app_components(
                self, 
                test_run_id: str, 
                **kwargs: Any
            ) -> TestRunAppComponents: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-03-01-preview', params_added_on={'2025-03-01-preview': ['api_version', 'test_run_id', 'accept']}, api_versions_list=['2025-03-01-preview', '2025-11-01-preview'])
        def get_latest_test_run_insights(
                self, 
                test_run_id: str, 
                **kwargs: Any
            ) -> TestRunInsights: ...

        @distributed_trace
        def get_metric_definitions(
                self, 
                test_run_id: str, 
                *, 
                metric_namespace: str, 
                **kwargs: Any
            ) -> MetricDefinitionCollection: ...

        @distributed_trace
        def get_metric_namespaces(
                self, 
                test_run_id: str, 
                **kwargs: Any
            ) -> MetricNamespaceCollection: ...

        @distributed_trace
        def get_server_metrics_config(
                self, 
                test_run_id: str, 
                **kwargs: Any
            ) -> TestRunServerMetricsConfiguration: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'test_profile_run_id', 'accept']}, api_versions_list=['2024-05-01-preview', '2024-07-01-preview', '2024-12-01-preview', '2025-03-01-preview', '2025-11-01-preview'])
        def get_test_profile_run(
                self, 
                test_profile_run_id: str, 
                **kwargs: Any
            ) -> TestProfileRun: ...

        @distributed_trace
        def get_test_run(
                self, 
                test_run_id: str, 
                **kwargs: Any
            ) -> TestRun: ...

        @distributed_trace
        def get_test_run_file(
                self, 
                test_run_id: str, 
                file_name: str, 
                **kwargs: Any
            ) -> TestRunFileInfo: ...

        @distributed_trace
        def list_metric_dimension_values(
                self, 
                test_run_id: str, 
                name: str, 
                *, 
                interval: Optional[Union[str, TimeGrain]] = ..., 
                metric_name: str, 
                metric_namespace: str, 
                time_interval: str, 
                **kwargs: Any
            ) -> ItemPaged[str]: ...

        @overload
        def list_metrics(
                self, 
                test_run_id: str, 
                body: Optional[MetricRequestPayload] = None, 
                *, 
                aggregation: Optional[str] = ..., 
                content_type: str = "application/json", 
                interval: Optional[Union[str, TimeGrain]] = ..., 
                metric_name: str, 
                metric_namespace: str, 
                time_interval: str, 
                **kwargs: Any
            ) -> ItemPaged[TimeSeriesElement]: ...

        @overload
        def list_metrics(
                self, 
                test_run_id: str, 
                body: Optional[JSON] = None, 
                *, 
                aggregation: Optional[str] = ..., 
                content_type: str = "application/json", 
                interval: Optional[Union[str, TimeGrain]] = ..., 
                metric_name: str, 
                metric_namespace: str, 
                time_interval: str, 
                **kwargs: Any
            ) -> ItemPaged[TimeSeriesElement]: ...

        @overload
        def list_metrics(
                self, 
                test_run_id: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                aggregation: Optional[str] = ..., 
                content_type: str = "application/json", 
                interval: Optional[Union[str, TimeGrain]] = ..., 
                metric_name: str, 
                metric_namespace: str, 
                time_interval: str, 
                **kwargs: Any
            ) -> ItemPaged[TimeSeriesElement]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'maxpagesize', 'min_start_date_time', 'max_start_date_time', 'min_end_date_time', 'max_end_date_time', 'created_date_start_time', 'created_date_end_time', 'test_profile_run_ids', 'test_profile_ids', 'statuses', 'accept']}, api_versions_list=['2024-05-01-preview', '2024-07-01-preview', '2024-12-01-preview', '2025-03-01-preview', '2025-11-01-preview'])
        def list_test_profile_runs(
                self, 
                *, 
                created_date_end_time: Optional[datetime] = ..., 
                created_date_start_time: Optional[datetime] = ..., 
                max_end_date_time: Optional[datetime] = ..., 
                max_start_date_time: Optional[datetime] = ..., 
                min_end_date_time: Optional[datetime] = ..., 
                min_start_date_time: Optional[datetime] = ..., 
                statuses: Optional[list[str]] = ..., 
                test_profile_ids: Optional[list[str]] = ..., 
                test_profile_run_ids: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[TestProfileRun]: ...

        @distributed_trace
        @api_version_validation(params_added_on={'2024-07-01-preview': ['created_by_types'], '2025-03-01-preview': ['test_ids']}, api_versions_list=['2022-11-01', '2023-04-01-preview', '2024-03-01-preview', '2024-05-01-preview', '2024-07-01-preview', '2024-12-01-preview', '2025-03-01-preview', '2025-11-01-preview'])
        def list_test_runs(
                self, 
                *, 
                created_by_types: Optional[list[str]] = ..., 
                execution_from: Optional[datetime] = ..., 
                execution_to: Optional[datetime] = ..., 
                orderby: Optional[str] = ..., 
                search: Optional[str] = ..., 
                status: Optional[str] = ..., 
                test_id: Optional[str] = ..., 
                test_ids: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[TestRun]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'test_profile_run_id', 'accept']}, api_versions_list=['2024-05-01-preview', '2024-07-01-preview', '2024-12-01-preview', '2025-03-01-preview', '2025-11-01-preview'])
        def stop_test_profile_run(
                self, 
                test_profile_run_id: str, 
                **kwargs: Any
            ) -> TestProfileRun: ...

        @distributed_trace
        def stop_test_run(
                self, 
                test_run_id: str, 
                **kwargs: Any
            ) -> TestRun: ...

        @overload
        def update_latest_test_run_insights(
                self, 
                test_run_id: str, 
                body: TestRunInsights, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestRunInsights: ...

        @overload
        def update_latest_test_run_insights(
                self, 
                test_run_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestRunInsights: ...

        @overload
        def update_latest_test_run_insights(
                self, 
                test_run_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestRunInsights: ...


namespace azure.developer.loadtesting.aio

    class azure.developer.loadtesting.aio.LoadTestAdministrationClient(LoadTestAdministrationClientOperationsMixin): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def begin_clone_test(
                self, 
                test_id: str, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                new_test_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Test]: ...

        @overload
        async def begin_clone_test(
                self, 
                test_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Test]: ...

        @overload
        async def begin_clone_test(
                self, 
                test_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Test]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-11-01-preview', params_added_on={'2025-11-01-preview': ['api_version', 'test_id', 'accept']}, api_versions_list=['2025-11-01-preview'])
        async def begin_generate_test_plan_recommendations(
                self, 
                test_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Test]: ...

        @overload
        async def begin_upload_test_file(
                self, 
                test_id: str, 
                file_name: str, 
                body: IO, 
                *, 
                file_type: Optional[Union[str, FileType]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[TestFileInfo]: ...

        @overload
        async def begin_upload_test_file(
                self, 
                test_id: str, 
                file_name: str, 
                body: bytes, 
                *, 
                file_type: Optional[Union[str, FileType]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[TestFileInfo]: ...

        async def close(self) -> None: ...

        @overload
        async def create_or_update_app_components(
                self, 
                test_id: str, 
                body: TestAppComponents, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestAppComponents: ...

        @overload
        async def create_or_update_app_components(
                self, 
                test_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestAppComponents: ...

        @overload
        async def create_or_update_app_components(
                self, 
                test_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestAppComponents: ...

        @overload
        async def create_or_update_notification_rule(
                self, 
                notification_rule_id: str, 
                body: NotificationRule, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> NotificationRule: ...

        @overload
        async def create_or_update_notification_rule(
                self, 
                notification_rule_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> NotificationRule: ...

        @overload
        async def create_or_update_notification_rule(
                self, 
                notification_rule_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> NotificationRule: ...

        @overload
        async def create_or_update_server_metrics_config(
                self, 
                test_id: str, 
                body: TestServerMetricsConfiguration, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestServerMetricsConfiguration: ...

        @overload
        async def create_or_update_server_metrics_config(
                self, 
                test_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestServerMetricsConfiguration: ...

        @overload
        async def create_or_update_server_metrics_config(
                self, 
                test_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestServerMetricsConfiguration: ...

        @overload
        async def create_or_update_test(
                self, 
                test_id: str, 
                body: Test, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Test: ...

        @overload
        async def create_or_update_test(
                self, 
                test_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Test: ...

        @overload
        async def create_or_update_test(
                self, 
                test_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Test: ...

        @overload
        async def create_or_update_test_profile(
                self, 
                test_profile_id: str, 
                body: TestProfile, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestProfile: ...

        @overload
        async def create_or_update_test_profile(
                self, 
                test_profile_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestProfile: ...

        @overload
        async def create_or_update_test_profile(
                self, 
                test_profile_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestProfile: ...

        @overload
        async def create_or_update_trigger(
                self, 
                trigger_id: str, 
                body: Trigger, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Trigger: ...

        @overload
        async def create_or_update_trigger(
                self, 
                trigger_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Trigger: ...

        @overload
        async def create_or_update_trigger(
                self, 
                trigger_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Trigger: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'notification_rule_id']}, api_versions_list=['2024-12-01-preview', '2025-03-01-preview', '2025-11-01-preview'])
        async def delete_notification_rule(
                self, 
                notification_rule_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_test(
                self, 
                test_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_test_file(
                self, 
                test_id: str, 
                file_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'test_profile_id']}, api_versions_list=['2024-05-01-preview', '2024-07-01-preview', '2024-12-01-preview', '2025-03-01-preview', '2025-11-01-preview'])
        async def delete_test_profile(
                self, 
                test_profile_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_trigger(
                self, 
                trigger_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_app_components(
                self, 
                test_id: str, 
                **kwargs: Any
            ) -> TestAppComponents: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'notification_rule_id', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-03-01-preview', '2025-11-01-preview'])
        async def get_notification_rule(
                self, 
                notification_rule_id: str, 
                **kwargs: Any
            ) -> NotificationRule: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-03-01-preview', params_added_on={'2025-03-01-preview': ['api_version', 'operation_id', 'accept']}, api_versions_list=['2025-03-01-preview', '2025-11-01-preview'])
        async def get_operation_status(
                self, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...

        @distributed_trace_async
        async def get_server_metrics_config(
                self, 
                test_id: str, 
                **kwargs: Any
            ) -> TestServerMetricsConfiguration: ...

        @distributed_trace_async
        async def get_test(
                self, 
                test_id: str, 
                **kwargs: Any
            ) -> Test: ...

        @distributed_trace_async
        async def get_test_file(
                self, 
                test_id: str, 
                file_name: str, 
                **kwargs: Any
            ) -> TestFileInfo: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'test_profile_id', 'accept']}, api_versions_list=['2024-05-01-preview', '2024-07-01-preview', '2024-12-01-preview', '2025-03-01-preview', '2025-11-01-preview'])
        async def get_test_profile(
                self, 
                test_profile_id: str, 
                **kwargs: Any
            ) -> TestProfile: ...

        @distributed_trace_async
        async def get_trigger(
                self, 
                trigger_id: str, 
                **kwargs: Any
            ) -> Trigger: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'test_ids', 'scopes', 'last_modified_start_time', 'last_modified_end_time', 'maxpagesize', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-03-01-preview', '2025-11-01-preview'])
        def list_notification_rules(
                self, 
                *, 
                last_modified_end_time: Optional[datetime] = ..., 
                last_modified_start_time: Optional[datetime] = ..., 
                scopes: Optional[str] = ..., 
                test_ids: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[NotificationRule]: ...

        @distributed_trace
        def list_test_files(
                self, 
                test_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TestFileInfo]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'maxpagesize', 'last_modified_start_time', 'last_modified_end_time', 'test_profile_ids', 'test_ids', 'accept']}, api_versions_list=['2024-05-01-preview', '2024-07-01-preview', '2024-12-01-preview', '2025-03-01-preview', '2025-11-01-preview'])
        def list_test_profiles(
                self, 
                *, 
                last_modified_end_time: Optional[datetime] = ..., 
                last_modified_start_time: Optional[datetime] = ..., 
                test_ids: Optional[list[str]] = ..., 
                test_profile_ids: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[TestProfile]: ...

        @distributed_trace
        def list_tests(
                self, 
                *, 
                last_modified_end_time: Optional[datetime] = ..., 
                last_modified_start_time: Optional[datetime] = ..., 
                orderby: Optional[str] = ..., 
                search: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Test]: ...

        @distributed_trace
        def list_triggers(
                self, 
                *, 
                last_modified_end_time: Optional[datetime] = ..., 
                last_modified_start_time: Optional[datetime] = ..., 
                states: Optional[Union[str, TriggerState]] = ..., 
                test_ids: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Trigger]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


    class azure.developer.loadtesting.aio.LoadTestRunClient(LoadTestRunClientOperationsMixin): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-03-01-preview', params_added_on={'2025-03-01-preview': ['api_version', 'test_run_id', 'accept']}, api_versions_list=['2025-03-01-preview', '2025-11-01-preview'])
        async def begin_generate_test_run_insights(
                self, 
                test_run_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_test_profile_run(
                self, 
                test_profile_run_id: str, 
                body: TestProfileRun, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TestProfileRun]: ...

        @overload
        async def begin_test_profile_run(
                self, 
                test_profile_run_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TestProfileRun]: ...

        @overload
        async def begin_test_profile_run(
                self, 
                test_profile_run_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TestProfileRun]: ...

        @overload
        async def begin_test_run(
                self, 
                test_run_id: str, 
                body: TestRun, 
                *, 
                content_type: str = "application/merge-patch+json", 
                old_test_run_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[TestRun]: ...

        @overload
        async def begin_test_run(
                self, 
                test_run_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                old_test_run_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[TestRun]: ...

        @overload
        async def begin_test_run(
                self, 
                test_run_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                old_test_run_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[TestRun]: ...

        async def close(self) -> None: ...

        @overload
        async def create_or_update_app_components(
                self, 
                test_run_id: str, 
                body: TestRunAppComponents, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestRunAppComponents: ...

        @overload
        async def create_or_update_app_components(
                self, 
                test_run_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestRunAppComponents: ...

        @overload
        async def create_or_update_app_components(
                self, 
                test_run_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestRunAppComponents: ...

        @overload
        async def create_or_update_server_metrics_config(
                self, 
                test_run_id: str, 
                body: TestRunServerMetricsConfiguration, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestRunServerMetricsConfiguration: ...

        @overload
        async def create_or_update_server_metrics_config(
                self, 
                test_run_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestRunServerMetricsConfiguration: ...

        @overload
        async def create_or_update_server_metrics_config(
                self, 
                test_run_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestRunServerMetricsConfiguration: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'test_profile_run_id']}, api_versions_list=['2024-05-01-preview', '2024-07-01-preview', '2024-12-01-preview', '2025-03-01-preview', '2025-11-01-preview'])
        async def delete_test_profile_run(
                self, 
                test_profile_run_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_test_run(
                self, 
                test_run_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_app_components(
                self, 
                test_run_id: str, 
                **kwargs: Any
            ) -> TestRunAppComponents: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-03-01-preview', params_added_on={'2025-03-01-preview': ['api_version', 'test_run_id', 'accept']}, api_versions_list=['2025-03-01-preview', '2025-11-01-preview'])
        async def get_latest_test_run_insights(
                self, 
                test_run_id: str, 
                **kwargs: Any
            ) -> TestRunInsights: ...

        @distributed_trace_async
        async def get_metric_definitions(
                self, 
                test_run_id: str, 
                *, 
                metric_namespace: str, 
                **kwargs: Any
            ) -> MetricDefinitionCollection: ...

        @distributed_trace_async
        async def get_metric_namespaces(
                self, 
                test_run_id: str, 
                **kwargs: Any
            ) -> MetricNamespaceCollection: ...

        @distributed_trace_async
        async def get_server_metrics_config(
                self, 
                test_run_id: str, 
                **kwargs: Any
            ) -> TestRunServerMetricsConfiguration: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'test_profile_run_id', 'accept']}, api_versions_list=['2024-05-01-preview', '2024-07-01-preview', '2024-12-01-preview', '2025-03-01-preview', '2025-11-01-preview'])
        async def get_test_profile_run(
                self, 
                test_profile_run_id: str, 
                **kwargs: Any
            ) -> TestProfileRun: ...

        @distributed_trace_async
        async def get_test_run(
                self, 
                test_run_id: str, 
                **kwargs: Any
            ) -> TestRun: ...

        @distributed_trace_async
        async def get_test_run_file(
                self, 
                test_run_id: str, 
                file_name: str, 
                **kwargs: Any
            ) -> TestRunFileInfo: ...

        @distributed_trace
        def list_metric_dimension_values(
                self, 
                test_run_id: str, 
                name: str, 
                *, 
                interval: Optional[Union[str, TimeGrain]] = ..., 
                metric_name: str, 
                metric_namespace: str, 
                time_interval: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[str]: ...

        @overload
        def list_metrics(
                self, 
                test_run_id: str, 
                body: Optional[MetricRequestPayload] = None, 
                *, 
                aggregation: Optional[str] = ..., 
                content_type: str = "application/json", 
                interval: Optional[Union[str, TimeGrain]] = ..., 
                metric_name: str, 
                metric_namespace: str, 
                time_interval: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TimeSeriesElement]: ...

        @overload
        def list_metrics(
                self, 
                test_run_id: str, 
                body: Optional[JSON] = None, 
                *, 
                aggregation: Optional[str] = ..., 
                content_type: str = "application/json", 
                interval: Optional[Union[str, TimeGrain]] = ..., 
                metric_name: str, 
                metric_namespace: str, 
                time_interval: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TimeSeriesElement]: ...

        @overload
        def list_metrics(
                self, 
                test_run_id: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                aggregation: Optional[str] = ..., 
                content_type: str = "application/json", 
                interval: Optional[Union[str, TimeGrain]] = ..., 
                metric_name: str, 
                metric_namespace: str, 
                time_interval: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TimeSeriesElement]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'maxpagesize', 'min_start_date_time', 'max_start_date_time', 'min_end_date_time', 'max_end_date_time', 'created_date_start_time', 'created_date_end_time', 'test_profile_run_ids', 'test_profile_ids', 'statuses', 'accept']}, api_versions_list=['2024-05-01-preview', '2024-07-01-preview', '2024-12-01-preview', '2025-03-01-preview', '2025-11-01-preview'])
        def list_test_profile_runs(
                self, 
                *, 
                created_date_end_time: Optional[datetime] = ..., 
                created_date_start_time: Optional[datetime] = ..., 
                max_end_date_time: Optional[datetime] = ..., 
                max_start_date_time: Optional[datetime] = ..., 
                min_end_date_time: Optional[datetime] = ..., 
                min_start_date_time: Optional[datetime] = ..., 
                statuses: Optional[list[str]] = ..., 
                test_profile_ids: Optional[list[str]] = ..., 
                test_profile_run_ids: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[TestProfileRun]: ...

        @distributed_trace
        @api_version_validation(params_added_on={'2024-07-01-preview': ['created_by_types'], '2025-03-01-preview': ['test_ids']}, api_versions_list=['2022-11-01', '2023-04-01-preview', '2024-03-01-preview', '2024-05-01-preview', '2024-07-01-preview', '2024-12-01-preview', '2025-03-01-preview', '2025-11-01-preview'])
        def list_test_runs(
                self, 
                *, 
                created_by_types: Optional[list[str]] = ..., 
                execution_from: Optional[datetime] = ..., 
                execution_to: Optional[datetime] = ..., 
                orderby: Optional[str] = ..., 
                search: Optional[str] = ..., 
                status: Optional[str] = ..., 
                test_id: Optional[str] = ..., 
                test_ids: Optional[list[str]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[TestRun]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-05-01-preview', params_added_on={'2024-05-01-preview': ['api_version', 'test_profile_run_id', 'accept']}, api_versions_list=['2024-05-01-preview', '2024-07-01-preview', '2024-12-01-preview', '2025-03-01-preview', '2025-11-01-preview'])
        async def stop_test_profile_run(
                self, 
                test_profile_run_id: str, 
                **kwargs: Any
            ) -> TestProfileRun: ...

        @distributed_trace_async
        async def stop_test_run(
                self, 
                test_run_id: str, 
                **kwargs: Any
            ) -> TestRun: ...

        @overload
        async def update_latest_test_run_insights(
                self, 
                test_run_id: str, 
                body: TestRunInsights, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestRunInsights: ...

        @overload
        async def update_latest_test_run_insights(
                self, 
                test_run_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestRunInsights: ...

        @overload
        async def update_latest_test_run_insights(
                self, 
                test_run_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TestRunInsights: ...


namespace azure.developer.loadtesting.models

    class azure.developer.loadtesting.models.Aggregation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "Average"
        COUNT = "Count"
        NONE = "None"
        PERCENTILE75 = "Percentile75"
        PERCENTILE90 = "Percentile90"
        PERCENTILE95 = "Percentile95"
        PERCENTILE96 = "Percentile96"
        PERCENTILE97 = "Percentile97"
        PERCENTILE98 = "Percentile98"
        PERCENTILE99 = "Percentile99"
        PERCENTILE999 = "Percentile999"
        PERCENTILE9999 = "Percentile9999"
        TOTAL = "Total"


    class azure.developer.loadtesting.models.AppComponent(_Model):
        display_name: Optional[str]
        kind: Optional[str]
        resource_group: Optional[str]
        resource_id: str
        resource_name: str
        resource_type: str
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                resource_name: str, 
                resource_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.ArtifactsContainerInfo(_Model):
        expire_date_time: Optional[datetime]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                expire_date_time: Optional[datetime] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.AutoStopCriteria(_Model):
        auto_stop_disabled: Optional[bool]
        error_rate: Optional[float]
        error_rate_time_window_in_seconds: Optional[int]
        maximum_virtual_users_per_engine: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                auto_stop_disabled: Optional[bool] = ..., 
                error_rate: Optional[float] = ..., 
                error_rate_time_window_in_seconds: Optional[int] = ..., 
                maximum_virtual_users_per_engine: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.CertificateMetadata(_Model):
        name: Optional[str]
        type: Optional[Union[str, CertificateType]]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[Union[str, CertificateType]] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.CertificateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KEY_VAULT_CERTIFICATE_URI = "AKV_CERT_URI"


    class azure.developer.loadtesting.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_PIPELINES = "AzurePipelines"
        GITHUB_WORKFLOWS = "GitHubWorkflows"
        SCHEDULED_TRIGGER = "ScheduledTrigger"
        USER = "User"


    class azure.developer.loadtesting.models.DailyRecurrence(Recurrence, discriminator='Daily'):
        frequency: Literal[Frequency.DAILY]
        interval: int
        recurrence_end: RecurrenceEnd

        @overload
        def __init__(
                self, 
                *, 
                interval: int, 
                recurrence_end: Optional[RecurrenceEnd] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.DimensionFilter(_Model):
        name: Optional[str]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.DimensionValue(_Model):
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


    class azure.developer.loadtesting.models.ErrorDetails(_Model):
        code: Optional[str]
        message: Optional[str]
        properties: Optional[dict[str, list[str]]]


    class azure.developer.loadtesting.models.FileType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDITIONAL_ARTIFACTS = "ADDITIONAL_ARTIFACTS"
        BROWSER_RECORDING = "BROWSER_RECORDING"
        JMX_FILE = "JMX_FILE"
        TEST_PLAN_RECOMMENDATIONS = "TEST_PLAN_RECOMMENDATIONS"
        TEST_SCRIPT = "TEST_SCRIPT"
        URL_TEST_CONFIG = "URL_TEST_CONFIG"
        USER_PROPERTIES = "USER_PROPERTIES"
        ZIPPED_ARTIFACTS = "ZIPPED_ARTIFACTS"


    class azure.developer.loadtesting.models.FileValidationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_VALIDATED = "NOT_VALIDATED"
        VALIDATION_FAILURE = "VALIDATION_FAILURE"
        VALIDATION_INITIATED = "VALIDATION_INITIATED"
        VALIDATION_NOT_REQUIRED = "VALIDATION_NOT_REQUIRED"
        VALIDATION_SUCCESS = "VALIDATION_SUCCESS"


    class azure.developer.loadtesting.models.Frequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRON = "Cron"
        DAILY = "Daily"
        HOURLY = "Hourly"
        MONTHLY_BY_DATES = "MonthlyByDates"
        MONTHLY_BY_DAYS = "MonthlyByDays"
        WEEKLY = "Weekly"


    class azure.developer.loadtesting.models.FunctionFlexConsumptionResourceConfiguration(_Model):
        http_concurrency: Optional[int]
        instance_memory_mb: int

        @overload
        def __init__(
                self, 
                *, 
                http_concurrency: Optional[int] = ..., 
                instance_memory_mb: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.FunctionFlexConsumptionTargetResourceConfigurations(TargetResourceConfigurations, discriminator='FunctionsFlexConsumption'):
        configurations: Optional[dict[str, FunctionFlexConsumptionResourceConfiguration]]
        kind: Literal[ResourceKind.FUNCTIONS_FLEX_CONSUMPTION]

        @overload
        def __init__(
                self, 
                *, 
                configurations: Optional[dict[str, FunctionFlexConsumptionResourceConfiguration]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.HourlyRecurrence(Recurrence, discriminator='Hourly'):
        frequency: Literal[Frequency.HOURLY]
        interval: int
        recurrence_end: RecurrenceEnd

        @overload
        def __init__(
                self, 
                *, 
                interval: int, 
                recurrence_end: Optional[RecurrenceEnd] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.LoadTestConfiguration(_Model):
        engine_instances: Optional[int]
        optional_load_test_config: Optional[OptionalLoadTestConfiguration]
        quick_start_test: Optional[bool]
        regional_load_test_config: Optional[list[RegionalConfiguration]]
        split_all_csvs: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                engine_instances: Optional[int] = ..., 
                optional_load_test_config: Optional[OptionalLoadTestConfiguration] = ..., 
                quick_start_test: Optional[bool] = ..., 
                regional_load_test_config: Optional[list[RegionalConfiguration]] = ..., 
                split_all_csvs: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.ManagedIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.developer.loadtesting.models.MetricAvailability(_Model):
        time_grain: Optional[Union[str, TimeGrain]]

        @overload
        def __init__(
                self, 
                *, 
                time_grain: Optional[Union[str, TimeGrain]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.MetricDefinition(_Model):
        description: Optional[str]
        dimensions: Optional[list[NameAndDescription]]
        metric_availabilities: Optional[list[MetricAvailability]]
        name: Optional[str]
        namespace: Optional[str]
        primary_aggregation_type: Optional[Union[str, Aggregation]]
        supported_aggregation_types: Optional[list[str]]
        unit: Optional[Union[str, MetricUnit]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                dimensions: Optional[list[NameAndDescription]] = ..., 
                metric_availabilities: Optional[list[MetricAvailability]] = ..., 
                name: Optional[str] = ..., 
                namespace: Optional[str] = ..., 
                primary_aggregation_type: Optional[Union[str, Aggregation]] = ..., 
                supported_aggregation_types: Optional[list[str]] = ..., 
                unit: Optional[Union[str, MetricUnit]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.MetricDefinitionCollection(_Model):
        value: list[MetricDefinition]

        @overload
        def __init__(
                self, 
                *, 
                value: list[MetricDefinition]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.MetricNamespace(_Model):
        description: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.MetricNamespaceCollection(_Model):
        value: list[MetricNamespace]

        @overload
        def __init__(
                self, 
                *, 
                value: list[MetricNamespace]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.MetricRequestPayload(_Model):
        filters: Optional[list[DimensionFilter]]

        @overload
        def __init__(
                self, 
                *, 
                filters: Optional[list[DimensionFilter]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.MetricUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BYTES = "Bytes"
        BYTES_PER_SECOND = "BytesPerSecond"
        COUNT = "Count"
        COUNT_PER_SECOND = "CountPerSecond"
        MILLISECONDS = "Milliseconds"
        NOT_SPECIFIED = "NotSpecified"
        PERCENT = "Percent"
        SECONDS = "Seconds"


    class azure.developer.loadtesting.models.MetricValue(_Model):
        timestamp: Optional[datetime]
        value: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                timestamp: Optional[datetime] = ..., 
                value: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.MonthlyRecurrenceByDates(Recurrence, discriminator='MonthlyByDates'):
        dates_in_month: Optional[list[int]]
        frequency: Literal[Frequency.MONTHLY_BY_DATES]
        interval: Optional[int]
        recurrence_end: RecurrenceEnd

        @overload
        def __init__(
                self, 
                *, 
                dates_in_month: Optional[list[int]] = ..., 
                interval: Optional[int] = ..., 
                recurrence_end: Optional[RecurrenceEnd] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.MonthlyRecurrenceByWeekDays(Recurrence, discriminator='MonthlyByDays'):
        frequency: Literal[Frequency.MONTHLY_BY_DAYS]
        index: int
        interval: int
        recurrence_end: RecurrenceEnd
        week_days_in_month: Optional[list[Union[str, WeekDays]]]

        @overload
        def __init__(
                self, 
                *, 
                index: int, 
                interval: int, 
                recurrence_end: Optional[RecurrenceEnd] = ..., 
                week_days_in_month: Optional[list[Union[str, WeekDays]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.NameAndDescription(_Model):
        description: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.NotificationEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TEST_RUN_ENDED = "TestRunEnded"
        TEST_RUN_STARTED = "TestRunStarted"
        TRIGGER_COMPLETED = "TriggerCompleted"
        TRIGGER_DISABLED = "TriggerDisabled"


    class azure.developer.loadtesting.models.NotificationRule(_Model):
        action_group_ids: list[str]
        created_by: Optional[str]
        created_date_time: Optional[datetime]
        display_name: str
        last_modified_by: Optional[str]
        last_modified_date_time: Optional[datetime]
        notification_rule_id: str
        scope: str

        @overload
        def __init__(
                self, 
                *, 
                action_group_ids: list[str], 
                display_name: str, 
                scope: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.NotificationScopeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TESTS = "Tests"


    class azure.developer.loadtesting.models.OperationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLONE_TEST = "CloneTest"
        GENERATE_TEST_RUN_INSIGHTS = "GenerateTestRunInsights"
        TEST_PLAN_RECOMMENDATIONS = "TestPlanRecommendations"


    class azure.developer.loadtesting.models.OperationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        NOT_STARTED = "NotStarted"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.developer.loadtesting.models.OperationStatus(_Model):
        error: Optional[ODataV4Format]
        id: str
        kind: Union[str, OperationKind]
        status: Union[str, OperationState]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ODataV4Format] = ..., 
                kind: Union[str, OperationKind], 
                status: Union[str, OperationState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.OptionalLoadTestConfiguration(_Model):
        duration: Optional[int]
        endpoint_url: Optional[str]
        max_response_time_in_ms: Optional[int]
        ramp_up_time: Optional[int]
        requests_per_second: Optional[int]
        virtual_users: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                duration: Optional[int] = ..., 
                endpoint_url: Optional[str] = ..., 
                max_response_time_in_ms: Optional[int] = ..., 
                ramp_up_time: Optional[int] = ..., 
                requests_per_second: Optional[int] = ..., 
                virtual_users: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.PFMetrics(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "error"
        LATENCY = "latency"
        REQUESTS = "requests"
        REQUESTS_PER_SECOND = "requests_per_sec"
        RESPONSE_TIME_IN_MILLISECONDS = "response_time_ms"


    class azure.developer.loadtesting.models.PassFailAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTINUEEnum = "continue"
        STOP = "stop"


    class azure.developer.loadtesting.models.PassFailAggregationFunction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "avg"
        COUNT = "count"
        MAXIMUM = "max"
        MINIMUM = "min"
        PERCENTAGE = "percentage"
        PERCENTILE50 = "p50"
        PERCENTILE75 = "p75"
        PERCENTILE90 = "p90"
        PERCENTILE95 = "p95"
        PERCENTILE96 = "p96"
        PERCENTILE97 = "p97"
        PERCENTILE98 = "p98"
        PERCENTILE99 = "p99"
        PERCENTILE999 = "p99.9"
        PERCENTILE9999 = "p99.99"


    class azure.developer.loadtesting.models.PassFailCriteria(_Model):
        pass_fail_metrics: Optional[dict[str, PassFailMetric]]
        pass_fail_server_metrics: Optional[dict[str, PassFailServerMetric]]

        @overload
        def __init__(
                self, 
                *, 
                pass_fail_metrics: Optional[dict[str, PassFailMetric]] = ..., 
                pass_fail_server_metrics: Optional[dict[str, PassFailServerMetric]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.PassFailMetric(_Model):
        action: Optional[Union[str, PassFailAction]]
        actual_value: Optional[float]
        aggregate: Optional[Union[str, PassFailAggregationFunction]]
        client_metric: Optional[Union[str, PFMetrics]]
        condition: Optional[str]
        request_name: Optional[str]
        result: Optional[Union[str, PassFailResult]]
        value: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, PassFailAction]] = ..., 
                aggregate: Optional[Union[str, PassFailAggregationFunction]] = ..., 
                client_metric: Optional[Union[str, PFMetrics]] = ..., 
                condition: Optional[str] = ..., 
                request_name: Optional[str] = ..., 
                value: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.PassFailResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "failed"
        PASSED = "passed"
        UNDETERMINED = "undetermined"


    class azure.developer.loadtesting.models.PassFailServerMetric(_Model):
        action: Optional[Union[str, PassFailAction]]
        actual_value: Optional[float]
        aggregation: str
        condition: str
        metric_name: str
        metric_namespace: str
        resource_id: str
        result: Optional[Union[str, PassFailResult]]
        value: float

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, PassFailAction]] = ..., 
                aggregation: str, 
                condition: str, 
                metric_name: str, 
                metric_namespace: str, 
                resource_id: str, 
                value: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.PassFailTestResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "FAILED"
        NOT_APPLICABLE = "NOT_APPLICABLE"
        PASSED = "PASSED"


    class azure.developer.loadtesting.models.RecommendationCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COST_OPTIMIZED = "CostOptimized"
        THROUGHPUT_OPTIMIZED = "ThroughputOptimized"


    class azure.developer.loadtesting.models.Recurrence(_Model):
        frequency: str
        recurrence_end: Optional[RecurrenceEnd]

        @overload
        def __init__(
                self, 
                *, 
                frequency: str, 
                recurrence_end: Optional[RecurrenceEnd] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.RecurrenceEnd(_Model):
        end_date_time: Optional[datetime]
        number_of_occurrences: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                end_date_time: Optional[datetime] = ..., 
                number_of_occurrences: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.RecurrenceStatus(_Model):
        next_scheduled_date_times: Optional[list[datetime]]
        remaining_occurrences: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                next_scheduled_date_times: Optional[list[datetime]] = ..., 
                remaining_occurrences: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.RecurrenceWithCron(Recurrence, discriminator='Cron'):
        cron_expression: str
        frequency: Literal[Frequency.CRON]
        recurrence_end: RecurrenceEnd

        @overload
        def __init__(
                self, 
                *, 
                cron_expression: str, 
                recurrence_end: Optional[RecurrenceEnd] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.RegionalConfiguration(_Model):
        engine_instances: int
        region: str

        @overload
        def __init__(
                self, 
                *, 
                engine_instances: int, 
                region: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.RequestDataLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERRORS = "ERRORS"
        NONE = "NONE"


    class azure.developer.loadtesting.models.ResourceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FUNCTIONS_FLEX_CONSUMPTION = "FunctionsFlexConsumption"


    class azure.developer.loadtesting.models.ResourceMetric(_Model):
        aggregation: str
        display_description: Optional[str]
        id: Optional[str]
        metric_namespace: str
        name: str
        resource_id: str
        resource_type: str
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aggregation: str, 
                display_description: Optional[str] = ..., 
                metric_namespace: str, 
                name: str, 
                resource_id: str, 
                resource_type: str, 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.ScheduleTestsTrigger(Trigger, discriminator='ScheduleTestsTrigger'):
        created_by: str
        created_date_time: datetime
        description: str
        display_name: str
        kind: Literal[TriggerType.SCHEDULE_TESTS_TRIGGER]
        last_modified_by: str
        last_modified_date_time: datetime
        recurrence: Optional[Recurrence]
        recurrence_status: Optional[RecurrenceStatus]
        start_date_time: Optional[datetime]
        state: Union[str, TriggerState]
        state_details: StateDetails
        test_ids: list[str]
        trigger_id: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: str, 
                recurrence: Optional[Recurrence] = ..., 
                start_date_time: Optional[datetime] = ..., 
                state: Optional[Union[str, TriggerState]] = ..., 
                test_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.Secret(_Model):
        type: Optional[Union[str, SecretType]]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, SecretType]] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.SecretType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KEY_VAULT_SECRET_URI = "AKV_SECRET_URI"
        SECRET_VALUE = "SECRET_VALUE"


    class azure.developer.loadtesting.models.StateDetails(_Model):
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TargetResourceConfigurations(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.Test(_Model):
        auto_stop_criteria: Optional[AutoStopCriteria]
        baseline_test_run_id: Optional[str]
        certificate: Optional[CertificateMetadata]
        created_by: Optional[str]
        created_date_time: Optional[datetime]
        description: Optional[str]
        display_name: Optional[str]
        engine_built_in_identity_ids: Optional[list[str]]
        engine_built_in_identity_type: Optional[Union[str, ManagedIdentityType]]
        environment_variables: Optional[dict[str, str]]
        estimated_virtual_user_hours: Optional[float]
        input_artifacts: Optional[TestInputArtifacts]
        keyvault_reference_identity_id: Optional[str]
        keyvault_reference_identity_type: Optional[str]
        kind: Optional[Union[str, TestKind]]
        last_modified_by: Optional[str]
        last_modified_date_time: Optional[datetime]
        load_test_configuration: Optional[LoadTestConfiguration]
        metrics_reference_identity_id: Optional[str]
        metrics_reference_identity_type: Optional[Union[str, ManagedIdentityType]]
        pass_fail_criteria: Optional[PassFailCriteria]
        preferences: Optional[TestPreferences]
        public_ip_disabled: Optional[bool]
        secrets: Optional[dict[str, Secret]]
        subnet_id: Optional[str]
        test_id: str

        @overload
        def __init__(
                self, 
                *, 
                auto_stop_criteria: Optional[AutoStopCriteria] = ..., 
                baseline_test_run_id: Optional[str] = ..., 
                certificate: Optional[CertificateMetadata] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                engine_built_in_identity_ids: Optional[list[str]] = ..., 
                engine_built_in_identity_type: Optional[Union[str, ManagedIdentityType]] = ..., 
                environment_variables: Optional[dict[str, str]] = ..., 
                keyvault_reference_identity_id: Optional[str] = ..., 
                keyvault_reference_identity_type: Optional[str] = ..., 
                kind: Optional[Union[str, TestKind]] = ..., 
                load_test_configuration: Optional[LoadTestConfiguration] = ..., 
                metrics_reference_identity_id: Optional[str] = ..., 
                metrics_reference_identity_type: Optional[Union[str, ManagedIdentityType]] = ..., 
                pass_fail_criteria: Optional[PassFailCriteria] = ..., 
                preferences: Optional[TestPreferences] = ..., 
                public_ip_disabled: Optional[bool] = ..., 
                secrets: Optional[dict[str, Secret]] = ..., 
                subnet_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TestAppComponents(_Model):
        components: dict[str, AppComponent]
        created_by: Optional[str]
        created_date_time: Optional[datetime]
        last_modified_by: Optional[str]
        last_modified_date_time: Optional[datetime]
        test_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                components: dict[str, AppComponent]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TestFileInfo(_Model):
        expire_date_time: Optional[datetime]
        file_name: str
        file_type: Optional[Union[str, FileType]]
        url: Optional[str]
        validation_failure_details: Optional[str]
        validation_status: Optional[Union[str, FileValidationStatus]]

        @overload
        def __init__(
                self, 
                *, 
                file_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TestInputArtifacts(_Model):
        additional_file_info: Optional[list[TestFileInfo]]
        config_file_info: Optional[TestFileInfo]
        input_artifacts_zip_file_info: Optional[TestFileInfo]
        test_script_file_info: Optional[TestFileInfo]
        url_test_config_file_info: Optional[TestFileInfo]
        user_prop_file_info: Optional[TestFileInfo]

        @overload
        def __init__(
                self, 
                *, 
                config_file_info: Optional[TestFileInfo] = ..., 
                input_artifacts_zip_file_info: Optional[TestFileInfo] = ..., 
                test_script_file_info: Optional[TestFileInfo] = ..., 
                url_test_config_file_info: Optional[TestFileInfo] = ..., 
                user_prop_file_info: Optional[TestFileInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TestKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JMX = "JMX"
        LOCUST = "Locust"
        URL = "URL"


    class azure.developer.loadtesting.models.TestPreferences(_Model):
        enable_ai_error_insights: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enable_ai_error_insights: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TestProfile(_Model):
        created_by: Optional[str]
        created_date_time: Optional[datetime]
        description: Optional[str]
        display_name: Optional[str]
        last_modified_by: Optional[str]
        last_modified_date_time: Optional[datetime]
        target_resource_configurations: Optional[TargetResourceConfigurations]
        target_resource_id: Optional[str]
        test_id: Optional[str]
        test_profile_id: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                target_resource_configurations: Optional[TargetResourceConfigurations] = ..., 
                target_resource_id: Optional[str] = ..., 
                test_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TestProfileRun(_Model):
        created_by: Optional[str]
        created_date_time: Optional[datetime]
        description: Optional[str]
        display_name: Optional[str]
        duration_in_seconds: Optional[int]
        end_date_time: Optional[datetime]
        error_details: Optional[list[ErrorDetails]]
        last_modified_by: Optional[str]
        last_modified_date_time: Optional[datetime]
        recommendations: Optional[list[TestProfileRunRecommendation]]
        start_date_time: Optional[datetime]
        status: Optional[Union[str, TestProfileRunStatus]]
        target_resource_configurations: Optional[TargetResourceConfigurations]
        target_resource_id: Optional[str]
        test_profile_id: Optional[str]
        test_profile_run_id: str
        test_run_details: Optional[dict[str, TestRunDetail]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                test_profile_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TestProfileRunRecommendation(_Model):
        category: Union[str, RecommendationCategory]
        configurations: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                category: Union[str, RecommendationCategory], 
                configurations: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TestProfileRunStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "ACCEPTED"
        CANCELLED = "CANCELLED"
        CANCELLING = "CANCELLING"
        DONE = "DONE"
        EXECUTING = "EXECUTING"
        FAILED = "FAILED"
        NOT_STARTED = "NOTSTARTED"


    class azure.developer.loadtesting.models.TestRun(_Model):
        auto_stop_criteria: Optional[AutoStopCriteria]
        certificate: Optional[CertificateMetadata]
        created_by: Optional[str]
        created_by_type: Optional[Union[str, CreatedByType]]
        created_by_uri: Optional[str]
        created_date_time: Optional[datetime]
        debug_logs_enabled: Optional[bool]
        description: Optional[str]
        display_name: Optional[str]
        duration: Optional[int]
        end_date_time: Optional[datetime]
        environment_variables: Optional[dict[str, str]]
        error_details: Optional[list[ErrorDetails]]
        estimated_virtual_user_hours: Optional[float]
        executed_date_time: Optional[datetime]
        execution_end_date_time: Optional[datetime]
        execution_start_date_time: Optional[datetime]
        kind: Optional[Union[str, TestKind]]
        last_modified_by: Optional[str]
        last_modified_date_time: Optional[datetime]
        load_test_configuration: Optional[LoadTestConfiguration]
        pass_fail_criteria: Optional[PassFailCriteria]
        portal_url: Optional[str]
        public_ip_disabled: Optional[bool]
        regional_statistics: Optional[dict[str, TestRunStatistics]]
        request_data_level: Optional[Union[str, RequestDataLevel]]
        secrets: Optional[dict[str, Secret]]
        start_date_time: Optional[datetime]
        status: Optional[Union[str, TestRunStatus]]
        subnet_id: Optional[str]
        test_artifacts: Optional[TestRunArtifacts]
        test_id: Optional[str]
        test_result: Optional[Union[str, PassFailTestResult]]
        test_run_id: str
        test_run_statistics: Optional[dict[str, TestRunStatistics]]
        virtual_user_hours: Optional[float]
        virtual_users: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                auto_stop_criteria: Optional[AutoStopCriteria] = ..., 
                certificate: Optional[CertificateMetadata] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                debug_logs_enabled: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                environment_variables: Optional[dict[str, str]] = ..., 
                pass_fail_criteria: Optional[PassFailCriteria] = ..., 
                request_data_level: Optional[Union[str, RequestDataLevel]] = ..., 
                secrets: Optional[dict[str, Secret]] = ..., 
                test_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TestRunAppComponents(_Model):
        components: dict[str, AppComponent]
        created_by: Optional[str]
        created_date_time: Optional[datetime]
        last_modified_by: Optional[str]
        last_modified_date_time: Optional[datetime]
        test_run_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                components: dict[str, AppComponent]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TestRunArtifacts(_Model):
        input_artifacts: Optional[TestRunInputArtifacts]
        output_artifacts: Optional[TestRunOutputArtifacts]

        @overload
        def __init__(
                self, 
                *, 
                output_artifacts: Optional[TestRunOutputArtifacts] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TestRunDetail(_Model):
        configuration_id: str
        properties: dict[str, str]
        status: Union[str, TestRunStatus]

        @overload
        def __init__(
                self, 
                *, 
                configuration_id: str, 
                properties: dict[str, str], 
                status: Union[str, TestRunStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TestRunEndedEventCondition(_Model):
        test_run_results: Optional[list[Union[str, PassFailTestResult]]]
        test_run_statuses: Optional[list[Union[str, TestRunStatus]]]

        @overload
        def __init__(
                self, 
                *, 
                test_run_results: Optional[list[Union[str, PassFailTestResult]]] = ..., 
                test_run_statuses: Optional[list[Union[str, TestRunStatus]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TestRunEndedNotificationEventFilter(TestsNotificationEventFilter, discriminator='TestRunEnded'):
        condition: Optional[TestRunEndedEventCondition]
        kind: Literal[NotificationEventType.TEST_RUN_ENDED]

        @overload
        def __init__(
                self, 
                *, 
                condition: Optional[TestRunEndedEventCondition] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TestRunFileInfo(_Model):
        expire_date_time: Optional[datetime]
        file_name: str
        file_type: Optional[Union[str, FileType]]
        url: Optional[str]
        validation_failure_details: Optional[str]
        validation_status: Optional[Union[str, FileValidationStatus]]

        @overload
        def __init__(
                self, 
                *, 
                file_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TestRunInputArtifacts(_Model):
        additional_file_info: Optional[list[TestRunFileInfo]]
        config_file_info: Optional[TestRunFileInfo]
        input_artifacts_zip_file_info: Optional[TestRunFileInfo]
        test_script_file_info: Optional[TestRunFileInfo]
        url_test_config_file_info: Optional[TestRunFileInfo]
        user_prop_file_info: Optional[TestRunFileInfo]

        @overload
        def __init__(
                self, 
                *, 
                config_file_info: Optional[TestRunFileInfo] = ..., 
                input_artifacts_zip_file_info: Optional[TestRunFileInfo] = ..., 
                test_script_file_info: Optional[TestRunFileInfo] = ..., 
                url_test_config_file_info: Optional[TestRunFileInfo] = ..., 
                user_prop_file_info: Optional[TestRunFileInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TestRunInsightColumn(_Model):
        data_type: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                data_type: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TestRunInsights(_Model):
        columns: Optional[list[TestRunInsightColumn]]
        rows: Optional[dict[str, dict[str, str]]]
        status: Optional[Union[str, OperationState]]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                rows: Optional[dict[str, dict[str, str]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TestRunOutputArtifacts(_Model):
        artifacts_container_info: Optional[ArtifactsContainerInfo]
        logs_file_info: Optional[TestRunFileInfo]
        report_file_info: Optional[TestRunFileInfo]
        result_file_info: Optional[TestRunFileInfo]

        @overload
        def __init__(
                self, 
                *, 
                artifacts_container_info: Optional[ArtifactsContainerInfo] = ..., 
                logs_file_info: Optional[TestRunFileInfo] = ..., 
                report_file_info: Optional[TestRunFileInfo] = ..., 
                result_file_info: Optional[TestRunFileInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TestRunServerMetricsConfiguration(_Model):
        created_by: Optional[str]
        created_date_time: Optional[datetime]
        last_modified_by: Optional[str]
        last_modified_date_time: Optional[datetime]
        metrics: Optional[dict[str, ResourceMetric]]
        test_run_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                metrics: Optional[dict[str, ResourceMetric]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TestRunStartedNotificationEventFilter(TestsNotificationEventFilter, discriminator='TestRunStarted'):
        kind: Literal[NotificationEventType.TEST_RUN_STARTED]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TestRunStatistics(_Model):
        error_count: Optional[float]
        error_pct: Optional[float]
        max_res_time: Optional[float]
        mean_res_time: Optional[float]
        median_res_time: Optional[float]
        min_res_time: Optional[float]
        pct1_res_time: Optional[float]
        pct2_res_time: Optional[float]
        pct3_res_time: Optional[float]
        pct75_res_time: Optional[float]
        pct96_res_time: Optional[float]
        pct97_res_time: Optional[float]
        pct98_res_time: Optional[float]
        pct9999_res_time: Optional[float]
        pct999_res_time: Optional[float]
        received_k_bytes_per_sec: Optional[float]
        sample_count: Optional[float]
        sent_k_bytes_per_sec: Optional[float]
        throughput: Optional[float]
        transaction: Optional[str]


    class azure.developer.loadtesting.models.TestRunStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "ACCEPTED"
        CANCELLED = "CANCELLED"
        CANCELLING = "CANCELLING"
        CONFIGURED = "CONFIGURED"
        CONFIGURING = "CONFIGURING"
        DEPROVISIONED = "DEPROVISIONED"
        DEPROVISIONING = "DEPROVISIONING"
        DONE = "DONE"
        EXECUTED = "EXECUTED"
        EXECUTING = "EXECUTING"
        FAILED = "FAILED"
        NOT_STARTED = "NOTSTARTED"
        PROVISIONED = "PROVISIONED"
        PROVISIONING = "PROVISIONING"
        VALIDATION_FAILURE = "VALIDATION_FAILURE"
        VALIDATION_SUCCESS = "VALIDATION_SUCCESS"


    class azure.developer.loadtesting.models.TestServerMetricsConfiguration(_Model):
        created_by: Optional[str]
        created_date_time: Optional[datetime]
        last_modified_by: Optional[str]
        last_modified_date_time: Optional[datetime]
        metrics: dict[str, ResourceMetric]
        test_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                metrics: dict[str, ResourceMetric]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TestsNotificationEventFilter(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TestsNotificationRule(NotificationRule, discriminator='Tests'):
        action_group_ids: list[str]
        created_by: str
        created_date_time: datetime
        display_name: str
        event_filters: dict[str, TestsNotificationEventFilter]
        last_modified_by: str
        last_modified_date_time: datetime
        notification_rule_id: str
        scope: Literal[NotificationScopeType.TESTS]
        test_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                action_group_ids: list[str], 
                display_name: str, 
                event_filters: dict[str, TestsNotificationEventFilter], 
                test_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TimeGrain(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PT10S = "PT10S"
        PT1H = "PT1H"
        PT1M = "PT1M"
        PT5M = "PT5M"
        PT5S = "PT5S"


    class azure.developer.loadtesting.models.TimeSeriesElement(_Model):
        data: Optional[list[MetricValue]]
        dimension_values: Optional[list[DimensionValue]]

        @overload
        def __init__(
                self, 
                *, 
                data: Optional[list[MetricValue]] = ..., 
                dimension_values: Optional[list[DimensionValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.Trigger(_Model):
        created_by: Optional[str]
        created_date_time: Optional[datetime]
        description: Optional[str]
        display_name: str
        kind: str
        last_modified_by: Optional[str]
        last_modified_date_time: Optional[datetime]
        state: Optional[Union[str, TriggerState]]
        state_details: Optional[StateDetails]
        trigger_id: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: str, 
                kind: str, 
                state: Optional[Union[str, TriggerState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TriggerCompletedNotificationEventFilter(TestsNotificationEventFilter, discriminator='TriggerCompleted'):
        kind: Literal[NotificationEventType.TRIGGER_COMPLETED]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TriggerDisabledNotificationEventFilter(TestsNotificationEventFilter, discriminator='TriggerDisabled'):
        kind: Literal[NotificationEventType.TRIGGER_DISABLED]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.developer.loadtesting.models.TriggerState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        COMPLETED = "Completed"
        DISABLED = "Disabled"
        PAUSED = "Paused"


    class azure.developer.loadtesting.models.TriggerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SCHEDULE_TESTS_TRIGGER = "ScheduleTestsTrigger"


    class azure.developer.loadtesting.models.WeekDays(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.developer.loadtesting.models.WeeklyRecurrence(Recurrence, discriminator='Weekly'):
        days_of_week: Optional[list[Union[str, WeekDays]]]
        frequency: Literal[Frequency.WEEKLY]
        interval: Optional[int]
        recurrence_end: RecurrenceEnd

        @overload
        def __init__(
                self, 
                *, 
                days_of_week: Optional[list[Union[str, WeekDays]]] = ..., 
                interval: Optional[int] = ..., 
                recurrence_end: Optional[RecurrenceEnd] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


```