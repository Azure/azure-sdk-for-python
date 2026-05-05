```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.workloadorchestration

    class azure.mgmt.workloadorchestration.WorkloadOrchestrationMgmtClient: implements ContextManager 
        config_template_versions: ConfigTemplateVersionsOperations
        config_templates: ConfigTemplatesOperations
        contexts: ContextsOperations
        diagnostics: DiagnosticsOperations
        dynamic_schema_versions: DynamicSchemaVersionsOperations
        dynamic_schemas: DynamicSchemasOperations
        executions: ExecutionsOperations
        instance_histories: InstanceHistoriesOperations
        instances: InstancesOperations
        jobs: JobsOperations
        schema_references: SchemaReferencesOperations
        schema_versions: SchemaVersionsOperations
        schemas: SchemasOperations
        site_references: SiteReferencesOperations
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
        config_template_versions: ConfigTemplateVersionsOperations
        config_templates: ConfigTemplatesOperations
        contexts: ContextsOperations
        diagnostics: DiagnosticsOperations
        dynamic_schema_versions: DynamicSchemaVersionsOperations
        dynamic_schemas: DynamicSchemasOperations
        executions: ExecutionsOperations
        instance_histories: InstanceHistoriesOperations
        instances: InstancesOperations
        jobs: JobsOperations
        schema_references: SchemaReferencesOperations
        schema_versions: SchemaVersionsOperations
        schemas: SchemasOperations
        site_references: SiteReferencesOperations
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

    class azure.mgmt.workloadorchestration.aio.operations.ConfigTemplateVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                resource: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                properties: ConfigTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigTemplate: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                properties: JSON, 
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
                resource: JSON, 
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
                properties: Context, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Context]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                properties: JSON, 
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
                resource: JSON, 
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
                properties: Diagnostic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Diagnostic]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                diagnostic_name: str, 
                properties: JSON, 
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
                schema_version_name: str, 
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
                schema_version_name: str, 
                resource: JSON, 
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
                schema_version_name: str, 
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
                schema_version_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                schema_version_name: str, 
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
                schema_version_name: str, 
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
                schema_version_name: str, 
                properties: JSON, 
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
                schema_version_name: str, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                properties: Schema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schema: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                properties: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                resource: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                properties: SolutionTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionTemplate: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                properties: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                properties: Solution, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
        async def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                properties: Target, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Target]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                properties: JSON, 
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
                body: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
        targets: List[BulkDeployTargetDetails]

        @overload
        def __init__(
                self, 
                *, 
                targets: List[BulkDeployTargetDetails]
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
        solution_dependencies: Optional[List[SolutionDependencyParameter]]
        solution_instance_name: Optional[str]
        targets: List[BulkPublishTargetDetails]

        @overload
        def __init__(
                self, 
                *, 
                solution_dependencies: Optional[List[SolutionDependencyParameter]] = ..., 
                solution_instance_name: Optional[str] = ..., 
                targets: List[BulkPublishTargetDetails]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.BulkPublishTargetDetails(_Model):
        solution_instance_name: Optional[str]
        target_id: str

        @overload
        def __init__(
                self, 
                *, 
                solution_instance_name: Optional[str] = ..., 
                target_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ConfigTemplateProperties(_Model):
        description: str
        latest_version: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                description: str
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
        configurations: str
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                configurations: str
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
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ContextProperties(_Model):
        capabilities: List[Capability]
        hierarchies: List[Hierarchy]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: List[Capability], 
                hierarchies: List[Hierarchy]
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
        target_statuses: Optional[List[TargetStatus]]

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
                target_statuses: Optional[List[TargetStatus]] = ...
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
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.DiagnosticProperties(_Model):
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
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
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
        specification: Optional[Dict[str, Any]]
        status: Optional[ExecutionStatus]
        workflow_version_id: str

        @overload
        def __init__(
                self, 
                *, 
                specification: Optional[Dict[str, Any]] = ..., 
                workflow_version_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.ExecutionStatus(_Model):
        stage_history: Optional[List[StageStatus]]
        status: Optional[int]
        status_message: Optional[str]
        update_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                stage_history: Optional[List[StageStatus]] = ..., 
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
        correlation_id: Optional[str]
        end_time: Optional[datetime]
        error_details: Optional[ErrorDetail]
        job_parameter: Optional[JobParameterBase]
        job_type: Union[str, JobType]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        start_time: Optional[datetime]
        status: Union[str, JobStatus]
        steps: Optional[List[JobStep]]
        triggered_by: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                correlation_id: Optional[str] = ..., 
                end_time: Optional[datetime] = ..., 
                job_parameter: Optional[JobParameterBase] = ..., 
                job_type: Union[str, JobType], 
                start_time: Optional[datetime] = ..., 
                status: Union[str, JobStatus], 
                steps: Optional[List[JobStep]] = ..., 
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
        steps: Optional[List[JobStep]]

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
                steps: Optional[List[JobStep]] = ...
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
        STAGING = "staging"


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
                tags: Optional[Dict[str, str]] = ...
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
        value: str

        @overload
        def __init__(
                self, 
                *, 
                value: str
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
        dependencies: Optional[List[SolutionDependency]]
        solution_instance_name: Optional[str]
        solution_template_version_id: str
        solution_version_id: str
        target_id: str

        @overload
        def __init__(
                self, 
                *, 
                dependencies: Optional[List[SolutionDependency]] = ..., 
                solution_instance_name: Optional[str] = ..., 
                solution_template_version_id: str, 
                solution_version_id: str, 
                target_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionDependencyParameter(_Model):
        dependencies: Optional[List[SolutionDependencyParameter]]
        solution_instance_name: Optional[str]
        solution_template_id: Optional[str]
        solution_template_version: Optional[str]
        solution_version_id: Optional[str]
        target_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                dependencies: Optional[List[SolutionDependencyParameter]] = ..., 
                solution_instance_name: Optional[str] = ..., 
                solution_template_id: Optional[str] = ..., 
                solution_template_version: Optional[str] = ..., 
                solution_version_id: Optional[str] = ..., 
                target_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionProperties(_Model):
        available_solution_template_versions: Optional[List[AvailableSolutionTemplateVersion]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        solution_template_id: Optional[str]


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
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionTemplateParameter(_Model):
        solution_dependencies: Optional[List[SolutionDependencyParameter]]
        solution_instance_name: Optional[str]
        solution_template_version_id: str

        @overload
        def __init__(
                self, 
                *, 
                solution_dependencies: Optional[List[SolutionDependencyParameter]] = ..., 
                solution_instance_name: Optional[str] = ..., 
                solution_template_version_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionTemplateProperties(_Model):
        capabilities: List[str]
        description: str
        enable_external_validation: Optional[bool]
        latest_version: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        state: Optional[Union[str, ResourceState]]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: List[str], 
                description: str, 
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
        configurations: str
        orchestrator_type: Optional[Union[str, OrchestratorType]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        specification: Dict[str, Any]

        @overload
        def __init__(
                self, 
                *, 
                configurations: str, 
                orchestrator_type: Optional[Union[str, OrchestratorType]] = ..., 
                specification: Dict[str, Any]
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
        configuration: Optional[str]
        error_details: Optional[ErrorDetail]
        external_validation_id: Optional[str]
        latest_action_tracking_uri: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        review_id: Optional[str]
        revision: Optional[int]
        solution_dependencies: Optional[List[SolutionDependency]]
        solution_instance_name: Optional[str]
        solution_template_version_id: Optional[str]
        specification: Dict[str, Any]
        state: Optional[Union[str, State]]
        target_display_name: Optional[str]
        target_level_configuration: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                specification: Dict[str, Any]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.SolutionVersionSnapshot(_Model):
        solution_version_id: Optional[str]
        specification: Optional[Dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                solution_version_id: Optional[str] = ..., 
                specification: Optional[Dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.StageSpec(_Model):
        name: str
        specification: Optional[Dict[str, Any]]
        task_option: Optional[TaskOption]
        tasks: Optional[List[TaskSpec]]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                specification: Optional[Dict[str, Any]] = ..., 
                task_option: Optional[TaskOption] = ..., 
                tasks: Optional[List[TaskSpec]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.StageStatus(_Model):
        error_message: Optional[str]
        inputs: Optional[Dict[str, Any]]
        is_active: Optional[Union[str, ActiveState]]
        nextstage: Optional[str]
        outputs: Optional[Dict[str, Any]]
        stage: Optional[str]
        status: Optional[int]
        status_message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error_message: Optional[str] = ..., 
                inputs: Optional[Dict[str, Any]] = ..., 
                is_active: Optional[Union[str, ActiveState]] = ..., 
                nextstage: Optional[str] = ..., 
                outputs: Optional[Dict[str, Any]] = ..., 
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
        PENDING_EXTERNAL_VALIDATION = "PendingExternalValidation"
        READY_TO_DEPLOY = "ReadyToDeploy"
        READY_TO_UPGRADE = "ReadyToUpgrade"
        STAGING = "Staging"
        UNDEPLOYED = "Undeployed"
        UPGRADE_IN_REVIEW = "UpgradeInReview"


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
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.TargetProperties(_Model):
        capabilities: List[str]
        context_id: str
        description: str
        display_name: str
        hierarchy_level: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        solution_scope: Optional[str]
        state: Optional[Union[str, ResourceState]]
        status: Optional[DeploymentStatus]
        target_specification: Dict[str, Any]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: List[str], 
                context_id: str, 
                description: str, 
                display_name: str, 
                hierarchy_level: str, 
                solution_scope: Optional[str] = ..., 
                state: Optional[Union[str, ResourceState]] = ..., 
                target_specification: Dict[str, Any]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.TargetSnapshot(_Model):
        solution_scope: Optional[str]
        target_id: Optional[str]
        target_specification: Optional[Dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                solution_scope: Optional[str] = ..., 
                target_id: Optional[str] = ..., 
                target_specification: Optional[Dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.TargetStatus(_Model):
        component_statuses: Optional[List[ComponentStatus]]
        name: Optional[str]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                component_statuses: Optional[List[ComponentStatus]] = ..., 
                name: Optional[str] = ..., 
                status: Optional[str] = ...
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
        specification: Dict[str, Any]
        target_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                specification: Dict[str, Any], 
                target_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadorchestration.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: Optional[Dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ...
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
        specification: Optional[Dict[str, Any]]
        stage_spec: List[StageSpec]
        state: Optional[Union[str, State]]

        @overload
        def __init__(
                self, 
                *, 
                specification: Optional[Dict[str, Any]] = ..., 
                stage_spec: List[StageSpec]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.workloadorchestration.operations

    class azure.mgmt.workloadorchestration.operations.ConfigTemplateVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                resource: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                properties: ConfigTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigTemplate: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                config_template_name: str, 
                properties: JSON, 
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
                resource: JSON, 
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
                properties: Context, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Context]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                context_name: str, 
                properties: JSON, 
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
                resource: JSON, 
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
                properties: Diagnostic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Diagnostic]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                diagnostic_name: str, 
                properties: JSON, 
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
                schema_version_name: str, 
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
                schema_version_name: str, 
                resource: JSON, 
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
                schema_version_name: str, 
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
                schema_version_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                dynamic_schema_name: str, 
                schema_version_name: str, 
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
                schema_version_name: str, 
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
                schema_version_name: str, 
                properties: JSON, 
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
                schema_version_name: str, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                properties: Schema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schema: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                schema_name: str, 
                properties: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                resource: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                properties: SolutionTemplate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SolutionTemplate: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                solution_template_name: str, 
                properties: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                properties: Solution, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
        def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                properties: Target, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Target]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                target_name: str, 
                properties: JSON, 
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
                body: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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


```