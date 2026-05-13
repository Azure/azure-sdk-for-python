```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.batch

    class azure.batch.BatchClient(GenerateBatchClient): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureNamedKeyCredential, TokenCredential], 
                *, 
                api_version: str = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_deallocate_node(
                self, 
                pool_id: str, 
                node_id: str, 
                options: Optional[BatchNodeDeallocateOptions] = None, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_job(
                self, 
                job_id: str, 
                *, 
                etag: Optional[str] = ..., 
                force: Optional[bool] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_job_schedule(
                self, 
                job_schedule_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_pool(
                self, 
                pool_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_disable_job(
                self, 
                job_id: str, 
                disable_options: BatchJobDisableOptions, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_enable_job(
                self, 
                job_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_reboot_node(
                self, 
                pool_id: str, 
                node_id: str, 
                options: Optional[BatchNodeRebootOptions] = None, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_reimage_node(
                self, 
                pool_id: str, 
                node_id: str, 
                options: Optional[BatchNodeReimageOptions] = None, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_remove_nodes(
                self, 
                pool_id: str, 
                remove_options: BatchNodeRemoveOptions, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_resize_pool(
                self, 
                pool_id: str, 
                resize_options: BatchPoolResizeOptions, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start_node(
                self, 
                pool_id: str, 
                node_id: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_stop_pool_resize(
                self, 
                pool_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_terminate_job(
                self, 
                job_id: str, 
                options: Optional[BatchJobTerminateOptions] = None, 
                *, 
                etag: Optional[str] = ..., 
                force: Optional[bool] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_terminate_job_schedule(
                self, 
                job_schedule_id: str, 
                *, 
                etag: Optional[str] = ..., 
                force: Optional[bool] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        def close(self) -> None: ...

        @distributed_trace
        def create_job(
                self, 
                job: BatchJobCreateOptions, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def create_job_schedule(
                self, 
                job_schedule: BatchJobScheduleCreateOptions, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def create_node_user(
                self, 
                pool_id: str, 
                node_id: str, 
                user: BatchNodeUserCreateOptions, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def create_pool(
                self, 
                pool: BatchPoolCreateOptions, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def create_task(
                self, 
                job_id: str, 
                task: BatchTaskCreateOptions, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def create_task_collection(
                self, 
                job_id: str, 
                task_collection: BatchTaskGroup, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchCreateTaskCollectionResult: ...

        @distributed_trace
        def create_tasks(
                self, 
                job_id: str, 
                task_collection: List[BatchTaskCreateOptions], 
                *, 
                max_concurrency: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchCreateTaskCollectionResult: ...

        @distributed_trace
        def delete_node_file(
                self, 
                pool_id: str, 
                node_id: str, 
                file_path: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                recursive: Optional[bool] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_node_user(
                self, 
                pool_id: str, 
                node_id: str, 
                user_name: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_task(
                self, 
                job_id: str, 
                task_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_task_file(
                self, 
                job_id: str, 
                task_id: str, 
                file_path: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                recursive: Optional[bool] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def disable_job_schedule(
                self, 
                job_schedule_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def disable_node_scheduling(
                self, 
                pool_id: str, 
                node_id: str, 
                options: Optional[BatchNodeDisableSchedulingOptions] = None, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def disable_pool_auto_scale(
                self, 
                pool_id: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def download_node_file(
                self, 
                pool_id: str, 
                node_id: str, 
                file_path: str, 
                *, 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                ocp_date: Optional[datetime] = ..., 
                ocp_range: Optional[str] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def download_task_file(
                self, 
                job_id: str, 
                task_id: str, 
                file_path: str, 
                *, 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                ocp_date: Optional[datetime] = ..., 
                ocp_range: Optional[str] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def enable_job_schedule(
                self, 
                job_schedule_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def enable_node_scheduling(
                self, 
                pool_id: str, 
                node_id: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def enable_pool_auto_scale(
                self, 
                pool_id: str, 
                enable_auto_scale_options: BatchPoolEnableAutoScaleOptions, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def evaluate_pool_auto_scale(
                self, 
                pool_id: str, 
                evaluate_auto_scale_options: BatchPoolEvaluateAutoScaleOptions, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AutoScaleRun: ...

        @distributed_trace
        def get_application(
                self, 
                application_id: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchApplication: ...

        @distributed_trace
        def get_job(
                self, 
                job_id: str, 
                *, 
                etag: Optional[str] = ..., 
                expand: Optional[list[str]] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchJob: ...

        @distributed_trace
        def get_job_schedule(
                self, 
                job_schedule_id: str, 
                *, 
                etag: Optional[str] = ..., 
                expand: Optional[list[str]] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchJobSchedule: ...

        @distributed_trace
        def get_job_task_counts(
                self, 
                job_id: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchTaskCountsResult: ...

        @distributed_trace
        def get_node(
                self, 
                pool_id: str, 
                node_id: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchNode: ...

        @distributed_trace
        def get_node_extension(
                self, 
                pool_id: str, 
                node_id: str, 
                extension_name: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchNodeVMExtension: ...

        @distributed_trace
        def get_node_file_properties(
                self, 
                pool_id: str, 
                node_id: str, 
                file_path: str, 
                *, 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchFileProperties: ...

        @distributed_trace
        def get_node_remote_login_settings(
                self, 
                pool_id: str, 
                node_id: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchNodeRemoteLoginSettings: ...

        @distributed_trace
        def get_pool(
                self, 
                pool_id: str, 
                *, 
                etag: Optional[str] = ..., 
                expand: Optional[list[str]] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchPool: ...

        @distributed_trace
        def get_task(
                self, 
                job_id: str, 
                task_id: str, 
                *, 
                etag: Optional[str] = ..., 
                expand: Optional[list[str]] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchTask: ...

        @distributed_trace
        def get_task_file_properties(
                self, 
                job_id: str, 
                task_id: str, 
                file_path: str, 
                *, 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchFileProperties: ...

        @distributed_trace
        def job_schedule_exists(
                self, 
                job_schedule_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace
        def list_applications(
                self, 
                *, 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BatchApplication]: ...

        @distributed_trace
        def list_job_preparation_and_release_task_status(
                self, 
                job_id: str, 
                *, 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BatchJobPreparationAndReleaseTaskStatus]: ...

        @distributed_trace
        def list_job_schedules(
                self, 
                *, 
                expand: Optional[list[str]] = ..., 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BatchJobSchedule]: ...

        @distributed_trace
        def list_jobs(
                self, 
                *, 
                expand: Optional[list[str]] = ..., 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BatchJob]: ...

        @distributed_trace
        def list_jobs_from_schedule(
                self, 
                job_schedule_id: str, 
                *, 
                expand: Optional[list[str]] = ..., 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BatchJob]: ...

        @distributed_trace
        def list_node_extensions(
                self, 
                pool_id: str, 
                node_id: str, 
                *, 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BatchNodeVMExtension]: ...

        @distributed_trace
        def list_node_files(
                self, 
                pool_id: str, 
                node_id: str, 
                *, 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                recursive: Optional[bool] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BatchNodeFile]: ...

        @distributed_trace
        def list_nodes(
                self, 
                pool_id: str, 
                *, 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BatchNode]: ...

        @distributed_trace
        def list_pool_node_counts(
                self, 
                *, 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BatchPoolNodeCounts]: ...

        @distributed_trace
        def list_pool_usage_metrics(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                start_time: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BatchPoolUsageMetrics]: ...

        @distributed_trace
        def list_pools(
                self, 
                *, 
                expand: Optional[list[str]] = ..., 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BatchPool]: ...

        @distributed_trace
        def list_subtasks(
                self, 
                job_id: str, 
                task_id: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BatchSubtask]: ...

        @distributed_trace
        def list_supported_images(
                self, 
                *, 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BatchSupportedImage]: ...

        @distributed_trace
        def list_task_files(
                self, 
                job_id: str, 
                task_id: str, 
                *, 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                recursive: Optional[bool] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BatchNodeFile]: ...

        @distributed_trace
        def list_tasks(
                self, 
                job_id: str, 
                *, 
                expand: Optional[list[str]] = ..., 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BatchTask]: ...

        @distributed_trace
        def pool_exists(
                self, 
                pool_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace
        def reactivate_task(
                self, 
                job_id: str, 
                task_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def replace_job(
                self, 
                job_id: str, 
                job: BatchJob, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def replace_job_schedule(
                self, 
                job_schedule_id: str, 
                job_schedule: BatchJobSchedule, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def replace_node_user(
                self, 
                pool_id: str, 
                node_id: str, 
                user_name: str, 
                update_options: BatchNodeUserReplaceOptions, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def replace_pool_properties(
                self, 
                pool_id: str, 
                pool: BatchPoolReplaceOptions, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def replace_task(
                self, 
                job_id: str, 
                task_id: str, 
                task: BatchTask, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        @distributed_trace
        def terminate_task(
                self, 
                job_id: str, 
                task_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def update_job(
                self, 
                job_id: str, 
                job: BatchJobUpdateOptions, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def update_job_schedule(
                self, 
                job_schedule_id: str, 
                job_schedule: BatchJobScheduleUpdateOptions, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def update_pool(
                self, 
                pool_id: str, 
                pool: BatchPoolUpdateOptions, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def upload_node_logs(
                self, 
                pool_id: str, 
                node_id: str, 
                upload_options: UploadBatchServiceLogsOptions, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> UploadBatchServiceLogsResult: ...


namespace azure.batch.aio

    class azure.batch.aio.BatchClient(GenerateBatchClient): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureNamedKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: str = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace
        async def begin_deallocate_node(
                self, 
                pool_id: str, 
                node_id: str, 
                options: Optional[BatchNodeDeallocateOptions] = None, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace
        async def begin_delete_job(
                self, 
                job_id: str, 
                *, 
                etag: Optional[str] = ..., 
                force: Optional[bool] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace
        async def begin_delete_job_schedule(
                self, 
                job_schedule_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace
        async def begin_delete_pool(
                self, 
                pool_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace
        async def begin_disable_job(
                self, 
                job_id: str, 
                disable_options: BatchJobDisableOptions, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace
        async def begin_enable_job(
                self, 
                job_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace
        async def begin_reboot_node(
                self, 
                pool_id: str, 
                node_id: str, 
                options: Optional[BatchNodeRebootOptions] = None, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace
        async def begin_reimage_node(
                self, 
                pool_id: str, 
                node_id: str, 
                options: Optional[BatchNodeReimageOptions] = None, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace
        async def begin_remove_nodes(
                self, 
                pool_id: str, 
                remove_options: BatchNodeRemoveOptions, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace
        async def begin_resize_pool(
                self, 
                pool_id: str, 
                resize_options: BatchPoolResizeOptions, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace
        async def begin_start_node(
                self, 
                pool_id: str, 
                node_id: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace
        async def begin_stop_pool_resize(
                self, 
                pool_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace
        async def begin_terminate_job(
                self, 
                job_id: str, 
                options: Optional[BatchJobTerminateOptions] = None, 
                *, 
                etag: Optional[str] = ..., 
                force: Optional[bool] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace
        async def begin_terminate_job_schedule(
                self, 
                job_schedule_id: str, 
                *, 
                etag: Optional[str] = ..., 
                force: Optional[bool] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                polling_interval: int = 5, 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def create_job(
                self, 
                job: BatchJobCreateOptions, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def create_job_schedule(
                self, 
                job_schedule: BatchJobScheduleCreateOptions, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def create_node_user(
                self, 
                pool_id: str, 
                node_id: str, 
                user: BatchNodeUserCreateOptions, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def create_pool(
                self, 
                pool: BatchPoolCreateOptions, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def create_task(
                self, 
                job_id: str, 
                task: BatchTaskCreateOptions, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def create_task_collection(
                self, 
                job_id: str, 
                task_collection: BatchTaskGroup, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchCreateTaskCollectionResult: ...

        @distributed_trace
        async def create_tasks(
                self, 
                job_id: str, 
                task_collection: List[BatchTaskCreateOptions], 
                *, 
                max_concurrency: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchCreateTaskCollectionResult: ...

        @distributed_trace_async
        async def delete_node_file(
                self, 
                pool_id: str, 
                node_id: str, 
                file_path: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                recursive: Optional[bool] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_node_user(
                self, 
                pool_id: str, 
                node_id: str, 
                user_name: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_task(
                self, 
                job_id: str, 
                task_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_task_file(
                self, 
                job_id: str, 
                task_id: str, 
                file_path: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                recursive: Optional[bool] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def disable_job_schedule(
                self, 
                job_schedule_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def disable_node_scheduling(
                self, 
                pool_id: str, 
                node_id: str, 
                options: Optional[BatchNodeDisableSchedulingOptions] = None, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def disable_pool_auto_scale(
                self, 
                pool_id: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        async def download_node_file(
                self, 
                pool_id: str, 
                node_id: str, 
                file_path: str, 
                *, 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                ocp_date: Optional[datetime] = ..., 
                ocp_range: Optional[str] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace
        async def download_task_file(
                self, 
                job_id: str, 
                task_id: str, 
                file_path: str, 
                *, 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                ocp_date: Optional[datetime] = ..., 
                ocp_range: Optional[str] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def enable_job_schedule(
                self, 
                job_schedule_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def enable_node_scheduling(
                self, 
                pool_id: str, 
                node_id: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def enable_pool_auto_scale(
                self, 
                pool_id: str, 
                enable_auto_scale_options: BatchPoolEnableAutoScaleOptions, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def evaluate_pool_auto_scale(
                self, 
                pool_id: str, 
                evaluate_auto_scale_options: BatchPoolEvaluateAutoScaleOptions, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AutoScaleRun: ...

        @distributed_trace_async
        async def get_application(
                self, 
                application_id: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchApplication: ...

        @distributed_trace_async
        async def get_job(
                self, 
                job_id: str, 
                *, 
                etag: Optional[str] = ..., 
                expand: Optional[list[str]] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchJob: ...

        @distributed_trace_async
        async def get_job_schedule(
                self, 
                job_schedule_id: str, 
                *, 
                etag: Optional[str] = ..., 
                expand: Optional[list[str]] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchJobSchedule: ...

        @distributed_trace_async
        async def get_job_task_counts(
                self, 
                job_id: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchTaskCountsResult: ...

        @distributed_trace_async
        async def get_node(
                self, 
                pool_id: str, 
                node_id: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchNode: ...

        @distributed_trace_async
        async def get_node_extension(
                self, 
                pool_id: str, 
                node_id: str, 
                extension_name: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchNodeVMExtension: ...

        @distributed_trace
        async def get_node_file_properties(
                self, 
                pool_id: str, 
                node_id: str, 
                file_path: str, 
                *, 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchFileProperties: ...

        @distributed_trace_async
        async def get_node_remote_login_settings(
                self, 
                pool_id: str, 
                node_id: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchNodeRemoteLoginSettings: ...

        @distributed_trace_async
        async def get_pool(
                self, 
                pool_id: str, 
                *, 
                etag: Optional[str] = ..., 
                expand: Optional[list[str]] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchPool: ...

        @distributed_trace_async
        async def get_task(
                self, 
                job_id: str, 
                task_id: str, 
                *, 
                etag: Optional[str] = ..., 
                expand: Optional[list[str]] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchTask: ...

        @distributed_trace
        async def get_task_file_properties(
                self, 
                job_id: str, 
                task_id: str, 
                file_path: str, 
                *, 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> BatchFileProperties: ...

        @distributed_trace_async
        async def job_schedule_exists(
                self, 
                job_schedule_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace
        def list_applications(
                self, 
                *, 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BatchApplication]: ...

        @distributed_trace
        def list_job_preparation_and_release_task_status(
                self, 
                job_id: str, 
                *, 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BatchJobPreparationAndReleaseTaskStatus]: ...

        @distributed_trace
        def list_job_schedules(
                self, 
                *, 
                expand: Optional[list[str]] = ..., 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BatchJobSchedule]: ...

        @distributed_trace
        def list_jobs(
                self, 
                *, 
                expand: Optional[list[str]] = ..., 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BatchJob]: ...

        @distributed_trace
        def list_jobs_from_schedule(
                self, 
                job_schedule_id: str, 
                *, 
                expand: Optional[list[str]] = ..., 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BatchJob]: ...

        @distributed_trace
        def list_node_extensions(
                self, 
                pool_id: str, 
                node_id: str, 
                *, 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BatchNodeVMExtension]: ...

        @distributed_trace
        def list_node_files(
                self, 
                pool_id: str, 
                node_id: str, 
                *, 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                recursive: Optional[bool] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BatchNodeFile]: ...

        @distributed_trace
        def list_nodes(
                self, 
                pool_id: str, 
                *, 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BatchNode]: ...

        @distributed_trace
        def list_pool_node_counts(
                self, 
                *, 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BatchPoolNodeCounts]: ...

        @distributed_trace
        def list_pool_usage_metrics(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                start_time: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BatchPoolUsageMetrics]: ...

        @distributed_trace
        def list_pools(
                self, 
                *, 
                expand: Optional[list[str]] = ..., 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BatchPool]: ...

        @distributed_trace
        def list_subtasks(
                self, 
                job_id: str, 
                task_id: str, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BatchSubtask]: ...

        @distributed_trace
        def list_supported_images(
                self, 
                *, 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BatchSupportedImage]: ...

        @distributed_trace
        def list_task_files(
                self, 
                job_id: str, 
                task_id: str, 
                *, 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                recursive: Optional[bool] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BatchNodeFile]: ...

        @distributed_trace
        def list_tasks(
                self, 
                job_id: str, 
                *, 
                expand: Optional[list[str]] = ..., 
                filter: Optional[str] = ..., 
                max_results: Optional[int] = ..., 
                ocp_date: Optional[datetime] = ..., 
                select: Optional[list[str]] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BatchTask]: ...

        @distributed_trace_async
        async def pool_exists(
                self, 
                pool_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace_async
        async def reactivate_task(
                self, 
                job_id: str, 
                task_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def replace_job(
                self, 
                job_id: str, 
                job: BatchJob, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def replace_job_schedule(
                self, 
                job_schedule_id: str, 
                job_schedule: BatchJobSchedule, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def replace_node_user(
                self, 
                pool_id: str, 
                node_id: str, 
                user_name: str, 
                update_options: BatchNodeUserReplaceOptions, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def replace_pool_properties(
                self, 
                pool_id: str, 
                pool: BatchPoolReplaceOptions, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def replace_task(
                self, 
                job_id: str, 
                task_id: str, 
                task: BatchTask, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        @distributed_trace_async
        async def terminate_task(
                self, 
                job_id: str, 
                task_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def update_job(
                self, 
                job_id: str, 
                job: BatchJobUpdateOptions, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def update_job_schedule(
                self, 
                job_schedule_id: str, 
                job_schedule: BatchJobScheduleUpdateOptions, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def update_pool(
                self, 
                pool_id: str, 
                pool: BatchPoolUpdateOptions, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def upload_node_logs(
                self, 
                pool_id: str, 
                node_id: str, 
                upload_options: UploadBatchServiceLogsOptions, 
                *, 
                ocp_date: Optional[datetime] = ..., 
                service_timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> UploadBatchServiceLogsResult: ...


namespace azure.batch.models

    class azure.batch.models.AllocationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESIZING = "resizing"
        STEADY = "steady"
        STOPPING = "stopping"


    class azure.batch.models.AutoScaleRun(_Model):
        error: Optional[AutoScaleRunError]
        results: Optional[str]
        timestamp: datetime

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[AutoScaleRunError] = ..., 
                results: Optional[str] = ..., 
                timestamp: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.AutoScaleRunError(_Model):
        code: Optional[str]
        error_values: Optional[list[NameValuePair]]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                error_values: Optional[list[NameValuePair]] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.AutoUserScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        POOL = "pool"
        TASK = "task"


    class azure.batch.models.AutoUserSpecification(_Model):
        elevation_level: Optional[Union[str, ElevationLevel]]
        scope: Optional[Union[str, AutoUserScope]]

        @overload
        def __init__(
                self, 
                *, 
                elevation_level: Optional[Union[str, ElevationLevel]] = ..., 
                scope: Optional[Union[str, AutoUserScope]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.AutomaticOsUpgradePolicy(_Model):
        disable_automatic_rollback: Optional[bool]
        enable_automatic_os_upgrade: Optional[bool]
        os_rolling_upgrade_deferral: Optional[bool]
        use_rolling_upgrade_policy: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                disable_automatic_rollback: Optional[bool] = ..., 
                enable_automatic_os_upgrade: Optional[bool] = ..., 
                os_rolling_upgrade_deferral: Optional[bool] = ..., 
                use_rolling_upgrade_policy: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.AzureBlobFileSystemConfiguration(_Model):
        account_key: Optional[str]
        account_name: str
        blobfuse_options: Optional[str]
        container_name: str
        identity_reference: Optional[BatchNodeIdentityReference]
        relative_mount_path: str
        sas_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                account_key: Optional[str] = ..., 
                account_name: str, 
                blobfuse_options: Optional[str] = ..., 
                container_name: str, 
                identity_reference: Optional[BatchNodeIdentityReference] = ..., 
                relative_mount_path: str, 
                sas_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.AzureFileShareConfiguration(_Model):
        account_key: str
        account_name: str
        azure_file_url: str
        mount_options: Optional[str]
        relative_mount_path: str

        @overload
        def __init__(
                self, 
                *, 
                account_key: str, 
                account_name: str, 
                azure_file_url: str, 
                mount_options: Optional[str] = ..., 
                relative_mount_path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchAffinityInfo(_Model):
        affinity_id: str

        @overload
        def __init__(
                self, 
                *, 
                affinity_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchAllTasksCompleteMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_ACTION = "noaction"
        TERMINATE_JOB = "terminatejob"


    class azure.batch.models.BatchApplication(_Model):
        display_name: str
        id: str
        versions: list[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: str, 
                id: str, 
                versions: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchApplicationPackageReference(_Model):
        application_id: str
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                application_id: str, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchAutoPoolSpecification(_Model):
        auto_pool_id_prefix: Optional[str]
        keep_alive: Optional[bool]
        pool: Optional[BatchPoolSpecification]
        pool_lifetime_option: Union[str, BatchPoolLifetimeOption]

        @overload
        def __init__(
                self, 
                *, 
                auto_pool_id_prefix: Optional[str] = ..., 
                keep_alive: Optional[bool] = ..., 
                pool: Optional[BatchPoolSpecification] = ..., 
                pool_lifetime_option: Union[str, BatchPoolLifetimeOption]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchContainerConfiguration(_Model):
        container_image_names: Optional[list[str]]
        container_registries: Optional[list[ContainerRegistryReference]]
        type: Union[str, ContainerType]

        @overload
        def __init__(
                self, 
                *, 
                container_image_names: Optional[list[str]] = ..., 
                container_registries: Optional[list[ContainerRegistryReference]] = ..., 
                type: Union[str, ContainerType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchCreateTaskCollectionResult(_Model):
        result_values: Optional[list[BatchTaskCreateResult]]

        @overload
        def __init__(
                self, 
                *, 
                result_values: Optional[list[BatchTaskCreateResult]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchDiffDiskSettings(_Model):
        placement: Optional[Union[str, DiffDiskPlacement]]

        @overload
        def __init__(
                self, 
                *, 
                placement: Optional[Union[str, DiffDiskPlacement]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchError(_Model):
        code: Optional[str]
        error_values: Optional[list[BatchErrorDetail]]
        message: Optional[BatchErrorMessage]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                error_values: Optional[list[BatchErrorDetail]] = ..., 
                message: Optional[BatchErrorMessage] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchErrorDetail(_Model):
        key: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchErrorMessage(_Model):
        lang: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                lang: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchErrorSourceCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SERVER_ERROR = "servererror"
        USER_ERROR = "usererror"


    class azure.batch.models.BatchFileProperties:
        content_length: int
        content_type: Optional[str]
        creation_time: Optional[datetime]
        file_mode: Optional[str]
        is_directory: Optional[bool]
        last_modified: datetime
        url: Optional[str]

        def __init__(
                self, 
                *, 
                content_length: int, 
                content_type: Optional[str] = ..., 
                creation_time: Optional[datetime] = ..., 
                file_mode: Optional[str] = ..., 
                is_directory: Optional[bool] = ..., 
                last_modified: datetime, 
                url: Optional[str] = ...
            ) -> None: ...


    class azure.batch.models.BatchInboundNatPool(_Model):
        backend_port: int
        frontend_port_range_end: int
        frontend_port_range_start: int
        name: str
        network_security_group_rules: Optional[list[NetworkSecurityGroupRule]]
        protocol: Union[str, InboundEndpointProtocol]

        @overload
        def __init__(
                self, 
                *, 
                backend_port: int, 
                frontend_port_range_end: int, 
                frontend_port_range_start: int, 
                name: str, 
                network_security_group_rules: Optional[list[NetworkSecurityGroupRule]] = ..., 
                protocol: Union[str, InboundEndpointProtocol]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchJob(_Model):
        all_tasks_complete_mode: Optional[Union[str, BatchAllTasksCompleteMode]]
        allow_task_preemption: Optional[bool]
        common_environment_settings: Optional[list[EnvironmentSetting]]
        constraints: Optional[BatchJobConstraints]
        creation_time: datetime
        display_name: Optional[str]
        etag: str
        execution_info: Optional[BatchJobExecutionInfo]
        id: str
        job_manager_task: Optional[BatchJobManagerTask]
        job_preparation_task: Optional[BatchJobPreparationTask]
        job_release_task: Optional[BatchJobReleaseTask]
        job_statistics: Optional[BatchJobStatistics]
        last_modified: datetime
        max_parallel_tasks: Optional[int]
        metadata: Optional[list[BatchMetadataItem]]
        network_configuration: Optional[BatchJobNetworkConfiguration]
        pool_info: BatchPoolInfo
        previous_state: Optional[Union[str, BatchJobState]]
        previous_state_transition_time: Optional[datetime]
        priority: Optional[int]
        state: Union[str, BatchJobState]
        state_transition_time: datetime
        task_failure_mode: Optional[Union[str, BatchTaskFailureMode]]
        url: str
        uses_task_dependencies: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                all_tasks_complete_mode: Optional[Union[str, BatchAllTasksCompleteMode]] = ..., 
                allow_task_preemption: Optional[bool] = ..., 
                constraints: Optional[BatchJobConstraints] = ..., 
                max_parallel_tasks: Optional[int] = ..., 
                metadata: Optional[list[BatchMetadataItem]] = ..., 
                pool_info: BatchPoolInfo, 
                priority: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchJobActionKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "disable"
        NONE = "none"
        TERMINATE = "terminate"


    class azure.batch.models.BatchJobConstraints(_Model):
        max_task_retry_count: Optional[int]
        max_wall_clock_time: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                max_task_retry_count: Optional[int] = ..., 
                max_wall_clock_time: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchJobCreateOptions(_Model):
        all_tasks_complete_mode: Optional[Union[str, BatchAllTasksCompleteMode]]
        allow_task_preemption: Optional[bool]
        common_environment_settings: Optional[list[EnvironmentSetting]]
        constraints: Optional[BatchJobConstraints]
        display_name: Optional[str]
        id: str
        job_manager_task: Optional[BatchJobManagerTask]
        job_preparation_task: Optional[BatchJobPreparationTask]
        job_release_task: Optional[BatchJobReleaseTask]
        max_parallel_tasks: Optional[int]
        metadata: Optional[list[BatchMetadataItem]]
        network_configuration: Optional[BatchJobNetworkConfiguration]
        pool_info: BatchPoolInfo
        priority: Optional[int]
        task_failure_mode: Optional[Union[str, BatchTaskFailureMode]]
        uses_task_dependencies: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                all_tasks_complete_mode: Optional[Union[str, BatchAllTasksCompleteMode]] = ..., 
                allow_task_preemption: Optional[bool] = ..., 
                common_environment_settings: Optional[list[EnvironmentSetting]] = ..., 
                constraints: Optional[BatchJobConstraints] = ..., 
                display_name: Optional[str] = ..., 
                id: str, 
                job_manager_task: Optional[BatchJobManagerTask] = ..., 
                job_preparation_task: Optional[BatchJobPreparationTask] = ..., 
                job_release_task: Optional[BatchJobReleaseTask] = ..., 
                max_parallel_tasks: Optional[int] = ..., 
                metadata: Optional[list[BatchMetadataItem]] = ..., 
                network_configuration: Optional[BatchJobNetworkConfiguration] = ..., 
                pool_info: BatchPoolInfo, 
                priority: Optional[int] = ..., 
                task_failure_mode: Optional[Union[str, BatchTaskFailureMode]] = ..., 
                uses_task_dependencies: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchJobDefaultOrder(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATION_TIME = "creationtime"
        NONE = "none"


    class azure.batch.models.BatchJobDisableOptions(_Model):
        disable_tasks: Union[str, DisableBatchJobOption]

        @overload
        def __init__(
                self, 
                *, 
                disable_tasks: Union[str, DisableBatchJobOption]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchJobExecutionInfo(_Model):
        end_time: Optional[datetime]
        pool_id: Optional[str]
        scheduling_error: Optional[BatchJobSchedulingError]
        start_time: datetime
        termination_reason: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                pool_id: Optional[str] = ..., 
                scheduling_error: Optional[BatchJobSchedulingError] = ..., 
                start_time: datetime, 
                termination_reason: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchJobManagerTask(_Model):
        allow_low_priority_node: Optional[bool]
        application_package_references: Optional[list[BatchApplicationPackageReference]]
        command_line: str
        constraints: Optional[BatchTaskConstraints]
        container_settings: Optional[BatchTaskContainerSettings]
        display_name: Optional[str]
        environment_settings: Optional[list[EnvironmentSetting]]
        id: str
        kill_job_on_completion: Optional[bool]
        output_files: Optional[list[OutputFile]]
        required_slots: Optional[int]
        resource_files: Optional[list[ResourceFile]]
        run_exclusive: Optional[bool]
        user_identity: Optional[UserIdentity]

        @overload
        def __init__(
                self, 
                *, 
                allow_low_priority_node: Optional[bool] = ..., 
                application_package_references: Optional[list[BatchApplicationPackageReference]] = ..., 
                command_line: str, 
                constraints: Optional[BatchTaskConstraints] = ..., 
                container_settings: Optional[BatchTaskContainerSettings] = ..., 
                display_name: Optional[str] = ..., 
                environment_settings: Optional[list[EnvironmentSetting]] = ..., 
                id: str, 
                kill_job_on_completion: Optional[bool] = ..., 
                output_files: Optional[list[OutputFile]] = ..., 
                required_slots: Optional[int] = ..., 
                resource_files: Optional[list[ResourceFile]] = ..., 
                run_exclusive: Optional[bool] = ..., 
                user_identity: Optional[UserIdentity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchJobNetworkConfiguration(_Model):
        skip_withdraw_from_vnet: Optional[bool]
        subnet_id: str

        @overload
        def __init__(
                self, 
                *, 
                skip_withdraw_from_vnet: Optional[bool] = ..., 
                subnet_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchJobPreparationAndReleaseTaskStatus(_Model):
        job_preparation_task_execution_info: Optional[BatchJobPreparationTaskExecutionInfo]
        job_release_task_execution_info: Optional[BatchJobReleaseTaskExecutionInfo]
        node_id: Optional[str]
        node_url: Optional[str]
        pool_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                job_preparation_task_execution_info: Optional[BatchJobPreparationTaskExecutionInfo] = ..., 
                job_release_task_execution_info: Optional[BatchJobReleaseTaskExecutionInfo] = ..., 
                node_id: Optional[str] = ..., 
                node_url: Optional[str] = ..., 
                pool_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchJobPreparationTask(_Model):
        command_line: str
        constraints: Optional[BatchTaskConstraints]
        container_settings: Optional[BatchTaskContainerSettings]
        environment_settings: Optional[list[EnvironmentSetting]]
        id: Optional[str]
        rerun_on_node_reboot_after_success: Optional[bool]
        resource_files: Optional[list[ResourceFile]]
        user_identity: Optional[UserIdentity]
        wait_for_success: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                command_line: str, 
                constraints: Optional[BatchTaskConstraints] = ..., 
                container_settings: Optional[BatchTaskContainerSettings] = ..., 
                environment_settings: Optional[list[EnvironmentSetting]] = ..., 
                id: Optional[str] = ..., 
                rerun_on_node_reboot_after_success: Optional[bool] = ..., 
                resource_files: Optional[list[ResourceFile]] = ..., 
                user_identity: Optional[UserIdentity] = ..., 
                wait_for_success: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchJobPreparationTaskExecutionInfo(_Model):
        container_info: Optional[BatchTaskContainerExecutionInfo]
        end_time: Optional[datetime]
        exit_code: Optional[int]
        failure_info: Optional[BatchTaskFailureInfo]
        last_retry_time: Optional[datetime]
        result: Optional[Union[str, BatchTaskExecutionResult]]
        retry_count: int
        start_time: datetime
        state: Union[str, BatchJobPreparationTaskState]
        task_root_directory: Optional[str]
        task_root_directory_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                container_info: Optional[BatchTaskContainerExecutionInfo] = ..., 
                end_time: Optional[datetime] = ..., 
                exit_code: Optional[int] = ..., 
                failure_info: Optional[BatchTaskFailureInfo] = ..., 
                last_retry_time: Optional[datetime] = ..., 
                result: Optional[Union[str, BatchTaskExecutionResult]] = ..., 
                retry_count: int, 
                start_time: datetime, 
                state: Union[str, BatchJobPreparationTaskState], 
                task_root_directory: Optional[str] = ..., 
                task_root_directory_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchJobPreparationTaskState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        RUNNING = "running"


    class azure.batch.models.BatchJobReleaseTask(_Model):
        command_line: str
        container_settings: Optional[BatchTaskContainerSettings]
        environment_settings: Optional[list[EnvironmentSetting]]
        id: Optional[str]
        max_wall_clock_time: Optional[timedelta]
        resource_files: Optional[list[ResourceFile]]
        retention_time: Optional[timedelta]
        user_identity: Optional[UserIdentity]

        @overload
        def __init__(
                self, 
                *, 
                command_line: str, 
                container_settings: Optional[BatchTaskContainerSettings] = ..., 
                environment_settings: Optional[list[EnvironmentSetting]] = ..., 
                id: Optional[str] = ..., 
                max_wall_clock_time: Optional[timedelta] = ..., 
                resource_files: Optional[list[ResourceFile]] = ..., 
                retention_time: Optional[timedelta] = ..., 
                user_identity: Optional[UserIdentity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchJobReleaseTaskExecutionInfo(_Model):
        container_info: Optional[BatchTaskContainerExecutionInfo]
        end_time: Optional[datetime]
        exit_code: Optional[int]
        failure_info: Optional[BatchTaskFailureInfo]
        result: Optional[Union[str, BatchTaskExecutionResult]]
        start_time: datetime
        state: Union[str, BatchJobReleaseTaskState]
        task_root_directory: Optional[str]
        task_root_directory_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                container_info: Optional[BatchTaskContainerExecutionInfo] = ..., 
                end_time: Optional[datetime] = ..., 
                exit_code: Optional[int] = ..., 
                failure_info: Optional[BatchTaskFailureInfo] = ..., 
                result: Optional[Union[str, BatchTaskExecutionResult]] = ..., 
                start_time: datetime, 
                state: Union[str, BatchJobReleaseTaskState], 
                task_root_directory: Optional[str] = ..., 
                task_root_directory_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchJobReleaseTaskState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        RUNNING = "running"


    class azure.batch.models.BatchJobSchedule(_Model):
        creation_time: datetime
        display_name: Optional[str]
        etag: str
        execution_info: BatchJobScheduleExecutionInfo
        id: str
        job_schedule_statistics: Optional[BatchJobScheduleStatistics]
        job_specification: BatchJobSpecification
        last_modified: datetime
        metadata: Optional[list[BatchMetadataItem]]
        previous_state: Optional[Union[str, BatchJobScheduleState]]
        previous_state_transition_time: Optional[datetime]
        schedule: Optional[BatchJobScheduleConfiguration]
        state: Union[str, BatchJobScheduleState]
        state_transition_time: datetime
        url: str

        @overload
        def __init__(
                self, 
                *, 
                job_specification: BatchJobSpecification, 
                metadata: Optional[list[BatchMetadataItem]] = ..., 
                schedule: Optional[BatchJobScheduleConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchJobScheduleConfiguration(_Model):
        do_not_run_after: Optional[datetime]
        do_not_run_until: Optional[datetime]
        recurrence_interval: Optional[timedelta]
        start_window: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                do_not_run_after: Optional[datetime] = ..., 
                do_not_run_until: Optional[datetime] = ..., 
                recurrence_interval: Optional[timedelta] = ..., 
                start_window: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchJobScheduleCreateOptions(_Model):
        display_name: Optional[str]
        id: str
        job_specification: BatchJobSpecification
        metadata: Optional[list[BatchMetadataItem]]
        schedule: BatchJobScheduleConfiguration

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                id: str, 
                job_specification: BatchJobSpecification, 
                metadata: Optional[list[BatchMetadataItem]] = ..., 
                schedule: BatchJobScheduleConfiguration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchJobScheduleExecutionInfo(_Model):
        end_time: Optional[datetime]
        next_run_time: Optional[datetime]
        recent_job: Optional[RecentBatchJob]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                next_run_time: Optional[datetime] = ..., 
                recent_job: Optional[RecentBatchJob] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchJobScheduleState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        COMPLETED = "completed"
        DELETING = "deleting"
        DISABLED = "disabled"
        TERMINATING = "terminating"


    class azure.batch.models.BatchJobScheduleStatistics(_Model):
        failed_tasks_count: int
        kernel_cpu_time: timedelta
        last_update_time: datetime
        read_io_gib: float
        read_iops: int
        start_time: datetime
        succeeded_tasks_count: int
        task_retries_count: int
        url: str
        user_cpu_time: timedelta
        wait_time: timedelta
        wall_clock_time: timedelta
        write_io_gib: float
        write_iops: int

        @overload
        def __init__(
                self, 
                *, 
                failed_tasks_count: int, 
                kernel_cpu_time: timedelta, 
                last_update_time: datetime, 
                read_io_gib: float, 
                read_iops: int, 
                start_time: datetime, 
                succeeded_tasks_count: int, 
                task_retries_count: int, 
                url: str, 
                user_cpu_time: timedelta, 
                wait_time: timedelta, 
                wall_clock_time: timedelta, 
                write_io_gib: float, 
                write_iops: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchJobScheduleUpdateOptions(_Model):
        job_specification: Optional[BatchJobSpecification]
        metadata: Optional[list[BatchMetadataItem]]
        schedule: Optional[BatchJobScheduleConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                job_specification: Optional[BatchJobSpecification] = ..., 
                metadata: Optional[list[BatchMetadataItem]] = ..., 
                schedule: Optional[BatchJobScheduleConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchJobSchedulingError(_Model):
        category: Union[str, BatchErrorSourceCategory]
        code: Optional[str]
        details: Optional[list[NameValuePair]]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                category: Union[str, BatchErrorSourceCategory], 
                code: Optional[str] = ..., 
                details: Optional[list[NameValuePair]] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchJobSpecification(_Model):
        all_tasks_complete_mode: Optional[Union[str, BatchAllTasksCompleteMode]]
        allow_task_preemption: Optional[bool]
        common_environment_settings: Optional[list[EnvironmentSetting]]
        constraints: Optional[BatchJobConstraints]
        display_name: Optional[str]
        job_manager_task: Optional[BatchJobManagerTask]
        job_preparation_task: Optional[BatchJobPreparationTask]
        job_release_task: Optional[BatchJobReleaseTask]
        max_parallel_tasks: Optional[int]
        metadata: Optional[list[BatchMetadataItem]]
        network_configuration: Optional[BatchJobNetworkConfiguration]
        pool_info: BatchPoolInfo
        priority: Optional[int]
        task_failure_mode: Optional[Union[str, BatchTaskFailureMode]]
        uses_task_dependencies: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                all_tasks_complete_mode: Optional[Union[str, BatchAllTasksCompleteMode]] = ..., 
                allow_task_preemption: Optional[bool] = ..., 
                common_environment_settings: Optional[list[EnvironmentSetting]] = ..., 
                constraints: Optional[BatchJobConstraints] = ..., 
                display_name: Optional[str] = ..., 
                job_manager_task: Optional[BatchJobManagerTask] = ..., 
                job_preparation_task: Optional[BatchJobPreparationTask] = ..., 
                job_release_task: Optional[BatchJobReleaseTask] = ..., 
                max_parallel_tasks: Optional[int] = ..., 
                metadata: Optional[list[BatchMetadataItem]] = ..., 
                network_configuration: Optional[BatchJobNetworkConfiguration] = ..., 
                pool_info: BatchPoolInfo, 
                priority: Optional[int] = ..., 
                task_failure_mode: Optional[Union[str, BatchTaskFailureMode]] = ..., 
                uses_task_dependencies: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchJobState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        COMPLETED = "completed"
        DELETING = "deleting"
        DISABLED = "disabled"
        DISABLING = "disabling"
        ENABLING = "enabling"
        TERMINATING = "terminating"


    class azure.batch.models.BatchJobStatistics(_Model):
        failed_tasks_count: int
        kernel_cpu_time: timedelta
        last_update_time: datetime
        read_io_gib: float
        read_iops: int
        start_time: datetime
        succeeded_tasks_count: int
        task_retries_count: int
        url: str
        user_cpu_time: timedelta
        wait_time: timedelta
        wall_clock_time: timedelta
        write_io_gib: float
        write_iops: int

        @overload
        def __init__(
                self, 
                *, 
                failed_tasks_count: int, 
                kernel_cpu_time: timedelta, 
                last_update_time: datetime, 
                read_io_gib: float, 
                read_iops: int, 
                start_time: datetime, 
                succeeded_tasks_count: int, 
                task_retries_count: int, 
                url: str, 
                user_cpu_time: timedelta, 
                wait_time: timedelta, 
                wall_clock_time: timedelta, 
                write_io_gib: float, 
                write_iops: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchJobUpdateOptions(_Model):
        all_tasks_complete_mode: Optional[Union[str, BatchAllTasksCompleteMode]]
        allow_task_preemption: Optional[bool]
        constraints: Optional[BatchJobConstraints]
        max_parallel_tasks: Optional[int]
        metadata: Optional[list[BatchMetadataItem]]
        network_configuration: Optional[BatchJobNetworkConfiguration]
        pool_info: Optional[BatchPoolInfo]
        priority: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                all_tasks_complete_mode: Optional[Union[str, BatchAllTasksCompleteMode]] = ..., 
                allow_task_preemption: Optional[bool] = ..., 
                constraints: Optional[BatchJobConstraints] = ..., 
                max_parallel_tasks: Optional[int] = ..., 
                metadata: Optional[list[BatchMetadataItem]] = ..., 
                network_configuration: Optional[BatchJobNetworkConfiguration] = ..., 
                pool_info: Optional[BatchPoolInfo] = ..., 
                priority: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchMetadataItem(_Model):
        name: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchNode(_Model):
        affinity_id: str
        allocation_time: datetime
        endpoint_configuration: Optional[BatchNodeEndpointConfiguration]
        errors: Optional[list[BatchNodeError]]
        id: str
        ip_address: str
        ipv6_address: str
        is_dedicated: Optional[bool]
        last_boot_time: datetime
        node_agent_info: Optional[BatchNodeAgentInfo]
        recent_tasks: Optional[list[BatchTaskInfo]]
        running_task_slots_count: Optional[int]
        running_tasks_count: Optional[int]
        scheduling_state: Optional[Union[str, SchedulingState]]
        start_task: Optional[BatchStartTask]
        start_task_info: Optional[BatchStartTaskInfo]
        state: Union[str, BatchNodeState]
        state_transition_time: datetime
        total_tasks_run: int
        total_tasks_succeeded: Optional[int]
        url: str
        virtual_machine_info: VirtualMachineInfo
        vm_size: str


    class azure.batch.models.BatchNodeAgentInfo(_Model):
        last_update_time: datetime
        version: str

        @overload
        def __init__(
                self, 
                *, 
                last_update_time: datetime, 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchNodeCounts(_Model):
        creating: int
        deallocated: int
        deallocating: int
        idle: int
        leaving_pool: int
        offline: int
        preempted: int
        rebooting: int
        reimaging: int
        running: int
        start_task_failed: int
        starting: int
        total: int
        unknown: int
        unusable: int
        upgrading_os: int
        waiting_for_start_task: int

        @overload
        def __init__(
                self, 
                *, 
                creating: int, 
                deallocated: int, 
                deallocating: int, 
                idle: int, 
                leaving_pool: int, 
                offline: int, 
                preempted: int, 
                rebooting: int, 
                reimaging: int, 
                running: int, 
                start_task_failed: int, 
                starting: int, 
                total: int, 
                unknown: int, 
                unusable: int, 
                upgrading_os: int, 
                waiting_for_start_task: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchNodeDeallocationOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REQUEUE = "requeue"
        RETAINED_DATA = "retaineddata"
        TASK_COMPLETION = "taskcompletion"
        TERMINATE = "terminate"


    class azure.batch.models.BatchNodeDisableSchedulingOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REQUEUE = "requeue"
        TASK_COMPLETION = "taskcompletion"
        TERMINATE = "terminate"


    class azure.batch.models.BatchNodeDisableSchedulingOptions(_Model):
        node_disable_scheduling_option: Optional[Union[str, BatchNodeDisableSchedulingOption]]

        @overload
        def __init__(
                self, 
                *, 
                node_disable_scheduling_option: Optional[Union[str, BatchNodeDisableSchedulingOption]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchNodeEndpointConfiguration(_Model):
        inbound_endpoints: list[InboundEndpoint]

        @overload
        def __init__(
                self, 
                *, 
                inbound_endpoints: list[InboundEndpoint]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchNodeError(_Model):
        code: Optional[str]
        error_details: Optional[list[NameValuePair]]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                error_details: Optional[list[NameValuePair]] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchNodeFile(_Model):
        is_directory: Optional[bool]
        name: Optional[str]
        properties: Optional[FileProperties]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_directory: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[FileProperties] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchNodeFillType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PACK = "pack"
        SPREAD = "spread"


    class azure.batch.models.BatchNodeIdentityReference(_Model):
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchNodeInfo(_Model):
        affinity_id: Optional[str]
        node_id: Optional[str]
        node_url: Optional[str]
        pool_id: Optional[str]
        task_root_directory: Optional[str]
        task_root_directory_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                affinity_id: Optional[str] = ..., 
                node_id: Optional[str] = ..., 
                node_url: Optional[str] = ..., 
                pool_id: Optional[str] = ..., 
                task_root_directory: Optional[str] = ..., 
                task_root_directory_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchNodePlacementConfiguration(_Model):
        policy: Optional[Union[str, BatchNodePlacementPolicyType]]

        @overload
        def __init__(
                self, 
                *, 
                policy: Optional[Union[str, BatchNodePlacementPolicyType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchNodePlacementPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REGIONAL = "regional"
        ZONAL = "zonal"


    class azure.batch.models.BatchNodeRemoteLoginSettings(_Model):
        ipv6_remote_login_ip_address: Optional[str]
        ipv6_remote_login_port: Optional[int]
        remote_login_ip_address: str
        remote_login_port: int

        @overload
        def __init__(
                self, 
                *, 
                ipv6_remote_login_ip_address: Optional[str] = ..., 
                ipv6_remote_login_port: Optional[int] = ..., 
                remote_login_ip_address: str, 
                remote_login_port: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchNodeRemoveOptions(_Model):
        node_deallocation_option: Optional[Union[str, BatchNodeDeallocationOption]]
        node_ids: list[str]
        resize_timeout: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                node_deallocation_option: Optional[Union[str, BatchNodeDeallocationOption]] = ..., 
                node_ids: list[str], 
                resize_timeout: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchNodeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "creating"
        DEALLOCATED = "deallocated"
        DEALLOCATING = "deallocating"
        IDLE = "idle"
        LEAVING_POOL = "leavingpool"
        OFFLINE = "offline"
        PREEMPTED = "preempted"
        REBOOTING = "rebooting"
        REIMAGING = "reimaging"
        RUNNING = "running"
        STARTING = "starting"
        START_TASK_FAILED = "starttaskfailed"
        UNKNOWN = "unknown"
        UNUSABLE = "unusable"
        UPGRADING_OS = "upgradingos"
        WAITING_FOR_START_TASK = "waitingforstarttask"


    class azure.batch.models.BatchNodeUserCreateOptions(_Model):
        expiry_time: Optional[datetime]
        is_admin: Optional[bool]
        name: str
        password: Optional[str]
        ssh_public_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                expiry_time: Optional[datetime] = ..., 
                is_admin: Optional[bool] = ..., 
                name: str, 
                password: Optional[str] = ..., 
                ssh_public_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchNodeUserReplaceOptions(_Model):
        expiry_time: Optional[datetime]
        password: Optional[str]
        ssh_public_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                expiry_time: Optional[datetime] = ..., 
                password: Optional[str] = ..., 
                ssh_public_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchNodeVMExtension(_Model):
        instance_view: Optional[VMExtensionInstanceView]
        provisioning_state: Optional[str]
        vm_extension: Optional[VMExtension]

        @overload
        def __init__(
                self, 
                *, 
                instance_view: Optional[VMExtensionInstanceView] = ..., 
                provisioning_state: Optional[str] = ..., 
                vm_extension: Optional[VMExtension] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchOsDisk(_Model):
        caching: Optional[Union[str, CachingType]]
        disk_size_gb: Optional[int]
        ephemeral_os_disk_settings: Optional[BatchDiffDiskSettings]
        managed_disk: Optional[ManagedDisk]
        write_accelerator_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                caching: Optional[Union[str, CachingType]] = ..., 
                disk_size_gb: Optional[int] = ..., 
                ephemeral_os_disk_settings: Optional[BatchDiffDiskSettings] = ..., 
                managed_disk: Optional[ManagedDisk] = ..., 
                write_accelerator_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchPool(_Model):
        allocation_state: Optional[Union[str, AllocationState]]
        allocation_state_transition_time: Optional[datetime]
        application_package_references: Optional[list[BatchApplicationPackageReference]]
        auto_scale_evaluation_interval: Optional[timedelta]
        auto_scale_formula: Optional[str]
        auto_scale_run: Optional[AutoScaleRun]
        creation_time: datetime
        current_dedicated_nodes: int
        current_low_priority_nodes: int
        display_name: Optional[str]
        enable_auto_scale: Optional[bool]
        enable_inter_node_communication: Optional[bool]
        etag: str
        id: str
        identity: Optional[BatchPoolIdentity]
        last_modified: datetime
        metadata: Optional[list[BatchMetadataItem]]
        mount_configuration: Optional[list[MountConfiguration]]
        network_configuration: Optional[NetworkConfiguration]
        pool_statistics: Optional[BatchPoolStatistics]
        resize_errors: Optional[list[ResizeError]]
        resize_timeout: Optional[timedelta]
        start_task: Optional[BatchStartTask]
        state: Union[str, BatchPoolState]
        state_transition_time: datetime
        target_dedicated_nodes: Optional[int]
        target_low_priority_nodes: Optional[int]
        task_scheduling_policy: Optional[BatchTaskSchedulingPolicy]
        task_slots_per_node: Optional[int]
        upgrade_policy: Optional[UpgradePolicy]
        url: str
        user_accounts: Optional[list[UserAccount]]
        virtual_machine_configuration: Optional[VirtualMachineConfiguration]
        vm_size: str

        @overload
        def __init__(
                self, 
                *, 
                start_task: Optional[BatchStartTask] = ..., 
                upgrade_policy: Optional[UpgradePolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchPoolCreateOptions(_Model):
        application_package_references: Optional[list[BatchApplicationPackageReference]]
        auto_scale_evaluation_interval: Optional[timedelta]
        auto_scale_formula: Optional[str]
        display_name: Optional[str]
        enable_auto_scale: Optional[bool]
        enable_inter_node_communication: Optional[bool]
        id: str
        metadata: Optional[list[BatchMetadataItem]]
        mount_configuration: Optional[list[MountConfiguration]]
        network_configuration: Optional[NetworkConfiguration]
        resize_timeout: Optional[timedelta]
        start_task: Optional[BatchStartTask]
        target_dedicated_nodes: Optional[int]
        target_low_priority_nodes: Optional[int]
        task_scheduling_policy: Optional[BatchTaskSchedulingPolicy]
        task_slots_per_node: Optional[int]
        upgrade_policy: Optional[UpgradePolicy]
        user_accounts: Optional[list[UserAccount]]
        virtual_machine_configuration: Optional[VirtualMachineConfiguration]
        vm_size: str

        @overload
        def __init__(
                self, 
                *, 
                application_package_references: Optional[list[BatchApplicationPackageReference]] = ..., 
                auto_scale_evaluation_interval: Optional[timedelta] = ..., 
                auto_scale_formula: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enable_auto_scale: Optional[bool] = ..., 
                enable_inter_node_communication: Optional[bool] = ..., 
                id: str, 
                metadata: Optional[list[BatchMetadataItem]] = ..., 
                mount_configuration: Optional[list[MountConfiguration]] = ..., 
                network_configuration: Optional[NetworkConfiguration] = ..., 
                resize_timeout: Optional[timedelta] = ..., 
                start_task: Optional[BatchStartTask] = ..., 
                target_dedicated_nodes: Optional[int] = ..., 
                target_low_priority_nodes: Optional[int] = ..., 
                task_scheduling_policy: Optional[BatchTaskSchedulingPolicy] = ..., 
                task_slots_per_node: Optional[int] = ..., 
                upgrade_policy: Optional[UpgradePolicy] = ..., 
                user_accounts: Optional[list[UserAccount]] = ..., 
                virtual_machine_configuration: Optional[VirtualMachineConfiguration] = ..., 
                vm_size: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchPoolEnableAutoScaleOptions(_Model):
        auto_scale_evaluation_interval: Optional[timedelta]
        auto_scale_formula: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_scale_evaluation_interval: Optional[timedelta] = ..., 
                auto_scale_formula: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchPoolEndpointConfiguration(_Model):
        inbound_nat_pools: list[BatchInboundNatPool]

        @overload
        def __init__(
                self, 
                *, 
                inbound_nat_pools: list[BatchInboundNatPool]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchPoolEvaluateAutoScaleOptions(_Model):
        auto_scale_formula: str

        @overload
        def __init__(
                self, 
                *, 
                auto_scale_formula: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchPoolIdentity(_Model):
        type: Union[str, BatchPoolIdentityType]
        user_assigned_identities: Optional[list[BatchUserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, BatchPoolIdentityType], 
                user_assigned_identities: Optional[list[BatchUserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchPoolIdentityReference(_Model):
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchPoolIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        USER_ASSIGNED = "UserAssigned"


    class azure.batch.models.BatchPoolInfo(_Model):
        auto_pool_specification: Optional[BatchAutoPoolSpecification]
        pool_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_pool_specification: Optional[BatchAutoPoolSpecification] = ..., 
                pool_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchPoolLifetimeOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JOB = "job"
        JOB_SCHEDULE = "jobschedule"


    class azure.batch.models.BatchPoolNodeCounts(_Model):
        dedicated: Optional[BatchNodeCounts]
        low_priority: Optional[BatchNodeCounts]
        pool_id: str

        @overload
        def __init__(
                self, 
                *, 
                dedicated: Optional[BatchNodeCounts] = ..., 
                low_priority: Optional[BatchNodeCounts] = ..., 
                pool_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchPoolReplaceOptions(_Model):
        application_package_references: list[BatchApplicationPackageReference]
        metadata: list[BatchMetadataItem]
        start_task: Optional[BatchStartTask]

        @overload
        def __init__(
                self, 
                *, 
                application_package_references: list[BatchApplicationPackageReference], 
                metadata: list[BatchMetadataItem], 
                start_task: Optional[BatchStartTask] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchPoolResizeOptions(_Model):
        node_deallocation_option: Optional[Union[str, BatchNodeDeallocationOption]]
        resize_timeout: Optional[timedelta]
        target_dedicated_nodes: Optional[int]
        target_low_priority_nodes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                node_deallocation_option: Optional[Union[str, BatchNodeDeallocationOption]] = ..., 
                resize_timeout: Optional[timedelta] = ..., 
                target_dedicated_nodes: Optional[int] = ..., 
                target_low_priority_nodes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchPoolResourceStatistics(_Model):
        avg_cpu_percentage: float
        avg_disk_gib: float
        avg_memory_gib: float
        disk_read_gib: float
        disk_read_iops: int
        disk_write_gib: float
        disk_write_iops: int
        last_update_time: datetime
        network_read_gib: float
        network_write_gib: float
        peak_disk_gib: float
        peak_memory_gib: float
        start_time: datetime

        @overload
        def __init__(
                self, 
                *, 
                avg_cpu_percentage: float, 
                avg_disk_gib: float, 
                avg_memory_gib: float, 
                disk_read_gib: float, 
                disk_read_iops: int, 
                disk_write_gib: float, 
                disk_write_iops: int, 
                last_update_time: datetime, 
                network_read_gib: float, 
                network_write_gib: float, 
                peak_disk_gib: float, 
                peak_memory_gib: float, 
                start_time: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchPoolSpecification(_Model):
        application_package_references: Optional[list[BatchApplicationPackageReference]]
        auto_scale_evaluation_interval: Optional[timedelta]
        auto_scale_formula: Optional[str]
        display_name: Optional[str]
        enable_auto_scale: Optional[bool]
        enable_inter_node_communication: Optional[bool]
        metadata: Optional[list[BatchMetadataItem]]
        mount_configuration: Optional[list[MountConfiguration]]
        network_configuration: Optional[NetworkConfiguration]
        resize_timeout: Optional[timedelta]
        start_task: Optional[BatchStartTask]
        target_dedicated_nodes: Optional[int]
        target_low_priority_nodes: Optional[int]
        task_scheduling_policy: Optional[BatchTaskSchedulingPolicy]
        task_slots_per_node: Optional[int]
        upgrade_policy: Optional[UpgradePolicy]
        user_accounts: Optional[list[UserAccount]]
        virtual_machine_configuration: Optional[VirtualMachineConfiguration]
        vm_size: str

        @overload
        def __init__(
                self, 
                *, 
                application_package_references: Optional[list[BatchApplicationPackageReference]] = ..., 
                auto_scale_evaluation_interval: Optional[timedelta] = ..., 
                auto_scale_formula: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enable_auto_scale: Optional[bool] = ..., 
                enable_inter_node_communication: Optional[bool] = ..., 
                metadata: Optional[list[BatchMetadataItem]] = ..., 
                mount_configuration: Optional[list[MountConfiguration]] = ..., 
                network_configuration: Optional[NetworkConfiguration] = ..., 
                resize_timeout: Optional[timedelta] = ..., 
                start_task: Optional[BatchStartTask] = ..., 
                target_dedicated_nodes: Optional[int] = ..., 
                target_low_priority_nodes: Optional[int] = ..., 
                task_scheduling_policy: Optional[BatchTaskSchedulingPolicy] = ..., 
                task_slots_per_node: Optional[int] = ..., 
                upgrade_policy: Optional[UpgradePolicy] = ..., 
                user_accounts: Optional[list[UserAccount]] = ..., 
                virtual_machine_configuration: Optional[VirtualMachineConfiguration] = ..., 
                vm_size: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchPoolState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        DELETING = "deleting"


    class azure.batch.models.BatchPoolStatistics(_Model):
        last_update_time: datetime
        resource_statistics: Optional[BatchPoolResourceStatistics]
        start_time: datetime
        url: str
        usage_statistics: Optional[BatchPoolUsageStatistics]

        @overload
        def __init__(
                self, 
                *, 
                last_update_time: datetime, 
                resource_statistics: Optional[BatchPoolResourceStatistics] = ..., 
                start_time: datetime, 
                url: str, 
                usage_statistics: Optional[BatchPoolUsageStatistics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchPoolUpdateOptions(_Model):
        application_package_references: Optional[list[BatchApplicationPackageReference]]
        display_name: Optional[str]
        enable_inter_node_communication: Optional[bool]
        metadata: Optional[list[BatchMetadataItem]]
        mount_configuration: Optional[list[MountConfiguration]]
        network_configuration: Optional[NetworkConfiguration]
        start_task: Optional[BatchStartTask]
        task_scheduling_policy: Optional[BatchTaskSchedulingPolicy]
        task_slots_per_node: Optional[int]
        upgrade_policy: Optional[UpgradePolicy]
        user_accounts: Optional[list[UserAccount]]
        virtual_machine_configuration: Optional[VirtualMachineConfiguration]
        vm_size: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                application_package_references: Optional[list[BatchApplicationPackageReference]] = ..., 
                display_name: Optional[str] = ..., 
                enable_inter_node_communication: Optional[bool] = ..., 
                metadata: Optional[list[BatchMetadataItem]] = ..., 
                mount_configuration: Optional[list[MountConfiguration]] = ..., 
                network_configuration: Optional[NetworkConfiguration] = ..., 
                start_task: Optional[BatchStartTask] = ..., 
                task_scheduling_policy: Optional[BatchTaskSchedulingPolicy] = ..., 
                task_slots_per_node: Optional[int] = ..., 
                upgrade_policy: Optional[UpgradePolicy] = ..., 
                user_accounts: Optional[list[UserAccount]] = ..., 
                virtual_machine_configuration: Optional[VirtualMachineConfiguration] = ..., 
                vm_size: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchPoolUsageMetrics(_Model):
        end_time: datetime
        pool_id: str
        start_time: datetime
        total_core_hours: float
        vm_size: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: datetime, 
                pool_id: str, 
                start_time: datetime, 
                total_core_hours: float, 
                vm_size: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchPoolUsageStatistics(_Model):
        dedicated_core_time: timedelta
        last_update_time: datetime
        start_time: datetime

        @overload
        def __init__(
                self, 
                *, 
                dedicated_core_time: timedelta, 
                last_update_time: datetime, 
                start_time: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchPublicIpAddressConfiguration(_Model):
        ip_address_ids: Optional[list[str]]
        ip_address_provisioning_type: Optional[Union[str, IpAddressProvisioningType]]
        ip_families: Optional[list[Union[str, IPFamily]]]
        ip_tags: Optional[list[IPTag]]

        @overload
        def __init__(
                self, 
                *, 
                ip_address_ids: Optional[list[str]] = ..., 
                ip_address_provisioning_type: Optional[Union[str, IpAddressProvisioningType]] = ..., 
                ip_families: Optional[list[Union[str, IPFamily]]] = ..., 
                ip_tags: Optional[list[IPTag]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchStartTask(_Model):
        command_line: str
        container_settings: Optional[BatchTaskContainerSettings]
        environment_settings: Optional[list[EnvironmentSetting]]
        max_task_retry_count: Optional[int]
        resource_files: Optional[list[ResourceFile]]
        user_identity: Optional[UserIdentity]
        wait_for_success: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                command_line: str, 
                container_settings: Optional[BatchTaskContainerSettings] = ..., 
                environment_settings: Optional[list[EnvironmentSetting]] = ..., 
                max_task_retry_count: Optional[int] = ..., 
                resource_files: Optional[list[ResourceFile]] = ..., 
                user_identity: Optional[UserIdentity] = ..., 
                wait_for_success: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchStartTaskInfo(_Model):
        container_info: Optional[BatchTaskContainerExecutionInfo]
        end_time: Optional[datetime]
        exit_code: Optional[int]
        failure_info: Optional[BatchTaskFailureInfo]
        last_retry_time: Optional[datetime]
        result: Optional[Union[str, BatchTaskExecutionResult]]
        retry_count: int
        start_time: datetime
        state: Union[str, BatchStartTaskState]

        @overload
        def __init__(
                self, 
                *, 
                container_info: Optional[BatchTaskContainerExecutionInfo] = ..., 
                end_time: Optional[datetime] = ..., 
                exit_code: Optional[int] = ..., 
                failure_info: Optional[BatchTaskFailureInfo] = ..., 
                last_retry_time: Optional[datetime] = ..., 
                result: Optional[Union[str, BatchTaskExecutionResult]] = ..., 
                retry_count: int, 
                start_time: datetime, 
                state: Union[str, BatchStartTaskState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchStartTaskState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        RUNNING = "running"


    class azure.batch.models.BatchSubtask(_Model):
        container_info: Optional[BatchTaskContainerExecutionInfo]
        end_time: Optional[datetime]
        exit_code: Optional[int]
        failure_info: Optional[BatchTaskFailureInfo]
        id: Optional[int]
        node_info: Optional[BatchNodeInfo]
        previous_state: Optional[Union[str, BatchSubtaskState]]
        previous_state_transition_time: Optional[datetime]
        result: Optional[Union[str, BatchTaskExecutionResult]]
        start_time: Optional[datetime]
        state: Optional[Union[str, BatchSubtaskState]]
        state_transition_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                container_info: Optional[BatchTaskContainerExecutionInfo] = ..., 
                end_time: Optional[datetime] = ..., 
                exit_code: Optional[int] = ..., 
                failure_info: Optional[BatchTaskFailureInfo] = ..., 
                id: Optional[int] = ..., 
                node_info: Optional[BatchNodeInfo] = ..., 
                previous_state: Optional[Union[str, BatchSubtaskState]] = ..., 
                previous_state_transition_time: Optional[datetime] = ..., 
                result: Optional[Union[str, BatchTaskExecutionResult]] = ..., 
                start_time: Optional[datetime] = ..., 
                state: Optional[Union[str, BatchSubtaskState]] = ..., 
                state_transition_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchSubtaskState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        PREPARING = "preparing"
        RUNNING = "running"


    class azure.batch.models.BatchSupportedImage(_Model):
        batch_support_end_of_life: Optional[datetime]
        capabilities: Optional[list[str]]
        image_reference: BatchVmImageReference
        node_agent_sku_id: str
        os_type: Union[str, OSType]
        verification_type: Union[str, ImageVerificationType]

        @overload
        def __init__(
                self, 
                *, 
                batch_support_end_of_life: Optional[datetime] = ..., 
                capabilities: Optional[list[str]] = ..., 
                image_reference: BatchVmImageReference, 
                node_agent_sku_id: str, 
                os_type: Union[str, OSType], 
                verification_type: Union[str, ImageVerificationType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchTask(_Model):
        affinity_info: Optional[BatchAffinityInfo]
        application_package_references: Optional[list[BatchApplicationPackageReference]]
        command_line: str
        constraints: Optional[BatchTaskConstraints]
        container_settings: Optional[BatchTaskContainerSettings]
        creation_time: datetime
        depends_on: Optional[BatchTaskDependencies]
        display_name: Optional[str]
        environment_settings: Optional[list[EnvironmentSetting]]
        etag: str
        execution_info: Optional[BatchTaskExecutionInfo]
        exit_conditions: Optional[ExitConditions]
        id: str
        last_modified: datetime
        multi_instance_settings: Optional[MultiInstanceSettings]
        node_info: Optional[BatchNodeInfo]
        output_files: Optional[list[OutputFile]]
        previous_state: Optional[Union[str, BatchTaskState]]
        previous_state_transition_time: Optional[datetime]
        required_slots: Optional[int]
        resource_files: Optional[list[ResourceFile]]
        state: Union[str, BatchTaskState]
        state_transition_time: datetime
        task_statistics: Optional[BatchTaskStatistics]
        url: str
        user_identity: Optional[UserIdentity]

        @overload
        def __init__(
                self, 
                *, 
                constraints: Optional[BatchTaskConstraints] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchTaskAddStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLIENT_ERROR = "clienterror"
        SERVER_ERROR = "servererror"
        SUCCESS = "success"


    class azure.batch.models.BatchTaskConstraints(_Model):
        max_task_retry_count: Optional[int]
        max_wall_clock_time: Optional[timedelta]
        retention_time: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                max_task_retry_count: Optional[int] = ..., 
                max_wall_clock_time: Optional[timedelta] = ..., 
                retention_time: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchTaskContainerExecutionInfo(_Model):
        container_id: Optional[str]
        error: Optional[str]
        state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                container_id: Optional[str] = ..., 
                error: Optional[str] = ..., 
                state: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchTaskContainerSettings(_Model):
        container_host_batch_bind_mounts: Optional[list[ContainerHostBatchBindMountEntry]]
        container_run_options: Optional[str]
        image_name: str
        registry: Optional[ContainerRegistryReference]
        working_directory: Optional[Union[str, ContainerWorkingDirectory]]

        @overload
        def __init__(
                self, 
                *, 
                container_host_batch_bind_mounts: Optional[list[ContainerHostBatchBindMountEntry]] = ..., 
                container_run_options: Optional[str] = ..., 
                image_name: str, 
                registry: Optional[ContainerRegistryReference] = ..., 
                working_directory: Optional[Union[str, ContainerWorkingDirectory]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchTaskCounts(_Model):
        active: int
        completed: int
        failed: int
        running: int
        succeeded: int

        @overload
        def __init__(
                self, 
                *, 
                active: int, 
                completed: int, 
                failed: int, 
                running: int, 
                succeeded: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchTaskCountsResult(_Model):
        task_counts: BatchTaskCounts
        task_slot_counts: BatchTaskSlotCounts

        @overload
        def __init__(
                self, 
                *, 
                task_counts: BatchTaskCounts, 
                task_slot_counts: BatchTaskSlotCounts
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchTaskCreateOptions(_Model):
        affinity_info: Optional[BatchAffinityInfo]
        application_package_references: Optional[list[BatchApplicationPackageReference]]
        command_line: str
        constraints: Optional[BatchTaskConstraints]
        container_settings: Optional[BatchTaskContainerSettings]
        depends_on: Optional[BatchTaskDependencies]
        display_name: Optional[str]
        environment_settings: Optional[list[EnvironmentSetting]]
        exit_conditions: Optional[ExitConditions]
        id: str
        multi_instance_settings: Optional[MultiInstanceSettings]
        output_files: Optional[list[OutputFile]]
        required_slots: Optional[int]
        resource_files: Optional[list[ResourceFile]]
        user_identity: Optional[UserIdentity]

        @overload
        def __init__(
                self, 
                *, 
                affinity_info: Optional[BatchAffinityInfo] = ..., 
                application_package_references: Optional[list[BatchApplicationPackageReference]] = ..., 
                command_line: str, 
                constraints: Optional[BatchTaskConstraints] = ..., 
                container_settings: Optional[BatchTaskContainerSettings] = ..., 
                depends_on: Optional[BatchTaskDependencies] = ..., 
                display_name: Optional[str] = ..., 
                environment_settings: Optional[list[EnvironmentSetting]] = ..., 
                exit_conditions: Optional[ExitConditions] = ..., 
                id: str, 
                multi_instance_settings: Optional[MultiInstanceSettings] = ..., 
                output_files: Optional[list[OutputFile]] = ..., 
                required_slots: Optional[int] = ..., 
                resource_files: Optional[list[ResourceFile]] = ..., 
                user_identity: Optional[UserIdentity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchTaskCreateResult(_Model):
        error: Optional[BatchError]
        etag: Optional[str]
        last_modified: Optional[datetime]
        location: Optional[str]
        status: Union[str, BatchTaskAddStatus]
        task_id: str

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[BatchError] = ..., 
                etag: Optional[str] = ..., 
                last_modified: Optional[datetime] = ..., 
                location: Optional[str] = ..., 
                status: Union[str, BatchTaskAddStatus], 
                task_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchTaskDependencies(_Model):
        task_id_ranges: Optional[list[BatchTaskIdRange]]
        task_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                task_id_ranges: Optional[list[BatchTaskIdRange]] = ..., 
                task_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchTaskExecutionInfo(_Model):
        container_info: Optional[BatchTaskContainerExecutionInfo]
        end_time: Optional[datetime]
        exit_code: Optional[int]
        failure_info: Optional[BatchTaskFailureInfo]
        last_requeue_time: Optional[datetime]
        last_retry_time: Optional[datetime]
        requeue_count: int
        result: Optional[Union[str, BatchTaskExecutionResult]]
        retry_count: int
        start_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                container_info: Optional[BatchTaskContainerExecutionInfo] = ..., 
                end_time: Optional[datetime] = ..., 
                exit_code: Optional[int] = ..., 
                failure_info: Optional[BatchTaskFailureInfo] = ..., 
                last_requeue_time: Optional[datetime] = ..., 
                last_retry_time: Optional[datetime] = ..., 
                requeue_count: int, 
                result: Optional[Union[str, BatchTaskExecutionResult]] = ..., 
                retry_count: int, 
                start_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchTaskExecutionResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILURE = "failure"
        SUCCESS = "success"


    class azure.batch.models.BatchTaskFailureInfo(_Model):
        category: Union[str, BatchErrorSourceCategory]
        code: Optional[str]
        details: Optional[list[NameValuePair]]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                category: Union[str, BatchErrorSourceCategory], 
                code: Optional[str] = ..., 
                details: Optional[list[NameValuePair]] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchTaskFailureMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_ACTION = "noaction"
        PERFORM_EXIT_OPTIONS_JOB_ACTION = "performexitoptionsjobaction"


    class azure.batch.models.BatchTaskGroup(_Model):
        task_values: list[BatchTaskCreateOptions]

        @overload
        def __init__(
                self, 
                *, 
                task_values: list[BatchTaskCreateOptions]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchTaskIdRange(_Model):
        end: int
        start: int

        @overload
        def __init__(
                self, 
                *, 
                end: int, 
                start: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchTaskInfo(_Model):
        execution_info: Optional[BatchTaskExecutionInfo]
        job_id: Optional[str]
        subtask_id: Optional[int]
        task_id: Optional[str]
        task_state: Union[str, BatchTaskState]
        task_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                execution_info: Optional[BatchTaskExecutionInfo] = ..., 
                job_id: Optional[str] = ..., 
                subtask_id: Optional[int] = ..., 
                task_id: Optional[str] = ..., 
                task_state: Union[str, BatchTaskState], 
                task_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchTaskSchedulingPolicy(_Model):
        job_default_order: Optional[Union[str, BatchJobDefaultOrder]]
        node_fill_type: Union[str, BatchNodeFillType]

        @overload
        def __init__(
                self, 
                *, 
                job_default_order: Optional[Union[str, BatchJobDefaultOrder]] = ..., 
                node_fill_type: Union[str, BatchNodeFillType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchTaskSlotCounts(_Model):
        active: int
        completed: int
        failed: int
        running: int
        succeeded: int

        @overload
        def __init__(
                self, 
                *, 
                active: int, 
                completed: int, 
                failed: int, 
                running: int, 
                succeeded: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchTaskState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        COMPLETED = "completed"
        PREPARING = "preparing"
        RUNNING = "running"


    class azure.batch.models.BatchTaskStatistics(_Model):
        kernel_cpu_time: timedelta
        last_update_time: datetime
        read_io_gib: float
        read_iops: int
        start_time: datetime
        url: str
        user_cpu_time: timedelta
        wait_time: timedelta
        wall_clock_time: timedelta
        write_io_gib: float
        write_iops: int

        @overload
        def __init__(
                self, 
                *, 
                kernel_cpu_time: timedelta, 
                last_update_time: datetime, 
                read_io_gib: float, 
                read_iops: int, 
                start_time: datetime, 
                url: str, 
                user_cpu_time: timedelta, 
                wait_time: timedelta, 
                wall_clock_time: timedelta, 
                write_io_gib: float, 
                write_iops: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchUefiSettings(_Model):
        secure_boot_enabled: Optional[bool]
        vtpm_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                secure_boot_enabled: Optional[bool] = ..., 
                vtpm_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchUserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchVmDiskSecurityProfile(_Model):
        security_encryption_type: Optional[Union[str, SecurityEncryptionTypes]]

        @overload
        def __init__(
                self, 
                *, 
                security_encryption_type: Optional[Union[str, SecurityEncryptionTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.BatchVmImageReference(_Model):
        community_gallery_image_id: Optional[str]
        exact_version: Optional[str]
        offer: Optional[str]
        publisher: Optional[str]
        shared_gallery_image_id: Optional[str]
        sku: Optional[str]
        version: Optional[str]
        virtual_machine_image_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                community_gallery_image_id: Optional[str] = ..., 
                offer: Optional[str] = ..., 
                publisher: Optional[str] = ..., 
                shared_gallery_image_id: Optional[str] = ..., 
                sku: Optional[str] = ..., 
                version: Optional[str] = ..., 
                virtual_machine_image_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.CachingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "none"
        READ_ONLY = "readonly"
        READ_WRITE = "readwrite"


    class azure.batch.models.CifsMountConfiguration(_Model):
        mount_options: Optional[str]
        password: str
        relative_mount_path: str
        source: str
        username: str

        @overload
        def __init__(
                self, 
                *, 
                mount_options: Optional[str] = ..., 
                password: str, 
                relative_mount_path: str, 
                source: str, 
                username: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.ContainerHostBatchBindMountEntry(_Model):
        is_read_only: Optional[bool]
        source: Optional[Union[str, ContainerHostDataPath]]

        @overload
        def __init__(
                self, 
                *, 
                is_read_only: Optional[bool] = ..., 
                source: Optional[Union[str, ContainerHostDataPath]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.ContainerHostDataPath(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATIONS = "Applications"
        JOB_PREP = "JobPrep"
        SHARED = "Shared"
        STARTUP = "Startup"
        TASK = "Task"
        VFS_MOUNTS = "VfsMounts"


    class azure.batch.models.ContainerRegistryReference(_Model):
        identity_reference: Optional[BatchNodeIdentityReference]
        password: Optional[str]
        registry_server: Optional[str]
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity_reference: Optional[BatchNodeIdentityReference] = ..., 
                password: Optional[str] = ..., 
                registry_server: Optional[str] = ..., 
                username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.ContainerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRI_COMPATIBLE = "criCompatible"
        DOCKER_COMPATIBLE = "dockerCompatible"


    class azure.batch.models.ContainerWorkingDirectory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINER_IMAGE_DEFAULT = "containerImageDefault"
        TASK_WORKING_DIRECTORY = "taskWorkingDirectory"


    class azure.batch.models.CreateTasksError(HttpResponseError):

        def __init__(
                self, 
                pending_tasks: Optional[List[BatchTaskCreateOptions]] = None, 
                failure_tasks: Optional[List[BatchTaskCreateResult]] = None, 
                errors: Optional[List[Exception]] = None
            ) -> None: ...


    class azure.batch.models.DataDisk(_Model):
        caching: Optional[Union[str, CachingType]]
        disk_size_gb: int
        logical_unit_number: int
        managed_disk: Optional[ManagedDisk]

        @overload
        def __init__(
                self, 
                *, 
                caching: Optional[Union[str, CachingType]] = ..., 
                disk_size_gb: int, 
                logical_unit_number: int, 
                managed_disk: Optional[ManagedDisk] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.DependencyAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOCK = "block"
        SATISFY = "satisfy"


    class azure.batch.models.DiffDiskPlacement(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CACHE_DISK = "cachedisk"


    class azure.batch.models.DisableBatchJobOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REQUEUE = "requeue"
        TERMINATE = "terminate"
        WAIT = "wait"


    class azure.batch.models.DiskCustomerManagedKey(_Model):
        identity_reference: Optional[BatchPoolIdentityReference]
        key_url: Optional[str]
        rotation_to_latest_key_version_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                identity_reference: Optional[BatchPoolIdentityReference] = ..., 
                key_url: Optional[str] = ..., 
                rotation_to_latest_key_version_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.DiskEncryptionConfiguration(_Model):
        customer_managed_key: Optional[DiskCustomerManagedKey]
        targets: Optional[list[Union[str, DiskEncryptionTarget]]]

        @overload
        def __init__(
                self, 
                *, 
                customer_managed_key: Optional[DiskCustomerManagedKey] = ..., 
                targets: Optional[list[Union[str, DiskEncryptionTarget]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.DiskEncryptionSetParameters(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.DiskEncryptionTarget(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OS_DISK = "osdisk"
        TEMPORARY_DISK = "temporarydisk"


    class azure.batch.models.DynamicVNetAssignmentScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JOB = "job"
        NONE = "none"


    class azure.batch.models.ElevationLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADMIN = "admin"
        NON_ADMIN = "nonadmin"


    class azure.batch.models.EnvironmentSetting(_Model):
        name: str
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.ExitCodeMapping(_Model):
        code: int
        exit_options: ExitOptions

        @overload
        def __init__(
                self, 
                *, 
                code: int, 
                exit_options: ExitOptions
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.ExitCodeRangeMapping(_Model):
        end: int
        exit_options: ExitOptions
        start: int

        @overload
        def __init__(
                self, 
                *, 
                end: int, 
                exit_options: ExitOptions, 
                start: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.ExitConditions(_Model):
        default: Optional[ExitOptions]
        exit_code_ranges: Optional[list[ExitCodeRangeMapping]]
        exit_codes: Optional[list[ExitCodeMapping]]
        file_upload_error: Optional[ExitOptions]
        pre_processing_error: Optional[ExitOptions]

        @overload
        def __init__(
                self, 
                *, 
                default: Optional[ExitOptions] = ..., 
                exit_code_ranges: Optional[list[ExitCodeRangeMapping]] = ..., 
                exit_codes: Optional[list[ExitCodeMapping]] = ..., 
                file_upload_error: Optional[ExitOptions] = ..., 
                pre_processing_error: Optional[ExitOptions] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.ExitOptions(_Model):
        dependency_action: Optional[Union[str, DependencyAction]]
        job_action: Optional[Union[str, BatchJobActionKind]]

        @overload
        def __init__(
                self, 
                *, 
                dependency_action: Optional[Union[str, DependencyAction]] = ..., 
                job_action: Optional[Union[str, BatchJobActionKind]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.FileProperties(_Model):
        content_length: int
        content_type: Optional[str]
        creation_time: Optional[datetime]
        file_mode: Optional[str]
        last_modified: datetime

        @overload
        def __init__(
                self, 
                *, 
                content_length: int, 
                content_type: Optional[str] = ..., 
                creation_time: Optional[datetime] = ..., 
                file_mode: Optional[str] = ..., 
                last_modified: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.HostEndpointSettings(_Model):
        in_vm_access_control_profile_reference_id: Optional[str]
        mode: Optional[Union[str, HostEndpointSettingsModeTypes]]

        @overload
        def __init__(
                self, 
                *, 
                in_vm_access_control_profile_reference_id: Optional[str] = ..., 
                mode: Optional[Union[str, HostEndpointSettingsModeTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.HostEndpointSettingsModeTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        ENFORCE = "Enforce"


    class azure.batch.models.IPFamily(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IPV4 = "IPv4"
        IPV6 = "IPv6"


    class azure.batch.models.IPTag(_Model):
        ip_tag_type: Optional[str]
        tag: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ip_tag_type: Optional[str] = ..., 
                tag: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.ImageVerificationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        UNVERIFIED = "unverified"
        VERIFIED = "verified"


    class azure.batch.models.InboundEndpoint(_Model):
        backend_port: int
        frontend_port: int
        name: str
        protocol: Union[str, InboundEndpointProtocol]
        public_fqdn: str
        public_ip_address: str

        @overload
        def __init__(
                self, 
                *, 
                backend_port: int, 
                frontend_port: int, 
                name: str, 
                protocol: Union[str, InboundEndpointProtocol], 
                public_fqdn: str, 
                public_ip_address: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.InboundEndpointProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TCP = "tcp"
        UDP = "udp"


    class azure.batch.models.InstanceViewStatus(_Model):
        code: Optional[str]
        display_status: Optional[str]
        level: Optional[Union[str, StatusLevelTypes]]
        message: Optional[str]
        time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                display_status: Optional[str] = ..., 
                level: Optional[Union[str, StatusLevelTypes]] = ..., 
                message: Optional[str] = ..., 
                time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.IpAddressProvisioningType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BATCH_MANAGED = "batchmanaged"
        NO_PUBLIC_IP_ADDRESSES = "nopublicipaddresses"
        USER_MANAGED = "usermanaged"


    class azure.batch.models.LinuxUserConfiguration(_Model):
        gid: Optional[int]
        ssh_private_key: Optional[str]
        uid: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                gid: Optional[int] = ..., 
                ssh_private_key: Optional[str] = ..., 
                uid: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.LoginMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BATCH = "batch"
        INTERACTIVE = "interactive"


    class azure.batch.models.ManagedDisk(_Model):
        disk_encryption_set: Optional[DiskEncryptionSetParameters]
        security_profile: Optional[BatchVmDiskSecurityProfile]
        storage_account_type: Optional[Union[str, StorageAccountType]]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_set: Optional[DiskEncryptionSetParameters] = ..., 
                security_profile: Optional[BatchVmDiskSecurityProfile] = ..., 
                storage_account_type: Optional[Union[str, StorageAccountType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.MountConfiguration(_Model):
        azure_blob_file_system_configuration: Optional[AzureBlobFileSystemConfiguration]
        azure_file_share_configuration: Optional[AzureFileShareConfiguration]
        cifs_mount_configuration: Optional[CifsMountConfiguration]
        nfs_mount_configuration: Optional[NfsMountConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                azure_blob_file_system_configuration: Optional[AzureBlobFileSystemConfiguration] = ..., 
                azure_file_share_configuration: Optional[AzureFileShareConfiguration] = ..., 
                cifs_mount_configuration: Optional[CifsMountConfiguration] = ..., 
                nfs_mount_configuration: Optional[NfsMountConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.MultiInstanceSettings(_Model):
        common_resource_files: Optional[list[ResourceFile]]
        coordination_command_line: str
        number_of_instances: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                common_resource_files: Optional[list[ResourceFile]] = ..., 
                coordination_command_line: str, 
                number_of_instances: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.NameValuePair(_Model):
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


    class azure.batch.models.NetworkConfiguration(_Model):
        dynamic_vnet_assignment_scope: Optional[Union[str, DynamicVNetAssignmentScope]]
        enable_accelerated_networking: Optional[bool]
        endpoint_configuration: Optional[BatchPoolEndpointConfiguration]
        public_ip_address_configuration: Optional[BatchPublicIpAddressConfiguration]
        subnet_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                dynamic_vnet_assignment_scope: Optional[Union[str, DynamicVNetAssignmentScope]] = ..., 
                enable_accelerated_networking: Optional[bool] = ..., 
                endpoint_configuration: Optional[BatchPoolEndpointConfiguration] = ..., 
                public_ip_address_configuration: Optional[BatchPublicIpAddressConfiguration] = ..., 
                subnet_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.NetworkSecurityGroupRule(_Model):
        access: Union[str, NetworkSecurityGroupRuleAccess]
        priority: int
        source_address_prefix: str
        source_port_ranges: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                access: Union[str, NetworkSecurityGroupRuleAccess], 
                priority: int, 
                source_address_prefix: str, 
                source_port_ranges: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.NetworkSecurityGroupRuleAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "allow"
        DENY = "deny"


    class azure.batch.models.NfsMountConfiguration(_Model):
        mount_options: Optional[str]
        relative_mount_path: str
        source: str

        @overload
        def __init__(
                self, 
                *, 
                mount_options: Optional[str] = ..., 
                relative_mount_path: str, 
                source: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.OSType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "linux"
        WINDOWS = "windows"


    class azure.batch.models.OutputFile(_Model):
        destination: OutputFileDestination
        file_pattern: str
        upload_options: OutputFileUploadConfiguration

        @overload
        def __init__(
                self, 
                *, 
                destination: OutputFileDestination, 
                file_pattern: str, 
                upload_options: OutputFileUploadConfiguration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.OutputFileBlobContainerDestination(_Model):
        container_url: str
        identity_reference: Optional[BatchNodeIdentityReference]
        path: Optional[str]
        upload_headers: Optional[list[OutputFileUploadHeader]]

        @overload
        def __init__(
                self, 
                *, 
                container_url: str, 
                identity_reference: Optional[BatchNodeIdentityReference] = ..., 
                path: Optional[str] = ..., 
                upload_headers: Optional[list[OutputFileUploadHeader]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.OutputFileDestination(_Model):
        container: Optional[OutputFileBlobContainerDestination]

        @overload
        def __init__(
                self, 
                *, 
                container: Optional[OutputFileBlobContainerDestination] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.OutputFileUploadCondition(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TASK_COMPLETION = "taskcompletion"
        TASK_FAILURE = "taskfailure"
        TASK_SUCCESS = "tasksuccess"


    class azure.batch.models.OutputFileUploadConfiguration(_Model):
        upload_condition: Union[str, OutputFileUploadCondition]

        @overload
        def __init__(
                self, 
                *, 
                upload_condition: Union[str, OutputFileUploadCondition]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.OutputFileUploadHeader(_Model):
        name: str
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.ProxyAgentSettings(_Model):
        enabled: Optional[bool]
        imds: Optional[HostEndpointSettings]
        wire_server: Optional[HostEndpointSettings]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                imds: Optional[HostEndpointSettings] = ..., 
                wire_server: Optional[HostEndpointSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.RecentBatchJob(_Model):
        id: Optional[str]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.ResizeError(_Model):
        code: Optional[str]
        error_values: Optional[list[NameValuePair]]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                error_values: Optional[list[NameValuePair]] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.ResourceFile(_Model):
        auto_storage_container_name: Optional[str]
        blob_prefix: Optional[str]
        file_mode: Optional[str]
        file_path: Optional[str]
        http_url: Optional[str]
        identity_reference: Optional[BatchNodeIdentityReference]
        storage_container_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_storage_container_name: Optional[str] = ..., 
                blob_prefix: Optional[str] = ..., 
                file_mode: Optional[str] = ..., 
                file_path: Optional[str] = ..., 
                http_url: Optional[str] = ..., 
                identity_reference: Optional[BatchNodeIdentityReference] = ..., 
                storage_container_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.RollingUpgradePolicy(_Model):
        enable_cross_zone_upgrade: Optional[bool]
        max_batch_instance_percent: Optional[int]
        max_unhealthy_instance_percent: Optional[int]
        max_unhealthy_upgraded_instance_percent: Optional[int]
        pause_time_between_batches: Optional[timedelta]
        prioritize_unhealthy_instances: Optional[bool]
        rollback_failed_instances_on_policy_breach: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enable_cross_zone_upgrade: Optional[bool] = ..., 
                max_batch_instance_percent: Optional[int] = ..., 
                max_unhealthy_instance_percent: Optional[int] = ..., 
                max_unhealthy_upgraded_instance_percent: Optional[int] = ..., 
                pause_time_between_batches: Optional[timedelta] = ..., 
                prioritize_unhealthy_instances: Optional[bool] = ..., 
                rollback_failed_instances_on_policy_breach: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.SchedulingState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.batch.models.SecurityEncryptionTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISK_WITH_VM_GUEST_STATE = "DiskWithVMGuestState"
        NON_PERSISTED_TPM = "NonPersistedTPM"
        VM_GUEST_STATE_ONLY = "VMGuestStateOnly"


    class azure.batch.models.SecurityProfile(_Model):
        encryption_at_host: Optional[bool]
        proxy_agent_settings: Optional[ProxyAgentSettings]
        security_type: Optional[Union[str, SecurityTypes]]
        uefi_settings: Optional[BatchUefiSettings]

        @overload
        def __init__(
                self, 
                *, 
                encryption_at_host: Optional[bool] = ..., 
                proxy_agent_settings: Optional[ProxyAgentSettings] = ..., 
                security_type: Optional[Union[str, SecurityTypes]] = ..., 
                uefi_settings: Optional[BatchUefiSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.SecurityTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIDENTIAL_VM = "confidentialvm"
        TRUSTED_LAUNCH = "trustedLaunch"


    class azure.batch.models.ServiceArtifactReference(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.StatusLevelTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        INFO = "Info"
        WARNING = "Warning"


    class azure.batch.models.StorageAccountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_LRS = "premium_lrs"
        STANDARD_LRS = "standard_lrs"
        STANDARD_SSDLRS = "standardssd_lrs"


    class azure.batch.models.UpgradeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "automatic"
        MANUAL = "manual"
        ROLLING = "rolling"


    class azure.batch.models.UpgradePolicy(_Model):
        automatic_os_upgrade_policy: Optional[AutomaticOsUpgradePolicy]
        mode: Union[str, UpgradeMode]
        rolling_upgrade_policy: Optional[RollingUpgradePolicy]

        @overload
        def __init__(
                self, 
                *, 
                automatic_os_upgrade_policy: Optional[AutomaticOsUpgradePolicy] = ..., 
                mode: Union[str, UpgradeMode], 
                rolling_upgrade_policy: Optional[RollingUpgradePolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.UploadBatchServiceLogsOptions(_Model):
        container_url: str
        end_time: Optional[datetime]
        identity_reference: Optional[BatchNodeIdentityReference]
        start_time: datetime

        @overload
        def __init__(
                self, 
                *, 
                container_url: str, 
                end_time: Optional[datetime] = ..., 
                identity_reference: Optional[BatchNodeIdentityReference] = ..., 
                start_time: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.UploadBatchServiceLogsResult(_Model):
        number_of_files_uploaded: int
        virtual_directory_name: str

        @overload
        def __init__(
                self, 
                *, 
                number_of_files_uploaded: int, 
                virtual_directory_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.UserAccount(_Model):
        elevation_level: Optional[Union[str, ElevationLevel]]
        linux_user_configuration: Optional[LinuxUserConfiguration]
        name: str
        password: str
        windows_user_configuration: Optional[WindowsUserConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                elevation_level: Optional[Union[str, ElevationLevel]] = ..., 
                linux_user_configuration: Optional[LinuxUserConfiguration] = ..., 
                name: str, 
                password: str, 
                windows_user_configuration: Optional[WindowsUserConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.UserIdentity(_Model):
        auto_user: Optional[AutoUserSpecification]
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_user: Optional[AutoUserSpecification] = ..., 
                username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.VMExtension(_Model):
        auto_upgrade_minor_version: Optional[bool]
        enable_automatic_upgrade: Optional[bool]
        name: str
        protected_settings: Optional[dict[str, str]]
        provision_after_extensions: Optional[list[str]]
        publisher: str
        settings: Optional[dict[str, str]]
        type: str
        type_handler_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_upgrade_minor_version: Optional[bool] = ..., 
                enable_automatic_upgrade: Optional[bool] = ..., 
                name: str, 
                protected_settings: Optional[dict[str, str]] = ..., 
                provision_after_extensions: Optional[list[str]] = ..., 
                publisher: str, 
                settings: Optional[dict[str, str]] = ..., 
                type: str, 
                type_handler_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.VMExtensionInstanceView(_Model):
        name: Optional[str]
        statuses: Optional[list[InstanceViewStatus]]
        sub_statuses: Optional[list[InstanceViewStatus]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                statuses: Optional[list[InstanceViewStatus]] = ..., 
                sub_statuses: Optional[list[InstanceViewStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.VirtualMachineConfiguration(_Model):
        container_configuration: Optional[BatchContainerConfiguration]
        data_disks: Optional[list[DataDisk]]
        disk_encryption_configuration: Optional[DiskEncryptionConfiguration]
        extensions: Optional[list[VMExtension]]
        image_reference: BatchVmImageReference
        license_type: Optional[str]
        node_agent_sku_id: str
        node_placement_configuration: Optional[BatchNodePlacementConfiguration]
        os_disk: Optional[BatchOsDisk]
        security_profile: Optional[SecurityProfile]
        service_artifact_reference: Optional[ServiceArtifactReference]
        windows_configuration: Optional[WindowsConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                container_configuration: Optional[BatchContainerConfiguration] = ..., 
                data_disks: Optional[list[DataDisk]] = ..., 
                disk_encryption_configuration: Optional[DiskEncryptionConfiguration] = ..., 
                extensions: Optional[list[VMExtension]] = ..., 
                image_reference: BatchVmImageReference, 
                license_type: Optional[str] = ..., 
                node_agent_sku_id: str, 
                node_placement_configuration: Optional[BatchNodePlacementConfiguration] = ..., 
                os_disk: Optional[BatchOsDisk] = ..., 
                security_profile: Optional[SecurityProfile] = ..., 
                service_artifact_reference: Optional[ServiceArtifactReference] = ..., 
                windows_configuration: Optional[WindowsConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.VirtualMachineInfo(_Model):
        image_reference: Optional[BatchVmImageReference]
        scale_set_vm_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                image_reference: Optional[BatchVmImageReference] = ..., 
                scale_set_vm_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.WindowsConfiguration(_Model):
        enable_automatic_updates: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enable_automatic_updates: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.batch.models.WindowsUserConfiguration(_Model):
        login_mode: Optional[Union[str, LoginMode]]

        @overload
        def __init__(
                self, 
                *, 
                login_mode: Optional[Union[str, LoginMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


```