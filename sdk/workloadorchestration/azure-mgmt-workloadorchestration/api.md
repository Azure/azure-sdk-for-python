```py
namespace azure.mgmt.workloadorchestration

    class azure.mgmt.workloadorchestration.WorkloadOrchestrationMgmtClient: implements ContextManager 
        config_template_metadatas: ConfigTemplateMetadatasOperations
        config_template_schemas: ConfigTemplateSchemasOperations
        config_template_versions: ConfigTemplateVersionsOperations
        config_templates: ConfigTemplatesOperations
        contexts: ContextsOperations
        diagnostics: DiagnosticsOperations
        dynamic_schema_versions: DynamicSchemaVersionsOperations
        dynamic_schemas: DynamicSchemasOperations
        executions: ExecutionsOperations
        hierarchy_configuration_metadata_versions: HierarchyConfigurationMetadataVersionsOperations
        hierarchy_configuration_metadatas: HierarchyConfigurationMetadatasOperations
        instance_histories: InstanceHistoriesOperations
        instances: InstancesOperations
        jobs: JobsOperations
        schema_references: SchemaReferencesOperations
        schema_versions: SchemaVersionsOperations
        schemas: SchemasOperations
        site_references: SiteReferencesOperations
        solution_deployments: SolutionDeploymentsOperations
        solution_metadata_versions: SolutionMetadataVersionsOperations
        solution_metadatas: SolutionMetadatasOperations
        solution_schemas: SolutionSchemasOperations
        solution_template_versions: SolutionTemplateVersionsOperations
        solution_templates: SolutionTemplatesOperations
        solution_versions: SolutionVersionsOperations
        solutions: SolutionsOperations
        targets: TargetsOperations
        workflow_versions: WorkflowVersionsOperations
        workflows: WorkflowsOperations

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


namespace azure.mgmt.workloadorchestration.aio

    class azure.mgmt.workloadorchestration.aio.WorkloadOrchestrationMgmtClient: implements AsyncContextManager 
        config_template_metadatas: ConfigTemplateMetadatasOperations
        config_template_schemas: ConfigTemplateSchemasOperations
        config_template_versions: ConfigTemplateVersionsOperations
        config_templates: ConfigTemplatesOperations
        contexts: ContextsOperations
        diagnostics: DiagnosticsOperations
        dynamic_schema_versions: DynamicSchemaVersionsOperations
        dynamic_schemas: DynamicSchemasOperations
        executions: ExecutionsOperations
        hierarchy_configuration_metadata_versions: HierarchyConfigurationMetadataVersionsOperations
        hierarchy_configuration_metadatas: HierarchyConfigurationMetadatasOperations
        instance_histories: InstanceHistoriesOperations
        instances: InstancesOperations
        jobs: JobsOperations
        schema_references: SchemaReferencesOperations
        schema_versions: SchemaVersionsOperations
        schemas: SchemasOperations
        site_references: SiteReferencesOperations
        solution_deployments: SolutionDeploymentsOperations
        solution_metadata_versions: SolutionMetadataVersionsOperations
        solution_metadatas: SolutionMetadatasOperations
        solution_schemas: SolutionSchemasOperations
        solution_template_versions: SolutionTemplateVersionsOperations
        solution_templates: SolutionTemplatesOperations
        solution_versions: SolutionVersionsOperations
        solutions: SolutionsOperations
        targets: TargetsOperations
        workflow_versions: WorkflowVersionsOperations
        workflows: WorkflowsOperations

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


namespace azure.mgmt.workloadorchestration.aio.operations

    class azure.mgmt.workloadorchestration.aio.operations.ConfigTemplateMetadatasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_metadata_name: str, 
                resource: ConfigTemplateMetadata, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigTemplateMetadata]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_metadata_name: str, 
                resource: ConfigTemplateMetadata, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigTemplateMetadata]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_metadata_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigTemplateMetadata]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'config_template_name', 'config_template_metadata_name']}, api_versions_list=['2026-03-01', '2026-05-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_metadata_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_metadata_name: str, 
                properties: ConfigTemplateMetadataUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigTemplateMetadata]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_metadata_name: str, 
                properties: ConfigTemplateMetadataUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigTemplateMetadata]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_metadata_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigTemplateMetadata]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'config_template_name', 'config_template_metadata_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_metadata_name: str, 
                **kwargs: Any
            ) -> ConfigTemplateMetadata: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'config_template_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        def list_by_config_template(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ConfigTemplateMetadata]: ...


    class azure.mgmt.workloadorchestration.aio.operations.ConfigTemplateSchemasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'config_template_name', 'config_template_version_name', 'config_template_schema_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_version_name: str, 
                config_template_schema_name: str, 
                **kwargs: Any
            ) -> ConfigTemplateSchema: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'config_template_name', 'config_template_version_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        def list_by_config_template_version(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_version_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ConfigTemplateSchema]: ...


    class azure.mgmt.workloadorchestration.aio.operations.ConfigTemplateVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_version_name: str, 
                resource: ConfigTemplateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigTemplateVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_version_name: str, 
                resource: ConfigTemplateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigTemplateVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_version_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigTemplateVersion]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'config_template_name', 'config_template_version_name']}, api_versions_list=['2026-03-01', '2026-05-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_version_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_version_name: str, 
                **kwargs: Any
            ) -> ConfigTemplateVersion: ...

        @distributed_trace
        def list_by_config_template(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ConfigTemplateVersion]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_version_name: str, 
                properties: ConfigTemplateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigTemplateVersion: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_version_name: str, 
                properties: ConfigTemplateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigTemplateVersion: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_version_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigTemplateVersion: ...


    class azure.mgmt.workloadorchestration.aio.operations.ConfigTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                resource: ConfigTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigTemplate]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                resource: ConfigTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigTemplate]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigTemplate]: ...

        @overload
        async def begin_create_version(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: ConfigTemplateVersionWithUpdateType, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigTemplateVersion]: ...

        @overload
        async def begin_create_version(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: ConfigTemplateVersionWithUpdateType, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigTemplateVersion]: ...

        @overload
        async def begin_create_version(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigTemplateVersion]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_link_to_hierarchies(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: HierarchySelector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_link_to_hierarchies(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: HierarchySelector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_link_to_hierarchies(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_un_link_from_hierarchies(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: HierarchySelector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_un_link_from_hierarchies(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: HierarchySelector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_un_link_from_hierarchies(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                **kwargs: Any
            ) -> ConfigTemplate: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ConfigTemplate]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ConfigTemplate]: ...

        @overload
        async def remove_version(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: VersionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RemoveVersionResponse: ...

        @overload
        async def remove_version(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: VersionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RemoveVersionResponse: ...

        @overload
        async def remove_version(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RemoveVersionResponse: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                properties: ConfigTemplateUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigTemplate: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                properties: ConfigTemplateUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigTemplate: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigTemplate: ...


    class azure.mgmt.workloadorchestration.aio.operations.ContextsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                resource: Context, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Context]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                resource: Context, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Context]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Context]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                context_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                properties: ContextUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Context]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                properties: ContextUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Context]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Context]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                context_name: str, 
                **kwargs: Any
            ) -> Context: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Context]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Context]: ...


    class azure.mgmt.workloadorchestration.aio.operations.DiagnosticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                diagnostic_name: str, 
                resource: Diagnostic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Diagnostic]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                diagnostic_name: str, 
                resource: Diagnostic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Diagnostic]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                diagnostic_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Diagnostic]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                diagnostic_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                diagnostic_name: str, 
                properties: DiagnosticUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Diagnostic]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                diagnostic_name: str, 
                properties: DiagnosticUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Diagnostic]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                diagnostic_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Diagnostic]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                diagnostic_name: str, 
                **kwargs: Any
            ) -> Diagnostic: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Diagnostic]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Diagnostic]: ...


    class azure.mgmt.workloadorchestration.aio.operations.DynamicSchemaVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                dynamic_schema_version_name: str, 
                resource: DynamicSchemaVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DynamicSchemaVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                dynamic_schema_version_name: str, 
                resource: DynamicSchemaVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DynamicSchemaVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                dynamic_schema_version_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DynamicSchemaVersion]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                dynamic_schema_version_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                dynamic_schema_version_name: str, 
                **kwargs: Any
            ) -> DynamicSchemaVersion: ...

        @distributed_trace
        def list_by_dynamic_schema(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DynamicSchemaVersion]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                dynamic_schema_version_name: str, 
                properties: DynamicSchemaVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DynamicSchemaVersion: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                dynamic_schema_version_name: str, 
                properties: DynamicSchemaVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DynamicSchemaVersion: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                dynamic_schema_version_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DynamicSchemaVersion: ...


    class azure.mgmt.workloadorchestration.aio.operations.DynamicSchemasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                resource: DynamicSchema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DynamicSchema]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                resource: DynamicSchema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DynamicSchema]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DynamicSchema]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                **kwargs: Any
            ) -> DynamicSchema: ...

        @distributed_trace
        def list_by_schema(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DynamicSchema]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                properties: DynamicSchema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DynamicSchema: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                properties: DynamicSchema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DynamicSchema: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DynamicSchema: ...


    class azure.mgmt.workloadorchestration.aio.operations.ExecutionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                execution_name: str, 
                resource: Execution, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Execution]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                execution_name: str, 
                resource: Execution, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Execution]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                execution_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Execution]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                execution_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                execution_name: str, 
                properties: Execution, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Execution]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                execution_name: str, 
                properties: Execution, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Execution]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                execution_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Execution]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                execution_name: str, 
                **kwargs: Any
            ) -> Execution: ...

        @distributed_trace
        def list_by_workflow_version(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Execution]: ...


    class azure.mgmt.workloadorchestration.aio.operations.HierarchyConfigurationMetadataVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'resource_uri', 'hierarchy_configuration_metadata_name', 'hierarchy_configuration_metadata_version_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        async def get(
                self, 
                resource_uri: str, 
                hierarchy_configuration_metadata_name: str, 
                hierarchy_configuration_metadata_version_name: str, 
                **kwargs: Any
            ) -> HierarchyConfigurationMetadataVersion: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'resource_uri', 'hierarchy_configuration_metadata_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        def list_by_parent(
                self, 
                resource_uri: str, 
                hierarchy_configuration_metadata_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[HierarchyConfigurationMetadataVersion]: ...


    class azure.mgmt.workloadorchestration.aio.operations.HierarchyConfigurationMetadatasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'resource_uri', 'hierarchy_configuration_metadata_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        async def get(
                self, 
                resource_uri: str, 
                hierarchy_configuration_metadata_name: str, 
                **kwargs: Any
            ) -> HierarchyConfigurationMetadata: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'resource_uri', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        def list_by_parent(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[HierarchyConfigurationMetadata]: ...


    class azure.mgmt.workloadorchestration.aio.operations.InstanceHistoriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                instance_name: str, 
                instance_history_name: str, 
                **kwargs: Any
            ) -> InstanceHistory: ...

        @distributed_trace
        def list_by_instance(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                instance_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[InstanceHistory]: ...


    class azure.mgmt.workloadorchestration.aio.operations.InstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                instance_name: str, 
                resource: Instance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Instance]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                instance_name: str, 
                resource: Instance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Instance]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                instance_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Instance]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                instance_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                instance_name: str, 
                properties: Instance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Instance]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                instance_name: str, 
                properties: Instance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Instance]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                instance_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Instance]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                instance_name: str, 
                **kwargs: Any
            ) -> Instance: ...

        @distributed_trace
        def list_by_solution(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Instance]: ...


    class azure.mgmt.workloadorchestration.aio.operations.JobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                job_name: str, 
                **kwargs: Any
            ) -> Job: ...

        @distributed_trace
        def list_by_target(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Job]: ...


    class azure.mgmt.workloadorchestration.aio.operations.SchemaReferencesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                schema_reference_name: str, 
                resource: SchemaReference, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SchemaReference]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                schema_reference_name: str, 
                resource: SchemaReference, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SchemaReference]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                schema_reference_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SchemaReference]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_uri: str, 
                schema_reference_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                schema_reference_name: str, 
                **kwargs: Any
            ) -> SchemaReference: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SchemaReference]: ...

        @overload
        async def update(
                self, 
                resource_uri: str, 
                schema_reference_name: str, 
                properties: SchemaReference, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaReference: ...

        @overload
        async def update(
                self, 
                resource_uri: str, 
                schema_reference_name: str, 
                properties: SchemaReference, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaReference: ...

        @overload
        async def update(
                self, 
                resource_uri: str, 
                schema_reference_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaReference: ...


    class azure.mgmt.workloadorchestration.aio.operations.SchemaVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                resource: SchemaVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SchemaVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                resource: SchemaVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SchemaVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SchemaVersion]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                **kwargs: Any
            ) -> SchemaVersion: ...

        @distributed_trace
        def list_by_schema(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SchemaVersion]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                properties: SchemaVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaVersion: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                properties: SchemaVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaVersion: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaVersion: ...


    class azure.mgmt.workloadorchestration.aio.operations.SchemasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                resource: Schema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Schema]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                resource: Schema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Schema]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Schema]: ...

        @overload
        async def begin_create_version(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                body: SchemaVersionWithUpdateType, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SchemaVersion]: ...

        @overload
        async def begin_create_version(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                body: SchemaVersionWithUpdateType, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SchemaVersion]: ...

        @overload
        async def begin_create_version(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SchemaVersion]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                **kwargs: Any
            ) -> Schema: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Schema]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Schema]: ...

        @overload
        async def remove_version(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                body: VersionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RemoveVersionResponse: ...

        @overload
        async def remove_version(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                body: VersionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RemoveVersionResponse: ...

        @overload
        async def remove_version(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RemoveVersionResponse: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                properties: SchemaUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schema: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                properties: SchemaUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schema: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schema: ...


    class azure.mgmt.workloadorchestration.aio.operations.SiteReferencesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                site_reference_name: str, 
                resource: SiteReference, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SiteReference]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                site_reference_name: str, 
                resource: SiteReference, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SiteReference]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                site_reference_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SiteReference]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                context_name: str, 
                site_reference_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                site_reference_name: str, 
                properties: SiteReference, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SiteReference]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                site_reference_name: str, 
                properties: SiteReference, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SiteReference]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                site_reference_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SiteReference]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                context_name: str, 
                site_reference_name: str, 
                **kwargs: Any
            ) -> SiteReference: ...

        @distributed_trace
        def list_by_context(
                self, 
                resource_group_name: str, 
                context_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SiteReference]: ...


    class azure.mgmt.workloadorchestration.aio.operations.SolutionDeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                solution_deployment_name: str, 
                resource: SolutionDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionDeployment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                solution_deployment_name: str, 
                resource: SolutionDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionDeployment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                solution_deployment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionDeployment]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'solution_deployment_name']}, api_versions_list=['2026-05-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                solution_deployment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'solution_deployment_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                solution_deployment_name: str, 
                **kwargs: Any
            ) -> SolutionDeployment: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SolutionDeployment]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[SolutionDeployment]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                solution_deployment_name: str, 
                properties: SolutionDeploymentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionDeployment: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                solution_deployment_name: str, 
                properties: SolutionDeploymentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionDeployment: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                solution_deployment_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionDeployment: ...


    class azure.mgmt.workloadorchestration.aio.operations.SolutionMetadataVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'resource_uri', 'solution_metadata_name', 'solution_metadata_version_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        async def get(
                self, 
                resource_uri: str, 
                solution_metadata_name: str, 
                solution_metadata_version_name: str, 
                **kwargs: Any
            ) -> SolutionMetadataVersion: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'resource_uri', 'solution_metadata_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        def list_by_parent(
                self, 
                resource_uri: str, 
                solution_metadata_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SolutionMetadataVersion]: ...


    class azure.mgmt.workloadorchestration.aio.operations.SolutionMetadatasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'resource_uri', 'solution_metadata_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        async def get(
                self, 
                resource_uri: str, 
                solution_metadata_name: str, 
                **kwargs: Any
            ) -> SolutionMetadata: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'resource_uri', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        def list_by_parent(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SolutionMetadata]: ...


    class azure.mgmt.workloadorchestration.aio.operations.SolutionSchemasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'solution_template_name', 'solution_template_version_name', 'solution_schema_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                solution_schema_name: str, 
                **kwargs: Any
            ) -> SolutionSchema: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'solution_template_name', 'solution_template_version_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        def list_by_solution_template_version(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SolutionSchema]: ...


    class azure.mgmt.workloadorchestration.aio.operations.SolutionTemplateVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_bulk_deploy_solution(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                body: BulkDeploySolutionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_bulk_deploy_solution(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                body: BulkDeploySolutionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_bulk_deploy_solution(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_bulk_publish_solution(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                body: BulkPublishSolutionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_bulk_publish_solution(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                body: BulkPublishSolutionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_bulk_publish_solution(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_bulk_review_solution(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                body: BulkReviewSolutionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_bulk_review_solution(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                body: BulkReviewSolutionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_bulk_review_solution(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                resource: SolutionTemplateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionTemplateVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                resource: SolutionTemplateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionTemplateVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionTemplateVersion]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'solution_template_name', 'solution_template_version_name']}, api_versions_list=['2026-03-01', '2026-05-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                **kwargs: Any
            ) -> SolutionTemplateVersion: ...

        @distributed_trace
        def list_by_solution_template(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SolutionTemplateVersion]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                properties: SolutionTemplateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionTemplateVersion: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                properties: SolutionTemplateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionTemplateVersion: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionTemplateVersion: ...


    class azure.mgmt.workloadorchestration.aio.operations.SolutionTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                resource: SolutionTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionTemplate]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                resource: SolutionTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionTemplate]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionTemplate]: ...

        @overload
        async def begin_create_version(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                body: SolutionTemplateVersionWithUpdateType, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionTemplateVersion]: ...

        @overload
        async def begin_create_version(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                body: SolutionTemplateVersionWithUpdateType, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionTemplateVersion]: ...

        @overload
        async def begin_create_version(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionTemplateVersion]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_remove_version(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                body: VersionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_remove_version(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                body: VersionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_remove_version(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                **kwargs: Any
            ) -> SolutionTemplate: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SolutionTemplate]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[SolutionTemplate]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                properties: SolutionTemplateUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionTemplate: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                properties: SolutionTemplateUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionTemplate: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionTemplate: ...


    class azure.mgmt.workloadorchestration.aio.operations.SolutionVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                solution_version_name: str, 
                resource: SolutionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                solution_version_name: str, 
                resource: SolutionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                solution_version_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionVersion]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                solution_version_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                solution_version_name: str, 
                properties: SolutionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionVersion]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                solution_version_name: str, 
                properties: SolutionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionVersion]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                solution_version_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionVersion]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                solution_version_name: str, 
                **kwargs: Any
            ) -> SolutionVersion: ...

        @distributed_trace
        def list_by_solution(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SolutionVersion]: ...


    class azure.mgmt.workloadorchestration.aio.operations.SolutionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                resource: Solution, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Solution]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                resource: Solution, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Solution]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Solution]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                properties: SolutionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Solution]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                properties: SolutionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Solution]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Solution]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                **kwargs: Any
            ) -> Solution: ...

        @distributed_trace
        def list_by_target(
                self, 
                resource_group_name: str, 
                target_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Solution]: ...


    class azure.mgmt.workloadorchestration.aio.operations.TargetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                resource: Target, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Target]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                resource: Target, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Target]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Target]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                target_name: str, 
                *, 
                force_delete: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_install_solution(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: InstallSolutionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_install_solution(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: InstallSolutionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_install_solution(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_publish_solution_version(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: SolutionVersionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionVersion]: ...

        @overload
        async def begin_publish_solution_version(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: SolutionVersionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionVersion]: ...

        @overload
        async def begin_publish_solution_version(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionVersion]: ...

        @overload
        async def begin_remove_revision(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: RemoveRevisionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_remove_revision(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: RemoveRevisionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_remove_revision(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_resolve_configuration(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: SolutionTemplateParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResolvedConfiguration]: ...

        @overload
        async def begin_resolve_configuration(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: SolutionTemplateParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResolvedConfiguration]: ...

        @overload
        async def begin_resolve_configuration(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResolvedConfiguration]: ...

        @overload
        async def begin_review_solution_version(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: SolutionTemplateParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionVersion]: ...

        @overload
        async def begin_review_solution_version(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: SolutionTemplateParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionVersion]: ...

        @overload
        async def begin_review_solution_version(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionVersion]: ...

        @overload
        async def begin_uninstall_solution(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: UninstallSolutionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_uninstall_solution(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: UninstallSolutionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_uninstall_solution(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_unstage_solution_version(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: SolutionVersionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionVersion]: ...

        @overload
        async def begin_unstage_solution_version(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: SolutionVersionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionVersion]: ...

        @overload
        async def begin_unstage_solution_version(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionVersion]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                properties: TargetUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Target]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                properties: TargetUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Target]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Target]: ...

        @overload
        async def begin_update_external_validation_status(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: UpdateExternalValidationStatusParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionVersion]: ...

        @overload
        async def begin_update_external_validation_status(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: UpdateExternalValidationStatusParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionVersion]: ...

        @overload
        async def begin_update_external_validation_status(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionVersion]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                target_name: str, 
                **kwargs: Any
            ) -> Target: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Target]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Target]: ...


    class azure.mgmt.workloadorchestration.aio.operations.WorkflowVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                resource: WorkflowVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkflowVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                resource: WorkflowVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkflowVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkflowVersion]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                properties: WorkflowVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkflowVersion]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                properties: WorkflowVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkflowVersion]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkflowVersion]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                **kwargs: Any
            ) -> WorkflowVersion: ...

        @distributed_trace
        def list_by_workflow(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkflowVersion]: ...


    class azure.mgmt.workloadorchestration.aio.operations.WorkflowsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                resource: Workflow, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workflow]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                resource: Workflow, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workflow]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workflow]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                properties: Workflow, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workflow]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                properties: Workflow, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workflow]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workflow]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                **kwargs: Any
            ) -> Workflow: ...

        @distributed_trace
        def list_by_context(
                self, 
                resource_group_name: str, 
                context_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Workflow]: ...


namespace azure.mgmt.workloadorchestration.models

    class azure.mgmt.workloadorchestration.models.ActiveState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        INACTIVE = "inactive"


    class azure.mgmt.workloadorchestration.models.AdditionalData(_Model):
        workflow_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                workflow_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.AvailableSolutionTemplateVersion(_Model):
        is_configured: bool
        latest_config_revision: str
        solution_template_version: str

        @overload
        def __init__(
                self, 
                *, 
                is_configured: bool, 
                latest_config_revision: str, 
                solution_template_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.BulkDeploySolutionParameter(_Model):
        targets: list[BulkDeployTargetDetails]

        @overload
        def __init__(
                self, 
                *, 
                targets: list[BulkDeployTargetDetails]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.BulkDeployTargetDetails(_Model):
        solution_version_id: str

        @overload
        def __init__(
                self, 
                *, 
                solution_version_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.BulkPublishSolutionParameter(_Model):
        solution_configuration: Optional[str]
        solution_dependencies: Optional[list[SolutionDependencyParameter]]
        solution_instance_name: Optional[str]
        targets: list[BulkPublishTargetDetails]

        @overload
        def __init__(
                self, 
                *, 
                solution_configuration: Optional[str] = ..., 
                solution_dependencies: Optional[list[SolutionDependencyParameter]] = ..., 
                solution_instance_name: Optional[str] = ..., 
                targets: list[BulkPublishTargetDetails]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.BulkPublishTargetDetails(_Model):
        solution_configuration: Optional[str]
        solution_dependencies: Optional[list[SolutionDependencyParameter]]
        solution_instance_name: Optional[str]
        solution_version_id: Optional[str]
        target_id: str

        @overload
        def __init__(
                self, 
                *, 
                solution_configuration: Optional[str] = ..., 
                solution_dependencies: Optional[list[SolutionDependencyParameter]] = ..., 
                solution_instance_name: Optional[str] = ..., 
                solution_version_id: Optional[str] = ..., 
                target_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.BulkReviewSolutionParameter(_Model):
        solution_configuration: Optional[str]
        solution_dependencies: Optional[list[SolutionDependencyParameter]]
        solution_instance_name: Optional[str]
        targets: list[BulkReviewTargetDetails]

        @overload
        def __init__(
                self, 
                *, 
                solution_configuration: Optional[str] = ..., 
                solution_dependencies: Optional[list[SolutionDependencyParameter]] = ..., 
                solution_instance_name: Optional[str] = ..., 
                targets: list[BulkReviewTargetDetails]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.BulkReviewTargetDetails(_Model):
        solution_configuration: Optional[str]
        solution_dependencies: Optional[list[SolutionDependencyParameter]]
        solution_instance_name: Optional[str]
        target_id: str

        @overload
        def __init__(
                self, 
                *, 
                solution_configuration: Optional[str] = ..., 
                solution_dependencies: Optional[list[SolutionDependencyParameter]] = ..., 
                solution_instance_name: Optional[str] = ..., 
                target_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.CMStages(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIGURATION = "Configuration"
        DEPLOYMENT = "Deployment"
        EXTERNAL_VALIDATION = "ExternalValidation"
        PUBLISH = "Publish"
        STAGING = "Staging"
        UNINSTALLATION = "Uninstallation"
        UNSTAGING = "Unstaging"


    class azure.mgmt.workloadorchestration.models.Capability(_Model):
        description: str
        name: str
        state: Optional[Union[str, ResourceState]]

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                name: str, 
                state: Optional[Union[str, ResourceState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ComponentStatus(_Model):
        name: Optional[str]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ConfigTemplate(TrackedResource):
        e_tag: Optional[str]
        id: str
        location: str
        name: str
        properties: Optional[ConfigTemplateProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ConfigTemplateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ConfigTemplateConfigurationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIGURATION_COMPLETED = "ConfigurationCompleted"
        CONFIGURATION_PENDING = "ConfigurationPending"


    class azure.mgmt.workloadorchestration.models.ConfigTemplateMetadata(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[ConfigTemplateMetadataProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConfigTemplateMetadataProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ConfigTemplateMetadataProperties(_Model):
        context_id: Optional[str]
        linked_hierarchies: Optional[list[HierarchyMetadata]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        template_unique_identifier: Optional[str]
        un_linked_hierarchies: Optional[list[HierarchyMetadata]]

        @overload
        def __init__(
                self, 
                *, 
                context_id: Optional[str] = ..., 
                linked_hierarchies: Optional[list[HierarchyMetadata]] = ..., 
                un_linked_hierarchies: Optional[list[HierarchyMetadata]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ConfigTemplateMetadataUpdate(_Model):
        properties: Optional[ConfigTemplateMetadataUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConfigTemplateMetadataUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ConfigTemplateMetadataUpdateProperties(_Model):
        context_id: Optional[str]
        linked_hierarchies: Optional[list[HierarchyMetadata]]
        un_linked_hierarchies: Optional[list[HierarchyMetadata]]

        @overload
        def __init__(
                self, 
                *, 
                context_id: Optional[str] = ..., 
                linked_hierarchies: Optional[list[HierarchyMetadata]] = ..., 
                un_linked_hierarchies: Optional[list[HierarchyMetadata]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ConfigTemplateProperties(_Model):
        description: str
        latest_version: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        unique_identifier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ConfigTemplateSchema(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[ConfigTemplateSchemaProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConfigTemplateSchemaProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ConfigTemplateSchemaProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        template_unique_identifier: Optional[str]
        value: Optional[Union[str, dict[str, Any]]]


    class azure.mgmt.workloadorchestration.models.ConfigTemplateUpdate(_Model):
        properties: Optional[ConfigTemplateUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConfigTemplateUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ConfigTemplateUpdateProperties(_Model):
        description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ConfigTemplateVersion(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[ConfigTemplateVersionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConfigTemplateVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ConfigTemplateVersionProperties(_Model):
        configurations: Union[str, dict[str, Any]]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                configurations: Union[str, dict[str, Any]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ConfigTemplateVersionWithUpdateType(_Model):
        config_template_version: ConfigTemplateVersion
        update_type: Optional[Union[str, UpdateType]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                config_template_version: ConfigTemplateVersion, 
                update_type: Optional[Union[str, UpdateType]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ConfigurationModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        COMMON = "Common"


    class azure.mgmt.workloadorchestration.models.ConfigurationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIGURATION_COMPLETED = "ConfigurationCompleted"
        CONFIGURATION_PENDING = "ConfigurationPending"


    class azure.mgmt.workloadorchestration.models.ConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIERARCHY = "Hierarchy"
        SHARED = "Shared"


    class azure.mgmt.workloadorchestration.models.Context(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ContextProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ContextProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ContextProperties(_Model):
        capabilities: list[Capability]
        hierarchies: list[Hierarchy]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        unique_identifier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: list[Capability], 
                hierarchies: list[Hierarchy]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ContextUpdate(_Model):
        properties: Optional[ContextUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ContextUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ContextUpdateProperties(_Model):
        capabilities: Optional[list[Capability]]
        hierarchies: Optional[list[Hierarchy]]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: Optional[list[Capability]] = ..., 
                hierarchies: Optional[list[Hierarchy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.workloadorchestration.models.DeployJobParameter(JobParameterBase, discriminator='deploy'):
        job_type: Literal[JobType.DEPLOY]
        parameter: Optional[InstallSolutionParameter]

        @overload
        def __init__(
                self, 
                *, 
                parameter: Optional[InstallSolutionParameter] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.DeployJobStepStatistics(JobStepStatisticsBase, discriminator='deploy'):
        failed_count: Optional[int]
        statistics_type: Literal[JobType.DEPLOY]
        success_count: Optional[int]
        total_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                failed_count: Optional[int] = ..., 
                success_count: Optional[int] = ..., 
                total_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.DeploymentStatus(_Model):
        deployed: Optional[int]
        expected_running_job_id: Optional[int]
        generation: Optional[int]
        last_modified: Optional[datetime]
        running_job_id: Optional[int]
        status: Optional[str]
        status_details: Optional[str]
        target_statuses: Optional[list[TargetStatus]]

        @overload
        def __init__(
                self, 
                *, 
                deployed: Optional[int] = ..., 
                expected_running_job_id: Optional[int] = ..., 
                generation: Optional[int] = ..., 
                last_modified: Optional[datetime] = ..., 
                running_job_id: Optional[int] = ..., 
                status: Optional[str] = ..., 
                status_details: Optional[str] = ..., 
                target_statuses: Optional[list[TargetStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.Diagnostic(TrackedResource):
        e_tag: Optional[str]
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: Optional[DiagnosticProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: Optional[DiagnosticProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.DiagnosticProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]


    class azure.mgmt.workloadorchestration.models.DiagnosticUpdate(_Model):
        properties: Optional[DiagnosticUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DiagnosticUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.DiagnosticUpdateProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]


    class azure.mgmt.workloadorchestration.models.DynamicSchema(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[DynamicSchemaProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DynamicSchemaProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.DynamicSchemaProperties(_Model):
        configuration_model: Optional[Union[str, ConfigurationModel]]
        configuration_type: Optional[Union[str, ConfigurationType]]
        display_name: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]


    class azure.mgmt.workloadorchestration.models.DynamicSchemaVersion(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[SchemaVersionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SchemaVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ErrorAction(_Model):
        max_tolerated_failures: Optional[int]
        mode: Optional[Union[str, ErrorActionMode]]

        @overload
        def __init__(
                self, 
                *, 
                max_tolerated_failures: Optional[int] = ..., 
                mode: Optional[Union[str, ErrorActionMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ErrorActionMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SILENTLY_CONTINUE = "silentlyContinue"
        STOP_ON_ANY_FAILURE = "stopOnAnyFailure"
        STOP_ON_N_FAILURES = "stopOnNFailures"


    class azure.mgmt.workloadorchestration.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.workloadorchestration.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.workloadorchestration.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.Execution(ProxyResource):
        e_tag: Optional[str]
        extended_location: Optional[ExtendedLocation]
        id: str
        name: str
        properties: Optional[ExecutionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                properties: Optional[ExecutionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ExecutionProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        specification: Optional[dict[str, Any]]
        status: Optional[ExecutionStatus]
        workflow_version_id: str

        @overload
        def __init__(
                self, 
                *, 
                specification: Optional[dict[str, Any]] = ..., 
                workflow_version_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ExecutionStatus(_Model):
        stage_history: Optional[list[StageStatus]]
        status: Optional[int]
        status_message: Optional[str]
        update_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                stage_history: Optional[list[StageStatus]] = ..., 
                status: Optional[int] = ..., 
                status_message: Optional[str] = ..., 
                update_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ExtendedLocation(_Model):
        name: str
        type: Union[str, ExtendedLocationType]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                type: Union[str, ExtendedLocationType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ExtendedLocationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_LOCATION = "CustomLocation"
        EDGE_ZONE = "EdgeZone"


    class azure.mgmt.workloadorchestration.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.workloadorchestration.models.Hierarchy(_Model):
        description: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.HierarchyConfigurationMetadata(ExtensionResource):
        id: str
        name: str
        properties: Optional[HierarchyConfigurationMetadataProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HierarchyConfigurationMetadataProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.HierarchyConfigurationMetadataProperties(_Model):
        config_template_id: Optional[str]
        display_name: Optional[str]


    class azure.mgmt.workloadorchestration.models.HierarchyConfigurationMetadataVersion(ProxyResource):
        id: str
        name: str
        properties: Optional[HierarchyConfigurationMetadataVersionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HierarchyConfigurationMetadataVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.HierarchyConfigurationMetadataVersionProperties(_Model):
        config_template_version_id: Optional[str]
        configuration_status: Optional[Union[str, ConfigTemplateConfigurationState]]
        dynamic_configuration_version_id: Optional[str]
        parent_display_name: Optional[str]
        schema_id: Optional[str]


    class azure.mgmt.workloadorchestration.models.HierarchyMetadata(_Model):
        hierarchy_ids: Optional[list[str]]
        level: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                hierarchy_ids: Optional[list[str]] = ..., 
                level: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.HierarchySelector(_Model):
        context_id: str
        hierarchy_ids: Optional[list[str]]
        level: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                context_id: str, 
                hierarchy_ids: Optional[list[str]] = ..., 
                level: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.InstallSolutionParameter(_Model):
        solution_version_id: str

        @overload
        def __init__(
                self, 
                *, 
                solution_version_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.Instance(ProxyResource):
        e_tag: Optional[str]
        extended_location: Optional[ExtendedLocation]
        id: str
        name: str
        properties: Optional[InstanceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                properties: Optional[InstanceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.InstanceHistory(ProxyResource):
        e_tag: Optional[str]
        extended_location: Optional[ExtendedLocation]
        id: str
        name: str
        properties: Optional[InstanceHistoryProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                properties: Optional[InstanceHistoryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.InstanceHistoryProperties(_Model):
        active_state: Optional[Union[str, ActiveState]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        reconciliation_policy: Optional[ReconciliationPolicyProperties]
        solution_scope: Optional[str]
        solution_version: SolutionVersionSnapshot
        status: Optional[DeploymentStatus]
        target: TargetSnapshot

        @overload
        def __init__(
                self, 
                *, 
                active_state: Optional[Union[str, ActiveState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.InstanceProperties(_Model):
        active_state: Optional[Union[str, ActiveState]]
        deployment_timestamp_epoch: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        reconciliation_policy: Optional[ReconciliationPolicyProperties]
        solution_scope: Optional[str]
        solution_version_id: str
        status: Optional[DeploymentStatus]
        target_id: str

        @overload
        def __init__(
                self, 
                *, 
                active_state: Optional[Union[str, ActiveState]] = ..., 
                reconciliation_policy: Optional[ReconciliationPolicyProperties] = ..., 
                solution_scope: Optional[str] = ..., 
                solution_version_id: str, 
                target_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.InternalState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PENDING_VALIDATION = "PendingValidation"
        VALIDATED = "Validated"
        VALIDATED_WITHOUT_SCHEMA = "ValidatedWithoutSchema"
        VALIDATED_WITH_SCHEMA = "ValidatedWithSchema"


    class azure.mgmt.workloadorchestration.models.Job(ExtensionResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[JobProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[JobProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.JobParameterBase(_Model):
        job_type: str

        @overload
        def __init__(
                self, 
                *, 
                job_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.JobProperties(_Model):
        additional_data: Optional[AdditionalData]
        correlation_id: Optional[str]
        end_time: Optional[datetime]
        error_details: Optional[ErrorDetail]
        job_parameter: Optional[JobParameterBase]
        job_type: Union[str, JobType]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        start_time: Optional[datetime]
        status: Union[str, JobStatus]
        steps: Optional[list[JobStep]]
        triggered_by: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_data: Optional[AdditionalData] = ..., 
                correlation_id: Optional[str] = ..., 
                end_time: Optional[datetime] = ..., 
                job_parameter: Optional[JobParameterBase] = ..., 
                job_type: Union[str, JobType], 
                start_time: Optional[datetime] = ..., 
                status: Union[str, JobStatus], 
                steps: Optional[list[JobStep]] = ..., 
                triggered_by: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.JobStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NOT_STARTED = "NotStarted"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.workloadorchestration.models.JobStep(_Model):
        end_time: Optional[datetime]
        error_details: Optional[ErrorDetail]
        message: Optional[str]
        name: str
        start_time: Optional[datetime]
        statistics: Optional[JobStepStatisticsBase]
        status: Union[str, JobStatus]
        steps: Optional[list[JobStep]]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                message: Optional[str] = ..., 
                name: str, 
                start_time: Optional[datetime] = ..., 
                statistics: Optional[JobStepStatisticsBase] = ..., 
                status: Union[str, JobStatus], 
                steps: Optional[list[JobStep]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.JobStepStatisticsBase(_Model):
        statistics_type: str

        @overload
        def __init__(
                self, 
                *, 
                statistics_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.JobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEPLOY = "deploy"
        EXTERNAL_VALIDATION = "externalValidation"
        PUBLISH = "publish"
        STAGING = "staging"
        UNINSTALL = "uninstall"


    class azure.mgmt.workloadorchestration.models.OrchestratorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TO = "TO"


    class azure.mgmt.workloadorchestration.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        INITIALIZED = "Initialized"
        INPROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.workloadorchestration.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.workloadorchestration.models.PublishJobParameter(JobParameterBase, discriminator='publish'):
        job_type: Literal[JobType.PUBLISH]
        parameter: Optional[SolutionVersionParameter]

        @overload
        def __init__(
                self, 
                *, 
                parameter: Optional[SolutionVersionParameter] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.PublishJobStepStatistics(JobStepStatisticsBase, discriminator='publish'):
        failed_count: Optional[int]
        statistics_type: Literal[JobType.PUBLISH]
        success_count: Optional[int]
        total_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                failed_count: Optional[int] = ..., 
                success_count: Optional[int] = ..., 
                total_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ReconciliationPolicyProperties(_Model):
        interval: str
        state: Union[str, ReconciliationState]

        @overload
        def __init__(
                self, 
                *, 
                interval: str, 
                state: Union[str, ReconciliationState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ReconciliationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        INACTIVE = "inactive"


    class azure.mgmt.workloadorchestration.models.RemoveRevisionParameter(_Model):
        solution_template_id: str
        solution_version: str

        @overload
        def __init__(
                self, 
                *, 
                solution_template_id: str, 
                solution_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.RemoveVersionResponse(_Model):
        status: str

        @overload
        def __init__(
                self, 
                *, 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ResolvedConfiguration(_Model):
        configuration: str

        @overload
        def __init__(
                self, 
                *, 
                configuration: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.workloadorchestration.models.ResourceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        INACTIVE = "inactive"


    class azure.mgmt.workloadorchestration.models.Schema(TrackedResource):
        e_tag: Optional[str]
        id: str
        location: str
        name: str
        properties: Optional[SchemaProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[SchemaProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SchemaProperties(_Model):
        current_version: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]


    class azure.mgmt.workloadorchestration.models.SchemaReference(ExtensionResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[SchemaReferenceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SchemaReferenceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SchemaReferenceProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        schema_id: str

        @overload
        def __init__(
                self, 
                *, 
                schema_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SchemaUpdate(_Model):
        properties: Optional[SchemaUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SchemaUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SchemaUpdateProperties(_Model):
        current_version: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]


    class azure.mgmt.workloadorchestration.models.SchemaVersion(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[SchemaVersionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SchemaVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SchemaVersionProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        value: Union[str, dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                value: Union[str, dict[str, Any]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SchemaVersionWithUpdateType(_Model):
        schema_version: SchemaVersion
        update_type: Optional[Union[str, UpdateType]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                schema_version: SchemaVersion, 
                update_type: Optional[Union[str, UpdateType]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SiteReference(ProxyResource):
        id: str
        name: str
        properties: Optional[SiteReferenceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SiteReferenceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SiteReferenceProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        site_id: str

        @overload
        def __init__(
                self, 
                *, 
                site_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.Solution(ProxyResource):
        e_tag: Optional[str]
        extended_location: Optional[ExtendedLocation]
        id: str
        name: str
        properties: Optional[SolutionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                properties: Optional[SolutionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionDependency(_Model):
        dependencies: Optional[list[SolutionDependency]]
        solution_instance_name: Optional[str]
        solution_template_version_id: str
        solution_version_id: str
        target_id: str

        @overload
        def __init__(
                self, 
                *, 
                dependencies: Optional[list[SolutionDependency]] = ..., 
                solution_instance_name: Optional[str] = ..., 
                solution_template_version_id: str, 
                solution_version_id: str, 
                target_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionDependencyParameter(_Model):
        dependencies: Optional[list[SolutionDependencyParameter]]
        solution_instance_name: Optional[str]
        solution_template_id: Optional[str]
        solution_template_version: Optional[str]
        solution_version_id: Optional[str]
        target_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                dependencies: Optional[list[SolutionDependencyParameter]] = ..., 
                solution_instance_name: Optional[str] = ..., 
                solution_template_id: Optional[str] = ..., 
                solution_template_version: Optional[str] = ..., 
                solution_version_id: Optional[str] = ..., 
                target_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionDeployment(TrackedResource):
        e_tag: Optional[str]
        id: str
        location: str
        name: str
        properties: Optional[SolutionDeploymentProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[SolutionDeploymentProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionDeploymentProperties(_Model):
        input: Optional[dict[str, Any]]
        output: Optional[dict[str, Any]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        solution_template_properties: SolutionTemplateMetadata
        target_properties: TargetMetadata

        @overload
        def __init__(
                self, 
                *, 
                input: Optional[dict[str, Any]] = ..., 
                solution_template_properties: SolutionTemplateMetadata, 
                target_properties: TargetMetadata
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionDeploymentUpdate(_Model):
        properties: Optional[SolutionDeploymentUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SolutionDeploymentUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionDeploymentUpdateProperties(_Model):
        input: Optional[dict[str, Any]]
        solution_template_properties: Optional[SolutionTemplateMetadataUpdate]
        target_properties: Optional[TargetMetadata]

        @overload
        def __init__(
                self, 
                *, 
                input: Optional[dict[str, Any]] = ..., 
                solution_template_properties: Optional[SolutionTemplateMetadataUpdate] = ..., 
                target_properties: Optional[TargetMetadata] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionMetadata(ExtensionResource):
        id: str
        name: str
        properties: Optional[SolutionMetadataProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SolutionMetadataProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionMetadataProperties(_Model):
        current_version: Optional[str]
        display_name: Optional[str]
        latest_version: Optional[str]
        solution_template_id: Optional[str]


    class azure.mgmt.workloadorchestration.models.SolutionMetadataVersion(ProxyResource):
        id: str
        name: str
        properties: Optional[SolutionMetadataVersionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SolutionMetadataVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionMetadataVersionProperties(_Model):
        configuration_status: Optional[Union[str, ConfigurationState]]
        dynamic_configuration_version_id: Optional[str]
        parent_display_name: Optional[str]
        schema_id: Optional[str]
        solution_template_version_id: Optional[str]


    class azure.mgmt.workloadorchestration.models.SolutionProperties(_Model):
        available_solution_template_versions: Optional[list[AvailableSolutionTemplateVersion]]
        display_name: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        solution_template_id: Optional[str]


    class azure.mgmt.workloadorchestration.models.SolutionSchema(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[SolutionSchemaProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SolutionSchemaProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionSchemaProperties(_Model):
        level: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        template_unique_identifier: Optional[str]
        value: Optional[Union[str, dict[str, Any]]]


    class azure.mgmt.workloadorchestration.models.SolutionTemplate(TrackedResource):
        e_tag: Optional[str]
        id: str
        location: str
        name: str
        properties: Optional[SolutionTemplateProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[SolutionTemplateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionTemplateMetadata(_Model):
        name: str
        resource_group_name: Optional[str]
        subscription_id: Optional[str]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                resource_group_name: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionTemplateMetadataUpdate(_Model):
        name: Optional[str]
        resource_group_name: Optional[str]
        subscription_id: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                resource_group_name: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionTemplateParameter(_Model):
        solution_dependencies: Optional[list[SolutionDependencyParameter]]
        solution_instance_name: Optional[str]
        solution_template_version_id: str

        @overload
        def __init__(
                self, 
                *, 
                solution_dependencies: Optional[list[SolutionDependencyParameter]] = ..., 
                solution_instance_name: Optional[str] = ..., 
                solution_template_version_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionTemplateProperties(_Model):
        capabilities: list[str]
        description: str
        enable_external_validation: Optional[bool]
        latest_version: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        state: Optional[Union[str, ResourceState]]
        unique_identifier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: list[str], 
                description: str, 
                enable_external_validation: Optional[bool] = ..., 
                state: Optional[Union[str, ResourceState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionTemplateUpdate(_Model):
        properties: Optional[SolutionTemplateUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SolutionTemplateUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionTemplateUpdateProperties(_Model):
        capabilities: Optional[list[str]]
        description: Optional[str]
        enable_external_validation: Optional[bool]
        state: Optional[Union[str, ResourceState]]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: Optional[list[str]] = ..., 
                description: Optional[str] = ..., 
                enable_external_validation: Optional[bool] = ..., 
                state: Optional[Union[str, ResourceState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionTemplateVersion(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[SolutionTemplateVersionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SolutionTemplateVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionTemplateVersionProperties(_Model):
        configurations: Optional[Union[str, dict[str, Any]]]
        internal_state: Optional[Union[str, InternalState]]
        orchestrator_type: Optional[Union[str, OrchestratorType]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        specification: dict[str, Any]

        @overload
        def __init__(
                self, 
                *, 
                configurations: Optional[Union[str, dict[str, Any]]] = ..., 
                orchestrator_type: Optional[Union[str, OrchestratorType]] = ..., 
                specification: dict[str, Any]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionTemplateVersionWithUpdateType(_Model):
        solution_template_version: SolutionTemplateVersion
        update_type: Optional[Union[str, UpdateType]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                solution_template_version: SolutionTemplateVersion, 
                update_type: Optional[Union[str, UpdateType]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionUpdate(_Model):
        properties: Optional[SolutionUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SolutionUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionUpdateProperties(_Model):
        available_solution_template_versions: Optional[list[AvailableSolutionTemplateVersion]]
        display_name: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        solution_template_id: Optional[str]


    class azure.mgmt.workloadorchestration.models.SolutionVersion(ProxyResource):
        e_tag: Optional[str]
        extended_location: Optional[ExtendedLocation]
        id: str
        name: str
        properties: Optional[SolutionVersionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                properties: Optional[SolutionVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionVersionParameter(_Model):
        solution_version_id: str

        @overload
        def __init__(
                self, 
                *, 
                solution_version_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionVersionProperties(_Model):
        action_type: Optional[Union[str, JobType]]
        configuration: Optional[Union[str, dict[str, Any]]]
        current_stage: Optional[StageMap]
        error_details: Optional[ErrorDetail]
        external_validation_id: Optional[str]
        latest_action_tracking_uri: Optional[str]
        latest_action_triggered_by: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        review_id: Optional[str]
        revision: Optional[int]
        solution_dependencies: Optional[list[SolutionDependency]]
        solution_instance_name: Optional[str]
        solution_template_version_id: Optional[str]
        specification: dict[str, Any]
        stages: Optional[list[StageMap]]
        state: Optional[Union[str, State]]
        target_display_name: Optional[str]
        target_level_configuration: Optional[Union[str, dict[str, Any]]]

        @overload
        def __init__(
                self, 
                *, 
                specification: dict[str, Any]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionVersionSnapshot(_Model):
        solution_version_id: Optional[str]
        specification: Optional[dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                solution_version_id: Optional[str] = ..., 
                specification: Optional[dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.StageMap(_Model):
        child_stages: Optional[list[StageMap]]
        display_state: str
        end_time: Optional[datetime]
        stage: Union[str, CMStages]
        start_time: Optional[datetime]
        status: Union[str, StateCategory]


    class azure.mgmt.workloadorchestration.models.StageSpec(_Model):
        name: str
        specification: Optional[dict[str, Any]]
        task_option: Optional[TaskOption]
        tasks: Optional[list[TaskSpec]]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                specification: Optional[dict[str, Any]] = ..., 
                task_option: Optional[TaskOption] = ..., 
                tasks: Optional[list[TaskSpec]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.StageStatus(_Model):
        error_message: Optional[str]
        inputs: Optional[dict[str, Any]]
        is_active: Optional[Union[str, ActiveState]]
        nextstage: Optional[str]
        outputs: Optional[dict[str, Any]]
        stage: Optional[str]
        status: Optional[int]
        status_message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error_message: Optional[str] = ..., 
                inputs: Optional[dict[str, Any]] = ..., 
                is_active: Optional[Union[str, ActiveState]] = ..., 
                nextstage: Optional[str] = ..., 
                outputs: Optional[dict[str, Any]] = ..., 
                stage: Optional[str] = ..., 
                status: Optional[int] = ..., 
                status_message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.State(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEPLOYED = "Deployed"
        DEPLOYING = "Deploying"
        EXTERNAL_VALIDATION_FAILED = "ExternalValidationFailed"
        FAILED = "Failed"
        IN_REVIEW = "InReview"
        NOT_APPLICABLE = "NotApplicable"
        PENDING_EXTERNAL_VALIDATION = "PendingExternalValidation"
        READY_TO_DEPLOY = "ReadyToDeploy"
        READY_TO_UPGRADE = "ReadyToUpgrade"
        STAGING = "Staging"
        UNDEPLOYED = "Undeployed"
        UPGRADE_IN_REVIEW = "UpgradeInReview"


    class azure.mgmt.workloadorchestration.models.StateCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NONE = "None"
        PENDING = "Pending"


    class azure.mgmt.workloadorchestration.models.SystemData(_Model):
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


    class azure.mgmt.workloadorchestration.models.Target(TrackedResource):
        e_tag: Optional[str]
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: Optional[TargetProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: Optional[TargetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.TargetMetadata(_Model):
        capabilities: Optional[list[str]]
        target_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: Optional[list[str]] = ..., 
                target_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.TargetProperties(_Model):
        capabilities: list[str]
        context_id: str
        description: str
        display_name: str
        hierarchy_level: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        solution_scope: Optional[str]
        state: Optional[Union[str, ResourceState]]
        status: Optional[DeploymentStatus]
        target_specification: Optional[dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: list[str], 
                context_id: str, 
                description: str, 
                display_name: str, 
                hierarchy_level: str, 
                solution_scope: Optional[str] = ..., 
                state: Optional[Union[str, ResourceState]] = ..., 
                target_specification: Optional[dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.TargetSnapshot(_Model):
        solution_scope: Optional[str]
        target_id: Optional[str]
        target_specification: Optional[dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                solution_scope: Optional[str] = ..., 
                target_id: Optional[str] = ..., 
                target_specification: Optional[dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.TargetStatus(_Model):
        component_statuses: Optional[list[ComponentStatus]]
        name: Optional[str]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                component_statuses: Optional[list[ComponentStatus]] = ..., 
                name: Optional[str] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.TargetUpdate(_Model):
        properties: Optional[TargetUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TargetUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.TargetUpdateProperties(_Model):
        capabilities: Optional[list[str]]
        context_id: Optional[str]
        description: Optional[str]
        display_name: Optional[str]
        hierarchy_level: Optional[str]
        solution_scope: Optional[str]
        state: Optional[Union[str, ResourceState]]
        target_specification: Optional[dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: Optional[list[str]] = ..., 
                context_id: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                hierarchy_level: Optional[str] = ..., 
                solution_scope: Optional[str] = ..., 
                state: Optional[Union[str, ResourceState]] = ..., 
                target_specification: Optional[dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.TaskOption(_Model):
        concurrency: Optional[int]
        error_action: Optional[ErrorAction]

        @overload
        def __init__(
                self, 
                *, 
                concurrency: Optional[int] = ..., 
                error_action: Optional[ErrorAction] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.TaskSpec(_Model):
        name: str
        specification: dict[str, Any]
        target_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                specification: dict[str, Any], 
                target_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.TrackedResource(Resource):
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


    class azure.mgmt.workloadorchestration.models.UninstallJobParameter(JobParameterBase, discriminator='uninstall'):
        job_type: Literal[JobType.UNINSTALL]
        parameter: Optional[UninstallSolutionParameter]

        @overload
        def __init__(
                self, 
                *, 
                parameter: Optional[UninstallSolutionParameter] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.UninstallJobStepStatistics(JobStepStatisticsBase, discriminator='uninstall'):
        failed_count: Optional[int]
        statistics_type: Literal[JobType.UNINSTALL]
        success_count: Optional[int]
        total_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                failed_count: Optional[int] = ..., 
                success_count: Optional[int] = ..., 
                total_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.UninstallSolutionParameter(_Model):
        solution_instance_name: Optional[str]
        solution_template_id: str

        @overload
        def __init__(
                self, 
                *, 
                solution_instance_name: Optional[str] = ..., 
                solution_template_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.UpdateExternalValidationStatusParameter(_Model):
        error_details: Optional[ErrorDetail]
        external_validation_id: str
        solution_version_id: str
        validation_status: Union[str, ValidationStatus]

        @overload
        def __init__(
                self, 
                *, 
                error_details: Optional[ErrorDetail] = ..., 
                external_validation_id: str, 
                solution_version_id: str, 
                validation_status: Union[str, ValidationStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.UpdateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MAJOR = "Major"
        MINOR = "Minor"
        PATCH = "Patch"


    class azure.mgmt.workloadorchestration.models.ValidationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        VALID = "Valid"


    class azure.mgmt.workloadorchestration.models.VersionParameter(_Model):
        version: str

        @overload
        def __init__(
                self, 
                *, 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.Workflow(ProxyResource):
        e_tag: Optional[str]
        extended_location: Optional[ExtendedLocation]
        id: str
        name: str
        properties: Optional[WorkflowProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                properties: Optional[WorkflowProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.WorkflowProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        workflow_template_id: Optional[str]


    class azure.mgmt.workloadorchestration.models.WorkflowVersion(ProxyResource):
        e_tag: Optional[str]
        extended_location: Optional[ExtendedLocation]
        id: str
        name: str
        properties: Optional[WorkflowVersionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                properties: Optional[WorkflowVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.WorkflowVersionProperties(_Model):
        configuration: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        review_id: Optional[str]
        revision: Optional[int]
        specification: Optional[dict[str, Any]]
        stage_spec: list[StageSpec]
        state: Optional[Union[str, State]]

        @overload
        def __init__(
                self, 
                *, 
                specification: Optional[dict[str, Any]] = ..., 
                stage_spec: list[StageSpec]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.workloadorchestration.operations

    class azure.mgmt.workloadorchestration.operations.ConfigTemplateMetadatasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_metadata_name: str, 
                resource: ConfigTemplateMetadata, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfigTemplateMetadata]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_metadata_name: str, 
                resource: ConfigTemplateMetadata, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfigTemplateMetadata]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_metadata_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfigTemplateMetadata]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'config_template_name', 'config_template_metadata_name']}, api_versions_list=['2026-03-01', '2026-05-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_metadata_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_metadata_name: str, 
                properties: ConfigTemplateMetadataUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfigTemplateMetadata]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_metadata_name: str, 
                properties: ConfigTemplateMetadataUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfigTemplateMetadata]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_metadata_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfigTemplateMetadata]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'config_template_name', 'config_template_metadata_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_metadata_name: str, 
                **kwargs: Any
            ) -> ConfigTemplateMetadata: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'config_template_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        def list_by_config_template(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ConfigTemplateMetadata]: ...


    class azure.mgmt.workloadorchestration.operations.ConfigTemplateSchemasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'config_template_name', 'config_template_version_name', 'config_template_schema_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_version_name: str, 
                config_template_schema_name: str, 
                **kwargs: Any
            ) -> ConfigTemplateSchema: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'config_template_name', 'config_template_version_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        def list_by_config_template_version(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_version_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ConfigTemplateSchema]: ...


    class azure.mgmt.workloadorchestration.operations.ConfigTemplateVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_version_name: str, 
                resource: ConfigTemplateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfigTemplateVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_version_name: str, 
                resource: ConfigTemplateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfigTemplateVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_version_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfigTemplateVersion]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'config_template_name', 'config_template_version_name']}, api_versions_list=['2026-03-01', '2026-05-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_version_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_version_name: str, 
                **kwargs: Any
            ) -> ConfigTemplateVersion: ...

        @distributed_trace
        def list_by_config_template(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ConfigTemplateVersion]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_version_name: str, 
                properties: ConfigTemplateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigTemplateVersion: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_version_name: str, 
                properties: ConfigTemplateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigTemplateVersion: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                config_template_version_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigTemplateVersion: ...


    class azure.mgmt.workloadorchestration.operations.ConfigTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                resource: ConfigTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfigTemplate]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                resource: ConfigTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfigTemplate]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfigTemplate]: ...

        @overload
        def begin_create_version(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: ConfigTemplateVersionWithUpdateType, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfigTemplateVersion]: ...

        @overload
        def begin_create_version(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: ConfigTemplateVersionWithUpdateType, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfigTemplateVersion]: ...

        @overload
        def begin_create_version(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfigTemplateVersion]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_link_to_hierarchies(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: HierarchySelector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_link_to_hierarchies(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: HierarchySelector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_link_to_hierarchies(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_un_link_from_hierarchies(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: HierarchySelector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_un_link_from_hierarchies(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: HierarchySelector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_un_link_from_hierarchies(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                **kwargs: Any
            ) -> ConfigTemplate: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ConfigTemplate]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ConfigTemplate]: ...

        @overload
        def remove_version(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: VersionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RemoveVersionResponse: ...

        @overload
        def remove_version(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: VersionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RemoveVersionResponse: ...

        @overload
        def remove_version(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RemoveVersionResponse: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                properties: ConfigTemplateUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigTemplate: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                properties: ConfigTemplateUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigTemplate: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigTemplate: ...


    class azure.mgmt.workloadorchestration.operations.ContextsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                resource: Context, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Context]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                resource: Context, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Context]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Context]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                context_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                properties: ContextUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Context]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                properties: ContextUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Context]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Context]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                context_name: str, 
                **kwargs: Any
            ) -> Context: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Context]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Context]: ...


    class azure.mgmt.workloadorchestration.operations.DiagnosticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                diagnostic_name: str, 
                resource: Diagnostic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Diagnostic]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                diagnostic_name: str, 
                resource: Diagnostic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Diagnostic]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                diagnostic_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Diagnostic]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                diagnostic_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                diagnostic_name: str, 
                properties: DiagnosticUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Diagnostic]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                diagnostic_name: str, 
                properties: DiagnosticUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Diagnostic]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                diagnostic_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Diagnostic]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                diagnostic_name: str, 
                **kwargs: Any
            ) -> Diagnostic: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Diagnostic]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Diagnostic]: ...


    class azure.mgmt.workloadorchestration.operations.DynamicSchemaVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                dynamic_schema_version_name: str, 
                resource: DynamicSchemaVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DynamicSchemaVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                dynamic_schema_version_name: str, 
                resource: DynamicSchemaVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DynamicSchemaVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                dynamic_schema_version_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DynamicSchemaVersion]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                dynamic_schema_version_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                dynamic_schema_version_name: str, 
                **kwargs: Any
            ) -> DynamicSchemaVersion: ...

        @distributed_trace
        def list_by_dynamic_schema(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DynamicSchemaVersion]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                dynamic_schema_version_name: str, 
                properties: DynamicSchemaVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DynamicSchemaVersion: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                dynamic_schema_version_name: str, 
                properties: DynamicSchemaVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DynamicSchemaVersion: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                dynamic_schema_version_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DynamicSchemaVersion: ...


    class azure.mgmt.workloadorchestration.operations.DynamicSchemasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                resource: DynamicSchema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DynamicSchema]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                resource: DynamicSchema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DynamicSchema]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DynamicSchema]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                **kwargs: Any
            ) -> DynamicSchema: ...

        @distributed_trace
        def list_by_schema(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DynamicSchema]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                properties: DynamicSchema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DynamicSchema: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                properties: DynamicSchema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DynamicSchema: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DynamicSchema: ...


    class azure.mgmt.workloadorchestration.operations.ExecutionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                execution_name: str, 
                resource: Execution, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Execution]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                execution_name: str, 
                resource: Execution, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Execution]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                execution_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Execution]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                execution_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                execution_name: str, 
                properties: Execution, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Execution]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                execution_name: str, 
                properties: Execution, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Execution]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                execution_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Execution]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                execution_name: str, 
                **kwargs: Any
            ) -> Execution: ...

        @distributed_trace
        def list_by_workflow_version(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Execution]: ...


    class azure.mgmt.workloadorchestration.operations.HierarchyConfigurationMetadataVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'resource_uri', 'hierarchy_configuration_metadata_name', 'hierarchy_configuration_metadata_version_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        def get(
                self, 
                resource_uri: str, 
                hierarchy_configuration_metadata_name: str, 
                hierarchy_configuration_metadata_version_name: str, 
                **kwargs: Any
            ) -> HierarchyConfigurationMetadataVersion: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'resource_uri', 'hierarchy_configuration_metadata_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        def list_by_parent(
                self, 
                resource_uri: str, 
                hierarchy_configuration_metadata_name: str, 
                **kwargs: Any
            ) -> ItemPaged[HierarchyConfigurationMetadataVersion]: ...


    class azure.mgmt.workloadorchestration.operations.HierarchyConfigurationMetadatasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'resource_uri', 'hierarchy_configuration_metadata_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        def get(
                self, 
                resource_uri: str, 
                hierarchy_configuration_metadata_name: str, 
                **kwargs: Any
            ) -> HierarchyConfigurationMetadata: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'resource_uri', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        def list_by_parent(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> ItemPaged[HierarchyConfigurationMetadata]: ...


    class azure.mgmt.workloadorchestration.operations.InstanceHistoriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                instance_name: str, 
                instance_history_name: str, 
                **kwargs: Any
            ) -> InstanceHistory: ...

        @distributed_trace
        def list_by_instance(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                instance_name: str, 
                **kwargs: Any
            ) -> ItemPaged[InstanceHistory]: ...


    class azure.mgmt.workloadorchestration.operations.InstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                instance_name: str, 
                resource: Instance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Instance]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                instance_name: str, 
                resource: Instance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Instance]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                instance_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Instance]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                instance_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                instance_name: str, 
                properties: Instance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Instance]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                instance_name: str, 
                properties: Instance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Instance]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                instance_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Instance]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                instance_name: str, 
                **kwargs: Any
            ) -> Instance: ...

        @distributed_trace
        def list_by_solution(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Instance]: ...


    class azure.mgmt.workloadorchestration.operations.JobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                job_name: str, 
                **kwargs: Any
            ) -> Job: ...

        @distributed_trace
        def list_by_target(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> ItemPaged[Job]: ...


    class azure.mgmt.workloadorchestration.operations.SchemaReferencesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                schema_reference_name: str, 
                resource: SchemaReference, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SchemaReference]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                schema_reference_name: str, 
                resource: SchemaReference, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SchemaReference]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                schema_reference_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SchemaReference]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_uri: str, 
                schema_reference_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                schema_reference_name: str, 
                **kwargs: Any
            ) -> SchemaReference: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> ItemPaged[SchemaReference]: ...

        @overload
        def update(
                self, 
                resource_uri: str, 
                schema_reference_name: str, 
                properties: SchemaReference, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaReference: ...

        @overload
        def update(
                self, 
                resource_uri: str, 
                schema_reference_name: str, 
                properties: SchemaReference, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaReference: ...

        @overload
        def update(
                self, 
                resource_uri: str, 
                schema_reference_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaReference: ...


    class azure.mgmt.workloadorchestration.operations.SchemaVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                resource: SchemaVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SchemaVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                resource: SchemaVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SchemaVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SchemaVersion]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                **kwargs: Any
            ) -> SchemaVersion: ...

        @distributed_trace
        def list_by_schema(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SchemaVersion]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                properties: SchemaVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaVersion: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                properties: SchemaVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaVersion: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaVersion: ...


    class azure.mgmt.workloadorchestration.operations.SchemasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                resource: Schema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Schema]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                resource: Schema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Schema]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Schema]: ...

        @overload
        def begin_create_version(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                body: SchemaVersionWithUpdateType, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SchemaVersion]: ...

        @overload
        def begin_create_version(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                body: SchemaVersionWithUpdateType, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SchemaVersion]: ...

        @overload
        def begin_create_version(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SchemaVersion]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                **kwargs: Any
            ) -> Schema: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Schema]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Schema]: ...

        @overload
        def remove_version(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                body: VersionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RemoveVersionResponse: ...

        @overload
        def remove_version(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                body: VersionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RemoveVersionResponse: ...

        @overload
        def remove_version(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RemoveVersionResponse: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                properties: SchemaUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schema: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                properties: SchemaUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schema: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schema: ...


    class azure.mgmt.workloadorchestration.operations.SiteReferencesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                site_reference_name: str, 
                resource: SiteReference, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SiteReference]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                site_reference_name: str, 
                resource: SiteReference, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SiteReference]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                site_reference_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SiteReference]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                context_name: str, 
                site_reference_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                site_reference_name: str, 
                properties: SiteReference, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SiteReference]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                site_reference_name: str, 
                properties: SiteReference, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SiteReference]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                site_reference_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SiteReference]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                context_name: str, 
                site_reference_name: str, 
                **kwargs: Any
            ) -> SiteReference: ...

        @distributed_trace
        def list_by_context(
                self, 
                resource_group_name: str, 
                context_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SiteReference]: ...


    class azure.mgmt.workloadorchestration.operations.SolutionDeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                solution_deployment_name: str, 
                resource: SolutionDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionDeployment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                solution_deployment_name: str, 
                resource: SolutionDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionDeployment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                solution_deployment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionDeployment]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'solution_deployment_name']}, api_versions_list=['2026-05-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                solution_deployment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'solution_deployment_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                solution_deployment_name: str, 
                **kwargs: Any
            ) -> SolutionDeployment: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SolutionDeployment]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[SolutionDeployment]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                solution_deployment_name: str, 
                properties: SolutionDeploymentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionDeployment: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                solution_deployment_name: str, 
                properties: SolutionDeploymentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionDeployment: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                solution_deployment_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionDeployment: ...


    class azure.mgmt.workloadorchestration.operations.SolutionMetadataVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'resource_uri', 'solution_metadata_name', 'solution_metadata_version_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        def get(
                self, 
                resource_uri: str, 
                solution_metadata_name: str, 
                solution_metadata_version_name: str, 
                **kwargs: Any
            ) -> SolutionMetadataVersion: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'resource_uri', 'solution_metadata_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        def list_by_parent(
                self, 
                resource_uri: str, 
                solution_metadata_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SolutionMetadataVersion]: ...


    class azure.mgmt.workloadorchestration.operations.SolutionMetadatasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'resource_uri', 'solution_metadata_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        def get(
                self, 
                resource_uri: str, 
                solution_metadata_name: str, 
                **kwargs: Any
            ) -> SolutionMetadata: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'resource_uri', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        def list_by_parent(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> ItemPaged[SolutionMetadata]: ...


    class azure.mgmt.workloadorchestration.operations.SolutionSchemasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'solution_template_name', 'solution_template_version_name', 'solution_schema_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                solution_schema_name: str, 
                **kwargs: Any
            ) -> SolutionSchema: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'solution_template_name', 'solution_template_version_name', 'accept']}, api_versions_list=['2025-08-01', '2025-08-15-preview', '2026-03-01', '2026-05-01-preview'])
        def list_by_solution_template_version(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SolutionSchema]: ...


    class azure.mgmt.workloadorchestration.operations.SolutionTemplateVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_bulk_deploy_solution(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                body: BulkDeploySolutionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_bulk_deploy_solution(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                body: BulkDeploySolutionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_bulk_deploy_solution(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_bulk_publish_solution(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                body: BulkPublishSolutionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_bulk_publish_solution(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                body: BulkPublishSolutionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_bulk_publish_solution(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_bulk_review_solution(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                body: BulkReviewSolutionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_bulk_review_solution(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                body: BulkReviewSolutionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_bulk_review_solution(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                resource: SolutionTemplateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionTemplateVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                resource: SolutionTemplateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionTemplateVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionTemplateVersion]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'solution_template_name', 'solution_template_version_name']}, api_versions_list=['2026-03-01', '2026-05-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                **kwargs: Any
            ) -> SolutionTemplateVersion: ...

        @distributed_trace
        def list_by_solution_template(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SolutionTemplateVersion]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                properties: SolutionTemplateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionTemplateVersion: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                properties: SolutionTemplateVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionTemplateVersion: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                solution_template_version_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionTemplateVersion: ...


    class azure.mgmt.workloadorchestration.operations.SolutionTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                resource: SolutionTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionTemplate]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                resource: SolutionTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionTemplate]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionTemplate]: ...

        @overload
        def begin_create_version(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                body: SolutionTemplateVersionWithUpdateType, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionTemplateVersion]: ...

        @overload
        def begin_create_version(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                body: SolutionTemplateVersionWithUpdateType, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionTemplateVersion]: ...

        @overload
        def begin_create_version(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionTemplateVersion]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_remove_version(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                body: VersionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_remove_version(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                body: VersionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_remove_version(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                **kwargs: Any
            ) -> SolutionTemplate: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SolutionTemplate]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[SolutionTemplate]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                properties: SolutionTemplateUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionTemplate: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                properties: SolutionTemplateUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionTemplate: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionTemplate: ...


    class azure.mgmt.workloadorchestration.operations.SolutionVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                solution_version_name: str, 
                resource: SolutionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                solution_version_name: str, 
                resource: SolutionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                solution_version_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionVersion]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                solution_version_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                solution_version_name: str, 
                properties: SolutionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionVersion]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                solution_version_name: str, 
                properties: SolutionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionVersion]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                solution_version_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionVersion]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                solution_version_name: str, 
                **kwargs: Any
            ) -> SolutionVersion: ...

        @distributed_trace
        def list_by_solution(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SolutionVersion]: ...


    class azure.mgmt.workloadorchestration.operations.SolutionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                resource: Solution, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Solution]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                resource: Solution, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Solution]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Solution]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                properties: SolutionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Solution]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                properties: SolutionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Solution]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Solution]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                target_name: str, 
                solution_name: str, 
                **kwargs: Any
            ) -> Solution: ...

        @distributed_trace
        def list_by_target(
                self, 
                resource_group_name: str, 
                target_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Solution]: ...


    class azure.mgmt.workloadorchestration.operations.TargetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                resource: Target, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Target]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                resource: Target, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Target]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Target]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                target_name: str, 
                *, 
                force_delete: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_install_solution(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: InstallSolutionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_install_solution(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: InstallSolutionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_install_solution(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_publish_solution_version(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: SolutionVersionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionVersion]: ...

        @overload
        def begin_publish_solution_version(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: SolutionVersionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionVersion]: ...

        @overload
        def begin_publish_solution_version(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionVersion]: ...

        @overload
        def begin_remove_revision(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: RemoveRevisionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_remove_revision(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: RemoveRevisionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_remove_revision(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_resolve_configuration(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: SolutionTemplateParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResolvedConfiguration]: ...

        @overload
        def begin_resolve_configuration(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: SolutionTemplateParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResolvedConfiguration]: ...

        @overload
        def begin_resolve_configuration(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResolvedConfiguration]: ...

        @overload
        def begin_review_solution_version(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: SolutionTemplateParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionVersion]: ...

        @overload
        def begin_review_solution_version(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: SolutionTemplateParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionVersion]: ...

        @overload
        def begin_review_solution_version(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionVersion]: ...

        @overload
        def begin_uninstall_solution(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: UninstallSolutionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_uninstall_solution(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: UninstallSolutionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_uninstall_solution(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_unstage_solution_version(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: SolutionVersionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionVersion]: ...

        @overload
        def begin_unstage_solution_version(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: SolutionVersionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionVersion]: ...

        @overload
        def begin_unstage_solution_version(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionVersion]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                properties: TargetUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Target]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                properties: TargetUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Target]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Target]: ...

        @overload
        def begin_update_external_validation_status(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: UpdateExternalValidationStatusParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionVersion]: ...

        @overload
        def begin_update_external_validation_status(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: UpdateExternalValidationStatusParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionVersion]: ...

        @overload
        def begin_update_external_validation_status(
                self, 
                resource_group_name: str, 
                target_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionVersion]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                target_name: str, 
                **kwargs: Any
            ) -> Target: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Target]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Target]: ...


    class azure.mgmt.workloadorchestration.operations.WorkflowVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                resource: WorkflowVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkflowVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                resource: WorkflowVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkflowVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkflowVersion]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                properties: WorkflowVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkflowVersion]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                properties: WorkflowVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkflowVersion]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkflowVersion]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                version_name: str, 
                **kwargs: Any
            ) -> WorkflowVersion: ...

        @distributed_trace
        def list_by_workflow(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WorkflowVersion]: ...


    class azure.mgmt.workloadorchestration.operations.WorkflowsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                resource: Workflow, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workflow]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                resource: Workflow, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workflow]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workflow]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                properties: Workflow, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workflow]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                properties: Workflow, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workflow]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workflow]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                context_name: str, 
                workflow_name: str, 
                **kwargs: Any
            ) -> Workflow: ...

        @distributed_trace
        def list_by_context(
                self, 
                resource_group_name: str, 
                context_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Workflow]: ...


namespace azure.mgmt.workloadorchestration.types

    class azure.mgmt.workloadorchestration.types.AvailableSolutionTemplateVersion(TypedDict, total=False):
        key "isConfigured": Required[bool]
        key "latestConfigRevision": Required[str]
        key "solutionTemplateVersion": Required[str]
        isConfigured: bool
        latestConfigRevision: str
        solutionTemplateVersion: str


    class azure.mgmt.workloadorchestration.types.BulkDeploySolutionParameter(TypedDict, total=False):
        key "targets": Required[list[BulkDeployTargetDetails]]
        targets: list[BulkDeployTargetDetails]


    class azure.mgmt.workloadorchestration.types.BulkDeployTargetDetails(TypedDict, total=False):
        key "solutionVersionId": Required[str]
        solutionVersionId: str


    class azure.mgmt.workloadorchestration.types.BulkPublishSolutionParameter(TypedDict, total=False):
        key "solutionConfiguration": str
        key "solutionInstanceName": str
        key "targets": Required[list[BulkPublishTargetDetails]]
        solutionConfiguration: str
        solutionDependencies: list[SolutionDependencyParameter]
        solutionInstanceName: str
        targets: list[BulkPublishTargetDetails]


    class azure.mgmt.workloadorchestration.types.BulkPublishTargetDetails(TypedDict, total=False):
        key "solutionConfiguration": str
        key "solutionInstanceName": str
        key "solutionVersionId": str
        key "targetId": Required[str]
        solutionConfiguration: str
        solutionDependencies: list[SolutionDependencyParameter]
        solutionInstanceName: str
        solutionVersionId: str
        targetId: str


    class azure.mgmt.workloadorchestration.types.BulkReviewSolutionParameter(TypedDict, total=False):
        key "solutionConfiguration": str
        key "solutionInstanceName": str
        key "targets": Required[list[BulkReviewTargetDetails]]
        solutionConfiguration: str
        solutionDependencies: list[SolutionDependencyParameter]
        solutionInstanceName: str
        targets: list[BulkReviewTargetDetails]


    class azure.mgmt.workloadorchestration.types.BulkReviewTargetDetails(TypedDict, total=False):
        key "solutionConfiguration": str
        key "solutionInstanceName": str
        key "targetId": Required[str]
        solutionConfiguration: str
        solutionDependencies: list[SolutionDependencyParameter]
        solutionInstanceName: str
        targetId: str


    class azure.mgmt.workloadorchestration.types.Capability(TypedDict, total=False):
        key "description": Required[str]
        key "name": Required[str]
        key "state": Union[str, ResourceState]
        description: str
        name: str
        state: Union[str, ResourceState]


    class azure.mgmt.workloadorchestration.types.ComponentStatus(TypedDict, total=False):
        key "name": str
        key "status": str
        name: str
        status: str


    class azure.mgmt.workloadorchestration.types.ConfigTemplate(TrackedResource):
        key "eTag": str
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ConfigTemplateProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        location: str
        name: str
        properties: ConfigTemplateProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.workloadorchestration.types.ConfigTemplateMetadata(ProxyResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('ConfigTemplateMetadataProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        name: str
        properties: ConfigTemplateMetadataProperties
        systemData: SystemData
        type: str


    class azure.mgmt.workloadorchestration.types.ConfigTemplateMetadataProperties(TypedDict, total=False):
        key "contextId": str
        key "provisioningState": Union[str, ProvisioningState]
        key "templateUniqueIdentifier": str
        contextId: str
        linkedHierarchies: list[HierarchyMetadata]
        provisioningState: Union[str, ProvisioningState]
        templateUniqueIdentifier: str
        unLinkedHierarchies: list[HierarchyMetadata]


    class azure.mgmt.workloadorchestration.types.ConfigTemplateMetadataUpdate(TypedDict, total=False):
        key "properties": ForwardRef('ConfigTemplateMetadataUpdateProperties', module='types')
        properties: ConfigTemplateMetadataUpdateProperties


    class azure.mgmt.workloadorchestration.types.ConfigTemplateMetadataUpdateProperties(TypedDict, total=False):
        key "contextId": str
        contextId: str
        linkedHierarchies: list[HierarchyMetadata]
        unLinkedHierarchies: list[HierarchyMetadata]


    class azure.mgmt.workloadorchestration.types.ConfigTemplateProperties(TypedDict, total=False):
        key "description": Required[str]
        key "latestVersion": str
        key "provisioningState": Union[str, ProvisioningState]
        key "uniqueIdentifier": str
        description: str
        latestVersion: str
        provisioningState: Union[str, ProvisioningState]
        uniqueIdentifier: str


    class azure.mgmt.workloadorchestration.types.ConfigTemplateUpdate(TypedDict, total=False):
        key "properties": ForwardRef('ConfigTemplateUpdateProperties', module='types')
        properties: ConfigTemplateUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.workloadorchestration.types.ConfigTemplateUpdateProperties(TypedDict, total=False):
        key "description": str
        description: str


    class azure.mgmt.workloadorchestration.types.ConfigTemplateVersion(ProxyResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('ConfigTemplateVersionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        name: str
        properties: ConfigTemplateVersionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.workloadorchestration.types.ConfigTemplateVersionProperties(TypedDict, total=False):
        key "configurations": Required[Union[str, dict[str, Any]]]
        key "provisioningState": Union[str, ProvisioningState]
        configurations: Union[str, dict[str, Any]]
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.workloadorchestration.types.ConfigTemplateVersionWithUpdateType(TypedDict, total=False):
        key "configTemplateVersion": Required[ConfigTemplateVersion]
        key "updateType": Union[str, UpdateType]
        key "version": str
        configTemplateVersion: ConfigTemplateVersion
        updateType: Union[str, UpdateType]
        version: str


    class azure.mgmt.workloadorchestration.types.Context(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ContextProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ContextProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.workloadorchestration.types.ContextProperties(TypedDict, total=False):
        key "capabilities": Required[list[Capability]]
        key "hierarchies": Required[list[Hierarchy]]
        key "provisioningState": Union[str, ProvisioningState]
        key "uniqueIdentifier": str
        capabilities: list[Capability]
        hierarchies: list[Hierarchy]
        provisioningState: Union[str, ProvisioningState]
        uniqueIdentifier: str


    class azure.mgmt.workloadorchestration.types.ContextUpdate(TypedDict, total=False):
        key "properties": ForwardRef('ContextUpdateProperties', module='types')
        properties: ContextUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.workloadorchestration.types.ContextUpdateProperties(TypedDict, total=False):
        capabilities: list[Capability]
        hierarchies: list[Hierarchy]


    class azure.mgmt.workloadorchestration.types.DeploymentStatus(TypedDict, total=False):
        key "deployed": int
        key "expectedRunningJobId": int
        key "generation": int
        key "lastModified": str
        key "runningJobId": int
        key "status": str
        key "statusDetails": str
        deployed: int
        expectedRunningJobId: int
        generation: int
        lastModified: str
        runningJobId: int
        status: str
        statusDetails: str
        targetStatuses: list[TargetStatus]


    class azure.mgmt.workloadorchestration.types.Diagnostic(TrackedResource):
        key "eTag": str
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('DiagnosticProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: DiagnosticProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.workloadorchestration.types.DiagnosticProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.workloadorchestration.types.DiagnosticUpdate(TypedDict, total=False):
        key "properties": ForwardRef('DiagnosticUpdateProperties', module='types')
        properties: DiagnosticUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.workloadorchestration.types.DiagnosticUpdateProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.workloadorchestration.types.DynamicSchema(ProxyResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('DynamicSchemaProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        name: str
        properties: DynamicSchemaProperties
        systemData: SystemData
        type: str


    class azure.mgmt.workloadorchestration.types.DynamicSchemaProperties(TypedDict, total=False):
        key "configurationModel": Union[str, ConfigurationModel]
        key "configurationType": Union[str, ConfigurationType]
        key "displayName": str
        key "provisioningState": Union[str, ProvisioningState]
        configurationModel: Union[str, ConfigurationModel]
        configurationType: Union[str, ConfigurationType]
        displayName: str
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.workloadorchestration.types.DynamicSchemaVersion(ProxyResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('SchemaVersionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        name: str
        properties: SchemaVersionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.workloadorchestration.types.ErrorAction(TypedDict, total=False):
        key "maxToleratedFailures": int
        key "mode": Union[str, ErrorActionMode]
        maxToleratedFailures: int
        mode: Union[str, ErrorActionMode]


    class azure.mgmt.workloadorchestration.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.workloadorchestration.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.workloadorchestration.types.Execution(ProxyResource):
        key "eTag": str
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "name": str
        key "properties": ForwardRef('ExecutionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        extendedLocation: ExtendedLocation
        id: str
        name: str
        properties: ExecutionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.workloadorchestration.types.ExecutionProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "status": ForwardRef('ExecutionStatus', module='types')
        key "workflowVersionId": Required[str]
        provisioningState: Union[str, ProvisioningState]
        specification: dict[str, Any]
        status: ExecutionStatus
        workflowVersionId: str


    class azure.mgmt.workloadorchestration.types.ExecutionStatus(TypedDict, total=False):
        key "status": int
        key "statusMessage": str
        key "updateTime": str
        stageHistory: list[StageStatus]
        status: int
        statusMessage: str
        updateTime: str


    class azure.mgmt.workloadorchestration.types.ExtendedLocation(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Union[str, ExtendedLocationType]]
        name: str
        type: Union[str, ExtendedLocationType]


    class azure.mgmt.workloadorchestration.types.ExtensionResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.workloadorchestration.types.Hierarchy(TypedDict, total=False):
        key "description": Required[str]
        key "name": Required[str]
        description: str
        name: str


    class azure.mgmt.workloadorchestration.types.HierarchyMetadata(TypedDict, total=False):
        key "level": str
        hierarchyIds: list[str]
        level: str


    class azure.mgmt.workloadorchestration.types.HierarchySelector(TypedDict, total=False):
        key "contextId": Required[str]
        key "level": str
        contextId: str
        hierarchyIds: list[str]
        level: str


    class azure.mgmt.workloadorchestration.types.InstallSolutionParameter(TypedDict, total=False):
        key "solutionVersionId": Required[str]
        solutionVersionId: str


    class azure.mgmt.workloadorchestration.types.Instance(ProxyResource):
        key "eTag": str
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "name": str
        key "properties": ForwardRef('InstanceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        extendedLocation: ExtendedLocation
        id: str
        name: str
        properties: InstanceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.workloadorchestration.types.InstanceProperties(TypedDict, total=False):
        key "activeState": Union[str, ActiveState]
        key "deploymentTimestampEpoch": int
        key "provisioningState": Union[str, ProvisioningState]
        key "reconciliationPolicy": ForwardRef('ReconciliationPolicyProperties', module='types')
        key "solutionScope": str
        key "solutionVersionId": Required[str]
        key "status": ForwardRef('DeploymentStatus', module='types')
        key "targetId": Required[str]
        activeState: Union[str, ActiveState]
        deploymentTimestampEpoch: int
        provisioningState: Union[str, ProvisioningState]
        reconciliationPolicy: ReconciliationPolicyProperties
        solutionScope: str
        solutionVersionId: str
        status: DeploymentStatus
        targetId: str


    class azure.mgmt.workloadorchestration.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.workloadorchestration.types.ReconciliationPolicyProperties(TypedDict, total=False):
        key "interval": Required[str]
        key "state": Required[Union[str, ReconciliationState]]
        interval: str
        state: Union[str, ReconciliationState]


    class azure.mgmt.workloadorchestration.types.RemoveRevisionParameter(TypedDict, total=False):
        key "solutionTemplateId": Required[str]
        key "solutionVersion": Required[str]
        solutionTemplateId: str
        solutionVersion: str


    class azure.mgmt.workloadorchestration.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.workloadorchestration.types.Schema(TrackedResource):
        key "eTag": str
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('SchemaProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        location: str
        name: str
        properties: SchemaProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.workloadorchestration.types.SchemaProperties(TypedDict, total=False):
        key "currentVersion": str
        key "provisioningState": Union[str, ProvisioningState]
        currentVersion: str
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.workloadorchestration.types.SchemaReference(ExtensionResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('SchemaReferenceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        name: str
        properties: SchemaReferenceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.workloadorchestration.types.SchemaReferenceProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "schemaId": Required[str]
        provisioningState: Union[str, ProvisioningState]
        schemaId: str


    class azure.mgmt.workloadorchestration.types.SchemaUpdate(TypedDict, total=False):
        key "properties": ForwardRef('SchemaUpdateProperties', module='types')
        properties: SchemaUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.workloadorchestration.types.SchemaUpdateProperties(TypedDict, total=False):
        key "currentVersion": str
        key "provisioningState": Union[str, ProvisioningState]
        currentVersion: str
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.workloadorchestration.types.SchemaVersion(ProxyResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('SchemaVersionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        name: str
        properties: SchemaVersionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.workloadorchestration.types.SchemaVersionProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "value": Required[Union[str, dict[str, Any]]]
        provisioningState: Union[str, ProvisioningState]
        value: Union[str, dict[str, Any]]


    class azure.mgmt.workloadorchestration.types.SchemaVersionWithUpdateType(TypedDict, total=False):
        key "schemaVersion": Required[SchemaVersion]
        key "updateType": Union[str, UpdateType]
        key "version": str
        schemaVersion: SchemaVersion
        updateType: Union[str, UpdateType]
        version: str


    class azure.mgmt.workloadorchestration.types.SiteReference(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SiteReferenceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SiteReferenceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.workloadorchestration.types.SiteReferenceProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "siteId": Required[str]
        provisioningState: Union[str, ProvisioningState]
        siteId: str


    class azure.mgmt.workloadorchestration.types.Solution(ProxyResource):
        key "eTag": str
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "name": str
        key "properties": ForwardRef('SolutionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        extendedLocation: ExtendedLocation
        id: str
        name: str
        properties: SolutionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.workloadorchestration.types.SolutionDependency(TypedDict, total=False):
        key "solutionInstanceName": str
        key "solutionTemplateVersionId": Required[str]
        key "solutionVersionId": Required[str]
        key "targetId": Required[str]
        dependencies: list[SolutionDependency]
        solutionInstanceName: str
        solutionTemplateVersionId: str
        solutionVersionId: str
        targetId: str


    class azure.mgmt.workloadorchestration.types.SolutionDependencyParameter(TypedDict, total=False):
        key "solutionInstanceName": str
        key "solutionTemplateId": str
        key "solutionTemplateVersion": str
        key "solutionVersionId": str
        key "targetId": str
        dependencies: list[SolutionDependencyParameter]
        solutionInstanceName: str
        solutionTemplateId: str
        solutionTemplateVersion: str
        solutionVersionId: str
        targetId: str


    class azure.mgmt.workloadorchestration.types.SolutionDeployment(TrackedResource):
        key "eTag": str
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('SolutionDeploymentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        location: str
        name: str
        properties: SolutionDeploymentProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.workloadorchestration.types.SolutionDeploymentProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "solutionTemplateProperties": Required[SolutionTemplateMetadata]
        key "targetProperties": Required[TargetMetadata]
        input: dict[str, Any]
        output: dict[str, Any]
        provisioningState: Union[str, ProvisioningState]
        solutionTemplateProperties: SolutionTemplateMetadata
        targetProperties: TargetMetadata


    class azure.mgmt.workloadorchestration.types.SolutionDeploymentUpdate(TypedDict, total=False):
        key "properties": ForwardRef('SolutionDeploymentUpdateProperties', module='types')
        properties: SolutionDeploymentUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.workloadorchestration.types.SolutionDeploymentUpdateProperties(TypedDict, total=False):
        key "solutionTemplateProperties": ForwardRef('SolutionTemplateMetadataUpdate', module='types')
        key "targetProperties": ForwardRef('TargetMetadata', module='types')
        input: dict[str, Any]
        solutionTemplateProperties: SolutionTemplateMetadataUpdate
        targetProperties: TargetMetadata


    class azure.mgmt.workloadorchestration.types.SolutionProperties(TypedDict, total=False):
        key "displayName": str
        key "provisioningState": Union[str, ProvisioningState]
        key "solutionTemplateId": str
        availableSolutionTemplateVersions: list[AvailableSolutionTemplateVersion]
        displayName: str
        provisioningState: Union[str, ProvisioningState]
        solutionTemplateId: str


    class azure.mgmt.workloadorchestration.types.SolutionTemplate(TrackedResource):
        key "eTag": str
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('SolutionTemplateProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        location: str
        name: str
        properties: SolutionTemplateProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.workloadorchestration.types.SolutionTemplateMetadata(TypedDict, total=False):
        key "name": Required[str]
        key "resourceGroupName": str
        key "subscriptionId": str
        key "version": Required[str]
        name: str
        resourceGroupName: str
        subscriptionId: str
        version: str


    class azure.mgmt.workloadorchestration.types.SolutionTemplateMetadataUpdate(TypedDict, total=False):
        key "name": str
        key "resourceGroupName": str
        key "subscriptionId": str
        key "version": str
        name: str
        resourceGroupName: str
        subscriptionId: str
        version: str


    class azure.mgmt.workloadorchestration.types.SolutionTemplateParameter(TypedDict, total=False):
        key "solutionInstanceName": str
        key "solutionTemplateVersionId": Required[str]
        solutionDependencies: list[SolutionDependencyParameter]
        solutionInstanceName: str
        solutionTemplateVersionId: str


    class azure.mgmt.workloadorchestration.types.SolutionTemplateProperties(TypedDict, total=False):
        key "capabilities": Required[list[str]]
        key "description": Required[str]
        key "enableExternalValidation": bool
        key "latestVersion": str
        key "provisioningState": Union[str, ProvisioningState]
        key "state": Union[str, ResourceState]
        key "uniqueIdentifier": str
        capabilities: list[str]
        description: str
        enableExternalValidation: bool
        latestVersion: str
        provisioningState: Union[str, ProvisioningState]
        state: Union[str, ResourceState]
        uniqueIdentifier: str


    class azure.mgmt.workloadorchestration.types.SolutionTemplateUpdate(TypedDict, total=False):
        key "properties": ForwardRef('SolutionTemplateUpdateProperties', module='types')
        properties: SolutionTemplateUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.workloadorchestration.types.SolutionTemplateUpdateProperties(TypedDict, total=False):
        key "description": str
        key "enableExternalValidation": bool
        key "state": Union[str, ResourceState]
        capabilities: list[str]
        description: str
        enableExternalValidation: bool
        state: Union[str, ResourceState]


    class azure.mgmt.workloadorchestration.types.SolutionTemplateVersion(ProxyResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('SolutionTemplateVersionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        name: str
        properties: SolutionTemplateVersionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.workloadorchestration.types.SolutionTemplateVersionProperties(TypedDict, total=False):
        key "configurations": Union[str, dict[str, Any]]
        key "internalState": Union[str, InternalState]
        key "orchestratorType": Union[str, OrchestratorType]
        key "provisioningState": Union[str, ProvisioningState]
        key "specification": Required[dict[str, Any]]
        configurations: Union[str, dict[str, Any]]
        internalState: Union[str, InternalState]
        orchestratorType: Union[str, OrchestratorType]
        provisioningState: Union[str, ProvisioningState]
        specification: dict[str, Any]


    class azure.mgmt.workloadorchestration.types.SolutionTemplateVersionWithUpdateType(TypedDict, total=False):
        key "solutionTemplateVersion": Required[SolutionTemplateVersion]
        key "updateType": Union[str, UpdateType]
        key "version": str
        solutionTemplateVersion: SolutionTemplateVersion
        updateType: Union[str, UpdateType]
        version: str


    class azure.mgmt.workloadorchestration.types.SolutionUpdate(TypedDict, total=False):
        key "properties": ForwardRef('SolutionUpdateProperties', module='types')
        properties: SolutionUpdateProperties


    class azure.mgmt.workloadorchestration.types.SolutionUpdateProperties(TypedDict, total=False):
        key "displayName": str
        key "provisioningState": Union[str, ProvisioningState]
        key "solutionTemplateId": str
        availableSolutionTemplateVersions: list[AvailableSolutionTemplateVersion]
        displayName: str
        provisioningState: Union[str, ProvisioningState]
        solutionTemplateId: str


    class azure.mgmt.workloadorchestration.types.SolutionVersion(ProxyResource):
        key "eTag": str
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "name": str
        key "properties": ForwardRef('SolutionVersionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        extendedLocation: ExtendedLocation
        id: str
        name: str
        properties: SolutionVersionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.workloadorchestration.types.SolutionVersionParameter(TypedDict, total=False):
        key "solutionVersionId": Required[str]
        solutionVersionId: str


    class azure.mgmt.workloadorchestration.types.SolutionVersionProperties(TypedDict, total=False):
        key "actionType": Union[str, JobType]
        key "configuration": Union[str, dict[str, Any]]
        key "currentStage": ForwardRef('StageMap', module='types')
        key "errorDetails": ForwardRef('ErrorDetail', module='types')
        key "externalValidationId": str
        key "latestActionTrackingUri": str
        key "latestActionTriggeredBy": str
        key "provisioningState": Union[str, ProvisioningState]
        key "reviewId": str
        key "revision": int
        key "solutionInstanceName": str
        key "solutionTemplateVersionId": str
        key "specification": Required[dict[str, Any]]
        key "state": Union[str, State]
        key "targetDisplayName": str
        key "targetLevelConfiguration": Union[str, dict[str, Any]]
        actionType: Union[str, JobType]
        configuration: Union[str, dict[str, Any]]
        currentStage: StageMap
        errorDetails: ErrorDetail
        externalValidationId: str
        latestActionTrackingUri: str
        latestActionTriggeredBy: str
        provisioningState: Union[str, ProvisioningState]
        reviewId: str
        revision: int
        solutionDependencies: list[SolutionDependency]
        solutionInstanceName: str
        solutionTemplateVersionId: str
        specification: dict[str, Any]
        stages: list[StageMap]
        state: Union[str, State]
        targetDisplayName: str
        targetLevelConfiguration: Union[str, dict[str, Any]]


    class azure.mgmt.workloadorchestration.types.StageMap(TypedDict, total=False):
        key "displayState": Required[str]
        key "endTime": str
        key "stage": Required[Union[str, CMStages]]
        key "startTime": str
        key "status": Required[Union[str, StateCategory]]
        childStages: list[StageMap]
        displayState: str
        endTime: str
        stage: Union[str, CMStages]
        startTime: str
        status: Union[str, StateCategory]


    class azure.mgmt.workloadorchestration.types.StageSpec(TypedDict, total=False):
        key "name": Required[str]
        key "taskOption": ForwardRef('TaskOption', module='types')
        name: str
        specification: dict[str, Any]
        taskOption: TaskOption
        tasks: list[TaskSpec]


    class azure.mgmt.workloadorchestration.types.StageStatus(TypedDict, total=False):
        key "errorMessage": str
        key "isActive": Union[str, ActiveState]
        key "nextstage": str
        key "stage": str
        key "status": int
        key "statusMessage": str
        errorMessage: str
        inputs: dict[str, Any]
        isActive: Union[str, ActiveState]
        nextstage: str
        outputs: dict[str, Any]
        stage: str
        status: int
        statusMessage: str


    class azure.mgmt.workloadorchestration.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.workloadorchestration.types.Target(TrackedResource):
        key "eTag": str
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('TargetProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: TargetProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.workloadorchestration.types.TargetMetadata(TypedDict, total=False):
        capabilities: list[str]
        targetIds: list[str]


    class azure.mgmt.workloadorchestration.types.TargetProperties(TypedDict, total=False):
        key "capabilities": Required[list[str]]
        key "contextId": Required[str]
        key "description": Required[str]
        key "displayName": Required[str]
        key "hierarchyLevel": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        key "solutionScope": str
        key "state": Union[str, ResourceState]
        key "status": ForwardRef('DeploymentStatus', module='types')
        capabilities: list[str]
        contextId: str
        description: str
        displayName: str
        hierarchyLevel: str
        provisioningState: Union[str, ProvisioningState]
        solutionScope: str
        state: Union[str, ResourceState]
        status: DeploymentStatus
        targetSpecification: dict[str, Any]


    class azure.mgmt.workloadorchestration.types.TargetStatus(TypedDict, total=False):
        key "name": str
        key "status": str
        componentStatuses: list[ComponentStatus]
        name: str
        status: str


    class azure.mgmt.workloadorchestration.types.TargetUpdate(TypedDict, total=False):
        key "properties": ForwardRef('TargetUpdateProperties', module='types')
        properties: TargetUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.workloadorchestration.types.TargetUpdateProperties(TypedDict, total=False):
        key "contextId": str
        key "description": str
        key "displayName": str
        key "hierarchyLevel": str
        key "solutionScope": str
        key "state": Union[str, ResourceState]
        capabilities: list[str]
        contextId: str
        description: str
        displayName: str
        hierarchyLevel: str
        solutionScope: str
        state: Union[str, ResourceState]
        targetSpecification: dict[str, Any]


    class azure.mgmt.workloadorchestration.types.TaskOption(TypedDict, total=False):
        key "concurrency": int
        key "errorAction": ForwardRef('ErrorAction', module='types')
        concurrency: int
        errorAction: ErrorAction


    class azure.mgmt.workloadorchestration.types.TaskSpec(TypedDict, total=False):
        key "name": Required[str]
        key "specification": Required[dict[str, Any]]
        key "targetId": str
        name: str
        specification: dict[str, Any]
        targetId: str


    class azure.mgmt.workloadorchestration.types.TrackedResource(Resource):
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


    class azure.mgmt.workloadorchestration.types.UninstallSolutionParameter(TypedDict, total=False):
        key "solutionInstanceName": str
        key "solutionTemplateId": Required[str]
        solutionInstanceName: str
        solutionTemplateId: str


    class azure.mgmt.workloadorchestration.types.UpdateExternalValidationStatusParameter(TypedDict, total=False):
        key "errorDetails": ForwardRef('ErrorDetail', module='types')
        key "externalValidationId": Required[str]
        key "solutionVersionId": Required[str]
        key "validationStatus": Required[Union[str, ValidationStatus]]
        errorDetails: ErrorDetail
        externalValidationId: str
        solutionVersionId: str
        validationStatus: Union[str, ValidationStatus]


    class azure.mgmt.workloadorchestration.types.VersionParameter(TypedDict, total=False):
        key "version": Required[str]
        version: str


    class azure.mgmt.workloadorchestration.types.Workflow(ProxyResource):
        key "eTag": str
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "name": str
        key "properties": ForwardRef('WorkflowProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        extendedLocation: ExtendedLocation
        id: str
        name: str
        properties: WorkflowProperties
        systemData: SystemData
        type: str


    class azure.mgmt.workloadorchestration.types.WorkflowProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "workflowTemplateId": str
        provisioningState: Union[str, ProvisioningState]
        workflowTemplateId: str


    class azure.mgmt.workloadorchestration.types.WorkflowVersion(ProxyResource):
        key "eTag": str
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "name": str
        key "properties": ForwardRef('WorkflowVersionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        extendedLocation: ExtendedLocation
        id: str
        name: str
        properties: WorkflowVersionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.workloadorchestration.types.WorkflowVersionProperties(TypedDict, total=False):
        key "configuration": str
        key "provisioningState": Union[str, ProvisioningState]
        key "reviewId": str
        key "revision": int
        key "stageSpec": Required[list[StageSpec]]
        key "state": Union[str, State]
        configuration: str
        provisioningState: Union[str, ProvisioningState]
        reviewId: str
        revision: int
        specification: dict[str, Any]
        stageSpec: list[StageSpec]
        state: Union[str, State]


```