```py
namespace azure.mgmt.storagecache

    class azure.mgmt.storagecache.StorageCacheManagementClient(_StorageCacheManagementClientOperationsMixin): implements ContextManager 
        aml_filesystems: AmlFilesystemsOperations
        asc_operations: AscOperationsOperations
        asc_usages: AscUsagesOperations
        auto_export_jobs: AutoExportJobsOperations
        auto_import_jobs: AutoImportJobsOperations
        caches: CachesOperations
        expansion_jobs: ExpansionJobsOperations
        import_jobs: ImportJobsOperations
        operations: Operations
        rebalance_jobs: RebalanceJobsOperations
        skus: SkusOperations
        storage_target: StorageTargetOperations
        storage_targets: StorageTargetsOperations
        usage_models: UsageModelsOperations

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

        @overload
        def check_aml_fs_subnets(
                self, 
                aml_filesystem_subnet_info: Optional[AmlFilesystemSubnetInfo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def check_aml_fs_subnets(
                self, 
                aml_filesystem_subnet_info: Optional[AmlFilesystemSubnetInfo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def check_aml_fs_subnets(
                self, 
                aml_filesystem_subnet_info: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @overload
        def get_required_aml_fs_subnets_size(
                self, 
                required_aml_filesystem_subnets_size_info: Optional[RequiredAmlFilesystemSubnetsSizeInfo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RequiredAmlFilesystemSubnetsSize: ...

        @overload
        def get_required_aml_fs_subnets_size(
                self, 
                required_aml_filesystem_subnets_size_info: Optional[RequiredAmlFilesystemSubnetsSizeInfo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RequiredAmlFilesystemSubnetsSize: ...

        @overload
        def get_required_aml_fs_subnets_size(
                self, 
                required_aml_filesystem_subnets_size_info: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RequiredAmlFilesystemSubnetsSize: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.storagecache.aio

    class azure.mgmt.storagecache.aio.StorageCacheManagementClient(_StorageCacheManagementClientOperationsMixin): implements AsyncContextManager 
        aml_filesystems: AmlFilesystemsOperations
        asc_operations: AscOperationsOperations
        asc_usages: AscUsagesOperations
        auto_export_jobs: AutoExportJobsOperations
        auto_import_jobs: AutoImportJobsOperations
        caches: CachesOperations
        expansion_jobs: ExpansionJobsOperations
        import_jobs: ImportJobsOperations
        operations: Operations
        rebalance_jobs: RebalanceJobsOperations
        skus: SkusOperations
        storage_target: StorageTargetOperations
        storage_targets: StorageTargetsOperations
        usage_models: UsageModelsOperations

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

        @overload
        async def check_aml_fs_subnets(
                self, 
                aml_filesystem_subnet_info: Optional[AmlFilesystemSubnetInfo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def check_aml_fs_subnets(
                self, 
                aml_filesystem_subnet_info: Optional[AmlFilesystemSubnetInfo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def check_aml_fs_subnets(
                self, 
                aml_filesystem_subnet_info: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @overload
        async def get_required_aml_fs_subnets_size(
                self, 
                required_aml_filesystem_subnets_size_info: Optional[RequiredAmlFilesystemSubnetsSizeInfo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RequiredAmlFilesystemSubnetsSize: ...

        @overload
        async def get_required_aml_fs_subnets_size(
                self, 
                required_aml_filesystem_subnets_size_info: Optional[RequiredAmlFilesystemSubnetsSizeInfo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RequiredAmlFilesystemSubnetsSize: ...

        @overload
        async def get_required_aml_fs_subnets_size(
                self, 
                required_aml_filesystem_subnets_size_info: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RequiredAmlFilesystemSubnetsSize: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.storagecache.aio.operations

    class azure.mgmt.storagecache.aio.operations.AmlFilesystemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def archive(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                archive_info: Optional[AmlFilesystemArchiveInfo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def archive(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                archive_info: Optional[AmlFilesystemArchiveInfo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def archive(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                archive_info: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                aml_filesystem: AmlFilesystem, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AmlFilesystem]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                aml_filesystem: AmlFilesystem, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AmlFilesystem]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                aml_filesystem: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AmlFilesystem]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                aml_filesystem: AmlFilesystemUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AmlFilesystem]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                aml_filesystem: AmlFilesystemUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AmlFilesystem]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                aml_filesystem: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AmlFilesystem]: ...

        @distributed_trace_async
        async def cancel_archive(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                **kwargs: Any
            ) -> AmlFilesystem: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[AmlFilesystem]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AmlFilesystem]: ...


    class azure.mgmt.storagecache.aio.operations.AscOperationsOperations:

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
            ) -> AscOperation: ...


    class azure.mgmt.storagecache.aio.operations.AscUsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ResourceUsage]: ...


    class azure.mgmt.storagecache.aio.operations.AutoExportJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_export_job_name: str, 
                auto_export_job: AutoExportJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutoExportJob]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_export_job_name: str, 
                auto_export_job: AutoExportJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutoExportJob]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_export_job_name: str, 
                auto_export_job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutoExportJob]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_export_job_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_export_job_name: str, 
                auto_export_job: AutoExportJobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutoExportJob]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_export_job_name: str, 
                auto_export_job: AutoExportJobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutoExportJob]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_export_job_name: str, 
                auto_export_job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutoExportJob]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_export_job_name: str, 
                **kwargs: Any
            ) -> AutoExportJob: ...

        @distributed_trace
        def list_by_aml_filesystem(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AutoExportJob]: ...


    class azure.mgmt.storagecache.aio.operations.AutoImportJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_import_job_name: str, 
                auto_import_job: AutoImportJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutoImportJob]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_import_job_name: str, 
                auto_import_job: AutoImportJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutoImportJob]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_import_job_name: str, 
                auto_import_job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutoImportJob]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_import_job_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_import_job_name: str, 
                auto_import_job: AutoImportJobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutoImportJob]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_import_job_name: str, 
                auto_import_job: AutoImportJobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutoImportJob]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_import_job_name: str, 
                auto_import_job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutoImportJob]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_import_job_name: str, 
                **kwargs: Any
            ) -> AutoImportJob: ...

        @distributed_trace
        def list_by_aml_filesystem(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AutoImportJob]: ...


    class azure.mgmt.storagecache.aio.operations.CachesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                cache: Cache, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cache]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                cache: Cache, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cache]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                cache: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cache]: ...

        @distributed_trace_async
        async def begin_debug_info(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_flush(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_pause_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                priming_job_id: Optional[PrimingJobIdParameter] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_pause_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                priming_job_id: Optional[PrimingJobIdParameter] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_pause_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                priming_job_id: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_resume_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                priming_job_id: Optional[PrimingJobIdParameter] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_resume_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                priming_job_id: Optional[PrimingJobIdParameter] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_resume_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                priming_job_id: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_space_allocation(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                space_allocation: Optional[List[StorageTargetSpaceAllocation]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_space_allocation(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                space_allocation: Optional[List[StorageTargetSpaceAllocation]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_space_allocation(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                space_allocation: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_start_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                primingjob: Optional[PrimingJob] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_start_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                primingjob: Optional[PrimingJob] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_start_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                primingjob: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_stop(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_stop_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                priming_job_id: Optional[PrimingJobIdParameter] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_stop_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                priming_job_id: Optional[PrimingJobIdParameter] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_stop_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                priming_job_id: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                cache: Optional[Cache] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cache]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                cache: Optional[Cache] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cache]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                cache: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cache]: ...

        @distributed_trace_async
        async def begin_upgrade_firmware(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> Cache: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Cache]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Cache]: ...


    class azure.mgmt.storagecache.aio.operations.ExpansionJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                expansion_job_name: str, 
                expansion_job: ExpansionJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExpansionJob]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                expansion_job_name: str, 
                expansion_job: ExpansionJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExpansionJob]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                expansion_job_name: str, 
                expansion_job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExpansionJob]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                expansion_job_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                expansion_job_name: str, 
                expansion_job: ExpansionJobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExpansionJob]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                expansion_job_name: str, 
                expansion_job: ExpansionJobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExpansionJob]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                expansion_job_name: str, 
                expansion_job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExpansionJob]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                expansion_job_name: str, 
                **kwargs: Any
            ) -> ExpansionJob: ...

        @distributed_trace
        def list_by_aml_filesystem(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ExpansionJob]: ...


    class azure.mgmt.storagecache.aio.operations.ImportJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                import_job_name: str, 
                import_job: ImportJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ImportJob]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                import_job_name: str, 
                import_job: ImportJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ImportJob]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                import_job_name: str, 
                import_job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ImportJob]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                import_job_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                import_job_name: str, 
                import_job: ImportJobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ImportJob]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                import_job_name: str, 
                import_job: ImportJobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ImportJob]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                import_job_name: str, 
                import_job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ImportJob]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                import_job_name: str, 
                **kwargs: Any
            ) -> ImportJob: ...

        @distributed_trace
        def list_by_aml_filesystem(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ImportJob]: ...


    class azure.mgmt.storagecache.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ApiOperation]: ...


    class azure.mgmt.storagecache.aio.operations.RebalanceJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-08-01', params_added_on={'2026-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'aml_filesystem_name', 'rebalance_job_name']}, api_versions_list=['2026-08-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                rebalance_job_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                rebalance_job_name: str, 
                properties: RebalanceJobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RebalanceJob]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                rebalance_job_name: str, 
                properties: RebalanceJobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RebalanceJob]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                rebalance_job_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RebalanceJob]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-08-01', params_added_on={'2026-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'aml_filesystem_name', 'rebalance_job_name', 'accept']}, api_versions_list=['2026-08-01'])
        async def get(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                rebalance_job_name: str, 
                **kwargs: Any
            ) -> RebalanceJob: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01', params_added_on={'2026-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'aml_filesystem_name', 'accept']}, api_versions_list=['2026-08-01'])
        def list_by_aml_filesystem(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RebalanceJob]: ...


    class azure.mgmt.storagecache.aio.operations.SkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ResourceSku]: ...


    class azure.mgmt.storagecache.aio.operations.StorageTargetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_flush(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                storage_target_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_invalidate(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                storage_target_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_resume(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                storage_target_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_suspend(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                storage_target_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


    class azure.mgmt.storagecache.aio.operations.StorageTargetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                storage_target_name: str, 
                storagetarget: StorageTarget, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageTarget]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                storage_target_name: str, 
                storagetarget: StorageTarget, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageTarget]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                storage_target_name: str, 
                storagetarget: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageTarget]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                storage_target_name: str, 
                *, 
                force: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_dns_refresh(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                storage_target_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_restore_defaults(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                storage_target_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                storage_target_name: str, 
                **kwargs: Any
            ) -> StorageTarget: ...

        @distributed_trace
        def list_by_cache(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StorageTarget]: ...


    class azure.mgmt.storagecache.aio.operations.UsageModelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[UsageModel]: ...


namespace azure.mgmt.storagecache.models

    class azure.mgmt.storagecache.models.AmlFilesystem(TrackedResource):
        id: str
        identity: Optional[AmlFilesystemIdentity]
        location: str
        name: str
        properties: Optional[AmlFilesystemProperties]
        sku: Optional[SkuName]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[AmlFilesystemIdentity] = ..., 
                location: str, 
                properties: Optional[AmlFilesystemProperties] = ..., 
                sku: Optional[SkuName] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagecache.models.AmlFilesystemArchive(_Model):
        filesystem_path: Optional[str]
        status: Optional[AmlFilesystemArchiveStatus]


    class azure.mgmt.storagecache.models.AmlFilesystemArchiveInfo(_Model):
        filesystem_path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                filesystem_path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.AmlFilesystemArchiveStatus(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        last_completion_time: Optional[datetime]
        last_started_time: Optional[datetime]
        percent_complete: Optional[int]
        state: Optional[Union[str, ArchiveStatusType]]


    class azure.mgmt.storagecache.models.AmlFilesystemCheckSubnetError(_Model):
        filesystem_subnet: Optional[AmlFilesystemCheckSubnetErrorFilesystemSubnet]

        @overload
        def __init__(
                self, 
                *, 
                filesystem_subnet: Optional[AmlFilesystemCheckSubnetErrorFilesystemSubnet] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.AmlFilesystemCheckSubnetErrorFilesystemSubnet(_Model):
        message: Optional[str]
        status: Optional[Union[str, FilesystemSubnetStatusType]]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                status: Optional[Union[str, FilesystemSubnetStatusType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.AmlFilesystemClientInfo(_Model):
        container_storage_interface: Optional[AmlFilesystemContainerStorageInterface]
        lustre_version: Optional[str]
        mgs_address: Optional[str]
        mount_command: Optional[str]


    class azure.mgmt.storagecache.models.AmlFilesystemContainerStorageInterface(_Model):
        persistent_volume: Optional[str]
        persistent_volume_claim: Optional[str]
        storage_class: Optional[str]


    class azure.mgmt.storagecache.models.AmlFilesystemEncryptionSettings(_Model):
        key_encryption_key: Optional[KeyVaultKeyReference]

        @overload
        def __init__(
                self, 
                *, 
                key_encryption_key: Optional[KeyVaultKeyReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.AmlFilesystemHealth(_Model):
        state: Optional[Union[str, AmlFilesystemHealthStateType]]
        status_code: Optional[str]
        status_description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                state: Optional[Union[str, AmlFilesystemHealthStateType]] = ..., 
                status_code: Optional[str] = ..., 
                status_description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.AmlFilesystemHealthStateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        DEGRADED = "Degraded"
        EXPANDING = "Expanding"
        MAINTENANCE = "Maintenance"
        TRANSITIONING = "Transitioning"
        UNAVAILABLE = "Unavailable"


    class azure.mgmt.storagecache.models.AmlFilesystemHsmSettings(_Model):
        container: str
        import_prefix: Optional[str]
        import_prefixes_initial: Optional[list[str]]
        logging_container: str

        @overload
        def __init__(
                self, 
                *, 
                container: str, 
                import_prefix: Optional[str] = ..., 
                import_prefixes_initial: Optional[list[str]] = ..., 
                logging_container: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.AmlFilesystemIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, AmlFilesystemIdentityType]]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentitiesValue]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, AmlFilesystemIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentitiesValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.AmlFilesystemIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.storagecache.models.AmlFilesystemProperties(_Model):
        client_info: Optional[AmlFilesystemClientInfo]
        cluster_uuid: Optional[str]
        current_storage_capacity_ti_b: Optional[float]
        encryption_settings: Optional[AmlFilesystemEncryptionSettings]
        filesystem_subnet: str
        health: Optional[AmlFilesystemHealth]
        hsm: Optional[AmlFilesystemPropertiesHsm]
        maintenance_window: AmlFilesystemPropertiesMaintenanceWindow
        provisioning_state: Optional[Union[str, AmlFilesystemProvisioningStateType]]
        root_squash_settings: Optional[AmlFilesystemRootSquashSettings]
        storage_capacity_ti_b: float
        throughput_provisioned_m_bps: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                encryption_settings: Optional[AmlFilesystemEncryptionSettings] = ..., 
                filesystem_subnet: str, 
                hsm: Optional[AmlFilesystemPropertiesHsm] = ..., 
                maintenance_window: AmlFilesystemPropertiesMaintenanceWindow, 
                root_squash_settings: Optional[AmlFilesystemRootSquashSettings] = ..., 
                storage_capacity_ti_b: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.AmlFilesystemPropertiesHsm(_Model):
        archive_status: Optional[list[AmlFilesystemArchive]]
        settings: Optional[AmlFilesystemHsmSettings]

        @overload
        def __init__(
                self, 
                *, 
                settings: Optional[AmlFilesystemHsmSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.AmlFilesystemPropertiesMaintenanceWindow(_Model):
        day_of_week: Optional[Union[str, MaintenanceDayOfWeekType]]
        time_of_day_utc: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                day_of_week: Optional[Union[str, MaintenanceDayOfWeekType]] = ..., 
                time_of_day_utc: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.AmlFilesystemProvisioningStateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.storagecache.models.AmlFilesystemRootSquashSettings(_Model):
        mode: Optional[Union[str, AmlFilesystemSquashMode]]
        no_squash_nid_lists: Optional[str]
        squash_gid: Optional[int]
        squash_uid: Optional[int]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, AmlFilesystemSquashMode]] = ..., 
                no_squash_nid_lists: Optional[str] = ..., 
                squash_gid: Optional[int] = ..., 
                squash_uid: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.AmlFilesystemSquashMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        NONE = "None"
        ROOT_ONLY = "RootOnly"


    class azure.mgmt.storagecache.models.AmlFilesystemSubnetInfo(_Model):
        filesystem_subnet: Optional[str]
        location: Optional[str]
        sku: Optional[SkuName]
        storage_capacity_ti_b: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                filesystem_subnet: Optional[str] = ..., 
                location: Optional[str] = ..., 
                sku: Optional[SkuName] = ..., 
                storage_capacity_ti_b: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.AmlFilesystemUpdate(_Model):
        properties: Optional[AmlFilesystemUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AmlFilesystemUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagecache.models.AmlFilesystemUpdateProperties(_Model):
        encryption_settings: Optional[AmlFilesystemEncryptionSettings]
        maintenance_window: Optional[AmlFilesystemUpdatePropertiesMaintenanceWindow]
        root_squash_settings: Optional[AmlFilesystemRootSquashSettings]

        @overload
        def __init__(
                self, 
                *, 
                encryption_settings: Optional[AmlFilesystemEncryptionSettings] = ..., 
                maintenance_window: Optional[AmlFilesystemUpdatePropertiesMaintenanceWindow] = ..., 
                root_squash_settings: Optional[AmlFilesystemRootSquashSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.AmlFilesystemUpdatePropertiesMaintenanceWindow(_Model):
        day_of_week: Optional[Union[str, MaintenanceDayOfWeekType]]
        time_of_day_utc: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                day_of_week: Optional[Union[str, MaintenanceDayOfWeekType]] = ..., 
                time_of_day_utc: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.ApiOperation(_Model):
        display: Optional[ApiOperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[ApiOperationProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[ApiOperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[ApiOperationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagecache.models.ApiOperationDisplay(_Model):
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


    class azure.mgmt.storagecache.models.ApiOperationProperties(_Model):
        service_specification: Optional[ApiOperationPropertiesServiceSpecification]

        @overload
        def __init__(
                self, 
                *, 
                service_specification: Optional[ApiOperationPropertiesServiceSpecification] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.ApiOperationPropertiesServiceSpecification(_Model):
        log_specifications: Optional[list[LogSpecification]]
        metric_specifications: Optional[list[MetricSpecification]]

        @overload
        def __init__(
                self, 
                *, 
                log_specifications: Optional[list[LogSpecification]] = ..., 
                metric_specifications: Optional[list[MetricSpecification]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.ArchiveStatusType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CANCELLING = "Cancelling"
        COMPLETED = "Completed"
        FAILED = "Failed"
        FS_SCAN_IN_PROGRESS = "FSScanInProgress"
        IDLE = "Idle"
        IN_PROGRESS = "InProgress"
        NOT_CONFIGURED = "NotConfigured"


    class azure.mgmt.storagecache.models.AscOperation(_Model):
        end_time: Optional[str]
        error: Optional[AscOperationErrorResponse]
        id: Optional[str]
        name: Optional[str]
        properties: Optional[AscOperationProperties]
        start_time: Optional[str]
        status: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[str] = ..., 
                error: Optional[AscOperationErrorResponse] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[AscOperationProperties] = ..., 
                start_time: Optional[str] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagecache.models.AscOperationErrorResponse(_Model):
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


    class azure.mgmt.storagecache.models.AscOperationProperties(_Model):
        output: Optional[dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                output: Optional[dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.AutoExportJob(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[AutoExportJobProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[AutoExportJobProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.AutoExportJobAdminStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"


    class azure.mgmt.storagecache.models.AutoExportJobProperties(_Model):
        admin_status: Optional[Union[str, AutoExportJobAdminStatus]]
        auto_export_prefixes: Optional[list[str]]
        provisioning_state: Optional[Union[str, AutoExportJobProvisioningStateType]]
        status: Optional[AutoExportJobPropertiesStatus]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                admin_status: Optional[Union[str, AutoExportJobAdminStatus]] = ..., 
                auto_export_prefixes: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagecache.models.AutoExportJobPropertiesStatus(_Model):
        current_iteration_files_discovered: Optional[int]
        current_iteration_files_exported: Optional[int]
        current_iteration_files_failed: Optional[int]
        current_iteration_mi_b_discovered: Optional[int]
        current_iteration_mi_b_exported: Optional[int]
        export_iteration_count: Optional[int]
        last_completion_time_utc: Optional[datetime]
        last_started_time_utc: Optional[datetime]
        last_successful_iteration_completion_time_utc: Optional[datetime]
        state: Optional[Union[str, AutoExportStatusType]]
        status_code: Optional[str]
        status_message: Optional[str]
        total_files_exported: Optional[int]
        total_files_failed: Optional[int]
        total_mi_b_exported: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                state: Optional[Union[str, AutoExportStatusType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.AutoExportJobProvisioningStateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.storagecache.models.AutoExportJobUpdate(_Model):
        properties: Optional[AutoExportJobUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AutoExportJobUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagecache.models.AutoExportJobUpdateProperties(_Model):
        admin_status: Optional[Union[str, AutoExportJobAdminStatus]]

        @overload
        def __init__(
                self, 
                *, 
                admin_status: Optional[Union[str, AutoExportJobAdminStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.AutoExportStatusType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        DISABLE_FAILED = "DisableFailed"
        DISABLING = "Disabling"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"


    class azure.mgmt.storagecache.models.AutoImportJob(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[AutoImportJobProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[AutoImportJobProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.AutoImportJobProperties(_Model):
        admin_status: Optional[Union[str, AutoImportJobPropertiesAdminStatus]]
        auto_import_prefixes: Optional[list[str]]
        conflict_resolution_mode: Optional[Union[str, ConflictResolutionMode]]
        enable_deletions: Optional[bool]
        maximum_errors: Optional[int]
        provisioning_state: Optional[Union[str, AutoImportJobPropertiesProvisioningState]]
        status: Optional[AutoImportJobPropertiesStatus]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                admin_status: Optional[Union[str, AutoImportJobPropertiesAdminStatus]] = ..., 
                auto_import_prefixes: Optional[list[str]] = ..., 
                conflict_resolution_mode: Optional[Union[str, ConflictResolutionMode]] = ..., 
                enable_deletions: Optional[bool] = ..., 
                maximum_errors: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagecache.models.AutoImportJobPropertiesAdminStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"


    class azure.mgmt.storagecache.models.AutoImportJobPropertiesProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.storagecache.models.AutoImportJobPropertiesStatus(_Model):
        blob_sync_events: Optional[AutoImportJobPropertiesStatusBlobSyncEvents]
        imported_directories: Optional[int]
        imported_files: Optional[int]
        imported_symlinks: Optional[int]
        last_completion_time_utc: Optional[datetime]
        last_started_time_utc: Optional[datetime]
        preexisting_directories: Optional[int]
        preexisting_files: Optional[int]
        preexisting_symlinks: Optional[int]
        rate_of_blob_import: Optional[int]
        rate_of_blob_walk: Optional[int]
        scan_end_time: Optional[datetime]
        scan_start_time: Optional[datetime]
        state: Optional[Union[str, AutoImportJobState]]
        status_code: Optional[str]
        status_message: Optional[str]
        total_blobs_imported: Optional[int]
        total_blobs_walked: Optional[int]
        total_conflicts: Optional[int]
        total_errors: Optional[int]


    class azure.mgmt.storagecache.models.AutoImportJobPropertiesStatusBlobSyncEvents(_Model):
        deletions: Optional[int]
        imported_directories: Optional[int]
        imported_files: Optional[int]
        imported_symlinks: Optional[int]
        last_change_feed_event_consumed_time: Optional[datetime]
        last_time_fully_synchronized: Optional[datetime]
        preexisting_directories: Optional[int]
        preexisting_files: Optional[int]
        preexisting_symlinks: Optional[int]
        rate_of_blob_import: Optional[int]
        total_blobs_imported: Optional[int]
        total_conflicts: Optional[int]
        total_errors: Optional[int]


    class azure.mgmt.storagecache.models.AutoImportJobState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        DISABLING = "Disabling"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"


    class azure.mgmt.storagecache.models.AutoImportJobUpdate(_Model):
        properties: Optional[AutoImportJobUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AutoImportJobUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagecache.models.AutoImportJobUpdateProperties(_Model):
        admin_status: Optional[Union[str, AutoImportJobUpdatePropertiesAdminStatus]]

        @overload
        def __init__(
                self, 
                *, 
                admin_status: Optional[Union[str, AutoImportJobUpdatePropertiesAdminStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.AutoImportJobUpdatePropertiesAdminStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"


    class azure.mgmt.storagecache.models.BlobNfsTarget(_Model):
        target: Optional[str]
        usage_model: Optional[str]
        verification_timer: Optional[int]
        write_back_timer: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                target: Optional[str] = ..., 
                usage_model: Optional[str] = ..., 
                verification_timer: Optional[int] = ..., 
                write_back_timer: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.Cache(ProxyResource):
        id: str
        identity: Optional[CacheIdentity]
        location: Optional[str]
        name: str
        properties: Optional[CacheProperties]
        sku: Optional[CacheSku]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[CacheIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[CacheProperties] = ..., 
                sku: Optional[CacheSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagecache.models.CacheActiveDirectorySettings(_Model):
        cache_net_bios_name: str
        credentials: Optional[CacheActiveDirectorySettingsCredentials]
        domain_joined: Optional[Union[str, DomainJoinedType]]
        domain_name: str
        domain_net_bios_name: str
        primary_dns_ip_address: str
        secondary_dns_ip_address: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cache_net_bios_name: str, 
                credentials: Optional[CacheActiveDirectorySettingsCredentials] = ..., 
                domain_name: str, 
                domain_net_bios_name: str, 
                primary_dns_ip_address: str, 
                secondary_dns_ip_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.CacheActiveDirectorySettingsCredentials(_Model):
        password: Optional[str]
        username: str

        @overload
        def __init__(
                self, 
                *, 
                password: Optional[str] = ..., 
                username: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.CacheDirectorySettings(_Model):
        active_directory: Optional[CacheActiveDirectorySettings]
        username_download: Optional[CacheUsernameDownloadSettings]

        @overload
        def __init__(
                self, 
                *, 
                active_directory: Optional[CacheActiveDirectorySettings] = ..., 
                username_download: Optional[CacheUsernameDownloadSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.CacheEncryptionSettings(_Model):
        key_encryption_key: Optional[KeyVaultKeyReference]
        rotation_to_latest_key_version_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                key_encryption_key: Optional[KeyVaultKeyReference] = ..., 
                rotation_to_latest_key_version_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.CacheHealth(_Model):
        conditions: Optional[list[Condition]]
        state: Optional[Union[str, HealthStateType]]
        status_description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                state: Optional[Union[str, HealthStateType]] = ..., 
                status_description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.CacheIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, CacheIdentityType]]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentitiesValue]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, CacheIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentitiesValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.CacheIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.storagecache.models.CacheNetworkSettings(_Model):
        dns_search_domain: Optional[str]
        dns_servers: Optional[list[str]]
        mtu: Optional[int]
        ntp_server: Optional[str]
        utility_addresses: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                dns_search_domain: Optional[str] = ..., 
                dns_servers: Optional[list[str]] = ..., 
                mtu: Optional[int] = ..., 
                ntp_server: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.CacheProperties(_Model):
        cache_size_gb: Optional[int]
        directory_services_settings: Optional[CacheDirectorySettings]
        encryption_settings: Optional[CacheEncryptionSettings]
        health: Optional[CacheHealth]
        mount_addresses: Optional[list[str]]
        network_settings: Optional[CacheNetworkSettings]
        priming_jobs: Optional[list[PrimingJob]]
        provisioning_state: Optional[Union[str, ProvisioningStateType]]
        security_settings: Optional[CacheSecuritySettings]
        space_allocation: Optional[list[StorageTargetSpaceAllocation]]
        subnet: Optional[str]
        upgrade_settings: Optional[CacheUpgradeSettings]
        upgrade_status: Optional[CacheUpgradeStatus]
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                cache_size_gb: Optional[int] = ..., 
                directory_services_settings: Optional[CacheDirectorySettings] = ..., 
                encryption_settings: Optional[CacheEncryptionSettings] = ..., 
                network_settings: Optional[CacheNetworkSettings] = ..., 
                priming_jobs: Optional[list[PrimingJob]] = ..., 
                security_settings: Optional[CacheSecuritySettings] = ..., 
                subnet: Optional[str] = ..., 
                upgrade_settings: Optional[CacheUpgradeSettings] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.CacheSecuritySettings(_Model):
        access_policies: Optional[list[NfsAccessPolicy]]

        @overload
        def __init__(
                self, 
                *, 
                access_policies: Optional[list[NfsAccessPolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.CacheSku(_Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.CacheUpgradeSettings(_Model):
        scheduled_time: Optional[datetime]
        upgrade_schedule_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                scheduled_time: Optional[datetime] = ..., 
                upgrade_schedule_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.CacheUpgradeStatus(_Model):
        current_firmware_version: Optional[str]
        firmware_update_deadline: Optional[datetime]
        firmware_update_status: Optional[Union[str, FirmwareStatusType]]
        last_firmware_update: Optional[datetime]
        pending_firmware_version: Optional[str]


    class azure.mgmt.storagecache.models.CacheUsernameDownloadSettings(_Model):
        auto_download_certificate: Optional[bool]
        ca_certificate_uri: Optional[str]
        credentials: Optional[CacheUsernameDownloadSettingsCredentials]
        encrypt_ldap_connection: Optional[bool]
        extended_groups: Optional[bool]
        group_file_uri: Optional[str]
        ldap_base_dn: Optional[str]
        ldap_server: Optional[str]
        require_valid_certificate: Optional[bool]
        user_file_uri: Optional[str]
        username_downloaded: Optional[Union[str, UsernameDownloadedType]]
        username_source: Optional[Union[str, UsernameSource]]

        @overload
        def __init__(
                self, 
                *, 
                auto_download_certificate: Optional[bool] = ..., 
                ca_certificate_uri: Optional[str] = ..., 
                credentials: Optional[CacheUsernameDownloadSettingsCredentials] = ..., 
                encrypt_ldap_connection: Optional[bool] = ..., 
                extended_groups: Optional[bool] = ..., 
                group_file_uri: Optional[str] = ..., 
                ldap_base_dn: Optional[str] = ..., 
                ldap_server: Optional[str] = ..., 
                require_valid_certificate: Optional[bool] = ..., 
                user_file_uri: Optional[str] = ..., 
                username_source: Optional[Union[str, UsernameSource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.CacheUsernameDownloadSettingsCredentials(_Model):
        bind_dn: Optional[str]
        bind_password: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                bind_dn: Optional[str] = ..., 
                bind_password: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.ClfsTarget(_Model):
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.CloudError(_Model):
        error: Optional[CloudErrorBody]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[CloudErrorBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.CloudErrorBody(_Model):
        code: Optional[str]
        details: Optional[list[CloudErrorBody]]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[list[CloudErrorBody]] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.Condition(_Model):
        message: Optional[str]
        timestamp: Optional[datetime]


    class azure.mgmt.storagecache.models.ConflictResolutionMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAIL = "Fail"
        OVERWRITE_ALWAYS = "OverwriteAlways"
        OVERWRITE_IF_DIRTY = "OverwriteIfDirty"
        SKIP = "Skip"


    class azure.mgmt.storagecache.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.storagecache.models.DomainJoinedType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        NO = "No"
        YES = "Yes"


    class azure.mgmt.storagecache.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.storagecache.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.storagecache.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.ExpansionJob(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ExpansionJobProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ExpansionJobProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.ExpansionJobProperties(_Model):
        new_storage_capacity_ti_b: Optional[float]
        provisioning_state: Optional[Union[str, ExpansionJobPropertiesProvisioningState]]
        rebalance_job_id: Optional[str]
        run_rebalance_job: Optional[bool]
        status: Optional[ExpansionJobPropertiesStatus]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                new_storage_capacity_ti_b: Optional[float] = ..., 
                run_rebalance_job: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagecache.models.ExpansionJobPropertiesProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.storagecache.models.ExpansionJobPropertiesStatus(_Model):
        completion_time_utc: Optional[datetime]
        percent_complete: Optional[float]
        start_time_utc: Optional[datetime]
        state: Optional[Union[str, ExpansionJobStatusType]]
        status_code: Optional[str]
        status_message: Optional[str]


    class azure.mgmt.storagecache.models.ExpansionJobStatusType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        ROLLING_BACK = "RollingBack"


    class azure.mgmt.storagecache.models.ExpansionJobUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.FilesystemSubnetStatusType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        OK = "Ok"


    class azure.mgmt.storagecache.models.FirmwareStatusType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "available"
        UNAVAILABLE = "unavailable"


    class azure.mgmt.storagecache.models.HealthStateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEGRADED = "Degraded"
        DOWN = "Down"
        FLUSHING = "Flushing"
        HEALTHY = "Healthy"
        START_FAILED = "StartFailed"
        STOPPED = "Stopped"
        STOPPING = "Stopping"
        TRANSITIONING = "Transitioning"
        UNKNOWN = "Unknown"
        UPGRADE_FAILED = "UpgradeFailed"
        UPGRADING = "Upgrading"
        WAITING_FOR_KEY = "WaitingForKey"


    class azure.mgmt.storagecache.models.ImportJob(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ImportJobProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ImportJobProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.ImportJobAdminStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CANCEL = "Cancel"


    class azure.mgmt.storagecache.models.ImportJobProperties(_Model):
        admin_status: Optional[Union[str, ImportJobAdminStatus]]
        conflict_resolution_mode: Optional[Union[str, ConflictResolutionMode]]
        import_prefixes: Optional[list[str]]
        maximum_errors: Optional[int]
        provisioning_state: Optional[Union[str, ImportJobProvisioningStateType]]
        status: Optional[ImportJobPropertiesStatus]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                admin_status: Optional[Union[str, ImportJobAdminStatus]] = ..., 
                conflict_resolution_mode: Optional[Union[str, ConflictResolutionMode]] = ..., 
                import_prefixes: Optional[list[str]] = ..., 
                maximum_errors: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagecache.models.ImportJobPropertiesStatus(_Model):
        blobs_imported_per_second: Optional[int]
        blobs_walked_per_second: Optional[int]
        imported_directories: Optional[int]
        imported_files: Optional[int]
        imported_symlinks: Optional[int]
        last_completion_time: Optional[datetime]
        last_started_time: Optional[datetime]
        preexisting_directories: Optional[int]
        preexisting_files: Optional[int]
        preexisting_symlinks: Optional[int]
        state: Optional[Union[str, ImportStatusType]]
        status_message: Optional[str]
        total_blobs_imported: Optional[int]
        total_blobs_walked: Optional[int]
        total_conflicts: Optional[int]
        total_errors: Optional[int]


    class azure.mgmt.storagecache.models.ImportJobProvisioningStateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.storagecache.models.ImportJobUpdate(_Model):
        properties: Optional[ImportJobUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ImportJobUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagecache.models.ImportJobUpdateProperties(_Model):
        admin_status: Optional[Union[str, ImportJobAdminStatus]]

        @overload
        def __init__(
                self, 
                *, 
                admin_status: Optional[Union[str, ImportJobAdminStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.ImportStatusType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CANCELLING = "Cancelling"
        COMPLETED = "Completed"
        COMPLETED_PARTIAL = "CompletedPartial"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"


    class azure.mgmt.storagecache.models.KeyVaultKeyReference(_Model):
        key_url: str
        source_vault: KeyVaultKeyReferenceSourceVault

        @overload
        def __init__(
                self, 
                *, 
                key_url: str, 
                source_vault: KeyVaultKeyReferenceSourceVault
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.KeyVaultKeyReferenceSourceVault(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.LogSpecification(_Model):
        display_name: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.MaintenanceDayOfWeekType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.storagecache.models.MetricAggregationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "Average"
        COUNT = "Count"
        MAXIMUM = "Maximum"
        MINIMUM = "Minimum"
        NONE = "None"
        NOT_SPECIFIED = "NotSpecified"
        TOTAL = "Total"


    class azure.mgmt.storagecache.models.MetricDimension(_Model):
        display_name: Optional[str]
        internal_name: Optional[str]
        name: Optional[str]
        to_be_exported_for_shoebox: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                internal_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                to_be_exported_for_shoebox: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.MetricSpecification(_Model):
        aggregation_type: Optional[str]
        dimensions: Optional[list[MetricDimension]]
        display_description: Optional[str]
        display_name: Optional[str]
        metric_class: Optional[str]
        name: Optional[str]
        supported_aggregation_types: Optional[list[Union[str, MetricAggregationType]]]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_type: Optional[str] = ..., 
                dimensions: Optional[list[MetricDimension]] = ..., 
                display_description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                metric_class: Optional[str] = ..., 
                name: Optional[str] = ..., 
                supported_aggregation_types: Optional[list[Union[str, MetricAggregationType]]] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.NamespaceJunction(_Model):
        namespace_path: Optional[str]
        nfs_access_policy: Optional[str]
        nfs_export: Optional[str]
        target_path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                namespace_path: Optional[str] = ..., 
                nfs_access_policy: Optional[str] = ..., 
                nfs_export: Optional[str] = ..., 
                target_path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.Nfs3Target(_Model):
        target: Optional[str]
        usage_model: Optional[str]
        verification_timer: Optional[int]
        write_back_timer: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                target: Optional[str] = ..., 
                usage_model: Optional[str] = ..., 
                verification_timer: Optional[int] = ..., 
                write_back_timer: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.NfsAccessPolicy(_Model):
        access_rules: list[NfsAccessRule]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                access_rules: list[NfsAccessRule], 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.NfsAccessRule(_Model):
        access: Union[str, NfsAccessRuleAccess]
        anonymous_gid: Optional[str]
        anonymous_uid: Optional[str]
        filter: Optional[str]
        root_squash: Optional[bool]
        scope: Union[str, NfsAccessRuleScope]
        submount_access: Optional[bool]
        suid: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                access: Union[str, NfsAccessRuleAccess], 
                anonymous_gid: Optional[str] = ..., 
                anonymous_uid: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                root_squash: Optional[bool] = ..., 
                scope: Union[str, NfsAccessRuleScope], 
                submount_access: Optional[bool] = ..., 
                suid: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.NfsAccessRuleAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO = "no"
        RO = "ro"
        RW = "rw"


    class azure.mgmt.storagecache.models.NfsAccessRuleScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"
        HOST = "host"
        NETWORK = "network"


    class azure.mgmt.storagecache.models.OperationalStateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUSY = "Busy"
        FLUSHING = "Flushing"
        READY = "Ready"
        SUSPENDED = "Suspended"


    class azure.mgmt.storagecache.models.PrimingJob(_Model):
        priming_job_details: Optional[str]
        priming_job_id: Optional[str]
        priming_job_name: str
        priming_job_percent_complete: Optional[float]
        priming_job_state: Optional[Union[str, PrimingJobState]]
        priming_job_status: Optional[str]
        priming_manifest_url: str

        @overload
        def __init__(
                self, 
                *, 
                priming_job_name: str, 
                priming_manifest_url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.PrimingJobIdParameter(_Model):
        priming_job_id: str

        @overload
        def __init__(
                self, 
                *, 
                priming_job_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.PrimingJobState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE = "Complete"
        PAUSED = "Paused"
        QUEUED = "Queued"
        RUNNING = "Running"


    class azure.mgmt.storagecache.models.ProvisioningStateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.storagecache.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.storagecache.models.ReasonCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_AVAILABLE_FOR_SUBSCRIPTION = "NotAvailableForSubscription"
        QUOTA_ID = "QuotaId"


    class azure.mgmt.storagecache.models.RebalanceJob(ProxyResource):
        id: str
        name: str
        properties: Optional[RebalanceJobProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RebalanceJobProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.RebalanceJobAdminStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CANCEL = "Cancel"


    class azure.mgmt.storagecache.models.RebalanceJobProperties(_Model):
        admin_status: Optional[Union[str, RebalanceJobAdminStatus]]
        expansion_job_id: Optional[str]
        provisioning_state: Optional[Union[str, RebalanceJobPropertiesProvisioningState]]
        status: Optional[RebalanceJobPropertiesStatus]


    class azure.mgmt.storagecache.models.RebalanceJobPropertiesProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.storagecache.models.RebalanceJobPropertiesStatus(_Model):
        balance_percent: Optional[float]
        bytes_moved: Optional[int]
        completion_time_utc: Optional[datetime]
        dirs_migrated: Optional[int]
        estimated_remaining_seconds: Optional[int]
        files_migrated: Optional[int]
        files_moved_per_second: Optional[float]
        percent_complete: Optional[float]
        start_time_utc: Optional[datetime]
        state: Optional[Union[str, RebalanceJobStatusType]]
        status_code: Optional[str]
        status_message: Optional[str]
        throughput_mi_bps: Optional[float]
        total_errors: Optional[int]
        total_skipped: Optional[int]


    class azure.mgmt.storagecache.models.RebalanceJobStatusType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CANCELLING = "Cancelling"
        COMPLETED = "Completed"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        ROLLING_BACK = "RollingBack"


    class azure.mgmt.storagecache.models.RebalanceJobUpdate(_Model):
        properties: Optional[RebalanceJobUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RebalanceJobUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.RebalanceJobUpdateProperties(_Model):
        admin_status: Optional[Union[str, RebalanceJobAdminStatus]]

        @overload
        def __init__(
                self, 
                *, 
                admin_status: Optional[Union[str, RebalanceJobAdminStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.RequiredAmlFilesystemSubnetsSize(_Model):
        filesystem_subnet_size: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                filesystem_subnet_size: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.RequiredAmlFilesystemSubnetsSizeInfo(_Model):
        sku: Optional[SkuName]
        storage_capacity_ti_b: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                sku: Optional[SkuName] = ..., 
                storage_capacity_ti_b: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.storagecache.models.ResourceSku(_Model):
        capabilities: Optional[list[ResourceSkuCapabilities]]
        location_info: Optional[list[ResourceSkuLocationInfo]]
        locations: Optional[list[str]]
        name: Optional[str]
        resource_type: Optional[str]
        restrictions: Optional[list[Restriction]]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: Optional[list[ResourceSkuCapabilities]] = ..., 
                location_info: Optional[list[ResourceSkuLocationInfo]] = ..., 
                name: Optional[str] = ..., 
                restrictions: Optional[list[Restriction]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.ResourceSkuCapabilities(_Model):
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


    class azure.mgmt.storagecache.models.ResourceSkuLocationInfo(_Model):
        location: Optional[str]
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.ResourceUsage(_Model):
        current_value: Optional[int]
        limit: Optional[int]
        name: Optional[ResourceUsageName]
        unit: Optional[str]


    class azure.mgmt.storagecache.models.ResourceUsageName(_Model):
        localized_value: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                localized_value: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.Restriction(_Model):
        reason_code: Optional[Union[str, ReasonCode]]
        type: Optional[str]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                reason_code: Optional[Union[str, ReasonCode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.SkuName(_Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.StorageTarget(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[StorageTargetProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StorageTargetProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.storagecache.models.StorageTargetProperties(_Model):
        allocation_percentage: Optional[int]
        blob_nfs: Optional[BlobNfsTarget]
        clfs: Optional[ClfsTarget]
        junctions: Optional[list[NamespaceJunction]]
        nfs3: Optional[Nfs3Target]
        provisioning_state: Optional[Union[str, ProvisioningStateType]]
        state: Optional[Union[str, OperationalStateType]]
        target_type: Union[str, StorageTargetType]
        unknown: Optional[UnknownTarget]

        @overload
        def __init__(
                self, 
                *, 
                blob_nfs: Optional[BlobNfsTarget] = ..., 
                clfs: Optional[ClfsTarget] = ..., 
                junctions: Optional[list[NamespaceJunction]] = ..., 
                nfs3: Optional[Nfs3Target] = ..., 
                state: Optional[Union[str, OperationalStateType]] = ..., 
                target_type: Union[str, StorageTargetType], 
                unknown: Optional[UnknownTarget] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.StorageTargetSpaceAllocation(_Model):
        allocation_percentage: Optional[int]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                allocation_percentage: Optional[int] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.StorageTargetType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB_NFS = "blobNfs"
        CLFS = "clfs"
        NFS3 = "nfs3"
        UNKNOWN = "unknown"


    class azure.mgmt.storagecache.models.SystemData(_Model):
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


    class azure.mgmt.storagecache.models.TrackedResource(Resource):
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


    class azure.mgmt.storagecache.models.UnknownTarget(_Model):
        attributes: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.UsageModel(_Model):
        display: Optional[UsageModelDisplay]
        model_name: Optional[str]
        target_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[UsageModelDisplay] = ..., 
                model_name: Optional[str] = ..., 
                target_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.UsageModelDisplay(_Model):
        description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storagecache.models.UserAssignedIdentitiesValue(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.storagecache.models.UsernameDownloadedType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        NO = "No"
        YES = "Yes"


    class azure.mgmt.storagecache.models.UsernameSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AD = "AD"
        FILE = "File"
        LDAP = "LDAP"
        NONE = "None"


namespace azure.mgmt.storagecache.operations

    class azure.mgmt.storagecache.operations.AmlFilesystemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def archive(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                archive_info: Optional[AmlFilesystemArchiveInfo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def archive(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                archive_info: Optional[AmlFilesystemArchiveInfo] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def archive(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                archive_info: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                aml_filesystem: AmlFilesystem, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AmlFilesystem]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                aml_filesystem: AmlFilesystem, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AmlFilesystem]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                aml_filesystem: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AmlFilesystem]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                aml_filesystem: AmlFilesystemUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AmlFilesystem]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                aml_filesystem: AmlFilesystemUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AmlFilesystem]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                aml_filesystem: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AmlFilesystem]: ...

        @distributed_trace
        def cancel_archive(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                **kwargs: Any
            ) -> AmlFilesystem: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[AmlFilesystem]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AmlFilesystem]: ...


    class azure.mgmt.storagecache.operations.AscOperationsOperations:

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
            ) -> AscOperation: ...


    class azure.mgmt.storagecache.operations.AscUsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[ResourceUsage]: ...


    class azure.mgmt.storagecache.operations.AutoExportJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_export_job_name: str, 
                auto_export_job: AutoExportJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutoExportJob]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_export_job_name: str, 
                auto_export_job: AutoExportJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutoExportJob]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_export_job_name: str, 
                auto_export_job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutoExportJob]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_export_job_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_export_job_name: str, 
                auto_export_job: AutoExportJobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutoExportJob]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_export_job_name: str, 
                auto_export_job: AutoExportJobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutoExportJob]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_export_job_name: str, 
                auto_export_job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutoExportJob]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_export_job_name: str, 
                **kwargs: Any
            ) -> AutoExportJob: ...

        @distributed_trace
        def list_by_aml_filesystem(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AutoExportJob]: ...


    class azure.mgmt.storagecache.operations.AutoImportJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_import_job_name: str, 
                auto_import_job: AutoImportJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutoImportJob]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_import_job_name: str, 
                auto_import_job: AutoImportJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutoImportJob]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_import_job_name: str, 
                auto_import_job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutoImportJob]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_import_job_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_import_job_name: str, 
                auto_import_job: AutoImportJobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutoImportJob]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_import_job_name: str, 
                auto_import_job: AutoImportJobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutoImportJob]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_import_job_name: str, 
                auto_import_job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutoImportJob]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                auto_import_job_name: str, 
                **kwargs: Any
            ) -> AutoImportJob: ...

        @distributed_trace
        def list_by_aml_filesystem(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AutoImportJob]: ...


    class azure.mgmt.storagecache.operations.CachesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                cache: Cache, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cache]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                cache: Cache, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cache]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                cache: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cache]: ...

        @distributed_trace
        def begin_debug_info(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_flush(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_pause_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                priming_job_id: Optional[PrimingJobIdParameter] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_pause_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                priming_job_id: Optional[PrimingJobIdParameter] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_pause_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                priming_job_id: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_resume_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                priming_job_id: Optional[PrimingJobIdParameter] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_resume_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                priming_job_id: Optional[PrimingJobIdParameter] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_resume_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                priming_job_id: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_space_allocation(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                space_allocation: Optional[List[StorageTargetSpaceAllocation]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_space_allocation(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                space_allocation: Optional[List[StorageTargetSpaceAllocation]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_space_allocation(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                space_allocation: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_start_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                primingjob: Optional[PrimingJob] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_start_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                primingjob: Optional[PrimingJob] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_start_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                primingjob: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_stop(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_stop_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                priming_job_id: Optional[PrimingJobIdParameter] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_stop_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                priming_job_id: Optional[PrimingJobIdParameter] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_stop_priming_job(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                priming_job_id: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                cache: Optional[Cache] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cache]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                cache: Optional[Cache] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cache]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                cache: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cache]: ...

        @distributed_trace
        def begin_upgrade_firmware(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> Cache: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Cache]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Cache]: ...


    class azure.mgmt.storagecache.operations.ExpansionJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                expansion_job_name: str, 
                expansion_job: ExpansionJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExpansionJob]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                expansion_job_name: str, 
                expansion_job: ExpansionJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExpansionJob]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                expansion_job_name: str, 
                expansion_job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExpansionJob]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                expansion_job_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                expansion_job_name: str, 
                expansion_job: ExpansionJobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExpansionJob]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                expansion_job_name: str, 
                expansion_job: ExpansionJobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExpansionJob]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                expansion_job_name: str, 
                expansion_job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExpansionJob]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                expansion_job_name: str, 
                **kwargs: Any
            ) -> ExpansionJob: ...

        @distributed_trace
        def list_by_aml_filesystem(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ExpansionJob]: ...


    class azure.mgmt.storagecache.operations.ImportJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                import_job_name: str, 
                import_job: ImportJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ImportJob]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                import_job_name: str, 
                import_job: ImportJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ImportJob]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                import_job_name: str, 
                import_job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ImportJob]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                import_job_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                import_job_name: str, 
                import_job: ImportJobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ImportJob]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                import_job_name: str, 
                import_job: ImportJobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ImportJob]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                import_job_name: str, 
                import_job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ImportJob]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                import_job_name: str, 
                **kwargs: Any
            ) -> ImportJob: ...

        @distributed_trace
        def list_by_aml_filesystem(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ImportJob]: ...


    class azure.mgmt.storagecache.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ApiOperation]: ...


    class azure.mgmt.storagecache.operations.RebalanceJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01', params_added_on={'2026-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'aml_filesystem_name', 'rebalance_job_name']}, api_versions_list=['2026-08-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                rebalance_job_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                rebalance_job_name: str, 
                properties: RebalanceJobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RebalanceJob]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                rebalance_job_name: str, 
                properties: RebalanceJobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RebalanceJob]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                rebalance_job_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RebalanceJob]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01', params_added_on={'2026-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'aml_filesystem_name', 'rebalance_job_name', 'accept']}, api_versions_list=['2026-08-01'])
        def get(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                rebalance_job_name: str, 
                **kwargs: Any
            ) -> RebalanceJob: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01', params_added_on={'2026-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'aml_filesystem_name', 'accept']}, api_versions_list=['2026-08-01'])
        def list_by_aml_filesystem(
                self, 
                resource_group_name: str, 
                aml_filesystem_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RebalanceJob]: ...


    class azure.mgmt.storagecache.operations.SkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ResourceSku]: ...


    class azure.mgmt.storagecache.operations.StorageTargetOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_flush(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                storage_target_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_invalidate(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                storage_target_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_resume(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                storage_target_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_suspend(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                storage_target_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...


    class azure.mgmt.storagecache.operations.StorageTargetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                storage_target_name: str, 
                storagetarget: StorageTarget, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageTarget]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                storage_target_name: str, 
                storagetarget: StorageTarget, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageTarget]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                storage_target_name: str, 
                storagetarget: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageTarget]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                storage_target_name: str, 
                *, 
                force: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_dns_refresh(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                storage_target_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_restore_defaults(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                storage_target_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                storage_target_name: str, 
                **kwargs: Any
            ) -> StorageTarget: ...

        @distributed_trace
        def list_by_cache(
                self, 
                resource_group_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> ItemPaged[StorageTarget]: ...


    class azure.mgmt.storagecache.operations.UsageModelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[UsageModel]: ...


namespace azure.mgmt.storagecache.types

    class azure.mgmt.storagecache.types.AmlFilesystem(TrackedResource):
        key "id": str
        key "identity": ForwardRef('AmlFilesystemIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('AmlFilesystemProperties', module='types')
        key "sku": ForwardRef('SkuName', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: AmlFilesystemIdentity
        location: str
        name: str
        properties: AmlFilesystemProperties
        sku: SkuName
        systemData: SystemData
        tags: dict[str, str]
        type: str
        zones: list[str]


    class azure.mgmt.storagecache.types.AmlFilesystemArchive(TypedDict, total=False):
        key "filesystemPath": str
        key "status": ForwardRef('AmlFilesystemArchiveStatus', module='types')
        filesystemPath: str
        status: AmlFilesystemArchiveStatus


    class azure.mgmt.storagecache.types.AmlFilesystemArchiveInfo(TypedDict, total=False):
        key "filesystemPath": str
        filesystemPath: str


    class azure.mgmt.storagecache.types.AmlFilesystemArchiveStatus(TypedDict, total=False):
        key "errorCode": str
        key "errorMessage": str
        key "lastCompletionTime": str
        key "lastStartedTime": str
        key "percentComplete": int
        key "state": Union[str, ArchiveStatusType]
        errorCode: str
        errorMessage: str
        lastCompletionTime: str
        lastStartedTime: str
        percentComplete: int
        state: Union[str, ArchiveStatusType]


    class azure.mgmt.storagecache.types.AmlFilesystemClientInfo(TypedDict, total=False):
        key "containerStorageInterface": ForwardRef('AmlFilesystemContainerStorageInterface', module='types')
        key "lustreVersion": str
        key "mgsAddress": str
        key "mountCommand": str
        containerStorageInterface: AmlFilesystemContainerStorageInterface
        lustreVersion: str
        mgsAddress: str
        mountCommand: str


    class azure.mgmt.storagecache.types.AmlFilesystemContainerStorageInterface(TypedDict, total=False):
        key "persistentVolume": str
        key "persistentVolumeClaim": str
        key "storageClass": str
        persistentVolume: str
        persistentVolumeClaim: str
        storageClass: str


    class azure.mgmt.storagecache.types.AmlFilesystemEncryptionSettings(TypedDict, total=False):
        key "keyEncryptionKey": ForwardRef('KeyVaultKeyReference', module='types')
        keyEncryptionKey: KeyVaultKeyReference


    class azure.mgmt.storagecache.types.AmlFilesystemHealth(TypedDict, total=False):
        key "state": Union[str, AmlFilesystemHealthStateType]
        key "statusCode": str
        key "statusDescription": str
        state: Union[str, AmlFilesystemHealthStateType]
        statusCode: str
        statusDescription: str


    class azure.mgmt.storagecache.types.AmlFilesystemHsmSettings(TypedDict, total=False):
        key "container": Required[str]
        key "importPrefix": str
        key "loggingContainer": Required[str]
        container: str
        importPrefix: str
        importPrefixesInitial: list[str]
        loggingContainer: str


    class azure.mgmt.storagecache.types.AmlFilesystemIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, AmlFilesystemIdentityType]
        principalId: str
        tenantId: str
        type: Union[str, AmlFilesystemIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentitiesValue]


    class azure.mgmt.storagecache.types.AmlFilesystemProperties(TypedDict, total=False):
        key "clientInfo": ForwardRef('AmlFilesystemClientInfo', module='types')
        key "clusterUuid": str
        key "currentStorageCapacityTiB": float
        key "encryptionSettings": ForwardRef('AmlFilesystemEncryptionSettings', module='types')
        key "filesystemSubnet": Required[str]
        key "health": ForwardRef('AmlFilesystemHealth', module='types')
        key "hsm": ForwardRef('AmlFilesystemPropertiesHsm', module='types')
        key "maintenanceWindow": Required[AmlFilesystemPropertiesMaintenanceWindow]
        key "provisioningState": Union[str, AmlFilesystemProvisioningStateType]
        key "rootSquashSettings": ForwardRef('AmlFilesystemRootSquashSettings', module='types')
        key "storageCapacityTiB": Required[float]
        key "throughputProvisionedMBps": int
        clientInfo: AmlFilesystemClientInfo
        clusterUuid: str
        currentStorageCapacityTiB: float
        encryptionSettings: AmlFilesystemEncryptionSettings
        filesystemSubnet: str
        health: AmlFilesystemHealth
        hsm: AmlFilesystemPropertiesHsm
        maintenanceWindow: AmlFilesystemPropertiesMaintenanceWindow
        provisioningState: Union[str, AmlFilesystemProvisioningStateType]
        rootSquashSettings: AmlFilesystemRootSquashSettings
        storageCapacityTiB: float
        throughputProvisionedMBps: int


    class azure.mgmt.storagecache.types.AmlFilesystemPropertiesHsm(TypedDict, total=False):
        key "settings": ForwardRef('AmlFilesystemHsmSettings', module='types')
        archiveStatus: list[AmlFilesystemArchive]
        settings: AmlFilesystemHsmSettings


    class azure.mgmt.storagecache.types.AmlFilesystemPropertiesMaintenanceWindow(TypedDict, total=False):
        key "dayOfWeek": Union[str, MaintenanceDayOfWeekType]
        key "timeOfDayUTC": str
        dayOfWeek: Union[str, MaintenanceDayOfWeekType]
        timeOfDayUTC: str


    class azure.mgmt.storagecache.types.AmlFilesystemRootSquashSettings(TypedDict, total=False):
        key "mode": Union[str, AmlFilesystemSquashMode]
        key "noSquashNidLists": str
        key "squashGID": int
        key "squashUID": int
        key "status": str
        mode: Union[str, AmlFilesystemSquashMode]
        noSquashNidLists: str
        squashGID: int
        squashUID: int
        status: str


    class azure.mgmt.storagecache.types.AmlFilesystemSubnetInfo(TypedDict, total=False):
        key "filesystemSubnet": str
        key "location": str
        key "sku": ForwardRef('SkuName', module='types')
        key "storageCapacityTiB": float
        filesystemSubnet: str
        location: str
        sku: SkuName
        storageCapacityTiB: float


    class azure.mgmt.storagecache.types.AmlFilesystemUpdate(TypedDict, total=False):
        key "properties": ForwardRef('AmlFilesystemUpdateProperties', module='types')
        properties: AmlFilesystemUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.storagecache.types.AmlFilesystemUpdateProperties(TypedDict, total=False):
        key "encryptionSettings": ForwardRef('AmlFilesystemEncryptionSettings', module='types')
        key "maintenanceWindow": ForwardRef('AmlFilesystemUpdatePropertiesMaintenanceWindow', module='types')
        key "rootSquashSettings": ForwardRef('AmlFilesystemRootSquashSettings', module='types')
        encryptionSettings: AmlFilesystemEncryptionSettings
        maintenanceWindow: AmlFilesystemUpdatePropertiesMaintenanceWindow
        rootSquashSettings: AmlFilesystemRootSquashSettings


    class azure.mgmt.storagecache.types.AmlFilesystemUpdatePropertiesMaintenanceWindow(TypedDict, total=False):
        key "dayOfWeek": Union[str, MaintenanceDayOfWeekType]
        key "timeOfDayUTC": str
        dayOfWeek: Union[str, MaintenanceDayOfWeekType]
        timeOfDayUTC: str


    class azure.mgmt.storagecache.types.AutoExportJob(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('AutoExportJobProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: AutoExportJobProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.storagecache.types.AutoExportJobProperties(TypedDict, total=False):
        key "adminStatus": Union[str, AutoExportJobAdminStatus]
        key "provisioningState": Union[str, AutoExportJobProvisioningStateType]
        key "status": ForwardRef('AutoExportJobPropertiesStatus', module='types')
        adminStatus: Union[str, AutoExportJobAdminStatus]
        autoExportPrefixes: list[str]
        provisioningState: Union[str, AutoExportJobProvisioningStateType]
        status: AutoExportJobPropertiesStatus


    class azure.mgmt.storagecache.types.AutoExportJobPropertiesStatus(TypedDict, total=False):
        key "currentIterationFilesDiscovered": int
        key "currentIterationFilesExported": int
        key "currentIterationFilesFailed": int
        key "currentIterationMiBDiscovered": int
        key "currentIterationMiBExported": int
        key "exportIterationCount": int
        key "lastCompletionTimeUTC": str
        key "lastStartedTimeUTC": str
        key "lastSuccessfulIterationCompletionTimeUTC": str
        key "state": Union[str, AutoExportStatusType]
        key "statusCode": str
        key "statusMessage": str
        key "totalFilesExported": int
        key "totalFilesFailed": int
        key "totalMiBExported": int
        currentIterationFilesDiscovered: int
        currentIterationFilesExported: int
        currentIterationFilesFailed: int
        currentIterationMiBDiscovered: int
        currentIterationMiBExported: int
        exportIterationCount: int
        lastCompletionTimeUTC: str
        lastStartedTimeUTC: str
        lastSuccessfulIterationCompletionTimeUTC: str
        state: Union[str, AutoExportStatusType]
        statusCode: str
        statusMessage: str
        totalFilesExported: int
        totalFilesFailed: int
        totalMiBExported: int


    class azure.mgmt.storagecache.types.AutoExportJobUpdate(TypedDict, total=False):
        key "properties": ForwardRef('AutoExportJobUpdateProperties', module='types')
        properties: AutoExportJobUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.storagecache.types.AutoExportJobUpdateProperties(TypedDict, total=False):
        key "adminStatus": Union[str, AutoExportJobAdminStatus]
        adminStatus: Union[str, AutoExportJobAdminStatus]


    class azure.mgmt.storagecache.types.AutoImportJob(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('AutoImportJobProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: AutoImportJobProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.storagecache.types.AutoImportJobProperties(TypedDict, total=False):
        key "adminStatus": Union[str, AutoImportJobPropertiesAdminStatus]
        key "conflictResolutionMode": Union[str, ConflictResolutionMode]
        key "enableDeletions": bool
        key "maximumErrors": int
        key "provisioningState": Union[str, AutoImportJobPropertiesProvisioningState]
        key "status": ForwardRef('AutoImportJobPropertiesStatus', module='types')
        adminStatus: Union[str, AutoImportJobPropertiesAdminStatus]
        autoImportPrefixes: list[str]
        conflictResolutionMode: Union[str, ConflictResolutionMode]
        enableDeletions: bool
        maximumErrors: int
        provisioningState: Union[str, AutoImportJobPropertiesProvisioningState]
        status: AutoImportJobPropertiesStatus


    class azure.mgmt.storagecache.types.AutoImportJobPropertiesStatus(TypedDict, total=False):
        key "blobSyncEvents": ForwardRef('AutoImportJobPropertiesStatusBlobSyncEvents', module='types')
        key "importedDirectories": int
        key "importedFiles": int
        key "importedSymlinks": int
        key "lastCompletionTimeUTC": str
        key "lastStartedTimeUTC": str
        key "preexistingDirectories": int
        key "preexistingFiles": int
        key "preexistingSymlinks": int
        key "rateOfBlobImport": int
        key "rateOfBlobWalk": int
        key "scanEndTime": str
        key "scanStartTime": str
        key "state": Union[str, AutoImportJobState]
        key "statusCode": str
        key "statusMessage": str
        key "totalBlobsImported": int
        key "totalBlobsWalked": int
        key "totalConflicts": int
        key "totalErrors": int
        blobSyncEvents: AutoImportJobPropertiesStatusBlobSyncEvents
        importedDirectories: int
        importedFiles: int
        importedSymlinks: int
        lastCompletionTimeUTC: str
        lastStartedTimeUTC: str
        preexistingDirectories: int
        preexistingFiles: int
        preexistingSymlinks: int
        rateOfBlobImport: int
        rateOfBlobWalk: int
        scanEndTime: str
        scanStartTime: str
        state: Union[str, AutoImportJobState]
        statusCode: str
        statusMessage: str
        totalBlobsImported: int
        totalBlobsWalked: int
        totalConflicts: int
        totalErrors: int


    class azure.mgmt.storagecache.types.AutoImportJobPropertiesStatusBlobSyncEvents(TypedDict, total=False):
        key "deletions": int
        key "importedDirectories": int
        key "importedFiles": int
        key "importedSymlinks": int
        key "lastChangeFeedEventConsumedTime": str
        key "lastTimeFullySynchronized": str
        key "preexistingDirectories": int
        key "preexistingFiles": int
        key "preexistingSymlinks": int
        key "rateOfBlobImport": int
        key "totalBlobsImported": int
        key "totalConflicts": int
        key "totalErrors": int
        deletions: int
        importedDirectories: int
        importedFiles: int
        importedSymlinks: int
        lastChangeFeedEventConsumedTime: str
        lastTimeFullySynchronized: str
        preexistingDirectories: int
        preexistingFiles: int
        preexistingSymlinks: int
        rateOfBlobImport: int
        totalBlobsImported: int
        totalConflicts: int
        totalErrors: int


    class azure.mgmt.storagecache.types.AutoImportJobUpdate(TypedDict, total=False):
        key "properties": ForwardRef('AutoImportJobUpdateProperties', module='types')
        properties: AutoImportJobUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.storagecache.types.AutoImportJobUpdateProperties(TypedDict, total=False):
        key "adminStatus": Union[str, AutoImportJobUpdatePropertiesAdminStatus]
        adminStatus: Union[str, AutoImportJobUpdatePropertiesAdminStatus]


    class azure.mgmt.storagecache.types.BlobNfsTarget(TypedDict, total=False):
        key "target": str
        key "usageModel": str
        key "verificationTimer": int
        key "writeBackTimer": int
        target: str
        usageModel: str
        verificationTimer: int
        writeBackTimer: int


    class azure.mgmt.storagecache.types.Cache(ProxyResource):
        key "id": str
        key "identity": ForwardRef('CacheIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": ForwardRef('CacheProperties', module='types')
        key "sku": ForwardRef('CacheSku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: CacheIdentity
        location: str
        name: str
        properties: CacheProperties
        sku: CacheSku
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.storagecache.types.CacheActiveDirectorySettings(TypedDict, total=False):
        key "cacheNetBiosName": Required[str]
        key "credentials": ForwardRef('CacheActiveDirectorySettingsCredentials', module='types')
        key "domainJoined": Union[str, DomainJoinedType]
        key "domainName": Required[str]
        key "domainNetBiosName": Required[str]
        key "primaryDnsIpAddress": Required[str]
        key "secondaryDnsIpAddress": str
        cacheNetBiosName: str
        credentials: CacheActiveDirectorySettingsCredentials
        domainJoined: Union[str, DomainJoinedType]
        domainName: str
        domainNetBiosName: str
        primaryDnsIpAddress: str
        secondaryDnsIpAddress: str


    class azure.mgmt.storagecache.types.CacheActiveDirectorySettingsCredentials(TypedDict, total=False):
        key "password": str
        key "username": Required[str]
        password: str
        username: str


    class azure.mgmt.storagecache.types.CacheDirectorySettings(TypedDict, total=False):
        key "activeDirectory": ForwardRef('CacheActiveDirectorySettings', module='types')
        key "usernameDownload": ForwardRef('CacheUsernameDownloadSettings', module='types')
        activeDirectory: CacheActiveDirectorySettings
        usernameDownload: CacheUsernameDownloadSettings


    class azure.mgmt.storagecache.types.CacheEncryptionSettings(TypedDict, total=False):
        key "keyEncryptionKey": ForwardRef('KeyVaultKeyReference', module='types')
        key "rotationToLatestKeyVersionEnabled": bool
        keyEncryptionKey: KeyVaultKeyReference
        rotationToLatestKeyVersionEnabled: bool


    class azure.mgmt.storagecache.types.CacheHealth(TypedDict, total=False):
        key "state": Union[str, HealthStateType]
        key "statusDescription": str
        conditions: list[Condition]
        state: Union[str, HealthStateType]
        statusDescription: str


    class azure.mgmt.storagecache.types.CacheIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, CacheIdentityType]
        principalId: str
        tenantId: str
        type: Union[str, CacheIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentitiesValue]


    class azure.mgmt.storagecache.types.CacheNetworkSettings(TypedDict, total=False):
        key "dnsSearchDomain": str
        key "mtu": int
        key "ntpServer": str
        dnsSearchDomain: str
        dnsServers: list[str]
        mtu: int
        ntpServer: str
        utilityAddresses: list[str]


    class azure.mgmt.storagecache.types.CacheProperties(TypedDict, total=False):
        key "cacheSizeGB": int
        key "directoryServicesSettings": ForwardRef('CacheDirectorySettings', module='types')
        key "encryptionSettings": ForwardRef('CacheEncryptionSettings', module='types')
        key "health": ForwardRef('CacheHealth', module='types')
        key "networkSettings": ForwardRef('CacheNetworkSettings', module='types')
        key "provisioningState": Union[str, ProvisioningStateType]
        key "securitySettings": ForwardRef('CacheSecuritySettings', module='types')
        key "subnet": str
        key "upgradeSettings": ForwardRef('CacheUpgradeSettings', module='types')
        key "upgradeStatus": ForwardRef('CacheUpgradeStatus', module='types')
        cacheSizeGB: int
        directoryServicesSettings: CacheDirectorySettings
        encryptionSettings: CacheEncryptionSettings
        health: CacheHealth
        mountAddresses: list[str]
        networkSettings: CacheNetworkSettings
        primingJobs: list[PrimingJob]
        provisioningState: Union[str, ProvisioningStateType]
        securitySettings: CacheSecuritySettings
        spaceAllocation: list[StorageTargetSpaceAllocation]
        subnet: str
        upgradeSettings: CacheUpgradeSettings
        upgradeStatus: CacheUpgradeStatus
        zones: list[str]


    class azure.mgmt.storagecache.types.CacheSecuritySettings(TypedDict, total=False):
        accessPolicies: list[NfsAccessPolicy]


    class azure.mgmt.storagecache.types.CacheSku(TypedDict, total=False):
        key "name": str
        name: str


    class azure.mgmt.storagecache.types.CacheUpgradeSettings(TypedDict, total=False):
        key "scheduledTime": str
        key "upgradeScheduleEnabled": bool
        scheduledTime: str
        upgradeScheduleEnabled: bool


    class azure.mgmt.storagecache.types.CacheUpgradeStatus(TypedDict, total=False):
        key "currentFirmwareVersion": str
        key "firmwareUpdateDeadline": str
        key "firmwareUpdateStatus": Union[str, FirmwareStatusType]
        key "lastFirmwareUpdate": str
        key "pendingFirmwareVersion": str
        currentFirmwareVersion: str
        firmwareUpdateDeadline: str
        firmwareUpdateStatus: Union[str, FirmwareStatusType]
        lastFirmwareUpdate: str
        pendingFirmwareVersion: str


    class azure.mgmt.storagecache.types.CacheUsernameDownloadSettings(TypedDict, total=False):
        key "autoDownloadCertificate": bool
        key "caCertificateURI": str
        key "credentials": ForwardRef('CacheUsernameDownloadSettingsCredentials', module='types')
        key "encryptLdapConnection": bool
        key "extendedGroups": bool
        key "groupFileURI": str
        key "ldapBaseDN": str
        key "ldapServer": str
        key "requireValidCertificate": bool
        key "userFileURI": str
        key "usernameDownloaded": Union[str, UsernameDownloadedType]
        key "usernameSource": Union[str, UsernameSource]
        autoDownloadCertificate: bool
        caCertificateURI: str
        credentials: CacheUsernameDownloadSettingsCredentials
        encryptLdapConnection: bool
        extendedGroups: bool
        groupFileURI: str
        ldapBaseDN: str
        ldapServer: str
        requireValidCertificate: bool
        userFileURI: str
        usernameDownloaded: Union[str, UsernameDownloadedType]
        usernameSource: Union[str, UsernameSource]


    class azure.mgmt.storagecache.types.CacheUsernameDownloadSettingsCredentials(TypedDict, total=False):
        key "bindDn": str
        key "bindPassword": str
        bindDn: str
        bindPassword: str


    class azure.mgmt.storagecache.types.ClfsTarget(TypedDict, total=False):
        key "target": str
        target: str


    class azure.mgmt.storagecache.types.Condition(TypedDict, total=False):
        key "message": str
        key "timestamp": str
        message: str
        timestamp: str


    class azure.mgmt.storagecache.types.ExpansionJob(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ExpansionJobProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ExpansionJobProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.storagecache.types.ExpansionJobProperties(TypedDict, total=False):
        key "newStorageCapacityTiB": float
        key "provisioningState": Union[str, ExpansionJobPropertiesProvisioningState]
        key "rebalanceJobId": str
        key "runRebalanceJob": bool
        key "status": ForwardRef('ExpansionJobPropertiesStatus', module='types')
        newStorageCapacityTiB: float
        provisioningState: Union[str, ExpansionJobPropertiesProvisioningState]
        rebalanceJobId: str
        runRebalanceJob: bool
        status: ExpansionJobPropertiesStatus


    class azure.mgmt.storagecache.types.ExpansionJobPropertiesStatus(TypedDict, total=False):
        key "completionTimeUTC": str
        key "percentComplete": float
        key "startTimeUTC": str
        key "state": Union[str, ExpansionJobStatusType]
        key "statusCode": str
        key "statusMessage": str
        completionTimeUTC: str
        percentComplete: float
        startTimeUTC: str
        state: Union[str, ExpansionJobStatusType]
        statusCode: str
        statusMessage: str


    class azure.mgmt.storagecache.types.ExpansionJobUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.storagecache.types.ImportJob(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ImportJobProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ImportJobProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.storagecache.types.ImportJobProperties(TypedDict, total=False):
        key "adminStatus": Union[str, ImportJobAdminStatus]
        key "conflictResolutionMode": Union[str, ConflictResolutionMode]
        key "maximumErrors": int
        key "provisioningState": Union[str, ImportJobProvisioningStateType]
        key "status": ForwardRef('ImportJobPropertiesStatus', module='types')
        adminStatus: Union[str, ImportJobAdminStatus]
        conflictResolutionMode: Union[str, ConflictResolutionMode]
        importPrefixes: list[str]
        maximumErrors: int
        provisioningState: Union[str, ImportJobProvisioningStateType]
        status: ImportJobPropertiesStatus


    class azure.mgmt.storagecache.types.ImportJobPropertiesStatus(TypedDict, total=False):
        key "blobsImportedPerSecond": int
        key "blobsWalkedPerSecond": int
        key "importedDirectories": int
        key "importedFiles": int
        key "importedSymlinks": int
        key "lastCompletionTime": str
        key "lastStartedTime": str
        key "preexistingDirectories": int
        key "preexistingFiles": int
        key "preexistingSymlinks": int
        key "state": Union[str, ImportStatusType]
        key "statusMessage": str
        key "totalBlobsImported": int
        key "totalBlobsWalked": int
        key "totalConflicts": int
        key "totalErrors": int
        blobsImportedPerSecond: int
        blobsWalkedPerSecond: int
        importedDirectories: int
        importedFiles: int
        importedSymlinks: int
        lastCompletionTime: str
        lastStartedTime: str
        preexistingDirectories: int
        preexistingFiles: int
        preexistingSymlinks: int
        state: Union[str, ImportStatusType]
        statusMessage: str
        totalBlobsImported: int
        totalBlobsWalked: int
        totalConflicts: int
        totalErrors: int


    class azure.mgmt.storagecache.types.ImportJobUpdate(TypedDict, total=False):
        key "properties": ForwardRef('ImportJobUpdateProperties', module='types')
        properties: ImportJobUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.storagecache.types.ImportJobUpdateProperties(TypedDict, total=False):
        key "adminStatus": Union[str, ImportJobAdminStatus]
        adminStatus: Union[str, ImportJobAdminStatus]


    class azure.mgmt.storagecache.types.KeyVaultKeyReference(TypedDict, total=False):
        key "keyUrl": Required[str]
        key "sourceVault": Required[KeyVaultKeyReferenceSourceVault]
        keyUrl: str
        sourceVault: KeyVaultKeyReferenceSourceVault


    class azure.mgmt.storagecache.types.KeyVaultKeyReferenceSourceVault(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.storagecache.types.NamespaceJunction(TypedDict, total=False):
        key "namespacePath": str
        key "nfsAccessPolicy": str
        key "nfsExport": str
        key "targetPath": str
        namespacePath: str
        nfsAccessPolicy: str
        nfsExport: str
        targetPath: str


    class azure.mgmt.storagecache.types.Nfs3Target(TypedDict, total=False):
        key "target": str
        key "usageModel": str
        key "verificationTimer": int
        key "writeBackTimer": int
        target: str
        usageModel: str
        verificationTimer: int
        writeBackTimer: int


    class azure.mgmt.storagecache.types.NfsAccessPolicy(TypedDict, total=False):
        key "accessRules": Required[list[NfsAccessRule]]
        key "name": Required[str]
        accessRules: list[NfsAccessRule]
        name: str


    class azure.mgmt.storagecache.types.NfsAccessRule(TypedDict, total=False):
        key "access": Required[Union[str, NfsAccessRuleAccess]]
        key "anonymousGID": str
        key "anonymousUID": str
        key "filter": str
        key "rootSquash": bool
        key "scope": Required[Union[str, NfsAccessRuleScope]]
        key "submountAccess": bool
        key "suid": bool
        access: Union[str, NfsAccessRuleAccess]
        anonymousGID: str
        anonymousUID: str
        filter: str
        rootSquash: bool
        scope: Union[str, NfsAccessRuleScope]
        submountAccess: bool
        suid: bool


    class azure.mgmt.storagecache.types.PrimingJob(TypedDict, total=False):
        key "primingJobDetails": str
        key "primingJobId": str
        key "primingJobName": Required[str]
        key "primingJobPercentComplete": float
        key "primingJobState": Union[str, PrimingJobState]
        key "primingJobStatus": str
        key "primingManifestUrl": Required[str]
        primingJobDetails: str
        primingJobId: str
        primingJobName: str
        primingJobPercentComplete: float
        primingJobState: Union[str, PrimingJobState]
        primingJobStatus: str
        primingManifestUrl: str


    class azure.mgmt.storagecache.types.PrimingJobIdParameter(TypedDict, total=False):
        key "primingJobId": Required[str]
        primingJobId: str


    class azure.mgmt.storagecache.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.storagecache.types.RebalanceJobUpdate(TypedDict, total=False):
        key "properties": ForwardRef('RebalanceJobUpdateProperties', module='types')
        properties: RebalanceJobUpdateProperties


    class azure.mgmt.storagecache.types.RebalanceJobUpdateProperties(TypedDict, total=False):
        key "adminStatus": Union[str, RebalanceJobAdminStatus]
        adminStatus: Union[str, RebalanceJobAdminStatus]


    class azure.mgmt.storagecache.types.RequiredAmlFilesystemSubnetsSizeInfo(TypedDict, total=False):
        key "sku": ForwardRef('SkuName', module='types')
        key "storageCapacityTiB": float
        sku: SkuName
        storageCapacityTiB: float


    class azure.mgmt.storagecache.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.storagecache.types.SkuName(TypedDict, total=False):
        key "name": str
        name: str


    class azure.mgmt.storagecache.types.StorageTarget(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('StorageTargetProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: StorageTargetProperties
        systemData: SystemData
        type: str


    class azure.mgmt.storagecache.types.StorageTargetProperties(TypedDict, total=False):
        key "allocationPercentage": int
        key "blobNfs": ForwardRef('BlobNfsTarget', module='types')
        key "clfs": ForwardRef('ClfsTarget', module='types')
        key "nfs3": ForwardRef('Nfs3Target', module='types')
        key "provisioningState": Union[str, ProvisioningStateType]
        key "state": Union[str, OperationalStateType]
        key "targetType": Required[Union[str, StorageTargetType]]
        key "unknown": ForwardRef('UnknownTarget', module='types')
        allocationPercentage: int
        blobNfs: BlobNfsTarget
        clfs: ClfsTarget
        junctions: list[NamespaceJunction]
        nfs3: Nfs3Target
        provisioningState: Union[str, ProvisioningStateType]
        state: Union[str, OperationalStateType]
        targetType: Union[str, StorageTargetType]
        unknown: UnknownTarget


    class azure.mgmt.storagecache.types.StorageTargetSpaceAllocation(TypedDict, total=False):
        key "allocationPercentage": int
        key "name": str
        allocationPercentage: int
        name: str


    class azure.mgmt.storagecache.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.storagecache.types.TrackedResource(Resource):
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


    class azure.mgmt.storagecache.types.UnknownTarget(TypedDict, total=False):
        attributes: dict[str, str]


    class azure.mgmt.storagecache.types.UserAssignedIdentitiesValue(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


```