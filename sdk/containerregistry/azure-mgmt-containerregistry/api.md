```py
namespace azure.mgmt.containerregistry

    class azure.mgmt.containerregistry.ContainerRegistryManagementClient: implements ContextManager 
        archive_versions: ArchiveVersionsOperations
        archives: ArchivesOperations
        cache_rules: CacheRulesOperations
        connected_registries: ConnectedRegistriesOperations
        credential_sets: CredentialSetsOperations
        export_pipelines: ExportPipelinesOperations
        import_pipelines: ImportPipelinesOperations
        operations: Operations
        pipeline_runs: PipelineRunsOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        registries: RegistriesOperations
        replications: ReplicationsOperations
        scope_maps: ScopeMapsOperations
        tokens: TokensOperations
        webhooks: WebhooksOperations

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


namespace azure.mgmt.containerregistry.aio

    class azure.mgmt.containerregistry.aio.ContainerRegistryManagementClient: implements AsyncContextManager 
        archive_versions: ArchiveVersionsOperations
        archives: ArchivesOperations
        cache_rules: CacheRulesOperations
        connected_registries: ConnectedRegistriesOperations
        credential_sets: CredentialSetsOperations
        export_pipelines: ExportPipelinesOperations
        import_pipelines: ImportPipelinesOperations
        operations: Operations
        pipeline_runs: PipelineRunsOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        registries: RegistriesOperations
        replications: ReplicationsOperations
        scope_maps: ScopeMapsOperations
        tokens: TokensOperations
        webhooks: WebhooksOperations

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


namespace azure.mgmt.containerregistry.aio.operations

    class azure.mgmt.containerregistry.aio.operations.ArchiveVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'package_type', 'archive_name', 'archive_version_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                archive_version_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ArchiveVersion]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'package_type', 'archive_name', 'archive_version_name']}, api_versions_list=['2026-03-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                archive_version_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'package_type', 'archive_name', 'archive_version_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                archive_version_name: str, 
                **kwargs: Any
            ) -> ArchiveVersion: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'package_type', 'archive_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ArchiveVersion]: ...


    class azure.mgmt.containerregistry.aio.operations.ArchivesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                archive_create_parameters: Archive, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Archive]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                archive_create_parameters: Archive, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Archive]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                archive_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Archive]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'package_type', 'archive_name']}, api_versions_list=['2026-03-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'package_type', 'archive_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                **kwargs: Any
            ) -> Archive: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'package_type', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Archive]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                archive_update_parameters: ArchiveUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Archive: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                archive_update_parameters: ArchiveUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Archive: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                archive_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Archive: ...


    class azure.mgmt.containerregistry.aio.operations.CacheRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                cache_rule_name: str, 
                cache_rule_create_parameters: CacheRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CacheRule]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                cache_rule_name: str, 
                cache_rule_create_parameters: CacheRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CacheRule]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                cache_rule_name: str, 
                cache_rule_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CacheRule]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                cache_rule_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                cache_rule_name: str, 
                cache_rule_update_parameters: CacheRuleUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CacheRule]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                cache_rule_name: str, 
                cache_rule_update_parameters: CacheRuleUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CacheRule]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                cache_rule_name: str, 
                cache_rule_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CacheRule]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                cache_rule_name: str, 
                **kwargs: Any
            ) -> CacheRule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CacheRule]: ...


    class azure.mgmt.containerregistry.aio.operations.ConnectedRegistriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                connected_registry_name: str, 
                connected_registry_create_parameters: ConnectedRegistry, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConnectedRegistry]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                connected_registry_name: str, 
                connected_registry_create_parameters: ConnectedRegistry, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConnectedRegistry]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                connected_registry_name: str, 
                connected_registry_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConnectedRegistry]: ...

        @distributed_trace_async
        async def begin_deactivate(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                connected_registry_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                connected_registry_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                connected_registry_name: str, 
                connected_registry_update_parameters: ConnectedRegistryUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConnectedRegistry]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                connected_registry_name: str, 
                connected_registry_update_parameters: ConnectedRegistryUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConnectedRegistry]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                connected_registry_name: str, 
                connected_registry_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConnectedRegistry]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                connected_registry_name: str, 
                **kwargs: Any
            ) -> ConnectedRegistry: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ConnectedRegistry]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'connected_registry_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        async def resync(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                connected_registry_name: str, 
                **kwargs: Any
            ) -> ConnectedRegistry: ...


    class azure.mgmt.containerregistry.aio.operations.CredentialSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                credential_set_name: str, 
                credential_set_create_parameters: CredentialSet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CredentialSet]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                credential_set_name: str, 
                credential_set_create_parameters: CredentialSet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CredentialSet]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                credential_set_name: str, 
                credential_set_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CredentialSet]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                credential_set_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                credential_set_name: str, 
                credential_set_update_parameters: CredentialSetUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CredentialSet]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                credential_set_name: str, 
                credential_set_update_parameters: CredentialSetUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CredentialSet]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                credential_set_name: str, 
                credential_set_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CredentialSet]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                credential_set_name: str, 
                **kwargs: Any
            ) -> CredentialSet: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CredentialSet]: ...


    class azure.mgmt.containerregistry.aio.operations.ExportPipelinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                export_pipeline_name: str, 
                export_pipeline_create_parameters: ExportPipeline, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExportPipeline]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                export_pipeline_name: str, 
                export_pipeline_create_parameters: ExportPipeline, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExportPipeline]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                export_pipeline_name: str, 
                export_pipeline_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExportPipeline]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'export_pipeline_name']}, api_versions_list=['2026-03-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                export_pipeline_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'export_pipeline_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                export_pipeline_name: str, 
                **kwargs: Any
            ) -> ExportPipeline: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ExportPipeline]: ...


    class azure.mgmt.containerregistry.aio.operations.ImportPipelinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                import_pipeline_name: str, 
                import_pipeline_create_parameters: ImportPipeline, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ImportPipeline]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                import_pipeline_name: str, 
                import_pipeline_create_parameters: ImportPipeline, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ImportPipeline]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                import_pipeline_name: str, 
                import_pipeline_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ImportPipeline]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'import_pipeline_name']}, api_versions_list=['2026-03-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                import_pipeline_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'import_pipeline_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                import_pipeline_name: str, 
                **kwargs: Any
            ) -> ImportPipeline: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ImportPipeline]: ...


    class azure.mgmt.containerregistry.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[OperationDefinition]: ...


    class azure.mgmt.containerregistry.aio.operations.PipelineRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                pipeline_run_name: str, 
                pipeline_run_create_parameters: PipelineRun, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PipelineRun]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                pipeline_run_name: str, 
                pipeline_run_create_parameters: PipelineRun, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PipelineRun]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                pipeline_run_name: str, 
                pipeline_run_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PipelineRun]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'pipeline_run_name']}, api_versions_list=['2026-03-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                pipeline_run_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'pipeline_run_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                pipeline_run_name: str, 
                **kwargs: Any
            ) -> PipelineRun: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PipelineRun]: ...


    class azure.mgmt.containerregistry.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.containerregistry.aio.operations.RegistriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                registry: Registry, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Registry]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                registry: Registry, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Registry]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                registry: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Registry]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_generate_credentials(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                generate_credentials_parameters: GenerateCredentialsParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GenerateCredentialsResult]: ...

        @overload
        async def begin_generate_credentials(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                generate_credentials_parameters: GenerateCredentialsParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GenerateCredentialsResult]: ...

        @overload
        async def begin_generate_credentials(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                generate_credentials_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GenerateCredentialsResult]: ...

        @overload
        async def begin_import_image(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                parameters: ImportImageParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_import_image(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                parameters: ImportImageParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_import_image(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                registry_update_parameters: RegistryUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Registry]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                registry_update_parameters: RegistryUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Registry]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                registry_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Registry]: ...

        @overload
        async def check_name_availability(
                self, 
                registry_name_check_request: RegistryNameCheckRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegistryNameStatus: ...

        @overload
        async def check_name_availability(
                self, 
                registry_name_check_request: RegistryNameCheckRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegistryNameStatus: ...

        @overload
        async def check_name_availability(
                self, 
                registry_name_check_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegistryNameStatus: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> Registry: ...

        @distributed_trace_async
        async def get_private_link_resource(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Registry]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Registry]: ...

        @distributed_trace_async
        async def list_credentials(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> RegistryListCredentialsResult: ...

        @distributed_trace
        def list_private_link_resources(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...

        @distributed_trace_async
        async def list_usages(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> RegistryUsageListResult: ...

        @overload
        async def regenerate_credential(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                regenerate_credential_parameters: RegenerateCredentialParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegistryListCredentialsResult: ...

        @overload
        async def regenerate_credential(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                regenerate_credential_parameters: RegenerateCredentialParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegistryListCredentialsResult: ...

        @overload
        async def regenerate_credential(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                regenerate_credential_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegistryListCredentialsResult: ...


    class azure.mgmt.containerregistry.aio.operations.ReplicationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                replication_name: str, 
                replication: Replication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Replication]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                replication_name: str, 
                replication: Replication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Replication]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                replication_name: str, 
                replication: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Replication]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                replication_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                replication_name: str, 
                replication_update_parameters: ReplicationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Replication]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                replication_name: str, 
                replication_update_parameters: ReplicationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Replication]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                replication_name: str, 
                replication_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Replication]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                replication_name: str, 
                **kwargs: Any
            ) -> Replication: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Replication]: ...


    class azure.mgmt.containerregistry.aio.operations.ScopeMapsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                scope_map_name: str, 
                scope_map_create_parameters: ScopeMap, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ScopeMap]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                scope_map_name: str, 
                scope_map_create_parameters: ScopeMap, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ScopeMap]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                scope_map_name: str, 
                scope_map_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ScopeMap]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                scope_map_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                scope_map_name: str, 
                scope_map_update_parameters: ScopeMapUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ScopeMap]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                scope_map_name: str, 
                scope_map_update_parameters: ScopeMapUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ScopeMap]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                scope_map_name: str, 
                scope_map_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ScopeMap]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                scope_map_name: str, 
                **kwargs: Any
            ) -> ScopeMap: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ScopeMap]: ...


    class azure.mgmt.containerregistry.aio.operations.TokensOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                token_name: str, 
                token_create_parameters: Token, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Token]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                token_name: str, 
                token_create_parameters: Token, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Token]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                token_name: str, 
                token_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Token]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                token_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                token_name: str, 
                token_update_parameters: TokenUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Token]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                token_name: str, 
                token_update_parameters: TokenUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Token]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                token_name: str, 
                token_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Token]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                token_name: str, 
                **kwargs: Any
            ) -> Token: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Token]: ...


    class azure.mgmt.containerregistry.aio.operations.WebhooksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                webhook_name: str, 
                webhook_create_parameters: WebhookCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Webhook]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                webhook_name: str, 
                webhook_create_parameters: WebhookCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Webhook]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                webhook_name: str, 
                webhook_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Webhook]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                webhook_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                webhook_name: str, 
                webhook_update_parameters: WebhookUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Webhook]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                webhook_name: str, 
                webhook_update_parameters: WebhookUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Webhook]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                webhook_name: str, 
                webhook_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Webhook]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                webhook_name: str, 
                **kwargs: Any
            ) -> Webhook: ...

        @distributed_trace_async
        async def get_callback_config(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                webhook_name: str, 
                **kwargs: Any
            ) -> CallbackConfig: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Webhook]: ...

        @distributed_trace
        def list_events(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                webhook_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Event]: ...

        @distributed_trace_async
        async def ping(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                webhook_name: str, 
                **kwargs: Any
            ) -> EventInfo: ...


namespace azure.mgmt.containerregistry.models

    class azure.mgmt.containerregistry.models.Action(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"


    class azure.mgmt.containerregistry.models.ActionsRequired(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        RECREATE = "Recreate"


    class azure.mgmt.containerregistry.models.ActivationProperties(_Model):
        status: Optional[Union[str, ActivationStatus]]


    class azure.mgmt.containerregistry.models.ActivationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        INACTIVE = "Inactive"


    class azure.mgmt.containerregistry.models.Actor(_Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.AdditionalAuthenticationProperties(_Model):
        authentication_type: str

        @overload
        def __init__(
                self, 
                *, 
                authentication_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.AdditionalAuthenticationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GOOGLE_ARTIFACT_REGISTRY = "GoogleArtifactRegistry"


    class azure.mgmt.containerregistry.models.Archive(ProxyResource):
        id: str
        name: str
        properties: Optional[ArchiveProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ArchiveProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.ArchivePackageSourceProperties(_Model):
        type: Optional[Union[str, PackageSourceType]]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, PackageSourceType]] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.ArchiveProperties(_Model):
        package_source: Optional[ArchivePackageSourceProperties]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        published_version: Optional[str]
        repository_endpoint: Optional[str]
        repository_endpoint_prefix: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                package_source: Optional[ArchivePackageSourceProperties] = ..., 
                published_version: Optional[str] = ..., 
                repository_endpoint_prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.ArchiveUpdateParameters(_Model):
        properties: Optional[ArchiveUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ArchiveUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.ArchiveUpdateProperties(_Model):
        published_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                published_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.ArchiveVersion(ProxyResource):
        id: str
        name: str
        properties: Optional[ArchiveVersionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ArchiveVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.ArchiveVersionProperties(_Model):
        archive_version_error_message: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                archive_version_error_message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.AuditLogStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.containerregistry.models.AuthCredential(_Model):
        credential_health: Optional[CredentialHealth]
        name: Optional[Union[str, CredentialName]]
        password_secret_identifier: Optional[str]
        username_secret_identifier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[Union[str, CredentialName]] = ..., 
                password_secret_identifier: Optional[str] = ..., 
                username_secret_identifier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.AutoGeneratedDomainNameLabelScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_REUSE = "NoReuse"
        RESOURCE_GROUP_REUSE = "ResourceGroupReuse"
        SUBSCRIPTION_REUSE = "SubscriptionReuse"
        TENANT_REUSE = "TenantReuse"
        UNSECURE = "Unsecure"


    class azure.mgmt.containerregistry.models.AzureADAuthenticationAsArmPolicy(_Model):
        status: Optional[Union[str, AzureADAuthenticationAsArmPolicyStatus]]

        @overload
        def __init__(
                self, 
                *, 
                status: Optional[Union[str, AzureADAuthenticationAsArmPolicyStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.AzureADAuthenticationAsArmPolicyStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.mgmt.containerregistry.models.CacheRule(ProxyResource):
        id: str
        identity: Optional[IdentityProperties]
        name: str
        properties: Optional[CacheRuleProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityProperties] = ..., 
                properties: Optional[CacheRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.CacheRuleProperties(_Model):
        additional_authentication_properties: Optional[AdditionalAuthenticationProperties]
        creation_date: Optional[datetime]
        credential_set_resource_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        source_repository: Optional[str]
        target_repository: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_authentication_properties: Optional[AdditionalAuthenticationProperties] = ..., 
                credential_set_resource_id: Optional[str] = ..., 
                source_repository: Optional[str] = ..., 
                target_repository: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.CacheRuleUpdateParameters(_Model):
        identity: Optional[IdentityProperties]
        properties: Optional[CacheRuleUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityProperties] = ..., 
                properties: Optional[CacheRuleUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.CacheRuleUpdateProperties(_Model):
        additional_authentication_properties: Optional[AdditionalAuthenticationProperties]
        credential_set_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_authentication_properties: Optional[AdditionalAuthenticationProperties] = ..., 
                credential_set_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.CallbackConfig(_Model):
        custom_headers: Optional[dict[str, str]]
        service_uri: str

        @overload
        def __init__(
                self, 
                *, 
                custom_headers: Optional[dict[str, str]] = ..., 
                service_uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.CertificateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCAL_DIRECTORY = "LocalDirectory"


    class azure.mgmt.containerregistry.models.ConnectedRegistry(ProxyResource):
        id: str
        name: str
        properties: Optional[ConnectedRegistryProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConnectedRegistryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.ConnectedRegistryMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MIRROR = "Mirror"
        READ_ONLY = "ReadOnly"
        READ_WRITE = "ReadWrite"
        REGISTRY = "Registry"


    class azure.mgmt.containerregistry.models.ConnectedRegistryProperties(_Model):
        activation: Optional[ActivationProperties]
        client_token_ids: Optional[list[str]]
        connection_state: Optional[Union[str, ConnectionState]]
        garbage_collection: Optional[GarbageCollectionProperties]
        last_activity_time: Optional[datetime]
        logging: Optional[LoggingProperties]
        login_server: Optional[LoginServerProperties]
        mode: Union[str, ConnectedRegistryMode]
        notifications_list: Optional[list[str]]
        parent: ParentProperties
        provisioning_state: Optional[Union[str, ProvisioningState]]
        registry_sync_result: Optional[RegistrySyncResult]
        status_details: Optional[list[StatusDetailProperties]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_token_ids: Optional[list[str]] = ..., 
                garbage_collection: Optional[GarbageCollectionProperties] = ..., 
                logging: Optional[LoggingProperties] = ..., 
                login_server: Optional[LoginServerProperties] = ..., 
                mode: Union[str, ConnectedRegistryMode], 
                notifications_list: Optional[list[str]] = ..., 
                parent: ParentProperties, 
                registry_sync_result: Optional[RegistrySyncResult] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.ConnectedRegistryUpdateParameters(_Model):
        properties: Optional[ConnectedRegistryUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConnectedRegistryUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.ConnectedRegistryUpdateProperties(_Model):
        client_token_ids: Optional[list[str]]
        garbage_collection: Optional[GarbageCollectionProperties]
        logging: Optional[LoggingProperties]
        notifications_list: Optional[list[str]]
        sync_properties: Optional[SyncUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                client_token_ids: Optional[list[str]] = ..., 
                garbage_collection: Optional[GarbageCollectionProperties] = ..., 
                logging: Optional[LoggingProperties] = ..., 
                notifications_list: Optional[list[str]] = ..., 
                sync_properties: Optional[SyncUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.ConnectionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFFLINE = "Offline"
        ONLINE = "Online"
        SYNCING = "Syncing"
        UNHEALTHY = "Unhealthy"


    class azure.mgmt.containerregistry.models.ConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.containerregistry.models.ContainerRegistryResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_CONTAINER_REGISTRY_REGISTRIES = "Microsoft.ContainerRegistry/registries"


    class azure.mgmt.containerregistry.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.containerregistry.models.CredentialHealth(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        status: Optional[Union[str, CredentialHealthStatus]]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                status: Optional[Union[str, CredentialHealthStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.CredentialHealthStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        UNHEALTHY = "Unhealthy"


    class azure.mgmt.containerregistry.models.CredentialName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREDENTIAL1 = "Credential1"


    class azure.mgmt.containerregistry.models.CredentialSet(ProxyResource):
        id: str
        identity: Optional[IdentityProperties]
        name: str
        properties: Optional[CredentialSetProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityProperties] = ..., 
                properties: Optional[CredentialSetProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.CredentialSetProperties(_Model):
        auth_credentials: Optional[list[AuthCredential]]
        creation_date: Optional[datetime]
        login_server: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                auth_credentials: Optional[list[AuthCredential]] = ..., 
                login_server: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.CredentialSetUpdateParameters(_Model):
        identity: Optional[IdentityProperties]
        properties: Optional[CredentialSetUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityProperties] = ..., 
                properties: Optional[CredentialSetUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.CredentialSetUpdateProperties(_Model):
        auth_credentials: Optional[list[AuthCredential]]

        @overload
        def __init__(
                self, 
                *, 
                auth_credentials: Optional[list[AuthCredential]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.DefaultAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.containerregistry.models.EncryptionProperty(_Model):
        key_vault_properties: Optional[KeyVaultProperties]
        status: Optional[Union[str, EncryptionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                key_vault_properties: Optional[KeyVaultProperties] = ..., 
                status: Optional[Union[str, EncryptionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.EncryptionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.mgmt.containerregistry.models.EndpointProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        I_PV4 = "IPv4"
        I_PV4_AND_I_PV6 = "IPv4AndIPv6"


    class azure.mgmt.containerregistry.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.containerregistry.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.containerregistry.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.Event(EventInfo):
        event_request_message: Optional[EventRequestMessage]
        event_response_message: Optional[EventResponseMessage]
        id: str

        @overload
        def __init__(
                self, 
                *, 
                event_request_message: Optional[EventRequestMessage] = ..., 
                event_response_message: Optional[EventResponseMessage] = ..., 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.EventContent(_Model):
        action: Optional[str]
        actor: Optional[Actor]
        id: Optional[str]
        request: Optional[Request]
        source: Optional[Source]
        target: Optional[Target]
        timestamp: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[str] = ..., 
                actor: Optional[Actor] = ..., 
                id: Optional[str] = ..., 
                request: Optional[Request] = ..., 
                source: Optional[Source] = ..., 
                target: Optional[Target] = ..., 
                timestamp: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.EventInfo(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.EventRequestMessage(_Model):
        content: Optional[EventContent]
        headers: Optional[dict[str, str]]
        method: Optional[str]
        request_uri: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[EventContent] = ..., 
                headers: Optional[dict[str, str]] = ..., 
                method: Optional[str] = ..., 
                request_uri: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.EventResponseMessage(_Model):
        content: Optional[str]
        headers: Optional[dict[str, str]]
        reason_phrase: Optional[str]
        status_code: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[str] = ..., 
                headers: Optional[dict[str, str]] = ..., 
                reason_phrase: Optional[str] = ..., 
                status_code: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.ExportPipeline(ProxyResource):
        id: str
        identity: Optional[IdentityProperties]
        location: Optional[str]
        name: str
        properties: Optional[ExportPipelineProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityProperties] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ExportPipelineProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.ExportPipelineProperties(_Model):
        options: Optional[list[Union[str, PipelineOptions]]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        target: ExportPipelineTargetProperties

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[list[Union[str, PipelineOptions]]] = ..., 
                target: ExportPipelineTargetProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.ExportPipelineTargetProperties(_Model):
        key_vault_uri: Optional[str]
        storage_access_mode: Optional[Union[str, StorageAccessMode]]
        type: Optional[str]
        uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_vault_uri: Optional[str] = ..., 
                storage_access_mode: Optional[Union[str, StorageAccessMode]] = ..., 
                type: Optional[str] = ..., 
                uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.ExportPolicy(_Model):
        status: Optional[Union[str, ExportPolicyStatus]]

        @overload
        def __init__(
                self, 
                *, 
                status: Optional[Union[str, ExportPolicyStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.ExportPolicyStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.mgmt.containerregistry.models.GarAuthenticationProperties(AdditionalAuthenticationProperties, discriminator='GoogleArtifactRegistry'):
        authentication_type: Literal[AdditionalAuthenticationType.GOOGLE_ARTIFACT_REGISTRY]
        project_number: str
        workload_identity_pool: str
        workload_identity_provider: str

        @overload
        def __init__(
                self, 
                *, 
                project_number: str, 
                workload_identity_pool: str, 
                workload_identity_provider: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.GarbageCollectionProperties(_Model):
        enabled: Optional[bool]
        schedule: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                schedule: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.GenerateCredentialsParameters(_Model):
        expiry: Optional[datetime]
        name: Optional[Union[str, TokenPasswordName]]
        token_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                expiry: Optional[datetime] = ..., 
                name: Optional[Union[str, TokenPasswordName]] = ..., 
                token_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.GenerateCredentialsResult(_Model):
        passwords: Optional[list[TokenPassword]]
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                passwords: Optional[list[TokenPassword]] = ..., 
                username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.IPRule(_Model):
        action: Optional[Union[str, Action]]
        ip_address_or_range: str

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, Action]] = ..., 
                ip_address_or_range: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.IdentityProperties(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ResourceIdentityType]]
        user_assigned_identities: Optional[dict[str, UserIdentityProperties]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResourceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserIdentityProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.ImportImageParameters(_Model):
        mode: Optional[Union[str, ImportMode]]
        source: ImportSource
        target_tags: Optional[list[str]]
        untagged_target_repositories: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, ImportMode]] = ..., 
                source: ImportSource, 
                target_tags: Optional[list[str]] = ..., 
                untagged_target_repositories: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.ImportMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FORCE = "Force"
        NO_FORCE = "NoForce"


    class azure.mgmt.containerregistry.models.ImportPipeline(ProxyResource):
        id: str
        identity: Optional[IdentityProperties]
        location: Optional[str]
        name: str
        properties: Optional[ImportPipelineProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityProperties] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ImportPipelineProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.ImportPipelineProperties(_Model):
        options: Optional[list[Union[str, PipelineOptions]]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        source: ImportPipelineSourceProperties
        trigger: Optional[PipelineTriggerProperties]

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[list[Union[str, PipelineOptions]]] = ..., 
                source: ImportPipelineSourceProperties, 
                trigger: Optional[PipelineTriggerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.ImportPipelineSourceProperties(_Model):
        key_vault_uri: Optional[str]
        storage_access_mode: Optional[Union[str, StorageAccessMode]]
        type: Optional[Union[str, PipelineSourceType]]
        uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_vault_uri: Optional[str] = ..., 
                storage_access_mode: Optional[Union[str, StorageAccessMode]] = ..., 
                type: Optional[Union[str, PipelineSourceType]] = ..., 
                uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.ImportSource(_Model):
        credentials: Optional[ImportSourceCredentials]
        registry_uri: Optional[str]
        resource_id: Optional[str]
        source_image: str

        @overload
        def __init__(
                self, 
                *, 
                credentials: Optional[ImportSourceCredentials] = ..., 
                registry_uri: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                source_image: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.ImportSourceCredentials(_Model):
        password: str
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                password: str, 
                username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.KeyVaultProperties(_Model):
        identity: Optional[str]
        key_identifier: Optional[str]
        key_rotation_enabled: Optional[bool]
        last_key_rotation_timestamp: Optional[datetime]
        versioned_key_identifier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[str] = ..., 
                key_identifier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.LogLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEBUG = "Debug"
        ERROR = "Error"
        INFORMATION = "Information"
        NONE = "None"
        WARNING = "Warning"


    class azure.mgmt.containerregistry.models.LoggingProperties(_Model):
        audit_log_status: Optional[Union[str, AuditLogStatus]]
        log_level: Optional[Union[str, LogLevel]]

        @overload
        def __init__(
                self, 
                *, 
                audit_log_status: Optional[Union[str, AuditLogStatus]] = ..., 
                log_level: Optional[Union[str, LogLevel]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.LoginServerProperties(_Model):
        host: Optional[str]
        tls: Optional[TlsProperties]


    class azure.mgmt.containerregistry.models.MetadataSearch(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.containerregistry.models.NetworkRuleBypassOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SERVICES = "AzureServices"
        NONE = "None"


    class azure.mgmt.containerregistry.models.NetworkRuleSet(_Model):
        default_action: Union[str, DefaultAction]
        ip_rules: Optional[list[IPRule]]
        virtual_network_rules: Optional[list[VirtualNetworkRule]]

        @overload
        def __init__(
                self, 
                *, 
                default_action: Union[str, DefaultAction], 
                ip_rules: Optional[list[IPRule]] = ..., 
                virtual_network_rules: Optional[list[VirtualNetworkRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.OperationDefinition(_Model):
        display: Optional[OperationDisplayDefinition]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[OperationPropertiesDefinition]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplayDefinition] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[OperationPropertiesDefinition] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.OperationDisplayDefinition(_Model):
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


    class azure.mgmt.containerregistry.models.OperationLogSpecificationDefinition(_Model):
        blob_duration: Optional[str]
        display_name: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blob_duration: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.OperationMetricSpecificationDefinition(_Model):
        aggregation_type: Optional[str]
        display_description: Optional[str]
        display_name: Optional[str]
        internal_metric_name: Optional[str]
        name: Optional[str]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_type: Optional[str] = ..., 
                display_description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                internal_metric_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.OperationPropertiesDefinition(_Model):
        service_specification: Optional[OperationServiceSpecificationDefinition]

        @overload
        def __init__(
                self, 
                *, 
                service_specification: Optional[OperationServiceSpecificationDefinition] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.OperationServiceSpecificationDefinition(_Model):
        log_specifications: Optional[list[OperationLogSpecificationDefinition]]
        metric_specifications: Optional[list[OperationMetricSpecificationDefinition]]

        @overload
        def __init__(
                self, 
                *, 
                log_specifications: Optional[list[OperationLogSpecificationDefinition]] = ..., 
                metric_specifications: Optional[list[OperationMetricSpecificationDefinition]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.PackageSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REMOTE = "remote"


    class azure.mgmt.containerregistry.models.ParentProperties(_Model):
        id: Optional[str]
        sync_properties: SyncProperties

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                sync_properties: SyncProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.PasswordName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PASSWORD = "password"
        PASSWORD2 = "password2"


    class azure.mgmt.containerregistry.models.PipelineOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTINUE_ON_ERRORS = "ContinueOnErrors"
        DELETE_SOURCE_BLOB_ON_SUCCESS = "DeleteSourceBlobOnSuccess"
        OVERWRITE_BLOBS = "OverwriteBlobs"
        OVERWRITE_TAGS = "OverwriteTags"


    class azure.mgmt.containerregistry.models.PipelineRun(ProxyResource):
        id: str
        name: str
        properties: Optional[PipelineRunProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PipelineRunProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.PipelineRunProperties(_Model):
        force_update_tag: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        request: Optional[PipelineRunRequest]
        response: Optional[PipelineRunResponse]

        @overload
        def __init__(
                self, 
                *, 
                force_update_tag: Optional[str] = ..., 
                request: Optional[PipelineRunRequest] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.PipelineRunRequest(_Model):
        artifacts: Optional[list[str]]
        catalog_digest: Optional[str]
        pipeline_resource_id: Optional[str]
        source: Optional[PipelineRunSourceProperties]
        target: Optional[PipelineRunTargetProperties]

        @overload
        def __init__(
                self, 
                *, 
                artifacts: Optional[list[str]] = ..., 
                catalog_digest: Optional[str] = ..., 
                pipeline_resource_id: Optional[str] = ..., 
                source: Optional[PipelineRunSourceProperties] = ..., 
                target: Optional[PipelineRunTargetProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.PipelineRunResponse(_Model):
        catalog_digest: Optional[str]
        finish_time: Optional[datetime]
        imported_artifacts: Optional[list[str]]
        pipeline_run_error_message: Optional[str]
        progress: Optional[ProgressProperties]
        source: Optional[ImportPipelineSourceProperties]
        start_time: Optional[datetime]
        status: Optional[str]
        target: Optional[ExportPipelineTargetProperties]
        trigger: Optional[PipelineTriggerDescriptor]

        @overload
        def __init__(
                self, 
                *, 
                catalog_digest: Optional[str] = ..., 
                finish_time: Optional[datetime] = ..., 
                imported_artifacts: Optional[list[str]] = ..., 
                pipeline_run_error_message: Optional[str] = ..., 
                progress: Optional[ProgressProperties] = ..., 
                source: Optional[ImportPipelineSourceProperties] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                target: Optional[ExportPipelineTargetProperties] = ..., 
                trigger: Optional[PipelineTriggerDescriptor] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.PipelineRunSourceProperties(_Model):
        name: Optional[str]
        type: Optional[Union[str, PipelineRunSourceType]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[Union[str, PipelineRunSourceType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.PipelineRunSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_STORAGE_BLOB = "AzureStorageBlob"


    class azure.mgmt.containerregistry.models.PipelineRunTargetProperties(_Model):
        name: Optional[str]
        type: Optional[Union[str, PipelineRunTargetType]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[Union[str, PipelineRunTargetType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.PipelineRunTargetType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_STORAGE_BLOB = "AzureStorageBlob"


    class azure.mgmt.containerregistry.models.PipelineSourceTriggerDescriptor(_Model):
        timestamp: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                timestamp: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.PipelineSourceTriggerProperties(_Model):
        status: Union[str, TriggerStatus]

        @overload
        def __init__(
                self, 
                *, 
                status: Union[str, TriggerStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.PipelineSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_STORAGE_BLOB_CONTAINER = "AzureStorageBlobContainer"


    class azure.mgmt.containerregistry.models.PipelineTriggerDescriptor(_Model):
        source_trigger: Optional[PipelineSourceTriggerDescriptor]

        @overload
        def __init__(
                self, 
                *, 
                source_trigger: Optional[PipelineSourceTriggerDescriptor] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.PipelineTriggerProperties(_Model):
        source_trigger: Optional[PipelineSourceTriggerProperties]

        @overload
        def __init__(
                self, 
                *, 
                source_trigger: Optional[PipelineSourceTriggerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.Policies(_Model):
        azure_ad_authentication_as_arm_policy: Optional[AzureADAuthenticationAsArmPolicy]
        export_policy: Optional[ExportPolicy]
        quarantine_policy: Optional[QuarantinePolicy]
        retention_policy: Optional[RetentionPolicy]
        soft_delete_policy: Optional[SoftDeletePolicy]
        trust_policy: Optional[TrustPolicy]

        @overload
        def __init__(
                self, 
                *, 
                azure_ad_authentication_as_arm_policy: Optional[AzureADAuthenticationAsArmPolicy] = ..., 
                export_policy: Optional[ExportPolicy] = ..., 
                quarantine_policy: Optional[QuarantinePolicy] = ..., 
                retention_policy: Optional[RetentionPolicy] = ..., 
                soft_delete_policy: Optional[SoftDeletePolicy] = ..., 
                trust_policy: Optional[TrustPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.PolicyStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.mgmt.containerregistry.models.PrivateEndpoint(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.PrivateEndpointConnection(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.PrivateEndpointConnectionProperties(_Model):
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.PrivateLinkResource(Resource):
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                required_zone_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[Union[str, ActionsRequired]]
        description: Optional[str]
        status: Optional[Union[str, ConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[Union[str, ActionsRequired]] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, ConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.ProgressProperties(_Model):
        percentage: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                percentage: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.containerregistry.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.containerregistry.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.containerregistry.models.QuarantinePolicy(_Model):
        status: Optional[Union[str, PolicyStatus]]

        @overload
        def __init__(
                self, 
                *, 
                status: Optional[Union[str, PolicyStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.RegenerateCredentialParameters(_Model):
        name: Union[str, PasswordName]

        @overload
        def __init__(
                self, 
                *, 
                name: Union[str, PasswordName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.RegionalEndpoints(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.containerregistry.models.Registry(TrackedResource):
        id: str
        identity: Optional[IdentityProperties]
        location: str
        name: str
        properties: Optional[RegistryProperties]
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityProperties] = ..., 
                location: str, 
                properties: Optional[RegistryProperties] = ..., 
                sku: Sku, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.RegistryListCredentialsResult(_Model):
        passwords: Optional[list[RegistryPassword]]
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                passwords: Optional[list[RegistryPassword]] = ..., 
                username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.RegistryNameCheckRequest(_Model):
        auto_generated_domain_name_label_scope: Optional[Union[str, AutoGeneratedDomainNameLabelScope]]
        name: str
        resource_group_name: Optional[str]
        type: Union[str, ContainerRegistryResourceType]

        @overload
        def __init__(
                self, 
                *, 
                auto_generated_domain_name_label_scope: Optional[Union[str, AutoGeneratedDomainNameLabelScope]] = ..., 
                name: str, 
                resource_group_name: Optional[str] = ..., 
                type: Union[str, ContainerRegistryResourceType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.RegistryNameStatus(_Model):
        available_login_server_name: Optional[str]
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                available_login_server_name: Optional[str] = ..., 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.RegistryPassword(_Model):
        name: Optional[Union[str, PasswordName]]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[Union[str, PasswordName]] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.RegistryProperties(_Model):
        admin_user_enabled: Optional[bool]
        anonymous_pull_enabled: Optional[bool]
        auto_generated_domain_name_label_scope: Optional[Union[str, AutoGeneratedDomainNameLabelScope]]
        creation_date: Optional[datetime]
        data_endpoint_enabled: Optional[bool]
        data_endpoint_host_names: Optional[list[str]]
        encryption: Optional[EncryptionProperty]
        endpoint_protocol: Optional[Union[str, EndpointProtocol]]
        login_server: Optional[str]
        metadata_search: Optional[Union[str, MetadataSearch]]
        network_rule_bypass_allowed_for_tasks: Optional[bool]
        network_rule_bypass_options: Optional[Union[str, NetworkRuleBypassOptions]]
        network_rule_set: Optional[NetworkRuleSet]
        policies: Optional[Policies]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        regional_endpoint_host_names: Optional[list[str]]
        regional_endpoints: Optional[Union[str, RegionalEndpoints]]
        role_assignment_mode: Optional[Union[str, RoleAssignmentMode]]
        status: Optional[Status]
        writable_cache_repos: Optional[Union[str, WritableCacheRepos]]
        zone_redundancy: Optional[Union[str, ZoneRedundancy]]

        @overload
        def __init__(
                self, 
                *, 
                admin_user_enabled: Optional[bool] = ..., 
                anonymous_pull_enabled: Optional[bool] = ..., 
                auto_generated_domain_name_label_scope: Optional[Union[str, AutoGeneratedDomainNameLabelScope]] = ..., 
                data_endpoint_enabled: Optional[bool] = ..., 
                encryption: Optional[EncryptionProperty] = ..., 
                endpoint_protocol: Optional[Union[str, EndpointProtocol]] = ..., 
                metadata_search: Optional[Union[str, MetadataSearch]] = ..., 
                network_rule_bypass_allowed_for_tasks: Optional[bool] = ..., 
                network_rule_bypass_options: Optional[Union[str, NetworkRuleBypassOptions]] = ..., 
                network_rule_set: Optional[NetworkRuleSet] = ..., 
                policies: Optional[Policies] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                regional_endpoints: Optional[Union[str, RegionalEndpoints]] = ..., 
                role_assignment_mode: Optional[Union[str, RoleAssignmentMode]] = ..., 
                writable_cache_repos: Optional[Union[str, WritableCacheRepos]] = ..., 
                zone_redundancy: Optional[Union[str, ZoneRedundancy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.RegistryPropertiesUpdateParameters(_Model):
        admin_user_enabled: Optional[bool]
        anonymous_pull_enabled: Optional[bool]
        data_endpoint_enabled: Optional[bool]
        encryption: Optional[EncryptionProperty]
        endpoint_protocol: Optional[Union[str, EndpointProtocol]]
        metadata_search: Optional[Union[str, MetadataSearch]]
        network_rule_bypass_allowed_for_tasks: Optional[bool]
        network_rule_bypass_options: Optional[Union[str, NetworkRuleBypassOptions]]
        network_rule_set: Optional[NetworkRuleSet]
        policies: Optional[Policies]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        regional_endpoints: Optional[Union[str, RegionalEndpoints]]
        role_assignment_mode: Optional[Union[str, RoleAssignmentMode]]
        writable_cache_repos: Optional[Union[str, WritableCacheRepos]]

        @overload
        def __init__(
                self, 
                *, 
                admin_user_enabled: Optional[bool] = ..., 
                anonymous_pull_enabled: Optional[bool] = ..., 
                data_endpoint_enabled: Optional[bool] = ..., 
                encryption: Optional[EncryptionProperty] = ..., 
                endpoint_protocol: Optional[Union[str, EndpointProtocol]] = ..., 
                metadata_search: Optional[Union[str, MetadataSearch]] = ..., 
                network_rule_bypass_allowed_for_tasks: Optional[bool] = ..., 
                network_rule_bypass_options: Optional[Union[str, NetworkRuleBypassOptions]] = ..., 
                network_rule_set: Optional[NetworkRuleSet] = ..., 
                policies: Optional[Policies] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                regional_endpoints: Optional[Union[str, RegionalEndpoints]] = ..., 
                role_assignment_mode: Optional[Union[str, RoleAssignmentMode]] = ..., 
                writable_cache_repos: Optional[Union[str, WritableCacheRepos]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.RegistrySyncResult(_Model):
        last_successful_sync_end_time: Optional[datetime]
        last_sync_end_time: Optional[datetime]
        last_sync_start_time: Optional[datetime]
        sync_state: Union[str, SyncState]
        sync_trigger: Union[str, SyncTrigger]

        @overload
        def __init__(
                self, 
                *, 
                last_successful_sync_end_time: Optional[datetime] = ..., 
                last_sync_end_time: Optional[datetime] = ..., 
                last_sync_start_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.RegistryUpdateParameters(_Model):
        identity: Optional[IdentityProperties]
        properties: Optional[RegistryPropertiesUpdateParameters]
        sku: Optional[Sku]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityProperties] = ..., 
                properties: Optional[RegistryPropertiesUpdateParameters] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.RegistryUsage(_Model):
        current_value: Optional[int]
        limit: Optional[int]
        name: Optional[str]
        unit: Optional[Union[str, RegistryUsageUnit]]

        @overload
        def __init__(
                self, 
                *, 
                current_value: Optional[int] = ..., 
                limit: Optional[int] = ..., 
                name: Optional[str] = ..., 
                unit: Optional[Union[str, RegistryUsageUnit]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.RegistryUsageListResult(_Model):
        value: Optional[list[RegistryUsage]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[RegistryUsage]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.RegistryUsageUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BYTES = "Bytes"
        COUNT = "Count"


    class azure.mgmt.containerregistry.models.Replication(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ReplicationProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ReplicationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.ReplicationProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        region_endpoint_enabled: Optional[bool]
        status: Optional[Status]
        zone_redundancy: Optional[Union[str, ZoneRedundancy]]

        @overload
        def __init__(
                self, 
                *, 
                region_endpoint_enabled: Optional[bool] = ..., 
                zone_redundancy: Optional[Union[str, ZoneRedundancy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.ReplicationUpdateParameters(_Model):
        properties: Optional[ReplicationUpdateParametersProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ReplicationUpdateParametersProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.ReplicationUpdateParametersProperties(_Model):
        region_endpoint_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                region_endpoint_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.Request(_Model):
        addr: Optional[str]
        host: Optional[str]
        id: Optional[str]
        method: Optional[str]
        useragent: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                addr: Optional[str] = ..., 
                host: Optional[str] = ..., 
                id: Optional[str] = ..., 
                method: Optional[str] = ..., 
                useragent: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.containerregistry.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.containerregistry.models.RetentionPolicy(_Model):
        days: Optional[int]
        last_updated_time: Optional[datetime]
        status: Optional[Union[str, PolicyStatus]]

        @overload
        def __init__(
                self, 
                *, 
                days: Optional[int] = ..., 
                status: Optional[Union[str, PolicyStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.RoleAssignmentMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ABAC_REPOSITORY_PERMISSIONS = "AbacRepositoryPermissions"
        LEGACY_REGISTRY_PERMISSIONS = "LegacyRegistryPermissions"


    class azure.mgmt.containerregistry.models.ScopeMap(ProxyResource):
        id: str
        name: str
        properties: Optional[ScopeMapProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ScopeMapProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.ScopeMapProperties(_Model):
        actions: list[str]
        creation_date: Optional[datetime]
        description: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                actions: list[str], 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.ScopeMapPropertiesUpdateParameters(_Model):
        actions: Optional[list[str]]
        description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[list[str]] = ..., 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.ScopeMapUpdateParameters(_Model):
        properties: Optional[ScopeMapPropertiesUpdateParameters]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ScopeMapPropertiesUpdateParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.Sku(_Model):
        name: Union[str, SkuName]
        tier: Optional[Union[str, SkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                name: Union[str, SkuName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        CLASSIC = "Classic"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.containerregistry.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        CLASSIC = "Classic"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.containerregistry.models.SoftDeletePolicy(_Model):
        last_updated_time: Optional[datetime]
        retention_days: Optional[int]
        status: Optional[Union[str, PolicyStatus]]

        @overload
        def __init__(
                self, 
                *, 
                retention_days: Optional[int] = ..., 
                status: Optional[Union[str, PolicyStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.Source(_Model):
        addr: Optional[str]
        instance_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                addr: Optional[str] = ..., 
                instance_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.Status(_Model):
        display_status: Optional[str]
        message: Optional[str]
        timestamp: Optional[datetime]


    class azure.mgmt.containerregistry.models.StatusDetailProperties(_Model):
        code: Optional[str]
        correlation_id: Optional[str]
        description: Optional[str]
        timestamp: Optional[datetime]
        type: Optional[str]


    class azure.mgmt.containerregistry.models.StorageAccessMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED_IDENTITY = "ManagedIdentity"
        SAS_TOKEN = "SasToken"


    class azure.mgmt.containerregistry.models.SyncProperties(_Model):
        gateway_endpoint: Optional[str]
        last_sync_time: Optional[datetime]
        message_ttl: timedelta
        schedule: Optional[str]
        sync_window: Optional[timedelta]
        token_id: str

        @overload
        def __init__(
                self, 
                *, 
                message_ttl: timedelta, 
                schedule: Optional[str] = ..., 
                sync_window: Optional[timedelta] = ..., 
                token_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.SyncState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        NOT_ACTIVATED = "NotActivated"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"
        SYNCING = "Syncing"
        TIMED_OUT = "TimedOut"


    class azure.mgmt.containerregistry.models.SyncTrigger(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INITIAL_SYNC = "InitialSync"
        MANUAL_RESYNC = "ManualResync"
        RECOVERY_SERVICE = "RecoveryService"
        SYNC_TOKEN_UPDATE = "SyncTokenUpdate"


    class azure.mgmt.containerregistry.models.SyncUpdateProperties(_Model):
        message_ttl: Optional[timedelta]
        schedule: Optional[str]
        sync_window: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                message_ttl: Optional[timedelta] = ..., 
                schedule: Optional[str] = ..., 
                sync_window: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.SystemData(_Model):
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


    class azure.mgmt.containerregistry.models.Target(_Model):
        digest: Optional[str]
        length: Optional[int]
        media_type: Optional[str]
        name: Optional[str]
        repository: Optional[str]
        size: Optional[int]
        tag: Optional[str]
        url: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                digest: Optional[str] = ..., 
                length: Optional[int] = ..., 
                media_type: Optional[str] = ..., 
                name: Optional[str] = ..., 
                repository: Optional[str] = ..., 
                size: Optional[int] = ..., 
                tag: Optional[str] = ..., 
                url: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.TlsCertificateProperties(_Model):
        location: Optional[str]
        type: Optional[Union[str, CertificateType]]


    class azure.mgmt.containerregistry.models.TlsProperties(_Model):
        certificate: Optional[TlsCertificateProperties]
        status: Optional[Union[str, TlsStatus]]


    class azure.mgmt.containerregistry.models.TlsStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.containerregistry.models.Token(ProxyResource):
        id: str
        name: str
        properties: Optional[TokenProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TokenProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.TokenCertificate(_Model):
        encoded_pem_certificate: Optional[str]
        expiry: Optional[datetime]
        name: Optional[Union[str, TokenCertificateName]]
        thumbprint: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                encoded_pem_certificate: Optional[str] = ..., 
                expiry: Optional[datetime] = ..., 
                name: Optional[Union[str, TokenCertificateName]] = ..., 
                thumbprint: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.TokenCertificateName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CERTIFICATE1 = "certificate1"
        CERTIFICATE2 = "certificate2"


    class azure.mgmt.containerregistry.models.TokenCredentialsProperties(_Model):
        certificates: Optional[list[TokenCertificate]]
        passwords: Optional[list[TokenPassword]]

        @overload
        def __init__(
                self, 
                *, 
                certificates: Optional[list[TokenCertificate]] = ..., 
                passwords: Optional[list[TokenPassword]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.TokenPassword(_Model):
        creation_time: Optional[datetime]
        expiry: Optional[datetime]
        name: Optional[Union[str, TokenPasswordName]]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                creation_time: Optional[datetime] = ..., 
                expiry: Optional[datetime] = ..., 
                name: Optional[Union[str, TokenPasswordName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.TokenPasswordName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PASSWORD1 = "password1"
        PASSWORD2 = "password2"


    class azure.mgmt.containerregistry.models.TokenProperties(_Model):
        creation_date: Optional[datetime]
        credentials: Optional[TokenCredentialsProperties]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        scope_map_id: Optional[str]
        status: Optional[Union[str, TokenStatus]]

        @overload
        def __init__(
                self, 
                *, 
                credentials: Optional[TokenCredentialsProperties] = ..., 
                scope_map_id: Optional[str] = ..., 
                status: Optional[Union[str, TokenStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.TokenStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.mgmt.containerregistry.models.TokenUpdateParameters(_Model):
        properties: Optional[TokenUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TokenUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.TokenUpdateProperties(_Model):
        credentials: Optional[TokenCredentialsProperties]
        scope_map_id: Optional[str]
        status: Optional[Union[str, TokenStatus]]

        @overload
        def __init__(
                self, 
                *, 
                credentials: Optional[TokenCredentialsProperties] = ..., 
                scope_map_id: Optional[str] = ..., 
                status: Optional[Union[str, TokenStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.TrackedResource(Resource):
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


    class azure.mgmt.containerregistry.models.TriggerStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.containerregistry.models.TrustPolicy(_Model):
        status: Optional[Union[str, PolicyStatus]]
        type: Optional[Union[str, TrustPolicyType]]

        @overload
        def __init__(
                self, 
                *, 
                status: Optional[Union[str, PolicyStatus]] = ..., 
                type: Optional[Union[str, TrustPolicyType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.TrustPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOTARY = "Notary"


    class azure.mgmt.containerregistry.models.UserIdentityProperties(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.containerregistry.models.VirtualNetworkRule(_Model):
        action: Optional[Union[str, Action]]
        virtual_network_subnet_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, Action]] = ..., 
                virtual_network_subnet_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.Webhook(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[WebhookProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[WebhookProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.WebhookAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHART_DELETE = "chart_delete"
        CHART_PUSH = "chart_push"
        DELETE = "delete"
        PUSH = "push"
        QUARANTINE = "quarantine"


    class azure.mgmt.containerregistry.models.WebhookCreateParameters(_Model):
        location: str
        properties: Optional[WebhookPropertiesCreateParameters]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[WebhookPropertiesCreateParameters] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.WebhookProperties(_Model):
        actions: list[Union[str, WebhookAction]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        scope: Optional[str]
        status: Optional[Union[str, WebhookStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions: list[Union[str, WebhookAction]], 
                scope: Optional[str] = ..., 
                status: Optional[Union[str, WebhookStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.WebhookPropertiesCreateParameters(_Model):
        actions: list[Union[str, WebhookAction]]
        custom_headers: Optional[dict[str, str]]
        scope: Optional[str]
        service_uri: str
        status: Optional[Union[str, WebhookStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions: list[Union[str, WebhookAction]], 
                custom_headers: Optional[dict[str, str]] = ..., 
                scope: Optional[str] = ..., 
                service_uri: str, 
                status: Optional[Union[str, WebhookStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.WebhookPropertiesUpdateParameters(_Model):
        actions: Optional[list[Union[str, WebhookAction]]]
        custom_headers: Optional[dict[str, str]]
        scope: Optional[str]
        service_uri: Optional[str]
        status: Optional[Union[str, WebhookStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[list[Union[str, WebhookAction]]] = ..., 
                custom_headers: Optional[dict[str, str]] = ..., 
                scope: Optional[str] = ..., 
                service_uri: Optional[str] = ..., 
                status: Optional[Union[str, WebhookStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistry.models.WebhookStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.mgmt.containerregistry.models.WebhookUpdateParameters(_Model):
        properties: Optional[WebhookPropertiesUpdateParameters]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WebhookPropertiesUpdateParameters] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistry.models.WritableCacheRepos(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.containerregistry.models.ZoneRedundancy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


namespace azure.mgmt.containerregistry.operations

    class azure.mgmt.containerregistry.operations.ArchiveVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'package_type', 'archive_name', 'archive_version_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                archive_version_name: str, 
                **kwargs: Any
            ) -> LROPoller[ArchiveVersion]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'package_type', 'archive_name', 'archive_version_name']}, api_versions_list=['2026-03-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                archive_version_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'package_type', 'archive_name', 'archive_version_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                archive_version_name: str, 
                **kwargs: Any
            ) -> ArchiveVersion: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'package_type', 'archive_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ArchiveVersion]: ...


    class azure.mgmt.containerregistry.operations.ArchivesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                archive_create_parameters: Archive, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Archive]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                archive_create_parameters: Archive, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Archive]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                archive_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Archive]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'package_type', 'archive_name']}, api_versions_list=['2026-03-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'package_type', 'archive_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                **kwargs: Any
            ) -> Archive: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'package_type', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                **kwargs: Any
            ) -> ItemPaged[Archive]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                archive_update_parameters: ArchiveUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Archive: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                archive_update_parameters: ArchiveUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Archive: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                package_type: str, 
                archive_name: str, 
                archive_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Archive: ...


    class azure.mgmt.containerregistry.operations.CacheRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                cache_rule_name: str, 
                cache_rule_create_parameters: CacheRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CacheRule]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                cache_rule_name: str, 
                cache_rule_create_parameters: CacheRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CacheRule]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                cache_rule_name: str, 
                cache_rule_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CacheRule]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                cache_rule_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                cache_rule_name: str, 
                cache_rule_update_parameters: CacheRuleUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CacheRule]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                cache_rule_name: str, 
                cache_rule_update_parameters: CacheRuleUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CacheRule]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                cache_rule_name: str, 
                cache_rule_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CacheRule]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                cache_rule_name: str, 
                **kwargs: Any
            ) -> CacheRule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CacheRule]: ...


    class azure.mgmt.containerregistry.operations.ConnectedRegistriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                connected_registry_name: str, 
                connected_registry_create_parameters: ConnectedRegistry, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConnectedRegistry]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                connected_registry_name: str, 
                connected_registry_create_parameters: ConnectedRegistry, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConnectedRegistry]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                connected_registry_name: str, 
                connected_registry_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConnectedRegistry]: ...

        @distributed_trace
        def begin_deactivate(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                connected_registry_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                connected_registry_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                connected_registry_name: str, 
                connected_registry_update_parameters: ConnectedRegistryUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConnectedRegistry]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                connected_registry_name: str, 
                connected_registry_update_parameters: ConnectedRegistryUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConnectedRegistry]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                connected_registry_name: str, 
                connected_registry_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConnectedRegistry]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                connected_registry_name: str, 
                **kwargs: Any
            ) -> ConnectedRegistry: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ConnectedRegistry]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'connected_registry_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def resync(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                connected_registry_name: str, 
                **kwargs: Any
            ) -> ConnectedRegistry: ...


    class azure.mgmt.containerregistry.operations.CredentialSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                credential_set_name: str, 
                credential_set_create_parameters: CredentialSet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CredentialSet]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                credential_set_name: str, 
                credential_set_create_parameters: CredentialSet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CredentialSet]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                credential_set_name: str, 
                credential_set_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CredentialSet]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                credential_set_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                credential_set_name: str, 
                credential_set_update_parameters: CredentialSetUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CredentialSet]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                credential_set_name: str, 
                credential_set_update_parameters: CredentialSetUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CredentialSet]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                credential_set_name: str, 
                credential_set_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CredentialSet]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                credential_set_name: str, 
                **kwargs: Any
            ) -> CredentialSet: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CredentialSet]: ...


    class azure.mgmt.containerregistry.operations.ExportPipelinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                export_pipeline_name: str, 
                export_pipeline_create_parameters: ExportPipeline, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExportPipeline]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                export_pipeline_name: str, 
                export_pipeline_create_parameters: ExportPipeline, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExportPipeline]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                export_pipeline_name: str, 
                export_pipeline_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExportPipeline]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'export_pipeline_name']}, api_versions_list=['2026-03-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                export_pipeline_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'export_pipeline_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                export_pipeline_name: str, 
                **kwargs: Any
            ) -> ExportPipeline: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ExportPipeline]: ...


    class azure.mgmt.containerregistry.operations.ImportPipelinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                import_pipeline_name: str, 
                import_pipeline_create_parameters: ImportPipeline, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ImportPipeline]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                import_pipeline_name: str, 
                import_pipeline_create_parameters: ImportPipeline, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ImportPipeline]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                import_pipeline_name: str, 
                import_pipeline_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ImportPipeline]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'import_pipeline_name']}, api_versions_list=['2026-03-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                import_pipeline_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'import_pipeline_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                import_pipeline_name: str, 
                **kwargs: Any
            ) -> ImportPipeline: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ImportPipeline]: ...


    class azure.mgmt.containerregistry.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[OperationDefinition]: ...


    class azure.mgmt.containerregistry.operations.PipelineRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                pipeline_run_name: str, 
                pipeline_run_create_parameters: PipelineRun, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PipelineRun]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                pipeline_run_name: str, 
                pipeline_run_create_parameters: PipelineRun, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PipelineRun]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                pipeline_run_name: str, 
                pipeline_run_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PipelineRun]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'pipeline_run_name']}, api_versions_list=['2026-03-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                pipeline_run_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'pipeline_run_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                pipeline_run_name: str, 
                **kwargs: Any
            ) -> PipelineRun: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'registry_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PipelineRun]: ...


    class azure.mgmt.containerregistry.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.containerregistry.operations.RegistriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                registry: Registry, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Registry]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                registry: Registry, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Registry]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                registry: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Registry]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_generate_credentials(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                generate_credentials_parameters: GenerateCredentialsParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GenerateCredentialsResult]: ...

        @overload
        def begin_generate_credentials(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                generate_credentials_parameters: GenerateCredentialsParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GenerateCredentialsResult]: ...

        @overload
        def begin_generate_credentials(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                generate_credentials_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GenerateCredentialsResult]: ...

        @overload
        def begin_import_image(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                parameters: ImportImageParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_import_image(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                parameters: ImportImageParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_import_image(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                registry_update_parameters: RegistryUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Registry]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                registry_update_parameters: RegistryUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Registry]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                registry_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Registry]: ...

        @overload
        def check_name_availability(
                self, 
                registry_name_check_request: RegistryNameCheckRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegistryNameStatus: ...

        @overload
        def check_name_availability(
                self, 
                registry_name_check_request: RegistryNameCheckRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegistryNameStatus: ...

        @overload
        def check_name_availability(
                self, 
                registry_name_check_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegistryNameStatus: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> Registry: ...

        @distributed_trace
        def get_private_link_resource(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Registry]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Registry]: ...

        @distributed_trace
        def list_credentials(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> RegistryListCredentialsResult: ...

        @distributed_trace
        def list_private_link_resources(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...

        @distributed_trace
        def list_usages(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> RegistryUsageListResult: ...

        @overload
        def regenerate_credential(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                regenerate_credential_parameters: RegenerateCredentialParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegistryListCredentialsResult: ...

        @overload
        def regenerate_credential(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                regenerate_credential_parameters: RegenerateCredentialParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegistryListCredentialsResult: ...

        @overload
        def regenerate_credential(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                regenerate_credential_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegistryListCredentialsResult: ...


    class azure.mgmt.containerregistry.operations.ReplicationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                replication_name: str, 
                replication: Replication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Replication]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                replication_name: str, 
                replication: Replication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Replication]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                replication_name: str, 
                replication: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Replication]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                replication_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                replication_name: str, 
                replication_update_parameters: ReplicationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Replication]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                replication_name: str, 
                replication_update_parameters: ReplicationUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Replication]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                replication_name: str, 
                replication_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Replication]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                replication_name: str, 
                **kwargs: Any
            ) -> Replication: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Replication]: ...


    class azure.mgmt.containerregistry.operations.ScopeMapsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                scope_map_name: str, 
                scope_map_create_parameters: ScopeMap, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ScopeMap]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                scope_map_name: str, 
                scope_map_create_parameters: ScopeMap, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ScopeMap]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                scope_map_name: str, 
                scope_map_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ScopeMap]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                scope_map_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                scope_map_name: str, 
                scope_map_update_parameters: ScopeMapUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ScopeMap]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                scope_map_name: str, 
                scope_map_update_parameters: ScopeMapUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ScopeMap]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                scope_map_name: str, 
                scope_map_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ScopeMap]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                scope_map_name: str, 
                **kwargs: Any
            ) -> ScopeMap: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ScopeMap]: ...


    class azure.mgmt.containerregistry.operations.TokensOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                token_name: str, 
                token_create_parameters: Token, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Token]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                token_name: str, 
                token_create_parameters: Token, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Token]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                token_name: str, 
                token_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Token]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                token_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                token_name: str, 
                token_update_parameters: TokenUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Token]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                token_name: str, 
                token_update_parameters: TokenUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Token]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                token_name: str, 
                token_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Token]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                token_name: str, 
                **kwargs: Any
            ) -> Token: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Token]: ...


    class azure.mgmt.containerregistry.operations.WebhooksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                webhook_name: str, 
                webhook_create_parameters: WebhookCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Webhook]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                webhook_name: str, 
                webhook_create_parameters: WebhookCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Webhook]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                webhook_name: str, 
                webhook_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Webhook]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                webhook_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                webhook_name: str, 
                webhook_update_parameters: WebhookUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Webhook]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                webhook_name: str, 
                webhook_update_parameters: WebhookUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Webhook]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                webhook_name: str, 
                webhook_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Webhook]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                webhook_name: str, 
                **kwargs: Any
            ) -> Webhook: ...

        @distributed_trace
        def get_callback_config(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                webhook_name: str, 
                **kwargs: Any
            ) -> CallbackConfig: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Webhook]: ...

        @distributed_trace
        def list_events(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                webhook_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Event]: ...

        @distributed_trace
        def ping(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                webhook_name: str, 
                **kwargs: Any
            ) -> EventInfo: ...


namespace azure.mgmt.containerregistry.types

    class azure.mgmt.containerregistry.types.ActivationProperties(TypedDict, total=False):
        key "status": Union[str, ActivationStatus]
        status: Union[str, ActivationStatus]


    class azure.mgmt.containerregistry.types.Actor(TypedDict, total=False):
        key "name": str
        name: str


    class azure.mgmt.containerregistry.types.AdditionalAuthenticationProperties(TypedDict, total=False):
        key "authenticationType": Required[Literal[AdditionalAuthenticationType.GOOGLE_ARTIFACT_REGISTRY]]
        key "projectNumber": Required[str]
        key "workloadIdentityPool": Required[str]
        key "workloadIdentityProvider": Required[str]
        authentication_type: Literal[AdditionalAuthenticationType.GOOGLE_ARTIFACT_REGISTRY]
        project_number: str
        workload_identity_pool: str
        workload_identity_provider: str


    class azure.mgmt.containerregistry.types.AdditionalAuthenticationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GOOGLE_ARTIFACT_REGISTRY = "GoogleArtifactRegistry"


    class azure.mgmt.containerregistry.types.Archive(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ArchiveProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ArchiveProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerregistry.types.ArchivePackageSourceProperties(TypedDict, total=False):
        key "type": Union[str, PackageSourceType]
        key "url": str
        type: Union[str, PackageSourceType]
        url: str


    class azure.mgmt.containerregistry.types.ArchiveProperties(TypedDict, total=False):
        key "packageSource": ForwardRef('ArchivePackageSourceProperties', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "publishedVersion": str
        key "repositoryEndpoint": str
        key "repositoryEndpointPrefix": str
        package_source: ArchivePackageSourceProperties
        provisioning_state: Union[str, ProvisioningState]
        published_version: str
        repository_endpoint: str
        repository_endpoint_prefix: str


    class azure.mgmt.containerregistry.types.ArchiveUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('ArchiveUpdateProperties', module='types')
        properties: ArchiveUpdateProperties


    class azure.mgmt.containerregistry.types.ArchiveUpdateProperties(TypedDict, total=False):
        key "publishedVersion": str
        published_version: str


    class azure.mgmt.containerregistry.types.ArchiveVersion(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ArchiveVersionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ArchiveVersionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerregistry.types.ArchiveVersionProperties(TypedDict, total=False):
        key "archiveVersionErrorMessage": str
        key "provisioningState": Union[str, ProvisioningState]
        archive_version_error_message: str
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.containerregistry.types.AuthCredential(TypedDict, total=False):
        key "credentialHealth": ForwardRef('CredentialHealth', module='types')
        key "name": Union[str, CredentialName]
        key "passwordSecretIdentifier": str
        key "usernameSecretIdentifier": str
        credential_health: CredentialHealth
        name: Union[str, CredentialName]
        password_secret_identifier: str
        username_secret_identifier: str


    class azure.mgmt.containerregistry.types.AzureADAuthenticationAsArmPolicy(TypedDict, total=False):
        key "status": Union[str, AzureADAuthenticationAsArmPolicyStatus]
        status: Union[str, AzureADAuthenticationAsArmPolicyStatus]


    class azure.mgmt.containerregistry.types.CacheRule(ProxyResource):
        key "id": str
        key "identity": ForwardRef('IdentityProperties', module='types')
        key "name": str
        key "properties": ForwardRef('CacheRuleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: IdentityProperties
        name: str
        properties: CacheRuleProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerregistry.types.CacheRuleProperties(TypedDict, total=False):
        key "additionalAuthenticationProperties": ForwardRef('AdditionalAuthenticationProperties', module='types')
        key "creationDate": str
        key "credentialSetResourceId": str
        key "provisioningState": Union[str, ProvisioningState]
        key "sourceRepository": str
        key "targetRepository": str
        additional_authentication_properties: AdditionalAuthenticationProperties
        creation_date: str
        credential_set_resource_id: str
        provisioning_state: Union[str, ProvisioningState]
        source_repository: str
        target_repository: str


    class azure.mgmt.containerregistry.types.CacheRuleUpdateParameters(TypedDict, total=False):
        key "identity": ForwardRef('IdentityProperties', module='types')
        key "properties": ForwardRef('CacheRuleUpdateProperties', module='types')
        identity: IdentityProperties
        properties: CacheRuleUpdateProperties


    class azure.mgmt.containerregistry.types.CacheRuleUpdateProperties(TypedDict, total=False):
        key "additionalAuthenticationProperties": ForwardRef('AdditionalAuthenticationProperties', module='types')
        key "credentialSetResourceId": str
        additional_authentication_properties: AdditionalAuthenticationProperties
        credential_set_resource_id: str


    class azure.mgmt.containerregistry.types.CallbackConfig(TypedDict, total=False):
        key "serviceUri": Required[str]
        customHeaders: dict[str, str]
        custom_headers: dict[str, str]
        service_uri: str


    class azure.mgmt.containerregistry.types.ConnectedRegistry(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ConnectedRegistryProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ConnectedRegistryProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerregistry.types.ConnectedRegistryProperties(TypedDict, total=False):
        key "activation": ForwardRef('ActivationProperties', module='types')
        key "connectionState": Union[str, ConnectionState]
        key "garbageCollection": ForwardRef('GarbageCollectionProperties', module='types')
        key "lastActivityTime": str
        key "logging": ForwardRef('LoggingProperties', module='types')
        key "loginServer": ForwardRef('LoginServerProperties', module='types')
        key "mode": Required[Union[str, ConnectedRegistryMode]]
        key "parent": Required[ParentProperties]
        key "provisioningState": Union[str, ProvisioningState]
        key "registrySyncResult": ForwardRef('RegistrySyncResult', module='types')
        key "version": str
        activation: ActivationProperties
        clientTokenIds: list[str]
        client_token_ids: list[str]
        connection_state: Union[str, ConnectionState]
        garbage_collection: GarbageCollectionProperties
        last_activity_time: str
        logging: LoggingProperties
        login_server: LoginServerProperties
        mode: Union[str, ConnectedRegistryMode]
        notificationsList: list[str]
        notifications_list: list[str]
        parent: ParentProperties
        provisioning_state: Union[str, ProvisioningState]
        registry_sync_result: RegistrySyncResult
        statusDetails: list[StatusDetailProperties]
        status_details: list[StatusDetailProperties]
        version: str


    class azure.mgmt.containerregistry.types.ConnectedRegistryUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('ConnectedRegistryUpdateProperties', module='types')
        properties: ConnectedRegistryUpdateProperties


    class azure.mgmt.containerregistry.types.ConnectedRegistryUpdateProperties(TypedDict, total=False):
        key "garbageCollection": ForwardRef('GarbageCollectionProperties', module='types')
        key "logging": ForwardRef('LoggingProperties', module='types')
        key "syncProperties": ForwardRef('SyncUpdateProperties', module='types')
        clientTokenIds: list[str]
        client_token_ids: list[str]
        garbage_collection: GarbageCollectionProperties
        logging: LoggingProperties
        notificationsList: list[str]
        notifications_list: list[str]
        sync_properties: SyncUpdateProperties


    class azure.mgmt.containerregistry.types.CredentialHealth(TypedDict, total=False):
        key "errorCode": str
        key "errorMessage": str
        key "status": Union[str, CredentialHealthStatus]
        error_code: str
        error_message: str
        status: Union[str, CredentialHealthStatus]


    class azure.mgmt.containerregistry.types.CredentialSet(ProxyResource):
        key "id": str
        key "identity": ForwardRef('IdentityProperties', module='types')
        key "name": str
        key "properties": ForwardRef('CredentialSetProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: IdentityProperties
        name: str
        properties: CredentialSetProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerregistry.types.CredentialSetProperties(TypedDict, total=False):
        key "creationDate": str
        key "loginServer": str
        key "provisioningState": Union[str, ProvisioningState]
        authCredentials: list[AuthCredential]
        auth_credentials: list[AuthCredential]
        creation_date: str
        login_server: str
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.containerregistry.types.CredentialSetUpdateParameters(TypedDict, total=False):
        key "identity": ForwardRef('IdentityProperties', module='types')
        key "properties": ForwardRef('CredentialSetUpdateProperties', module='types')
        identity: IdentityProperties
        properties: CredentialSetUpdateProperties


    class azure.mgmt.containerregistry.types.CredentialSetUpdateProperties(TypedDict, total=False):
        authCredentials: list[AuthCredential]
        auth_credentials: list[AuthCredential]


    class azure.mgmt.containerregistry.types.EncryptionProperty(TypedDict, total=False):
        key "keyVaultProperties": ForwardRef('KeyVaultProperties', module='types')
        key "status": Union[str, EncryptionStatus]
        key_vault_properties: KeyVaultProperties
        status: Union[str, EncryptionStatus]


    class azure.mgmt.containerregistry.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.containerregistry.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.containerregistry.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        error: ErrorDetail


    class azure.mgmt.containerregistry.types.Event(EventInfo):
        key "eventRequestMessage": ForwardRef('EventRequestMessage', module='types')
        key "eventResponseMessage": ForwardRef('EventResponseMessage', module='types')
        key "id": str
        event_request_message: EventRequestMessage
        event_response_message: EventResponseMessage
        id: str


    class azure.mgmt.containerregistry.types.EventContent(TypedDict, total=False):
        key "action": str
        key "actor": ForwardRef('Actor', module='types')
        key "id": str
        key "request": ForwardRef('Request', module='types')
        key "source": ForwardRef('Source', module='types')
        key "target": ForwardRef('Target', module='types')
        key "timestamp": str
        action: str
        actor: Actor
        id: str
        request: Request
        source: Source
        target: Target
        timestamp: str


    class azure.mgmt.containerregistry.types.EventInfo(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.containerregistry.types.EventRequestMessage(TypedDict, total=False):
        key "content": ForwardRef('EventContent', module='types')
        key "method": str
        key "requestUri": str
        key "version": str
        content: EventContent
        headers: dict[str, str]
        method: str
        request_uri: str
        version: str


    class azure.mgmt.containerregistry.types.EventResponseMessage(TypedDict, total=False):
        key "content": str
        key "reasonPhrase": str
        key "statusCode": str
        key "version": str
        content: str
        headers: dict[str, str]
        reason_phrase: str
        status_code: str
        version: str


    class azure.mgmt.containerregistry.types.ExportPipeline(ProxyResource):
        key "id": str
        key "identity": ForwardRef('IdentityProperties', module='types')
        key "location": str
        key "name": str
        key "properties": ForwardRef('ExportPipelineProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: IdentityProperties
        location: str
        name: str
        properties: ExportPipelineProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerregistry.types.ExportPipelineProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "target": Required[ExportPipelineTargetProperties]
        options: list[Union[str, PipelineOptions]]
        provisioning_state: Union[str, ProvisioningState]
        target: ExportPipelineTargetProperties


    class azure.mgmt.containerregistry.types.ExportPipelineTargetProperties(TypedDict, total=False):
        key "keyVaultUri": str
        key "storageAccessMode": Union[str, StorageAccessMode]
        key "type": str
        key "uri": str
        key_vault_uri: str
        storage_access_mode: Union[str, StorageAccessMode]
        type: str
        uri: str


    class azure.mgmt.containerregistry.types.ExportPolicy(TypedDict, total=False):
        key "status": Union[str, ExportPolicyStatus]
        status: Union[str, ExportPolicyStatus]


    class azure.mgmt.containerregistry.types.GarAuthenticationProperties(TypedDict, total=False):
        key "authenticationType": Required[Literal[AdditionalAuthenticationType.GOOGLE_ARTIFACT_REGISTRY]]
        key "projectNumber": Required[str]
        key "workloadIdentityPool": Required[str]
        key "workloadIdentityProvider": Required[str]
        authentication_type: Literal[AdditionalAuthenticationType.GOOGLE_ARTIFACT_REGISTRY]
        project_number: str
        workload_identity_pool: str
        workload_identity_provider: str


    class azure.mgmt.containerregistry.types.GarbageCollectionProperties(TypedDict, total=False):
        key "enabled": bool
        key "schedule": str
        enabled: bool
        schedule: str


    class azure.mgmt.containerregistry.types.GenerateCredentialsParameters(TypedDict, total=False):
        key "expiry": str
        key "name": Union[str, TokenPasswordName]
        key "tokenId": str
        expiry: str
        name: Union[str, TokenPasswordName]
        token_id: str


    class azure.mgmt.containerregistry.types.GenerateCredentialsResult(TypedDict, total=False):
        key "username": str
        passwords: list[TokenPassword]
        username: str


    class azure.mgmt.containerregistry.types.IPRule(TypedDict, total=False):
        key "action": Union[str, Action]
        key "value": Required[str]
        action: Union[str, Action]
        ip_address_or_range: str


    class azure.mgmt.containerregistry.types.IdentityProperties(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, ResourceIdentityType]
        principal_id: str
        tenant_id: str
        type: Union[str, ResourceIdentityType]
        userAssignedIdentities: dict[str, UserIdentityProperties]
        user_assigned_identities: dict[str, UserIdentityProperties]


    class azure.mgmt.containerregistry.types.ImportImageParameters(TypedDict, total=False):
        key "mode": Union[str, ImportMode]
        key "source": Required[ImportSource]
        mode: Union[str, ImportMode]
        source: ImportSource
        targetTags: list[str]
        target_tags: list[str]
        untaggedTargetRepositories: list[str]
        untagged_target_repositories: list[str]


    class azure.mgmt.containerregistry.types.ImportPipeline(ProxyResource):
        key "id": str
        key "identity": ForwardRef('IdentityProperties', module='types')
        key "location": str
        key "name": str
        key "properties": ForwardRef('ImportPipelineProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: IdentityProperties
        location: str
        name: str
        properties: ImportPipelineProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerregistry.types.ImportPipelineProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "source": Required[ImportPipelineSourceProperties]
        key "trigger": ForwardRef('PipelineTriggerProperties', module='types')
        options: list[Union[str, PipelineOptions]]
        provisioning_state: Union[str, ProvisioningState]
        source: ImportPipelineSourceProperties
        trigger: PipelineTriggerProperties


    class azure.mgmt.containerregistry.types.ImportPipelineSourceProperties(TypedDict, total=False):
        key "keyVaultUri": str
        key "storageAccessMode": Union[str, StorageAccessMode]
        key "type": Union[str, PipelineSourceType]
        key "uri": str
        key_vault_uri: str
        storage_access_mode: Union[str, StorageAccessMode]
        type: Union[str, PipelineSourceType]
        uri: str


    class azure.mgmt.containerregistry.types.ImportSource(TypedDict, total=False):
        key "credentials": ForwardRef('ImportSourceCredentials', module='types')
        key "registryUri": str
        key "resourceId": str
        key "sourceImage": Required[str]
        credentials: ImportSourceCredentials
        registry_uri: str
        resource_id: str
        source_image: str


    class azure.mgmt.containerregistry.types.ImportSourceCredentials(TypedDict, total=False):
        key "password": Required[str]
        key "username": str
        password: str
        username: str


    class azure.mgmt.containerregistry.types.KeyVaultProperties(TypedDict, total=False):
        key "identity": str
        key "keyIdentifier": str
        key "keyRotationEnabled": bool
        key "lastKeyRotationTimestamp": str
        key "versionedKeyIdentifier": str
        identity: str
        key_identifier: str
        key_rotation_enabled: bool
        last_key_rotation_timestamp: str
        versioned_key_identifier: str


    class azure.mgmt.containerregistry.types.LoggingProperties(TypedDict, total=False):
        key "auditLogStatus": Union[str, AuditLogStatus]
        key "logLevel": Union[str, LogLevel]
        audit_log_status: Union[str, AuditLogStatus]
        log_level: Union[str, LogLevel]


    class azure.mgmt.containerregistry.types.LoginServerProperties(TypedDict, total=False):
        key "host": str
        key "tls": ForwardRef('TlsProperties', module='types')
        host: str
        tls: TlsProperties


    class azure.mgmt.containerregistry.types.NetworkRuleSet(TypedDict, total=False):
        key "defaultAction": Required[Union[str, DefaultAction]]
        default_action: Union[str, DefaultAction]
        ipRules: list[IPRule]
        ip_rules: list[IPRule]
        virtualNetworkRules: list[VirtualNetworkRule]
        virtual_network_rules: list[VirtualNetworkRule]


    class azure.mgmt.containerregistry.types.OperationDefinition(TypedDict, total=False):
        key "display": ForwardRef('OperationDisplayDefinition', module='types')
        key "isDataAction": bool
        key "name": str
        key "origin": str
        key "properties": ForwardRef('OperationPropertiesDefinition', module='types')
        display: OperationDisplayDefinition
        is_data_action: bool
        name: str
        origin: str
        properties: OperationPropertiesDefinition


    class azure.mgmt.containerregistry.types.OperationDisplayDefinition(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.containerregistry.types.OperationLogSpecificationDefinition(TypedDict, total=False):
        key "blobDuration": str
        key "displayName": str
        key "name": str
        blob_duration: str
        display_name: str
        name: str


    class azure.mgmt.containerregistry.types.OperationMetricSpecificationDefinition(TypedDict, total=False):
        key "aggregationType": str
        key "displayDescription": str
        key "displayName": str
        key "internalMetricName": str
        key "name": str
        key "unit": str
        aggregation_type: str
        display_description: str
        display_name: str
        internal_metric_name: str
        name: str
        unit: str


    class azure.mgmt.containerregistry.types.OperationPropertiesDefinition(TypedDict, total=False):
        key "serviceSpecification": ForwardRef('OperationServiceSpecificationDefinition', module='types')
        service_specification: OperationServiceSpecificationDefinition


    class azure.mgmt.containerregistry.types.OperationServiceSpecificationDefinition(TypedDict, total=False):
        logSpecifications: list[OperationLogSpecificationDefinition]
        log_specifications: list[OperationLogSpecificationDefinition]
        metricSpecifications: list[OperationMetricSpecificationDefinition]
        metric_specifications: list[OperationMetricSpecificationDefinition]


    class azure.mgmt.containerregistry.types.ParentProperties(TypedDict, total=False):
        key "id": str
        key "syncProperties": Required[SyncProperties]
        id: str
        sync_properties: SyncProperties


    class azure.mgmt.containerregistry.types.PipelineRun(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PipelineRunProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PipelineRunProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerregistry.types.PipelineRunProperties(TypedDict, total=False):
        key "forceUpdateTag": str
        key "provisioningState": Union[str, ProvisioningState]
        key "request": ForwardRef('PipelineRunRequest', module='types')
        key "response": ForwardRef('PipelineRunResponse', module='types')
        force_update_tag: str
        provisioning_state: Union[str, ProvisioningState]
        request: PipelineRunRequest
        response: PipelineRunResponse


    class azure.mgmt.containerregistry.types.PipelineRunRequest(TypedDict, total=False):
        key "catalogDigest": str
        key "pipelineResourceId": str
        key "source": ForwardRef('PipelineRunSourceProperties', module='types')
        key "target": ForwardRef('PipelineRunTargetProperties', module='types')
        artifacts: list[str]
        catalog_digest: str
        pipeline_resource_id: str
        source: PipelineRunSourceProperties
        target: PipelineRunTargetProperties


    class azure.mgmt.containerregistry.types.PipelineRunResponse(TypedDict, total=False):
        key "catalogDigest": str
        key "finishTime": str
        key "pipelineRunErrorMessage": str
        key "progress": ForwardRef('ProgressProperties', module='types')
        key "source": ForwardRef('ImportPipelineSourceProperties', module='types')
        key "startTime": str
        key "status": str
        key "target": ForwardRef('ExportPipelineTargetProperties', module='types')
        key "trigger": ForwardRef('PipelineTriggerDescriptor', module='types')
        catalog_digest: str
        finish_time: str
        importedArtifacts: list[str]
        imported_artifacts: list[str]
        pipeline_run_error_message: str
        progress: ProgressProperties
        source: ImportPipelineSourceProperties
        start_time: str
        status: str
        target: ExportPipelineTargetProperties
        trigger: PipelineTriggerDescriptor


    class azure.mgmt.containerregistry.types.PipelineRunSourceProperties(TypedDict, total=False):
        key "name": str
        key "type": Union[str, PipelineRunSourceType]
        name: str
        type: Union[str, PipelineRunSourceType]


    class azure.mgmt.containerregistry.types.PipelineRunTargetProperties(TypedDict, total=False):
        key "name": str
        key "type": Union[str, PipelineRunTargetType]
        name: str
        type: Union[str, PipelineRunTargetType]


    class azure.mgmt.containerregistry.types.PipelineSourceTriggerDescriptor(TypedDict, total=False):
        key "timestamp": str
        timestamp: str


    class azure.mgmt.containerregistry.types.PipelineSourceTriggerProperties(TypedDict, total=False):
        key "status": Required[Union[str, TriggerStatus]]
        status: Union[str, TriggerStatus]


    class azure.mgmt.containerregistry.types.PipelineTriggerDescriptor(TypedDict, total=False):
        key "sourceTrigger": ForwardRef('PipelineSourceTriggerDescriptor', module='types')
        source_trigger: PipelineSourceTriggerDescriptor


    class azure.mgmt.containerregistry.types.PipelineTriggerProperties(TypedDict, total=False):
        key "sourceTrigger": ForwardRef('PipelineSourceTriggerProperties', module='types')
        source_trigger: PipelineSourceTriggerProperties


    class azure.mgmt.containerregistry.types.Policies(TypedDict, total=False):
        key "azureADAuthenticationAsArmPolicy": ForwardRef('AzureADAuthenticationAsArmPolicy', module='types')
        key "exportPolicy": ForwardRef('ExportPolicy', module='types')
        key "quarantinePolicy": ForwardRef('QuarantinePolicy', module='types')
        key "retentionPolicy": ForwardRef('RetentionPolicy', module='types')
        key "softDeletePolicy": ForwardRef('SoftDeletePolicy', module='types')
        key "trustPolicy": ForwardRef('TrustPolicy', module='types')
        azure_ad_authentication_as_arm_policy: AzureADAuthenticationAsArmPolicy
        export_policy: ExportPolicy
        quarantine_policy: QuarantinePolicy
        retention_policy: RetentionPolicy
        soft_delete_policy: SoftDeletePolicy
        trust_policy: TrustPolicy


    class azure.mgmt.containerregistry.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.containerregistry.types.PrivateEndpointConnection(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerregistry.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": ForwardRef('PrivateLinkServiceConnectionState', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.containerregistry.types.PrivateLinkResource(Resource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateLinkResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateLinkResourceProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerregistry.types.PrivateLinkResourceProperties(TypedDict, total=False):
        key "groupId": str
        group_id: str
        requiredMembers: list[str]
        requiredZoneNames: list[str]
        required_members: list[str]
        required_zone_names: list[str]


    class azure.mgmt.containerregistry.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": Union[str, ActionsRequired]
        key "description": str
        key "status": Union[str, ConnectionStatus]
        actions_required: Union[str, ActionsRequired]
        description: str
        status: Union[str, ConnectionStatus]


    class azure.mgmt.containerregistry.types.ProgressProperties(TypedDict, total=False):
        key "percentage": str
        percentage: str


    class azure.mgmt.containerregistry.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.containerregistry.types.QuarantinePolicy(TypedDict, total=False):
        key "status": Union[str, PolicyStatus]
        status: Union[str, PolicyStatus]


    class azure.mgmt.containerregistry.types.RegenerateCredentialParameters(TypedDict, total=False):
        key "name": Required[Union[str, PasswordName]]
        name: Union[str, PasswordName]


    class azure.mgmt.containerregistry.types.Registry(TrackedResource):
        key "id": str
        key "identity": ForwardRef('IdentityProperties', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('RegistryProperties', module='types')
        key "sku": Required[Sku]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: IdentityProperties
        location: str
        name: str
        properties: RegistryProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.containerregistry.types.RegistryListCredentialsResult(TypedDict, total=False):
        key "username": str
        passwords: list[RegistryPassword]
        username: str


    class azure.mgmt.containerregistry.types.RegistryNameCheckRequest(TypedDict, total=False):
        key "autoGeneratedDomainNameLabelScope": Union[str, AutoGeneratedDomainNameLabelScope]
        key "name": Required[str]
        key "resourceGroupName": str
        key "type": Required[Union[str, ContainerRegistryResourceType]]
        auto_generated_domain_name_label_scope: Union[str, AutoGeneratedDomainNameLabelScope]
        name: str
        resource_group_name: str
        type: Union[str, ContainerRegistryResourceType]


    class azure.mgmt.containerregistry.types.RegistryNameStatus(TypedDict, total=False):
        key "availableLoginServerName": str
        key "message": str
        key "nameAvailable": bool
        key "reason": str
        available_login_server_name: str
        message: str
        name_available: bool
        reason: str


    class azure.mgmt.containerregistry.types.RegistryPassword(TypedDict, total=False):
        key "name": Union[str, PasswordName]
        key "value": str
        name: Union[str, PasswordName]
        value: str


    class azure.mgmt.containerregistry.types.RegistryProperties(TypedDict, total=False):
        key "adminUserEnabled": bool
        key "anonymousPullEnabled": bool
        key "autoGeneratedDomainNameLabelScope": Union[str, AutoGeneratedDomainNameLabelScope]
        key "creationDate": str
        key "dataEndpointEnabled": bool
        key "encryption": ForwardRef('EncryptionProperty', module='types')
        key "endpointProtocol": Union[str, EndpointProtocol]
        key "loginServer": str
        key "metadataSearch": Union[str, MetadataSearch]
        key "networkRuleBypassAllowedForTasks": bool
        key "networkRuleBypassOptions": Union[str, NetworkRuleBypassOptions]
        key "networkRuleSet": ForwardRef('NetworkRuleSet', module='types')
        key "policies": ForwardRef('Policies', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "regionalEndpoints": Union[str, RegionalEndpoints]
        key "roleAssignmentMode": Union[str, RoleAssignmentMode]
        key "status": ForwardRef('Status', module='types')
        key "writableCacheRepos": Union[str, WritableCacheRepos]
        key "zoneRedundancy": Union[str, ZoneRedundancy]
        admin_user_enabled: bool
        anonymous_pull_enabled: bool
        auto_generated_domain_name_label_scope: Union[str, AutoGeneratedDomainNameLabelScope]
        creation_date: str
        dataEndpointHostNames: list[str]
        data_endpoint_enabled: bool
        data_endpoint_host_names: list[str]
        encryption: EncryptionProperty
        endpoint_protocol: Union[str, EndpointProtocol]
        login_server: str
        metadata_search: Union[str, MetadataSearch]
        network_rule_bypass_allowed_for_tasks: bool
        network_rule_bypass_options: Union[str, NetworkRuleBypassOptions]
        network_rule_set: NetworkRuleSet
        policies: Policies
        privateEndpointConnections: list[PrivateEndpointConnection]
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: Union[str, ProvisioningState]
        public_network_access: Union[str, PublicNetworkAccess]
        regionalEndpointHostNames: list[str]
        regional_endpoint_host_names: list[str]
        regional_endpoints: Union[str, RegionalEndpoints]
        role_assignment_mode: Union[str, RoleAssignmentMode]
        status: Status
        writable_cache_repos: Union[str, WritableCacheRepos]
        zone_redundancy: Union[str, ZoneRedundancy]


    class azure.mgmt.containerregistry.types.RegistryPropertiesUpdateParameters(TypedDict, total=False):
        key "adminUserEnabled": bool
        key "anonymousPullEnabled": bool
        key "dataEndpointEnabled": bool
        key "encryption": ForwardRef('EncryptionProperty', module='types')
        key "endpointProtocol": Union[str, EndpointProtocol]
        key "metadataSearch": Union[str, MetadataSearch]
        key "networkRuleBypassAllowedForTasks": bool
        key "networkRuleBypassOptions": Union[str, NetworkRuleBypassOptions]
        key "networkRuleSet": ForwardRef('NetworkRuleSet', module='types')
        key "policies": ForwardRef('Policies', module='types')
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "regionalEndpoints": Union[str, RegionalEndpoints]
        key "roleAssignmentMode": Union[str, RoleAssignmentMode]
        key "writableCacheRepos": Union[str, WritableCacheRepos]
        admin_user_enabled: bool
        anonymous_pull_enabled: bool
        data_endpoint_enabled: bool
        encryption: EncryptionProperty
        endpoint_protocol: Union[str, EndpointProtocol]
        metadata_search: Union[str, MetadataSearch]
        network_rule_bypass_allowed_for_tasks: bool
        network_rule_bypass_options: Union[str, NetworkRuleBypassOptions]
        network_rule_set: NetworkRuleSet
        policies: Policies
        public_network_access: Union[str, PublicNetworkAccess]
        regional_endpoints: Union[str, RegionalEndpoints]
        role_assignment_mode: Union[str, RoleAssignmentMode]
        writable_cache_repos: Union[str, WritableCacheRepos]


    class azure.mgmt.containerregistry.types.RegistrySyncResult(TypedDict, total=False):
        key "lastSuccessfulSyncEndTime": str
        key "lastSyncEndTime": str
        key "lastSyncStartTime": str
        key "syncState": Required[Union[str, SyncState]]
        key "syncTrigger": Required[Union[str, SyncTrigger]]
        last_successful_sync_end_time: str
        last_sync_end_time: str
        last_sync_start_time: str
        sync_state: Union[str, SyncState]
        sync_trigger: Union[str, SyncTrigger]


    class azure.mgmt.containerregistry.types.RegistryUpdateParameters(TypedDict, total=False):
        key "identity": ForwardRef('IdentityProperties', module='types')
        key "properties": ForwardRef('RegistryPropertiesUpdateParameters', module='types')
        key "sku": ForwardRef('Sku', module='types')
        identity: IdentityProperties
        properties: RegistryPropertiesUpdateParameters
        sku: Sku
        tags: dict[str, str]


    class azure.mgmt.containerregistry.types.RegistryUsage(TypedDict, total=False):
        key "currentValue": int
        key "limit": int
        key "name": str
        key "unit": Union[str, RegistryUsageUnit]
        current_value: int
        limit: int
        name: str
        unit: Union[str, RegistryUsageUnit]


    class azure.mgmt.containerregistry.types.RegistryUsageListResult(TypedDict, total=False):
        value: list[RegistryUsage]


    class azure.mgmt.containerregistry.types.Replication(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ReplicationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ReplicationProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.containerregistry.types.ReplicationProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "regionEndpointEnabled": bool
        key "status": ForwardRef('Status', module='types')
        key "zoneRedundancy": Union[str, ZoneRedundancy]
        provisioning_state: Union[str, ProvisioningState]
        region_endpoint_enabled: bool
        status: Status
        zone_redundancy: Union[str, ZoneRedundancy]


    class azure.mgmt.containerregistry.types.ReplicationUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('ReplicationUpdateParametersProperties', module='types')
        properties: ReplicationUpdateParametersProperties
        tags: dict[str, str]


    class azure.mgmt.containerregistry.types.ReplicationUpdateParametersProperties(TypedDict, total=False):
        key "regionEndpointEnabled": bool
        region_endpoint_enabled: bool


    class azure.mgmt.containerregistry.types.Request(TypedDict, total=False):
        key "addr": str
        key "host": str
        key "id": str
        key "method": str
        key "useragent": str
        addr: str
        host: str
        id: str
        method: str
        useragent: str


    class azure.mgmt.containerregistry.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.containerregistry.types.RetentionPolicy(TypedDict, total=False):
        key "days": int
        key "lastUpdatedTime": str
        key "status": Union[str, PolicyStatus]
        days: int
        last_updated_time: str
        status: Union[str, PolicyStatus]


    class azure.mgmt.containerregistry.types.ScopeMap(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ScopeMapProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ScopeMapProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerregistry.types.ScopeMapProperties(TypedDict, total=False):
        key "actions": Required[list[str]]
        key "creationDate": str
        key "description": str
        key "provisioningState": Union[str, ProvisioningState]
        key "type": str
        actions: list[str]
        creation_date: str
        description: str
        provisioning_state: Union[str, ProvisioningState]
        type: str


    class azure.mgmt.containerregistry.types.ScopeMapPropertiesUpdateParameters(TypedDict, total=False):
        key "description": str
        actions: list[str]
        description: str


    class azure.mgmt.containerregistry.types.ScopeMapUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('ScopeMapPropertiesUpdateParameters', module='types')
        properties: ScopeMapPropertiesUpdateParameters


    class azure.mgmt.containerregistry.types.Sku(TypedDict, total=False):
        key "name": Required[Union[str, SkuName]]
        key "tier": Union[str, SkuTier]
        name: Union[str, SkuName]
        tier: Union[str, SkuTier]


    class azure.mgmt.containerregistry.types.SoftDeletePolicy(TypedDict, total=False):
        key "lastUpdatedTime": str
        key "retentionDays": int
        key "status": Union[str, PolicyStatus]
        last_updated_time: str
        retention_days: int
        status: Union[str, PolicyStatus]


    class azure.mgmt.containerregistry.types.Source(TypedDict, total=False):
        key "addr": str
        key "instanceID": str
        addr: str
        instance_id: str


    class azure.mgmt.containerregistry.types.Status(TypedDict, total=False):
        key "displayStatus": str
        key "message": str
        key "timestamp": str
        display_status: str
        message: str
        timestamp: str


    class azure.mgmt.containerregistry.types.StatusDetailProperties(TypedDict, total=False):
        key "code": str
        key "correlationId": str
        key "description": str
        key "timestamp": str
        key "type": str
        code: str
        correlation_id: str
        description: str
        timestamp: str
        type: str


    class azure.mgmt.containerregistry.types.SyncProperties(TypedDict, total=False):
        key "gatewayEndpoint": str
        key "lastSyncTime": str
        key "messageTtl": Required[str]
        key "schedule": str
        key "syncWindow": str
        key "tokenId": Required[str]
        gateway_endpoint: str
        last_sync_time: str
        message_ttl: str
        schedule: str
        sync_window: str
        token_id: str


    class azure.mgmt.containerregistry.types.SyncUpdateProperties(TypedDict, total=False):
        key "messageTtl": str
        key "schedule": str
        key "syncWindow": str
        message_ttl: str
        schedule: str
        sync_window: str


    class azure.mgmt.containerregistry.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.containerregistry.types.Target(TypedDict, total=False):
        key "digest": str
        key "length": int
        key "mediaType": str
        key "name": str
        key "repository": str
        key "size": int
        key "tag": str
        key "url": str
        key "version": str
        digest: str
        length: int
        media_type: str
        name: str
        repository: str
        size: int
        tag: str
        url: str
        version: str


    class azure.mgmt.containerregistry.types.TlsCertificateProperties(TypedDict, total=False):
        key "location": str
        key "type": Union[str, CertificateType]
        location: str
        type: Union[str, CertificateType]


    class azure.mgmt.containerregistry.types.TlsProperties(TypedDict, total=False):
        key "certificate": ForwardRef('TlsCertificateProperties', module='types')
        key "status": Union[str, TlsStatus]
        certificate: TlsCertificateProperties
        status: Union[str, TlsStatus]


    class azure.mgmt.containerregistry.types.Token(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('TokenProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: TokenProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerregistry.types.TokenCertificate(TypedDict, total=False):
        key "encodedPemCertificate": str
        key "expiry": str
        key "name": Union[str, TokenCertificateName]
        key "thumbprint": str
        encoded_pem_certificate: str
        expiry: str
        name: Union[str, TokenCertificateName]
        thumbprint: str


    class azure.mgmt.containerregistry.types.TokenCredentialsProperties(TypedDict, total=False):
        certificates: list[TokenCertificate]
        passwords: list[TokenPassword]


    class azure.mgmt.containerregistry.types.TokenPassword(TypedDict, total=False):
        key "creationTime": str
        key "expiry": str
        key "name": Union[str, TokenPasswordName]
        key "value": str
        creation_time: str
        expiry: str
        name: Union[str, TokenPasswordName]
        value: str


    class azure.mgmt.containerregistry.types.TokenProperties(TypedDict, total=False):
        key "creationDate": str
        key "credentials": ForwardRef('TokenCredentialsProperties', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "scopeMapId": str
        key "status": Union[str, TokenStatus]
        creation_date: str
        credentials: TokenCredentialsProperties
        provisioning_state: Union[str, ProvisioningState]
        scope_map_id: str
        status: Union[str, TokenStatus]


    class azure.mgmt.containerregistry.types.TokenUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('TokenUpdateProperties', module='types')
        properties: TokenUpdateProperties


    class azure.mgmt.containerregistry.types.TokenUpdateProperties(TypedDict, total=False):
        key "credentials": ForwardRef('TokenCredentialsProperties', module='types')
        key "scopeMapId": str
        key "status": Union[str, TokenStatus]
        credentials: TokenCredentialsProperties
        scope_map_id: str
        status: Union[str, TokenStatus]


    class azure.mgmt.containerregistry.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.containerregistry.types.TrustPolicy(TypedDict, total=False):
        key "status": Union[str, PolicyStatus]
        key "type": Union[str, TrustPolicyType]
        status: Union[str, PolicyStatus]
        type: Union[str, TrustPolicyType]


    class azure.mgmt.containerregistry.types.UserIdentityProperties(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.containerregistry.types.VirtualNetworkRule(TypedDict, total=False):
        key "action": Union[str, Action]
        key "virtualNetworkSubnetResourceId": Required[str]
        action: Union[str, Action]
        virtual_network_subnet_resource_id: str


    class azure.mgmt.containerregistry.types.Webhook(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('WebhookProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: WebhookProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.containerregistry.types.WebhookCreateParameters(TypedDict, total=False):
        key "location": Required[str]
        key "properties": ForwardRef('WebhookPropertiesCreateParameters', module='types')
        location: str
        properties: WebhookPropertiesCreateParameters
        tags: dict[str, str]


    class azure.mgmt.containerregistry.types.WebhookProperties(TypedDict, total=False):
        key "actions": Required[list[Union[str, WebhookAction]]]
        key "provisioningState": Union[str, ProvisioningState]
        key "scope": str
        key "status": Union[str, WebhookStatus]
        actions: list[Union[str, WebhookAction]]
        provisioning_state: Union[str, ProvisioningState]
        scope: str
        status: Union[str, WebhookStatus]


    class azure.mgmt.containerregistry.types.WebhookPropertiesCreateParameters(TypedDict, total=False):
        key "actions": Required[list[Union[str, WebhookAction]]]
        key "scope": str
        key "serviceUri": Required[str]
        key "status": Union[str, WebhookStatus]
        actions: list[Union[str, WebhookAction]]
        customHeaders: dict[str, str]
        custom_headers: dict[str, str]
        scope: str
        service_uri: str
        status: Union[str, WebhookStatus]


    class azure.mgmt.containerregistry.types.WebhookPropertiesUpdateParameters(TypedDict, total=False):
        key "scope": str
        key "serviceUri": str
        key "status": Union[str, WebhookStatus]
        actions: list[Union[str, WebhookAction]]
        customHeaders: dict[str, str]
        custom_headers: dict[str, str]
        scope: str
        service_uri: str
        status: Union[str, WebhookStatus]


    class azure.mgmt.containerregistry.types.WebhookUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('WebhookPropertiesUpdateParameters', module='types')
        properties: WebhookPropertiesUpdateParameters
        tags: dict[str, str]


```