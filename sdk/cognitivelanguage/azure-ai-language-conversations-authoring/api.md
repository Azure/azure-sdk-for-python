```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.ai.language.conversations.authoring

    class azure.ai.language.conversations.authoring.ConversationAuthoringClient(AuthoringClientGenerated): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def begin_delete_project(
                self, 
                project_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        def close(self) -> None: ...

        @overload
        def create_project(
                self, 
                project_name: str, 
                body: CreateProjectOptions, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ProjectDetails: ...

        @overload
        def create_project(
                self, 
                project_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ProjectDetails: ...

        @overload
        def create_project(
                self, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ProjectDetails: ...

        @distributed_trace
        def get_project(
                self, 
                project_name: str, 
                **kwargs: Any
            ) -> ProjectDetails: ...

        def get_project_client(self, project_name: str) -> ConversationAuthoringProjectClient: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-11-01', params_added_on={'2025-11-01': ['api_version', 'top', 'skip', 'maxpagesize', 'accept']}, api_versions_list=['2025-11-01', '2025-05-15-preview', '2025-11-15-preview'])
        def list_assigned_resource_deployments(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AssignedProjectDeploymentsMetadata]: ...

        @distributed_trace
        def list_projects(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ProjectDetails]: ...

        @distributed_trace
        def list_supported_languages(
                self, 
                *, 
                project_kind: Union[str, ProjectKind], 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SupportedLanguage]: ...

        @distributed_trace
        def list_supported_prebuilt_entities(
                self, 
                *, 
                language: Optional[str] = ..., 
                multilingual: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PrebuiltEntity]: ...

        @distributed_trace
        def list_training_config_versions(
                self, 
                *, 
                project_kind: Union[str, ProjectKind], 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[TrainingConfigVersion]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


    class azure.ai.language.conversations.authoring.ConversationAuthoringProjectClient(AuthoringProjectClientGenerated): implements ContextManager 
        deployment: DeploymentOperations
        exported_model: ExportedModelOperations
        project: ProjectOperations
        trained_model: TrainedModelOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: Optional[str] = ..., 
                project_name: str, 
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


namespace azure.ai.language.conversations.authoring.aio

    class azure.ai.language.conversations.authoring.aio.ConversationAuthoringClient(AuthoringClientGenerated): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete_project(
                self, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        async def close(self) -> None: ...

        @overload
        async def create_project(
                self, 
                project_name: str, 
                body: CreateProjectOptions, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ProjectDetails: ...

        @overload
        async def create_project(
                self, 
                project_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ProjectDetails: ...

        @overload
        async def create_project(
                self, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ProjectDetails: ...

        @distributed_trace_async
        async def get_project(
                self, 
                project_name: str, 
                **kwargs: Any
            ) -> ProjectDetails: ...

        def get_project_client(self, project_name: str) -> ConversationAuthoringProjectClient: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-11-01', params_added_on={'2025-11-01': ['api_version', 'top', 'skip', 'maxpagesize', 'accept']}, api_versions_list=['2025-11-01', '2025-05-15-preview', '2025-11-15-preview'])
        def list_assigned_resource_deployments(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AssignedProjectDeploymentsMetadata]: ...

        @distributed_trace
        def list_projects(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ProjectDetails]: ...

        @distributed_trace
        def list_supported_languages(
                self, 
                *, 
                project_kind: Union[str, ProjectKind], 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SupportedLanguage]: ...

        @distributed_trace
        def list_supported_prebuilt_entities(
                self, 
                *, 
                language: Optional[str] = ..., 
                multilingual: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PrebuiltEntity]: ...

        @distributed_trace
        def list_training_config_versions(
                self, 
                *, 
                project_kind: Union[str, ProjectKind], 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[TrainingConfigVersion]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


    class azure.ai.language.conversations.authoring.aio.ConversationAuthoringProjectClient(AuthoringProjectClientGenerated): implements AsyncContextManager 
        deployment: DeploymentOperations
        exported_model: ExportedModelOperations
        project: ProjectOperations
        trained_model: TrainedModelOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: Optional[str] = ..., 
                project_name: str, 
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


namespace azure.ai.language.conversations.authoring.aio.operations

    class azure.ai.language.conversations.authoring.aio.operations.DeploymentOperations(_GeneratedDeploymentOperations):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete_deployment(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_delete_deployment_from_resources(
                self, 
                deployment_name: str, 
                body: ProjectResourceIds, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_delete_deployment_from_resources(
                self, 
                deployment_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_delete_deployment_from_resources(
                self, 
                deployment_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace
        async def begin_deploy_project(
                self, 
                deployment_name: str, 
                body: Union[CreateDeploymentDetails, JSON, Any], 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get_deployment(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> ProjectDeployment: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-11-01', params_added_on={'2025-11-01': ['api_version', 'project_name', 'deployment_name', 'job_id', 'accept']}, api_versions_list=['2025-11-01', '2025-05-15-preview', '2025-11-15-preview'])
        async def get_deployment_delete_from_resources_status(
                self, 
                deployment_name: str, 
                job_id: str, 
                **kwargs: Any
            ) -> DeploymentDeleteFromResourcesState: ...

        @distributed_trace_async
        async def get_deployment_status(
                self, 
                deployment_name: str, 
                job_id: str, 
                **kwargs: Any
            ) -> DeploymentState: ...


    class azure.ai.language.conversations.authoring.aio.operations.ExportedModelOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update_exported_model(
                self, 
                exported_model_name: str, 
                body: ExportedModelDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update_exported_model(
                self, 
                exported_model_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update_exported_model(
                self, 
                exported_model_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-05-15-preview', params_added_on={'2025-05-15-preview': ['api_version', 'project_name', 'exported_model_name']}, api_versions_list=['2025-05-15-preview', '2025-11-15-preview'])
        async def begin_delete_exported_model(
                self, 
                exported_model_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-05-15-preview', params_added_on={'2025-05-15-preview': ['api_version', 'project_name', 'exported_model_name', 'accept']}, api_versions_list=['2025-05-15-preview', '2025-11-15-preview'])
        async def get_exported_model(
                self, 
                exported_model_name: str, 
                **kwargs: Any
            ) -> ExportedTrainedModel: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-05-15-preview', params_added_on={'2025-05-15-preview': ['api_version', 'project_name', 'exported_model_name', 'job_id', 'accept']}, api_versions_list=['2025-05-15-preview', '2025-11-15-preview'])
        async def get_exported_model_job_status(
                self, 
                exported_model_name: str, 
                job_id: str, 
                **kwargs: Any
            ) -> ExportedModelState: ...


    class azure.ai.language.conversations.authoring.aio.operations.ProjectOperations(ProjectOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_assign_project_resources(
                self, 
                body: AssignProjectResourcesDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_assign_project_resources(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_assign_project_resources(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_cancel_training_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[TrainingJobResult]: ...

        @overload
        async def begin_copy_project(
                self, 
                body: CopyProjectDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_copy_project(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_copy_project(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_export(
                self, 
                *, 
                asset_kind: Optional[str] = ..., 
                exported_project_format: Optional[Union[str, ExportedProjectFormat]] = ..., 
                string_index_type: Union[str, StringIndexType], 
                trained_model_label: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_import(
                self, 
                body: ExportedProject, 
                *, 
                content_type: str = "application/json", 
                exported_project_format: Optional[Union[str, ExportedProjectFormat]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_import(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                exported_project_format: Optional[Union[str, ExportedProjectFormat]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_import(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                exported_project_format: Optional[Union[str, ExportedProjectFormat]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_swap_deployments(
                self, 
                body: SwapDeploymentsDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_swap_deployments(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_swap_deployments(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_train(
                self, 
                body: TrainingJobDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TrainingJobResult]: ...

        @overload
        async def begin_train(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TrainingJobResult]: ...

        @overload
        async def begin_train(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TrainingJobResult]: ...

        @overload
        async def begin_unassign_project_resources(
                self, 
                body: ProjectResourceIds, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_unassign_project_resources(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_unassign_project_resources(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def copy_project_authorization(
                self, 
                *, 
                allow_overwrite: Optional[bool] = ..., 
                content_type: str = "application/json", 
                project_kind: Union[str, ProjectKind], 
                storage_input_container_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> CopyProjectDetails: ...

        @overload
        async def copy_project_authorization(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopyProjectDetails: ...

        @overload
        async def copy_project_authorization(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopyProjectDetails: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-11-01', params_added_on={'2025-11-01': ['api_version', 'project_name', 'job_id', 'accept']}, api_versions_list=['2025-11-01', '2025-05-15-preview', '2025-11-15-preview'])
        async def get_assign_project_resources_status(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> ProjectResourcesState: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-05-15-preview', params_added_on={'2025-05-15-preview': ['api_version', 'project_name', 'job_id', 'accept']}, api_versions_list=['2025-05-15-preview', '2025-11-15-preview'])
        async def get_copy_project_status(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> CopyProjectState: ...

        @distributed_trace_async
        async def get_export_status(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> ExportProjectState: ...

        @distributed_trace_async
        async def get_project(self, **kwargs: Any) -> ProjectDetails: ...

        @distributed_trace_async
        async def get_project_deletion_status(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> ProjectDeletionState: ...

        @distributed_trace_async
        async def get_swap_deployments_status(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> SwapDeploymentsState: ...

        @distributed_trace_async
        async def get_training_status(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> TrainingState: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-11-01', params_added_on={'2025-11-01': ['api_version', 'project_name', 'job_id', 'accept']}, api_versions_list=['2025-11-01', '2025-05-15-preview', '2025-11-15-preview'])
        async def get_unassign_project_resources_status(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> ProjectResourcesState: ...

        @distributed_trace
        def list_deployments(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ProjectDeployment]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-05-15-preview', params_added_on={'2025-05-15-preview': ['api_version', 'project_name', 'top', 'skip', 'maxpagesize', 'accept']}, api_versions_list=['2025-05-15-preview', '2025-11-15-preview'])
        def list_exported_models(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ExportedTrainedModel]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-11-01', params_added_on={'2025-11-01': ['api_version', 'project_name', 'top', 'skip', 'maxpagesize', 'accept']}, api_versions_list=['2025-11-01', '2025-05-15-preview', '2025-11-15-preview'])
        def list_project_resources(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AssignedProjectResource]: ...

        @distributed_trace
        def list_trained_models(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ProjectTrainedModel]: ...

        @distributed_trace
        def list_training_jobs(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[TrainingState]: ...


    class azure.ai.language.conversations.authoring.aio.operations.TrainedModelOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_evaluate_model(
                self, 
                trained_model_label: str, 
                body: EvaluationDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EvaluationJobResult]: ...

        @overload
        async def begin_evaluate_model(
                self, 
                trained_model_label: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EvaluationJobResult]: ...

        @overload
        async def begin_evaluate_model(
                self, 
                trained_model_label: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EvaluationJobResult]: ...

        @distributed_trace_async
        async def begin_load_snapshot(
                self, 
                trained_model_label: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def delete_trained_model(
                self, 
                trained_model_label: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-05-15-preview', params_added_on={'2025-05-15-preview': ['api_version', 'project_name', 'trained_model_label', 'job_id', 'accept']}, api_versions_list=['2025-05-15-preview', '2025-11-15-preview'])
        async def get_evaluation_status(
                self, 
                trained_model_label: str, 
                job_id: str, 
                **kwargs: Any
            ) -> EvaluationState: ...

        @distributed_trace_async
        async def get_load_snapshot_status(
                self, 
                trained_model_label: str, 
                job_id: str, 
                **kwargs: Any
            ) -> LoadSnapshotState: ...

        @distributed_trace
        def get_model_evaluation_results(
                self, 
                trained_model_label: str, 
                *, 
                skip: Optional[int] = ..., 
                string_index_type: Union[str, StringIndexType], 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[UtteranceEvaluationResult]: ...

        @distributed_trace_async
        async def get_model_evaluation_summary(
                self, 
                trained_model_label: str, 
                **kwargs: Any
            ) -> EvalSummary: ...

        @distributed_trace_async
        async def get_trained_model(
                self, 
                trained_model_label: str, 
                **kwargs: Any
            ) -> ProjectTrainedModel: ...


namespace azure.ai.language.conversations.authoring.models

    class azure.ai.language.conversations.authoring.models.AssignProjectResourcesDetails(_Model):
        metadata: list[ResourceMetadata]

        @overload
        def __init__(
                self, 
                *, 
                metadata: list[ResourceMetadata]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.AssignedProjectDeploymentMetadata(_Model):
        deployment_expires_on: date
        deployment_name: str
        last_deployed_on: datetime

        @overload
        def __init__(
                self, 
                *, 
                deployment_expires_on: date, 
                deployment_name: str, 
                last_deployed_on: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.AssignedProjectDeploymentsMetadata(_Model):
        deployments_metadata: list[AssignedProjectDeploymentMetadata]
        project_name: str

        @overload
        def __init__(
                self, 
                *, 
                deployments_metadata: list[AssignedProjectDeploymentMetadata]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.AssignedProjectResource(_Model):
        assigned_aoai_resource: Optional[DataGenerationConnectionInfo]
        region: str
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                assigned_aoai_resource: Optional[DataGenerationConnectionInfo] = ..., 
                region: str, 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.CompositionMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMBINE_COMPONENTS = "combineComponents"
        REQUIRE_EXACT_OVERLAP = "requireExactOverlap"
        RETURN_LONGEST_OVERLAP = "returnLongestOverlap"
        SEPARATE_COMPONENTS = "separateComponents"


    class azure.ai.language.conversations.authoring.models.ConfusionMatrixCell(_Model):
        normalized_value: float
        raw_value: float

        @overload
        def __init__(
                self, 
                *, 
                normalized_value: float, 
                raw_value: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ConfusionMatrixRow(_Model):


    class azure.ai.language.conversations.authoring.models.ConversationExportedAssociatedEntityLabel(_Model):
        category: str

        @overload
        def __init__(
                self, 
                *, 
                category: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ConversationExportedEntity(_Model):
        category: str
        composition_mode: Optional[Union[str, CompositionMode]]
        description: Optional[str]
        entities: Optional[ExportedEntityList]
        prebuilts: Optional[list[ExportedPrebuiltEntity]]
        regex: Optional[ExportedEntityRegex]
        required_components: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                category: str, 
                composition_mode: Optional[Union[str, CompositionMode]] = ..., 
                description: Optional[str] = ..., 
                entities: Optional[ExportedEntityList] = ..., 
                prebuilts: Optional[list[ExportedPrebuiltEntity]] = ..., 
                regex: Optional[ExportedEntityRegex] = ..., 
                required_components: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ConversationExportedIntent(_Model):
        associated_entities: Optional[list[ConversationExportedAssociatedEntityLabel]]
        category: str
        description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                associated_entities: Optional[list[ConversationExportedAssociatedEntityLabel]] = ..., 
                category: str, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ConversationExportedProjectAsset(ExportedProjectAsset, discriminator='Conversation'):
        entities: Optional[list[ConversationExportedEntity]]
        intents: Optional[list[ConversationExportedIntent]]
        project_kind: Literal[ProjectKind.CONVERSATION]
        utterances: Optional[list[ConversationExportedUtterance]]

        @overload
        def __init__(
                self, 
                *, 
                entities: Optional[list[ConversationExportedEntity]] = ..., 
                intents: Optional[list[ConversationExportedIntent]] = ..., 
                utterances: Optional[list[ConversationExportedUtterance]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ConversationExportedUtterance(_Model):
        dataset: Optional[Union[str, DatasetType]]
        entities: Optional[list[ExportedUtteranceEntityLabel]]
        intent: str
        language: Optional[str]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                dataset: Optional[Union[str, DatasetType]] = ..., 
                entities: Optional[list[ExportedUtteranceEntityLabel]] = ..., 
                intent: str, 
                language: Optional[str] = ..., 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.CopyProjectDetails(_Model):
        access_token: str
        expires_at: datetime
        project_kind: Union[str, ProjectKind]
        target_project_name: str
        target_resource_id: str
        target_resource_region: str

        @overload
        def __init__(
                self, 
                *, 
                access_token: str, 
                expires_at: datetime, 
                project_kind: Union[str, ProjectKind], 
                target_project_name: str, 
                target_resource_id: str, 
                target_resource_region: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.CopyProjectState(_Model):
        created_on: datetime
        errors: Optional[list[ODataV4Format]]
        expires_on: Optional[datetime]
        job_id: str
        last_updated_on: datetime
        status: Union[str, OperationStatus]
        warnings: Optional[list[ODataV4Format]]

        @overload
        def __init__(
                self, 
                *, 
                created_on: datetime, 
                errors: Optional[list[ODataV4Format]] = ..., 
                expires_on: Optional[datetime] = ..., 
                last_updated_on: datetime, 
                status: Union[str, OperationStatus], 
                warnings: Optional[list[ODataV4Format]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.CreateDeploymentDetails(_GeneratedCreateDeploymentDetails):
        azure_resource_ids: Union[list[AssignedProjectResource], list[str]]
        trained_model_label: str

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.language.conversations.authoring.models.CreateProjectOptions(_Model):
        description: Optional[str]
        language: str
        multilingual: Optional[bool]
        project_kind: Union[str, ProjectKind]
        project_name: str
        settings: Optional[ProjectSettings]
        storage_input_container_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                language: str, 
                multilingual: Optional[bool] = ..., 
                project_kind: Union[str, ProjectKind], 
                project_name: str, 
                settings: Optional[ProjectSettings] = ..., 
                storage_input_container_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.DataGenerationConnectionInfo(_Model):
        deployment_name: str
        kind: Union[str, DataGenerationConnectionKind]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                deployment_name: str, 
                kind: Union[str, DataGenerationConnectionKind], 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.DataGenerationConnectionKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_OPEN_AI = "AzureOpenAI"


    class azure.ai.language.conversations.authoring.models.DataGenerationSettings(_Model):
        data_generation_connection_info: DataGenerationConnectionInfo
        enable_data_generation: bool

        @overload
        def __init__(
                self, 
                *, 
                data_generation_connection_info: DataGenerationConnectionInfo, 
                enable_data_generation: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.DatasetType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TEST = "Test"
        TRAIN = "Train"


    class azure.ai.language.conversations.authoring.models.DeploymentDeleteFromResourcesState(_Model):
        created_on: datetime
        errors: Optional[list[ODataV4Format]]
        expires_on: Optional[datetime]
        job_id: str
        last_updated_on: datetime
        status: Union[str, OperationStatus]
        warnings: Optional[list[ODataV4Format]]

        @overload
        def __init__(
                self, 
                *, 
                created_on: datetime, 
                errors: Optional[list[ODataV4Format]] = ..., 
                expires_on: Optional[datetime] = ..., 
                last_updated_on: datetime, 
                status: Union[str, OperationStatus], 
                warnings: Optional[list[ODataV4Format]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.DeploymentState(_Model):
        created_on: datetime
        errors: Optional[list[ODataV4Format]]
        expires_on: Optional[datetime]
        job_id: str
        last_updated_on: datetime
        status: Union[str, OperationStatus]
        warnings: Optional[list[ODataV4Format]]

        @overload
        def __init__(
                self, 
                *, 
                created_on: datetime, 
                errors: Optional[list[ODataV4Format]] = ..., 
                expires_on: Optional[datetime] = ..., 
                last_updated_on: datetime, 
                status: Union[str, OperationStatus], 
                warnings: Optional[list[ODataV4Format]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.EntitiesEvaluationSummary(_Model):
        confusion_matrix: dict[str, ConfusionMatrixRow]
        entities: dict[str, EntityEvaluationSummary]
        macro_f1: float
        macro_precision: float
        macro_recall: float
        micro_f1: float
        micro_precision: float
        micro_recall: float

        @overload
        def __init__(
                self, 
                *, 
                confusion_matrix: dict[str, ConfusionMatrixRow], 
                entities: dict[str, EntityEvaluationSummary], 
                macro_f1: float, 
                macro_precision: float, 
                macro_recall: float, 
                micro_f1: float, 
                micro_precision: float, 
                micro_recall: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.EntityEvaluationSummary(_Model):
        f1: float
        false_negative_count: int
        false_positive_count: int
        precision: float
        recall: float
        true_negative_count: int
        true_positive_count: int

        @overload
        def __init__(
                self, 
                *, 
                f1: float, 
                false_negative_count: int, 
                false_positive_count: int, 
                precision: float, 
                recall: float, 
                true_negative_count: int, 
                true_positive_count: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.EvalSummary(_Model):
        entities_evaluation: EntitiesEvaluationSummary
        evaluation_options: Optional[EvaluationDetails]
        intents_evaluation: IntentsEvaluationSummary

        @overload
        def __init__(
                self, 
                *, 
                entities_evaluation: EntitiesEvaluationSummary, 
                evaluation_options: Optional[EvaluationDetails] = ..., 
                intents_evaluation: IntentsEvaluationSummary
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.EvaluationDetails(_Model):
        kind: Optional[Union[str, EvaluationKind]]
        testing_split_percentage: Optional[int]
        training_split_percentage: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, EvaluationKind]] = ..., 
                testing_split_percentage: Optional[int] = ..., 
                training_split_percentage: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.EvaluationJobResult(_Model):
        evaluation_details: EvaluationDetails
        model_label: str
        percent_complete: int
        training_config_version: str

        @overload
        def __init__(
                self, 
                *, 
                evaluation_details: EvaluationDetails, 
                model_label: str, 
                percent_complete: int, 
                training_config_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.EvaluationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANUAL = "manual"
        PERCENTAGE = "percentage"


    class azure.ai.language.conversations.authoring.models.EvaluationState(_Model):
        created_on: datetime
        errors: Optional[list[ODataV4Format]]
        expires_on: Optional[datetime]
        job_id: str
        last_updated_on: datetime
        result: EvaluationJobResult
        status: Union[str, OperationStatus]
        warnings: Optional[list[ODataV4Format]]

        @overload
        def __init__(
                self, 
                *, 
                created_on: datetime, 
                errors: Optional[list[ODataV4Format]] = ..., 
                expires_on: Optional[datetime] = ..., 
                last_updated_on: datetime, 
                result: EvaluationJobResult, 
                status: Union[str, OperationStatus], 
                warnings: Optional[list[ODataV4Format]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ExportProjectState(_Model):
        created_on: datetime
        errors: Optional[list[ODataV4Format]]
        expires_on: Optional[datetime]
        job_id: str
        last_updated_on: datetime
        result_uri: Optional[str]
        status: Union[str, OperationStatus]
        warnings: Optional[list[ODataV4Format]]

        @overload
        def __init__(
                self, 
                *, 
                created_on: datetime, 
                errors: Optional[list[ODataV4Format]] = ..., 
                expires_on: Optional[datetime] = ..., 
                last_updated_on: datetime, 
                result_uri: Optional[str] = ..., 
                status: Union[str, OperationStatus], 
                warnings: Optional[list[ODataV4Format]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ExportedConversationOrchestration(_Model):
        deployment_name: str
        project_name: str

        @overload
        def __init__(
                self, 
                *, 
                deployment_name: str, 
                project_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ExportedConversationOrchestrationDetails(ExportedOrchestrationDetails, discriminator='Conversation'):
        conversation_orchestration: ExportedConversationOrchestration
        target_project_kind: Literal[OrchestrationTargetProjectKind.CONVERSATION]

        @overload
        def __init__(
                self, 
                *, 
                conversation_orchestration: ExportedConversationOrchestration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ExportedEntityList(_Model):
        sublists: Optional[list[ExportedEntitySublist]]

        @overload
        def __init__(
                self, 
                *, 
                sublists: Optional[list[ExportedEntitySublist]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ExportedEntityListSynonym(_Model):
        language: Optional[str]
        synonyms: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                language: Optional[str] = ..., 
                synonyms: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ExportedEntityRegex(_Model):
        expressions: Optional[list[ExportedEntityRegexExpression]]

        @overload
        def __init__(
                self, 
                *, 
                expressions: Optional[list[ExportedEntityRegexExpression]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ExportedEntityRegexExpression(_Model):
        language: Optional[str]
        regex_key: Optional[str]
        regex_pattern: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                language: Optional[str] = ..., 
                regex_key: Optional[str] = ..., 
                regex_pattern: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ExportedEntitySublist(_Model):
        list_key: Optional[str]
        synonyms: Optional[list[ExportedEntityListSynonym]]

        @overload
        def __init__(
                self, 
                *, 
                list_key: Optional[str] = ..., 
                synonyms: Optional[list[ExportedEntityListSynonym]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ExportedLuisOrchestration(_Model):
        app_id: str
        app_version: Optional[str]
        slot_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                app_id: str, 
                app_version: Optional[str] = ..., 
                slot_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ExportedLuisOrchestrationDetails(ExportedOrchestrationDetails, discriminator='Luis'):
        luis_orchestration: ExportedLuisOrchestration
        target_project_kind: Literal[OrchestrationTargetProjectKind.LUIS]

        @overload
        def __init__(
                self, 
                *, 
                luis_orchestration: ExportedLuisOrchestration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ExportedModelDetails(_Model):
        trained_model_label: str

        @overload
        def __init__(
                self, 
                *, 
                trained_model_label: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ExportedModelState(_Model):
        created_on: datetime
        errors: Optional[list[ODataV4Format]]
        expires_on: Optional[datetime]
        job_id: str
        last_updated_on: datetime
        status: Union[str, OperationStatus]
        warnings: Optional[list[ODataV4Format]]

        @overload
        def __init__(
                self, 
                *, 
                created_on: datetime, 
                errors: Optional[list[ODataV4Format]] = ..., 
                expires_on: Optional[datetime] = ..., 
                last_updated_on: datetime, 
                status: Union[str, OperationStatus], 
                warnings: Optional[list[ODataV4Format]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ExportedOrchestrationDetails(_Model):
        target_project_kind: str

        @overload
        def __init__(
                self, 
                *, 
                target_project_kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ExportedPrebuiltEntity(_Model):
        category: str

        @overload
        def __init__(
                self, 
                *, 
                category: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ExportedProject(_Model):
        assets: Optional[ExportedProjectAsset]
        metadata: CreateProjectOptions
        project_file_version: str
        string_index_type: Union[str, StringIndexType]

        @overload
        def __init__(
                self, 
                *, 
                assets: Optional[ExportedProjectAsset] = ..., 
                metadata: CreateProjectOptions, 
                project_file_version: str, 
                string_index_type: Union[str, StringIndexType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ExportedProjectAsset(_Model):
        project_kind: str

        @overload
        def __init__(
                self, 
                *, 
                project_kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ExportedProjectFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONVERSATION = "Conversation"
        LUIS = "Luis"


    class azure.ai.language.conversations.authoring.models.ExportedQuestionAnsweringOrchestration(_Model):
        project_name: str

        @overload
        def __init__(
                self, 
                *, 
                project_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ExportedQuestionAnsweringOrchestrationDetails(ExportedOrchestrationDetails, discriminator='QuestionAnswering'):
        question_answering_orchestration: ExportedQuestionAnsweringOrchestration
        target_project_kind: Literal[OrchestrationTargetProjectKind.QUESTION_ANSWERING]

        @overload
        def __init__(
                self, 
                *, 
                question_answering_orchestration: ExportedQuestionAnsweringOrchestration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ExportedTrainedModel(_Model):
        exported_model_name: str
        last_exported_model_on: datetime
        last_trained_on: datetime
        model_expired_on: date
        model_id: str
        model_training_config_version: str

        @overload
        def __init__(
                self, 
                *, 
                last_exported_model_on: datetime, 
                last_trained_on: datetime, 
                model_expired_on: date, 
                model_id: str, 
                model_training_config_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ExportedUtteranceEntityLabel(_Model):
        category: str
        length: int
        offset: int

        @overload
        def __init__(
                self, 
                *, 
                category: str, 
                length: int, 
                offset: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ImportProjectState(_Model):
        created_on: datetime
        errors: Optional[list[ODataV4Format]]
        expires_on: Optional[datetime]
        job_id: str
        last_updated_on: datetime
        status: Union[str, OperationStatus]
        warnings: Optional[list[ODataV4Format]]

        @overload
        def __init__(
                self, 
                *, 
                created_on: datetime, 
                errors: Optional[list[ODataV4Format]] = ..., 
                expires_on: Optional[datetime] = ..., 
                last_updated_on: datetime, 
                status: Union[str, OperationStatus], 
                warnings: Optional[list[ODataV4Format]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.IntentEvaluationSummary(_Model):
        f1: float
        false_negative_count: int
        false_positive_count: int
        precision: float
        recall: float
        true_negative_count: int
        true_positive_count: int

        @overload
        def __init__(
                self, 
                *, 
                f1: float, 
                false_negative_count: int, 
                false_positive_count: int, 
                precision: float, 
                recall: float, 
                true_negative_count: int, 
                true_positive_count: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.IntentsEvaluationSummary(_Model):
        confusion_matrix: dict[str, ConfusionMatrixRow]
        intents: dict[str, IntentEvaluationSummary]
        macro_f1: float
        macro_precision: float
        macro_recall: float
        micro_f1: float
        micro_precision: float
        micro_recall: float

        @overload
        def __init__(
                self, 
                *, 
                confusion_matrix: dict[str, ConfusionMatrixRow], 
                intents: dict[str, IntentEvaluationSummary], 
                macro_f1: float, 
                macro_precision: float, 
                macro_recall: float, 
                micro_f1: float, 
                micro_precision: float, 
                micro_recall: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.LoadSnapshotState(_Model):
        created_on: datetime
        errors: Optional[list[ODataV4Format]]
        expires_on: Optional[datetime]
        job_id: str
        last_updated_on: datetime
        status: Union[str, OperationStatus]
        warnings: Optional[list[ODataV4Format]]

        @overload
        def __init__(
                self, 
                *, 
                created_on: datetime, 
                errors: Optional[list[ODataV4Format]] = ..., 
                expires_on: Optional[datetime] = ..., 
                last_updated_on: datetime, 
                status: Union[str, OperationStatus], 
                warnings: Optional[list[ODataV4Format]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.OperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "cancelled"
        CANCELLING = "cancelling"
        FAILED = "failed"
        NOT_STARTED = "notStarted"
        PARTIALLY_COMPLETED = "partiallyCompleted"
        RUNNING = "running"
        SUCCEEDED = "succeeded"


    class azure.ai.language.conversations.authoring.models.OrchestrationExportedIntent(_Model):
        category: str
        description: Optional[str]
        orchestration: Optional[ExportedOrchestrationDetails]

        @overload
        def __init__(
                self, 
                *, 
                category: str, 
                description: Optional[str] = ..., 
                orchestration: Optional[ExportedOrchestrationDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.OrchestrationExportedProjectAsset(ExportedProjectAsset, discriminator='Orchestration'):
        intents: Optional[list[OrchestrationExportedIntent]]
        project_kind: Literal[ProjectKind.ORCHESTRATION]
        utterances: Optional[list[OrchestrationExportedUtterance]]

        @overload
        def __init__(
                self, 
                *, 
                intents: Optional[list[OrchestrationExportedIntent]] = ..., 
                utterances: Optional[list[OrchestrationExportedUtterance]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.OrchestrationExportedUtterance(_Model):
        dataset: Optional[str]
        intent: str
        language: Optional[str]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                dataset: Optional[str] = ..., 
                intent: str, 
                language: Optional[str] = ..., 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.OrchestrationTargetProjectKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONVERSATION = "Conversation"
        LUIS = "Luis"
        QUESTION_ANSWERING = "QuestionAnswering"


    class azure.ai.language.conversations.authoring.models.PrebuiltEntity(_Model):
        category: str
        description: str
        examples: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                examples: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ProjectDeletionState(_Model):
        created_on: datetime
        errors: Optional[list[ODataV4Format]]
        expires_on: Optional[datetime]
        job_id: str
        last_updated_on: datetime
        status: Union[str, OperationStatus]
        warnings: Optional[list[ODataV4Format]]

        @overload
        def __init__(
                self, 
                *, 
                created_on: datetime, 
                errors: Optional[list[ODataV4Format]] = ..., 
                expires_on: Optional[datetime] = ..., 
                last_updated_on: datetime, 
                status: Union[str, OperationStatus], 
                warnings: Optional[list[ODataV4Format]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ProjectDeployment(_Model):
        assigned_resources: list[AssignedProjectResource]
        deployment_expired_on: date
        deployment_name: str
        last_deployed_on: datetime
        last_trained_on: datetime
        model_id: str
        model_training_config_version: str

        @overload
        def __init__(
                self, 
                *, 
                assigned_resources: list[AssignedProjectResource], 
                deployment_expired_on: date, 
                last_deployed_on: datetime, 
                last_trained_on: datetime, 
                model_id: str, 
                model_training_config_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ProjectDetails(_Model):
        created_on: datetime
        description: Optional[str]
        language: str
        last_deployed_on: Optional[datetime]
        last_modified_on: datetime
        last_trained_on: Optional[datetime]
        multilingual: Optional[bool]
        project_kind: Union[str, ProjectKind]
        project_name: str
        settings: Optional[ProjectSettings]
        storage_input_container_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                created_on: datetime, 
                description: Optional[str] = ..., 
                language: str, 
                last_deployed_on: Optional[datetime] = ..., 
                last_modified_on: datetime, 
                last_trained_on: Optional[datetime] = ..., 
                multilingual: Optional[bool] = ..., 
                project_kind: Union[str, ProjectKind], 
                project_name: str, 
                settings: Optional[ProjectSettings] = ..., 
                storage_input_container_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ProjectKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONVERSATION = "Conversation"
        CUSTOM_CONVERSATION_SUMMARIZATION = "CustomConversationSummarization"
        ORCHESTRATION = "Orchestration"


    class azure.ai.language.conversations.authoring.models.ProjectResourceIds(_Model):
        azure_resource_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                azure_resource_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ProjectResourcesState(_Model):
        created_on: datetime
        errors: Optional[list[ODataV4Format]]
        expires_on: Optional[datetime]
        job_id: str
        last_updated_on: datetime
        status: Union[str, OperationStatus]
        warnings: Optional[list[ODataV4Format]]

        @overload
        def __init__(
                self, 
                *, 
                created_on: datetime, 
                errors: Optional[list[ODataV4Format]] = ..., 
                expires_on: Optional[datetime] = ..., 
                last_updated_on: datetime, 
                status: Union[str, OperationStatus], 
                warnings: Optional[list[ODataV4Format]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ProjectSettings(_Model):
        confidence_threshold: float

        @overload
        def __init__(
                self, 
                *, 
                confidence_threshold: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ProjectTrainedModel(_Model):
        has_snapshot: bool
        label: str
        last_trained_on: datetime
        last_training_duration_in_seconds: int
        model_expired_on: date
        model_id: str
        model_training_config_version: str

        @overload
        def __init__(
                self, 
                *, 
                has_snapshot: bool, 
                last_trained_on: datetime, 
                last_training_duration_in_seconds: int, 
                model_expired_on: date, 
                model_id: str, 
                model_training_config_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.ResourceMetadata(_Model):
        azure_resource_id: str
        custom_domain: str
        region: str

        @overload
        def __init__(
                self, 
                *, 
                azure_resource_id: str, 
                custom_domain: str, 
                region: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.StringIndexType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        UTF16_CODE_UNIT = "Utf16CodeUnit"
        UTF32_CODE_UNIT = "Utf32CodeUnit"
        UTF8_CODE_UNIT = "Utf8CodeUnit"


    class azure.ai.language.conversations.authoring.models.SubTrainingState(_Model):
        ended_on: Optional[datetime]
        percent_complete: int
        started_on: Optional[datetime]
        status: Union[str, OperationStatus]

        @overload
        def __init__(
                self, 
                *, 
                ended_on: Optional[datetime] = ..., 
                percent_complete: int, 
                started_on: Optional[datetime] = ..., 
                status: Union[str, OperationStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.SupportedLanguage(_Model):
        language_code: str
        language_name: str

        @overload
        def __init__(
                self, 
                *, 
                language_code: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.SwapDeploymentsDetails(_Model):
        first_deployment_name: str
        second_deployment_name: str

        @overload
        def __init__(
                self, 
                *, 
                first_deployment_name: str, 
                second_deployment_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.SwapDeploymentsState(_Model):
        created_on: datetime
        errors: Optional[list[ODataV4Format]]
        expires_on: Optional[datetime]
        job_id: str
        last_updated_on: datetime
        status: Union[str, OperationStatus]
        warnings: Optional[list[ODataV4Format]]

        @overload
        def __init__(
                self, 
                *, 
                created_on: datetime, 
                errors: Optional[list[ODataV4Format]] = ..., 
                expires_on: Optional[datetime] = ..., 
                last_updated_on: datetime, 
                status: Union[str, OperationStatus], 
                warnings: Optional[list[ODataV4Format]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.TrainingConfigVersion(_Model):
        model_expiration_date: date
        training_config_version: str

        @overload
        def __init__(
                self, 
                *, 
                model_expiration_date: date
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.TrainingJobDetails(_Model):
        data_generation_settings: Optional[DataGenerationSettings]
        evaluation_options: Optional[EvaluationDetails]
        model_label: str
        training_config_version: Optional[str]
        training_mode: Union[str, TrainingMode]

        @overload
        def __init__(
                self, 
                *, 
                data_generation_settings: Optional[DataGenerationSettings] = ..., 
                evaluation_options: Optional[EvaluationDetails] = ..., 
                model_label: str, 
                training_config_version: Optional[str] = ..., 
                training_mode: Union[str, TrainingMode]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.TrainingJobResult(_Model):
        data_generation_status: SubTrainingState
        estimated_end_on: Optional[datetime]
        evaluation_status: Optional[SubTrainingState]
        model_label: str
        training_config_version: str
        training_mode: Optional[Union[str, TrainingMode]]
        training_status: SubTrainingState

        @overload
        def __init__(
                self, 
                *, 
                data_generation_status: SubTrainingState, 
                estimated_end_on: Optional[datetime] = ..., 
                evaluation_status: Optional[SubTrainingState] = ..., 
                model_label: str, 
                training_config_version: str, 
                training_mode: Optional[Union[str, TrainingMode]] = ..., 
                training_status: SubTrainingState
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.TrainingMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADVANCED = "advanced"
        STANDARD = "standard"


    class azure.ai.language.conversations.authoring.models.TrainingState(_Model):
        created_on: datetime
        errors: Optional[list[ODataV4Format]]
        expires_on: Optional[datetime]
        job_id: str
        last_updated_on: datetime
        result: TrainingJobResult
        status: Union[str, OperationStatus]
        warnings: Optional[list[ODataV4Format]]

        @overload
        def __init__(
                self, 
                *, 
                created_on: datetime, 
                errors: Optional[list[ODataV4Format]] = ..., 
                expires_on: Optional[datetime] = ..., 
                last_updated_on: datetime, 
                result: TrainingJobResult, 
                status: Union[str, OperationStatus], 
                warnings: Optional[list[ODataV4Format]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.UtteranceEntitiesEvaluationResult(_Model):
        expected_entities: list[UtteranceEntityEvaluationResult]
        predicted_entities: list[UtteranceEntityEvaluationResult]

        @overload
        def __init__(
                self, 
                *, 
                expected_entities: list[UtteranceEntityEvaluationResult], 
                predicted_entities: list[UtteranceEntityEvaluationResult]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.UtteranceEntityEvaluationResult(_Model):
        category: str
        length: int
        offset: int

        @overload
        def __init__(
                self, 
                *, 
                category: str, 
                length: int, 
                offset: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.UtteranceEvaluationResult(_Model):
        entities_result: UtteranceEntitiesEvaluationResult
        intents_result: UtteranceIntentsEvaluationResult
        language: str
        text: str

        @overload
        def __init__(
                self, 
                *, 
                entities_result: UtteranceEntitiesEvaluationResult, 
                intents_result: UtteranceIntentsEvaluationResult, 
                language: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.authoring.models.UtteranceIntentsEvaluationResult(_Model):
        expected_intent: str
        predicted_intent: str

        @overload
        def __init__(
                self, 
                *, 
                expected_intent: str, 
                predicted_intent: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.ai.language.conversations.authoring.operations

    class azure.ai.language.conversations.authoring.operations.DeploymentOperations(_GeneratedDeploymentOperations):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete_deployment(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_delete_deployment_from_resources(
                self, 
                deployment_name: str, 
                body: ProjectResourceIds, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_delete_deployment_from_resources(
                self, 
                deployment_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_delete_deployment_from_resources(
                self, 
                deployment_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_deploy_project(
                self, 
                deployment_name: str, 
                body: Union[CreateDeploymentDetails, JSON, Any], 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get_deployment(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> ProjectDeployment: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-11-01', params_added_on={'2025-11-01': ['api_version', 'project_name', 'deployment_name', 'job_id', 'accept']}, api_versions_list=['2025-11-01', '2025-05-15-preview', '2025-11-15-preview'])
        def get_deployment_delete_from_resources_status(
                self, 
                deployment_name: str, 
                job_id: str, 
                **kwargs: Any
            ) -> DeploymentDeleteFromResourcesState: ...

        @distributed_trace
        def get_deployment_status(
                self, 
                deployment_name: str, 
                job_id: str, 
                **kwargs: Any
            ) -> DeploymentState: ...


    class azure.ai.language.conversations.authoring.operations.ExportedModelOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update_exported_model(
                self, 
                exported_model_name: str, 
                body: ExportedModelDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update_exported_model(
                self, 
                exported_model_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update_exported_model(
                self, 
                exported_model_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-05-15-preview', params_added_on={'2025-05-15-preview': ['api_version', 'project_name', 'exported_model_name']}, api_versions_list=['2025-05-15-preview', '2025-11-15-preview'])
        def begin_delete_exported_model(
                self, 
                exported_model_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-05-15-preview', params_added_on={'2025-05-15-preview': ['api_version', 'project_name', 'exported_model_name', 'accept']}, api_versions_list=['2025-05-15-preview', '2025-11-15-preview'])
        def get_exported_model(
                self, 
                exported_model_name: str, 
                **kwargs: Any
            ) -> ExportedTrainedModel: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-05-15-preview', params_added_on={'2025-05-15-preview': ['api_version', 'project_name', 'exported_model_name', 'job_id', 'accept']}, api_versions_list=['2025-05-15-preview', '2025-11-15-preview'])
        def get_exported_model_job_status(
                self, 
                exported_model_name: str, 
                job_id: str, 
                **kwargs: Any
            ) -> ExportedModelState: ...


    class azure.ai.language.conversations.authoring.operations.ProjectOperations(ProjectOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_assign_project_resources(
                self, 
                body: AssignProjectResourcesDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_assign_project_resources(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_assign_project_resources(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_cancel_training_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> LROPoller[TrainingJobResult]: ...

        @overload
        def begin_copy_project(
                self, 
                body: CopyProjectDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_copy_project(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_copy_project(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_export(
                self, 
                *, 
                asset_kind: Optional[str] = ..., 
                exported_project_format: Optional[Union[str, ExportedProjectFormat]] = ..., 
                string_index_type: Union[str, StringIndexType], 
                trained_model_label: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_import(
                self, 
                body: ExportedProject, 
                *, 
                content_type: str = "application/json", 
                exported_project_format: Optional[Union[str, ExportedProjectFormat]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_import(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                exported_project_format: Optional[Union[str, ExportedProjectFormat]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_import(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                exported_project_format: Optional[Union[str, ExportedProjectFormat]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_swap_deployments(
                self, 
                body: SwapDeploymentsDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_swap_deployments(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_swap_deployments(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_train(
                self, 
                body: TrainingJobDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TrainingJobResult]: ...

        @overload
        def begin_train(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TrainingJobResult]: ...

        @overload
        def begin_train(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TrainingJobResult]: ...

        @overload
        def begin_unassign_project_resources(
                self, 
                body: ProjectResourceIds, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_unassign_project_resources(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_unassign_project_resources(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def copy_project_authorization(
                self, 
                *, 
                allow_overwrite: Optional[bool] = ..., 
                content_type: str = "application/json", 
                project_kind: Union[str, ProjectKind], 
                storage_input_container_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> CopyProjectDetails: ...

        @overload
        def copy_project_authorization(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopyProjectDetails: ...

        @overload
        def copy_project_authorization(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopyProjectDetails: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-11-01', params_added_on={'2025-11-01': ['api_version', 'project_name', 'job_id', 'accept']}, api_versions_list=['2025-11-01', '2025-05-15-preview', '2025-11-15-preview'])
        def get_assign_project_resources_status(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> ProjectResourcesState: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-05-15-preview', params_added_on={'2025-05-15-preview': ['api_version', 'project_name', 'job_id', 'accept']}, api_versions_list=['2025-05-15-preview', '2025-11-15-preview'])
        def get_copy_project_status(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> CopyProjectState: ...

        @distributed_trace
        def get_export_status(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> ExportProjectState: ...

        @distributed_trace
        def get_project(self, **kwargs: Any) -> ProjectDetails: ...

        @distributed_trace
        def get_project_deletion_status(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> ProjectDeletionState: ...

        @distributed_trace
        def get_swap_deployments_status(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> SwapDeploymentsState: ...

        @distributed_trace
        def get_training_status(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> TrainingState: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-11-01', params_added_on={'2025-11-01': ['api_version', 'project_name', 'job_id', 'accept']}, api_versions_list=['2025-11-01', '2025-05-15-preview', '2025-11-15-preview'])
        def get_unassign_project_resources_status(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> ProjectResourcesState: ...

        @distributed_trace
        def list_deployments(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ProjectDeployment]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-05-15-preview', params_added_on={'2025-05-15-preview': ['api_version', 'project_name', 'top', 'skip', 'maxpagesize', 'accept']}, api_versions_list=['2025-05-15-preview', '2025-11-15-preview'])
        def list_exported_models(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ExportedTrainedModel]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-11-01', params_added_on={'2025-11-01': ['api_version', 'project_name', 'top', 'skip', 'maxpagesize', 'accept']}, api_versions_list=['2025-11-01', '2025-05-15-preview', '2025-11-15-preview'])
        def list_project_resources(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AssignedProjectResource]: ...

        @distributed_trace
        def list_trained_models(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ProjectTrainedModel]: ...

        @distributed_trace
        def list_training_jobs(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[TrainingState]: ...


    class azure.ai.language.conversations.authoring.operations.TrainedModelOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_evaluate_model(
                self, 
                trained_model_label: str, 
                body: EvaluationDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EvaluationJobResult]: ...

        @overload
        def begin_evaluate_model(
                self, 
                trained_model_label: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EvaluationJobResult]: ...

        @overload
        def begin_evaluate_model(
                self, 
                trained_model_label: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EvaluationJobResult]: ...

        @distributed_trace
        def begin_load_snapshot(
                self, 
                trained_model_label: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def delete_trained_model(
                self, 
                trained_model_label: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-05-15-preview', params_added_on={'2025-05-15-preview': ['api_version', 'project_name', 'trained_model_label', 'job_id', 'accept']}, api_versions_list=['2025-05-15-preview', '2025-11-15-preview'])
        def get_evaluation_status(
                self, 
                trained_model_label: str, 
                job_id: str, 
                **kwargs: Any
            ) -> EvaluationState: ...

        @distributed_trace
        def get_load_snapshot_status(
                self, 
                trained_model_label: str, 
                job_id: str, 
                **kwargs: Any
            ) -> LoadSnapshotState: ...

        @distributed_trace
        def get_model_evaluation_results(
                self, 
                trained_model_label: str, 
                *, 
                skip: Optional[int] = ..., 
                string_index_type: Union[str, StringIndexType], 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[UtteranceEvaluationResult]: ...

        @distributed_trace
        def get_model_evaluation_summary(
                self, 
                trained_model_label: str, 
                **kwargs: Any
            ) -> EvalSummary: ...

        @distributed_trace
        def get_trained_model(
                self, 
                trained_model_label: str, 
                **kwargs: Any
            ) -> ProjectTrainedModel: ...


```