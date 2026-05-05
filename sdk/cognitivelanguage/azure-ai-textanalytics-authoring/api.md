```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.ai.textanalytics.authoring

    class azure.ai.textanalytics.authoring.TextAuthoringClient(AuthoringClientGenerated): implements ContextManager 

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

        def get_project_client(self, project_name: str) -> TextAuthoringProjectClient: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-11-15-preview', params_added_on={'2024-11-15-preview': ['api_version', 'top', 'skip', 'maxpagesize', 'accept']}, api_versions_list=['2024-11-15-preview', '2025-05-15-preview'])
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
                project_kind: Optional[Union[str, ProjectKind]] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SupportedLanguage]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-11-15-preview', params_added_on={'2024-11-15-preview': ['api_version', 'accept']}, api_versions_list=['2024-11-15-preview', '2025-05-15-preview'])
        def list_supported_prebuilt_entities(self, **kwargs: Any) -> ItemPaged[PrebuiltEntity]: ...

        @distributed_trace
        def list_training_config_versions(
                self, 
                *, 
                project_kind: Optional[Union[str, ProjectKind]] = ..., 
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


    class azure.ai.textanalytics.authoring.TextAuthoringProjectClient(AuthoringProjectClientGenerated): implements ContextManager 
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


namespace azure.ai.textanalytics.authoring.aio

    class azure.ai.textanalytics.authoring.aio.TextAuthoringClient(AuthoringClientGenerated): implements AsyncContextManager 

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

        def get_project_client(self, project_name: str) -> TextAuthoringProjectClient: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-11-15-preview', params_added_on={'2024-11-15-preview': ['api_version', 'top', 'skip', 'maxpagesize', 'accept']}, api_versions_list=['2024-11-15-preview', '2025-05-15-preview'])
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
                project_kind: Optional[Union[str, ProjectKind]] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SupportedLanguage]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-11-15-preview', params_added_on={'2024-11-15-preview': ['api_version', 'accept']}, api_versions_list=['2024-11-15-preview', '2025-05-15-preview'])
        def list_supported_prebuilt_entities(self, **kwargs: Any) -> AsyncItemPaged[PrebuiltEntity]: ...

        @distributed_trace
        def list_training_config_versions(
                self, 
                *, 
                project_kind: Optional[Union[str, ProjectKind]] = ..., 
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


    class azure.ai.textanalytics.authoring.aio.TextAuthoringProjectClient(AuthoringProjectClientGenerated): implements AsyncContextManager 
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


namespace azure.ai.textanalytics.authoring.aio.operations

    class azure.ai.textanalytics.authoring.aio.operations.DeploymentOperations:

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
                body: DeleteDeploymentDetails, 
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

        @overload
        async def begin_deploy_project(
                self, 
                deployment_name: str, 
                body: CreateDeploymentDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_deploy_project(
                self, 
                deployment_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_deploy_project(
                self, 
                deployment_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get_deployment(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> ProjectDeployment: ...


    class azure.ai.textanalytics.authoring.aio.operations.ExportedModelOperations:

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
        @api_version_validation(method_added_on='2024-11-15-preview', params_added_on={'2024-11-15-preview': ['api_version', 'project_name', 'exported_model_name']}, api_versions_list=['2024-11-15-preview', '2025-05-15-preview'])
        async def begin_delete_exported_model(
                self, 
                exported_model_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-11-15-preview', params_added_on={'2024-11-15-preview': ['api_version', 'project_name', 'exported_model_name', 'accept']}, api_versions_list=['2024-11-15-preview', '2025-05-15-preview'])
        async def get_exported_model(
                self, 
                exported_model_name: str, 
                **kwargs: Any
            ) -> ExportedTrainedModel: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-11-15-preview', params_added_on={'2024-11-15-preview': ['api_version', 'project_name', 'exported_model_name', 'accept']}, api_versions_list=['2024-11-15-preview', '2025-05-15-preview'])
        async def get_exported_model_manifest(
                self, 
                exported_model_name: str, 
                **kwargs: Any
            ) -> ExportedModelManifest: ...


    class azure.ai.textanalytics.authoring.aio.operations.ProjectOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_assign_deployment_resources(
                self, 
                body: AssignDeploymentResourcesDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_assign_deployment_resources(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_assign_deployment_resources(
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
                format: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_import(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                format: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_import(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                format: Optional[str] = ..., 
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
        async def begin_unassign_deployment_resources(
                self, 
                body: UnassignDeploymentResourcesDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_unassign_deployment_resources(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_unassign_deployment_resources(
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
        async def get_project(self, **kwargs: Any) -> ProjectDetails: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-11-15-preview', params_added_on={'2024-11-15-preview': ['api_version', 'project_name', 'top', 'skip', 'maxpagesize', 'accept']}, api_versions_list=['2024-11-15-preview', '2025-05-15-preview'])
        def list_deployment_resources(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AssignedDeploymentResource]: ...

        @distributed_trace
        def list_deployments(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ProjectDeployment]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-11-15-preview', params_added_on={'2024-11-15-preview': ['api_version', 'project_name', 'top', 'skip', 'maxpagesize', 'accept']}, api_versions_list=['2024-11-15-preview', '2025-05-15-preview'])
        def list_exported_models(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ExportedTrainedModel]: ...

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


    class azure.ai.textanalytics.authoring.aio.operations.TrainedModelOperations:

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

        @distributed_trace
        def list_model_evaluation_results(
                self, 
                trained_model_label: str, 
                *, 
                skip: Optional[int] = ..., 
                string_index_type: Union[str, StringIndexType], 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DocumentEvalResult]: ...


namespace azure.ai.textanalytics.authoring.models

    class azure.ai.textanalytics.authoring.models.AssignDeploymentResourcesDetails(_Model):
        resources_metadata: list[ResourceMetadata]

        @overload
        def __init__(
                self, 
                *, 
                resources_metadata: list[ResourceMetadata]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.AssignedDeploymentResource(_Model):
        azure_resource_id: str
        region: str

        @overload
        def __init__(
                self, 
                *, 
                region: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.AssignedProjectDeploymentMetadata(_Model):
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


    class azure.ai.textanalytics.authoring.models.AssignedProjectDeploymentsMetadata(_Model):
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


    class azure.ai.textanalytics.authoring.models.CompositionMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMBINE_COMPONENTS = "combineComponents"
        SEPARATE_COMPONENTS = "separateComponents"


    class azure.ai.textanalytics.authoring.models.ConfusionMatrixCell(_Model):
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


    class azure.ai.textanalytics.authoring.models.ConfusionMatrixRow(_Model):


    class azure.ai.textanalytics.authoring.models.CopyProjectDetails(_Model):
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


    class azure.ai.textanalytics.authoring.models.CopyProjectState(_Model):
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


    class azure.ai.textanalytics.authoring.models.CreateDeploymentDetails(_Model):
        assigned_resource_ids: Optional[list[str]]
        trained_model_label: str

        @overload
        def __init__(
                self, 
                *, 
                assigned_resource_ids: Optional[list[str]] = ..., 
                trained_model_label: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.CreateProjectOptions(_Model):
        description: Optional[str]
        language: str
        multilingual: Optional[bool]
        project_kind: Union[str, ProjectKind]
        project_name: str
        settings: Optional[ProjectSettings]
        storage_input_container_name: str

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
                storage_input_container_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.CustomEntityRecognitionDocumentEvalResult(DocumentEvalResult, discriminator='CustomEntityRecognition'):
        custom_entity_recognition_result: DocumentEntityRecognitionEvalResult
        language: str
        location: str
        project_kind: Literal[ProjectKind.CUSTOM_ENTITY_RECOGNITION]

        @overload
        def __init__(
                self, 
                *, 
                custom_entity_recognition_result: DocumentEntityRecognitionEvalResult, 
                language: str, 
                location: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.CustomEntityRecognitionEvalSummary(EvalSummary, discriminator='CustomEntityRecognition'):
        custom_entity_recognition_evaluation: EntityRecognitionEvalSummary
        evaluation_options: EvaluationDetails
        project_kind: Literal[ProjectKind.CUSTOM_ENTITY_RECOGNITION]

        @overload
        def __init__(
                self, 
                *, 
                custom_entity_recognition_evaluation: EntityRecognitionEvalSummary, 
                evaluation_options: EvaluationDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.CustomHealthcareDocumentEvalResult(DocumentEvalResult, discriminator='CustomHealthcare'):
        custom_healthcare_result: DocumentHealthcareEvalResult
        language: str
        location: str
        project_kind: Literal[ProjectKind.CUSTOM_HEALTHCARE]

        @overload
        def __init__(
                self, 
                *, 
                custom_healthcare_result: DocumentHealthcareEvalResult, 
                language: str, 
                location: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.CustomHealthcareEvalSummary(EvalSummary, discriminator='CustomHealthcare'):
        custom_healthcare_evaluation: EntityRecognitionEvalSummary
        evaluation_options: EvaluationDetails
        project_kind: Literal[ProjectKind.CUSTOM_HEALTHCARE]

        @overload
        def __init__(
                self, 
                *, 
                custom_healthcare_evaluation: EntityRecognitionEvalSummary, 
                evaluation_options: EvaluationDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.CustomMultiLabelClassificationDocumentEvalResult(DocumentEvalResult, discriminator='CustomMultiLabelClassification'):
        custom_multi_label_classification_result: DocumentMultiLabelClassificationEvalResult
        language: str
        location: str
        project_kind: Literal[ProjectKind.CUSTOM_MULTI_LABEL_CLASSIFICATION]

        @overload
        def __init__(
                self, 
                *, 
                custom_multi_label_classification_result: DocumentMultiLabelClassificationEvalResult, 
                language: str, 
                location: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.CustomMultiLabelClassificationEvalSummary(EvalSummary, discriminator='CustomMultiLabelClassification'):
        custom_multi_label_classification_evaluation: MultiLabelClassificationEvalSummary
        evaluation_options: EvaluationDetails
        project_kind: Literal[ProjectKind.CUSTOM_MULTI_LABEL_CLASSIFICATION]

        @overload
        def __init__(
                self, 
                *, 
                custom_multi_label_classification_evaluation: MultiLabelClassificationEvalSummary, 
                evaluation_options: EvaluationDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.CustomSingleLabelClassificationDocumentEvalResult(DocumentEvalResult, discriminator='CustomSingleLabelClassification'):
        custom_single_label_classification_result: DocumentSingleLabelClassificationEvalResult
        language: str
        location: str
        project_kind: Literal[ProjectKind.CUSTOM_SINGLE_LABEL_CLASSIFICATION]

        @overload
        def __init__(
                self, 
                *, 
                custom_single_label_classification_result: DocumentSingleLabelClassificationEvalResult, 
                language: str, 
                location: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.CustomSingleLabelClassificationEvalSummary(EvalSummary, discriminator='CustomSingleLabelClassification'):
        custom_single_label_classification_evaluation: SingleLabelClassificationEvalSummary
        evaluation_options: EvaluationDetails
        project_kind: Literal[ProjectKind.CUSTOM_SINGLE_LABEL_CLASSIFICATION]

        @overload
        def __init__(
                self, 
                *, 
                custom_single_label_classification_evaluation: SingleLabelClassificationEvalSummary, 
                evaluation_options: EvaluationDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.CustomTextSentimentDocumentEvalResult(DocumentEvalResult, discriminator='CustomTextSentiment'):
        custom_text_sentiment_result: DocumentTextSentimentEvalResult
        language: str
        location: str
        project_kind: Literal[ProjectKind.CUSTOM_TEXT_SENTIMENT]

        @overload
        def __init__(
                self, 
                *, 
                custom_text_sentiment_result: DocumentTextSentimentEvalResult, 
                language: str, 
                location: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.CustomTextSentimentEvalSummary(EvalSummary, discriminator='CustomTextSentiment'):
        custom_text_sentiment_evaluation: TextSentimentEvalSummary
        evaluation_options: EvaluationDetails
        project_kind: Literal[ProjectKind.CUSTOM_TEXT_SENTIMENT]

        @overload
        def __init__(
                self, 
                *, 
                custom_text_sentiment_evaluation: TextSentimentEvalSummary, 
                evaluation_options: EvaluationDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.CustomTextSentimentProjectAssets(ExportedProjectAsset, discriminator='CustomTextSentiment'):
        documents: Optional[list[ExportedCustomTextSentimentDocument]]
        project_kind: Literal[ProjectKind.CUSTOM_TEXT_SENTIMENT]

        @overload
        def __init__(
                self, 
                *, 
                documents: Optional[list[ExportedCustomTextSentimentDocument]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.DataGenerationConnectionInfo(_Model):
        deployment_name: str
        kind: Literal["AzureOpenAI"]
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                deployment_name: str, 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.DataGenerationSetting(_Model):
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


    class azure.ai.textanalytics.authoring.models.DeleteDeploymentDetails(_Model):
        assigned_resource_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                assigned_resource_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.DeploymentDeleteFromResourcesState(_Model):
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


    class azure.ai.textanalytics.authoring.models.DeploymentResource(_Model):
        region: str
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                region: str, 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.DeploymentResourcesState(_Model):
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


    class azure.ai.textanalytics.authoring.models.DeploymentState(_Model):
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


    class azure.ai.textanalytics.authoring.models.DocumentEntityLabelEvalResult(_Model):
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


    class azure.ai.textanalytics.authoring.models.DocumentEntityRecognitionEvalResult(_Model):
        entities: list[DocumentEntityRegionEvalResult]

        @overload
        def __init__(
                self, 
                *, 
                entities: list[DocumentEntityRegionEvalResult]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.DocumentEntityRegionEvalResult(_Model):
        expected_entities: list[DocumentEntityLabelEvalResult]
        predicted_entities: list[DocumentEntityLabelEvalResult]
        region_length: int
        region_offset: int

        @overload
        def __init__(
                self, 
                *, 
                expected_entities: list[DocumentEntityLabelEvalResult], 
                predicted_entities: list[DocumentEntityLabelEvalResult], 
                region_length: int, 
                region_offset: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.DocumentEvalResult(_Model):
        language: str
        location: str
        project_kind: str

        @overload
        def __init__(
                self, 
                *, 
                language: str, 
                location: str, 
                project_kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.DocumentHealthcareEvalResult(_Model):
        entities: list[DocumentEntityRegionEvalResult]

        @overload
        def __init__(
                self, 
                *, 
                entities: list[DocumentEntityRegionEvalResult]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.DocumentMultiLabelClassificationEvalResult(_Model):
        expected_classes: list[str]
        predicted_classes: list[str]

        @overload
        def __init__(
                self, 
                *, 
                expected_classes: list[str], 
                predicted_classes: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.DocumentSentimentLabelEvalResult(_Model):
        category: Union[str, Sentiment]
        length: int
        offset: int

        @overload
        def __init__(
                self, 
                *, 
                category: Union[str, Sentiment], 
                length: int, 
                offset: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.DocumentSingleLabelClassificationEvalResult(_Model):
        expected_class: str
        predicted_class: str

        @overload
        def __init__(
                self, 
                *, 
                expected_class: str, 
                predicted_class: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.DocumentTextSentimentEvalResult(_Model):
        expected_sentiment_spans: list[DocumentSentimentLabelEvalResult]
        predicted_sentiment_spans: list[DocumentSentimentLabelEvalResult]

        @overload
        def __init__(
                self, 
                *, 
                expected_sentiment_spans: list[DocumentSentimentLabelEvalResult], 
                predicted_sentiment_spans: list[DocumentSentimentLabelEvalResult]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.EntityEvalSummary(_Model):
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


    class azure.ai.textanalytics.authoring.models.EntityRecognitionEvalSummary(_Model):
        confusion_matrix: dict[str, ConfusionMatrixRow]
        entities: dict[str, EntityEvalSummary]
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
                entities: dict[str, EntityEvalSummary], 
                macro_f1: float, 
                macro_precision: float, 
                macro_recall: float, 
                micro_f1: float, 
                micro_precision: float, 
                micro_recall: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.EvalSummary(_Model):
        evaluation_options: EvaluationDetails
        project_kind: str

        @overload
        def __init__(
                self, 
                *, 
                evaluation_options: EvaluationDetails, 
                project_kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.EvaluationDetails(_Model):
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


    class azure.ai.textanalytics.authoring.models.EvaluationJobResult(_Model):
        evaluation_options: EvaluationDetails
        model_label: str
        percent_complete: int
        training_config_version: str

        @overload
        def __init__(
                self, 
                *, 
                evaluation_options: EvaluationDetails, 
                model_label: str, 
                percent_complete: int, 
                training_config_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.EvaluationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANUAL = "manual"
        PERCENTAGE = "percentage"


    class azure.ai.textanalytics.authoring.models.EvaluationState(_Model):
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


    class azure.ai.textanalytics.authoring.models.ExportProjectState(_Model):
        created_on: datetime
        errors: Optional[list[ODataV4Format]]
        expires_on: Optional[datetime]
        job_id: str
        last_updated_on: datetime
        result_url: Optional[str]
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
                result_url: Optional[str] = ..., 
                status: Union[str, OperationStatus], 
                warnings: Optional[list[ODataV4Format]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedClass(_Model):
        category: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedCompositeEntity(_Model):
        category: Optional[str]
        composition_setting: Optional[Union[str, CompositionMode]]
        entity_list: Optional[ExportedEntityList]
        list: ExportedEntityList
        prebuilts: Optional[list[ExportedPrebuiltEntity]]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                composition_setting: Optional[Union[str, CompositionMode]] = ..., 
                list: Optional[ExportedEntityList] = ..., 
                prebuilts: Optional[list[ExportedPrebuiltEntity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedCustomAbstractiveSummarizationDocument(_Model):
        dataset: Optional[str]
        language: Optional[str]
        location: Optional[str]
        summary_location: str

        @overload
        def __init__(
                self, 
                *, 
                dataset: Optional[str] = ..., 
                language: Optional[str] = ..., 
                location: Optional[str] = ..., 
                summary_location: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedCustomAbstractiveSummarizationProjectAsset(ExportedProjectAsset, discriminator='CustomAbstractiveSummarization'):
        documents: Optional[list[ExportedCustomAbstractiveSummarizationDocument]]
        project_kind: Literal[ProjectKind.CUSTOM_ABSTRACTIVE_SUMMARIZATION]

        @overload
        def __init__(
                self, 
                *, 
                documents: Optional[list[ExportedCustomAbstractiveSummarizationDocument]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedCustomEntityRecognitionDocument(_Model):
        dataset: Optional[str]
        entities: Optional[list[ExportedDocumentEntityRegion]]
        language: Optional[str]
        location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                dataset: Optional[str] = ..., 
                entities: Optional[list[ExportedDocumentEntityRegion]] = ..., 
                language: Optional[str] = ..., 
                location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedCustomEntityRecognitionProjectAsset(ExportedProjectAsset, discriminator='CustomEntityRecognition'):
        documents: Optional[list[ExportedCustomEntityRecognitionDocument]]
        entities: Optional[list[ExportedEntity]]
        project_kind: Literal[ProjectKind.CUSTOM_ENTITY_RECOGNITION]

        @overload
        def __init__(
                self, 
                *, 
                documents: Optional[list[ExportedCustomEntityRecognitionDocument]] = ..., 
                entities: Optional[list[ExportedEntity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedCustomHealthcareDocument(_Model):
        dataset: Optional[str]
        entities: Optional[list[ExportedDocumentEntityRegion]]
        language: Optional[str]
        location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                dataset: Optional[str] = ..., 
                entities: Optional[list[ExportedDocumentEntityRegion]] = ..., 
                language: Optional[str] = ..., 
                location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedCustomHealthcareProjectAsset(ExportedProjectAsset, discriminator='CustomHealthcare'):
        documents: Optional[list[ExportedCustomHealthcareDocument]]
        entities: Optional[list[ExportedCompositeEntity]]
        project_kind: Literal[ProjectKind.CUSTOM_HEALTHCARE]

        @overload
        def __init__(
                self, 
                *, 
                documents: Optional[list[ExportedCustomHealthcareDocument]] = ..., 
                entities: Optional[list[ExportedCompositeEntity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedCustomMultiLabelClassificationDocument(_Model):
        classes: Optional[list[ExportedDocumentClass]]
        dataset: Optional[str]
        language: Optional[str]
        location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                classes: Optional[list[ExportedDocumentClass]] = ..., 
                dataset: Optional[str] = ..., 
                language: Optional[str] = ..., 
                location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedCustomMultiLabelClassificationProjectAsset(ExportedProjectAsset, discriminator='CustomMultiLabelClassification'):
        classes: Optional[list[ExportedClass]]
        documents: Optional[list[ExportedCustomMultiLabelClassificationDocument]]
        project_kind: Literal[ProjectKind.CUSTOM_MULTI_LABEL_CLASSIFICATION]

        @overload
        def __init__(
                self, 
                *, 
                classes: Optional[list[ExportedClass]] = ..., 
                documents: Optional[list[ExportedCustomMultiLabelClassificationDocument]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedCustomSingleLabelClassificationDocument(_Model):
        dataset: Optional[str]
        document_class: Optional[ExportedDocumentClass]
        language: Optional[str]
        location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                dataset: Optional[str] = ..., 
                document_class: Optional[ExportedDocumentClass] = ..., 
                language: Optional[str] = ..., 
                location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedCustomSingleLabelClassificationProjectAsset(ExportedProjectAsset, discriminator='CustomSingleLabelClassification'):
        classes: Optional[list[ExportedClass]]
        documents: Optional[list[ExportedCustomSingleLabelClassificationDocument]]
        project_kind: Literal[ProjectKind.CUSTOM_SINGLE_LABEL_CLASSIFICATION]

        @overload
        def __init__(
                self, 
                *, 
                classes: Optional[list[ExportedClass]] = ..., 
                documents: Optional[list[ExportedCustomSingleLabelClassificationDocument]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedCustomTextSentimentDocument(_Model):
        dataset: Optional[str]
        language: Optional[str]
        location: Optional[str]
        sentiment_spans: Optional[list[ExportedDocumentSentimentLabel]]

        @overload
        def __init__(
                self, 
                *, 
                dataset: Optional[str] = ..., 
                language: Optional[str] = ..., 
                location: Optional[str] = ..., 
                sentiment_spans: Optional[list[ExportedDocumentSentimentLabel]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedDocumentClass(_Model):
        category: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedDocumentEntityLabel(_Model):
        category: Optional[str]
        length: Optional[int]
        offset: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                length: Optional[int] = ..., 
                offset: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedDocumentEntityRegion(_Model):
        labels: Optional[list[ExportedDocumentEntityLabel]]
        region_length: Optional[int]
        region_offset: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                labels: Optional[list[ExportedDocumentEntityLabel]] = ..., 
                region_length: Optional[int] = ..., 
                region_offset: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedDocumentSentimentLabel(_Model):
        category: Optional[Union[str, Sentiment]]
        length: Optional[int]
        offset: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[Union[str, Sentiment]] = ..., 
                length: Optional[int] = ..., 
                offset: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedEntity(_Model):
        category: Optional[str]
        description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedEntityList(_Model):
        sublists: Optional[list[ExportedEntitySublist]]

        @overload
        def __init__(
                self, 
                *, 
                sublists: Optional[list[ExportedEntitySublist]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedEntityListSynonym(_Model):
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


    class azure.ai.textanalytics.authoring.models.ExportedEntitySublist(_Model):
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


    class azure.ai.textanalytics.authoring.models.ExportedModelDetails(_Model):
        trained_model_label: str

        @overload
        def __init__(
                self, 
                *, 
                trained_model_label: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedModelManifest(_Model):
        model_files: list[ModelFile]

        @overload
        def __init__(
                self, 
                *, 
                model_files: list[ModelFile]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedModelState(_Model):
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


    class azure.ai.textanalytics.authoring.models.ExportedPrebuiltEntity(_Model):
        category: str

        @overload
        def __init__(
                self, 
                *, 
                category: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedProject(_Model):
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


    class azure.ai.textanalytics.authoring.models.ExportedProjectAsset(_Model):
        project_kind: str

        @overload
        def __init__(
                self, 
                *, 
                project_kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ExportedTrainedModel(_Model):
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


    class azure.ai.textanalytics.authoring.models.ImportProjectState(_Model):
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


    class azure.ai.textanalytics.authoring.models.LoadSnapshotState(_Model):
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


    class azure.ai.textanalytics.authoring.models.ModelFile(_Model):
        content_uri: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                content_uri: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.MultiLabelClassEvalSummary(_Model):
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


    class azure.ai.textanalytics.authoring.models.MultiLabelClassificationEvalSummary(_Model):
        classes: dict[str, MultiLabelClassEvalSummary]
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
                classes: dict[str, MultiLabelClassEvalSummary], 
                macro_f1: float, 
                macro_precision: float, 
                macro_recall: float, 
                micro_f1: float, 
                micro_precision: float, 
                micro_recall: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.OperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "cancelled"
        CANCELLING = "cancelling"
        FAILED = "failed"
        NOT_STARTED = "notStarted"
        PARTIALLY_COMPLETED = "partiallyCompleted"
        RUNNING = "running"
        SUCCEEDED = "succeeded"


    class azure.ai.textanalytics.authoring.models.PrebuiltEntity(_Model):
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


    class azure.ai.textanalytics.authoring.models.ProjectDeletionState(_Model):
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


    class azure.ai.textanalytics.authoring.models.ProjectDeployment(_Model):
        assigned_resources: list[DeploymentResource]
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
                assigned_resources: list[DeploymentResource], 
                deployment_expired_on: date, 
                last_deployed_on: datetime, 
                last_trained_on: datetime, 
                model_id: str, 
                model_training_config_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ProjectDetails(_Model):
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
        storage_input_container_name: str

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
                settings: Optional[ProjectSettings] = ..., 
                storage_input_container_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ProjectKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_ABSTRACTIVE_SUMMARIZATION = "CustomAbstractiveSummarization"
        CUSTOM_ENTITY_RECOGNITION = "CustomEntityRecognition"
        CUSTOM_HEALTHCARE = "CustomHealthcare"
        CUSTOM_MULTI_LABEL_CLASSIFICATION = "CustomMultiLabelClassification"
        CUSTOM_SINGLE_LABEL_CLASSIFICATION = "CustomSingleLabelClassification"
        CUSTOM_TEXT_SENTIMENT = "CustomTextSentiment"


    class azure.ai.textanalytics.authoring.models.ProjectSettings(_Model):
        aml_project_path: Optional[str]
        confidence_threshold: Optional[float]
        gpt_predictive_lookahead: Optional[int]
        is_labeling_locked: Optional[bool]
        run_gpt_predictions: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                aml_project_path: Optional[str] = ..., 
                confidence_threshold: Optional[float] = ..., 
                gpt_predictive_lookahead: Optional[int] = ..., 
                is_labeling_locked: Optional[bool] = ..., 
                run_gpt_predictions: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.ProjectTrainedModel(_Model):
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


    class azure.ai.textanalytics.authoring.models.ResourceMetadata(_Model):
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


    class azure.ai.textanalytics.authoring.models.Sentiment(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NEGATIVE = "negative"
        NEUTRAL = "neutral"
        POSITIVE = "positive"


    class azure.ai.textanalytics.authoring.models.SentimentEvalSummary(_Model):
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


    class azure.ai.textanalytics.authoring.models.SingleLabelClassEvalSummary(_Model):
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


    class azure.ai.textanalytics.authoring.models.SingleLabelClassificationEvalSummary(_Model):
        classes: dict[str, SingleLabelClassEvalSummary]
        confusion_matrix: dict[str, ConfusionMatrixRow]
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
                classes: dict[str, SingleLabelClassEvalSummary], 
                confusion_matrix: dict[str, ConfusionMatrixRow], 
                macro_f1: float, 
                macro_precision: float, 
                macro_recall: float, 
                micro_f1: float, 
                micro_precision: float, 
                micro_recall: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.SpanSentimentEvalSummary(_Model):
        confusion_matrix: dict[str, ConfusionMatrixRow]
        macro_f1: float
        macro_precision: float
        macro_recall: float
        micro_f1: float
        micro_precision: float
        micro_recall: float
        sentiments: dict[str, SentimentEvalSummary]

        @overload
        def __init__(
                self, 
                *, 
                confusion_matrix: dict[str, ConfusionMatrixRow], 
                macro_f1: float, 
                macro_precision: float, 
                macro_recall: float, 
                micro_f1: float, 
                micro_precision: float, 
                micro_recall: float, 
                sentiments: dict[str, SentimentEvalSummary]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.StringIndexType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        UTF16_CODE_UNIT = "Utf16CodeUnit"


    class azure.ai.textanalytics.authoring.models.SubTrainingState(_Model):
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


    class azure.ai.textanalytics.authoring.models.SupportedLanguage(_Model):
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


    class azure.ai.textanalytics.authoring.models.SwapDeploymentsDetails(_Model):
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


    class azure.ai.textanalytics.authoring.models.SwapDeploymentsState(_Model):
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


    class azure.ai.textanalytics.authoring.models.TextSentimentEvalSummary(_Model):
        macro_f1: float
        macro_precision: float
        macro_recall: float
        micro_f1: float
        micro_precision: float
        micro_recall: float
        span_sentiments_evaluation: SpanSentimentEvalSummary

        @overload
        def __init__(
                self, 
                *, 
                macro_f1: float, 
                macro_precision: float, 
                macro_recall: float, 
                micro_f1: float, 
                micro_precision: float, 
                micro_recall: float, 
                span_sentiments_evaluation: SpanSentimentEvalSummary
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.TrainingConfigVersion(_Model):
        model_expired_on: date
        training_config_version: str

        @overload
        def __init__(
                self, 
                *, 
                model_expired_on: date
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.TrainingJobDetails(_Model):
        data_generation_settings: Optional[DataGenerationSetting]
        evaluation_options: Optional[EvaluationDetails]
        model_label: str
        training_config_version: str

        @overload
        def __init__(
                self, 
                *, 
                data_generation_settings: Optional[DataGenerationSetting] = ..., 
                evaluation_options: Optional[EvaluationDetails] = ..., 
                model_label: str, 
                training_config_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.TrainingJobResult(_Model):
        estimated_end_on: Optional[datetime]
        evaluation_status: Optional[SubTrainingState]
        model_label: str
        training_config_version: str
        training_status: SubTrainingState

        @overload
        def __init__(
                self, 
                *, 
                estimated_end_on: Optional[datetime] = ..., 
                evaluation_status: Optional[SubTrainingState] = ..., 
                model_label: str, 
                training_config_version: str, 
                training_status: SubTrainingState
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.authoring.models.TrainingState(_Model):
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


    class azure.ai.textanalytics.authoring.models.UnassignDeploymentResourcesDetails(_Model):
        assigned_resource_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                assigned_resource_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.ai.textanalytics.authoring.operations

    class azure.ai.textanalytics.authoring.operations.DeploymentOperations:

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
                body: DeleteDeploymentDetails, 
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

        @overload
        def begin_deploy_project(
                self, 
                deployment_name: str, 
                body: CreateDeploymentDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_deploy_project(
                self, 
                deployment_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_deploy_project(
                self, 
                deployment_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get_deployment(
                self, 
                deployment_name: str, 
                **kwargs: Any
            ) -> ProjectDeployment: ...


    class azure.ai.textanalytics.authoring.operations.ExportedModelOperations:

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
        @api_version_validation(method_added_on='2024-11-15-preview', params_added_on={'2024-11-15-preview': ['api_version', 'project_name', 'exported_model_name']}, api_versions_list=['2024-11-15-preview', '2025-05-15-preview'])
        def begin_delete_exported_model(
                self, 
                exported_model_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-11-15-preview', params_added_on={'2024-11-15-preview': ['api_version', 'project_name', 'exported_model_name', 'accept']}, api_versions_list=['2024-11-15-preview', '2025-05-15-preview'])
        def get_exported_model(
                self, 
                exported_model_name: str, 
                **kwargs: Any
            ) -> ExportedTrainedModel: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-11-15-preview', params_added_on={'2024-11-15-preview': ['api_version', 'project_name', 'exported_model_name', 'accept']}, api_versions_list=['2024-11-15-preview', '2025-05-15-preview'])
        def get_exported_model_manifest(
                self, 
                exported_model_name: str, 
                **kwargs: Any
            ) -> ExportedModelManifest: ...


    class azure.ai.textanalytics.authoring.operations.ProjectOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_assign_deployment_resources(
                self, 
                body: AssignDeploymentResourcesDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_assign_deployment_resources(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_assign_deployment_resources(
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
                format: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_import(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                format: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_import(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                format: Optional[str] = ..., 
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
        def begin_unassign_deployment_resources(
                self, 
                body: UnassignDeploymentResourcesDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_unassign_deployment_resources(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_unassign_deployment_resources(
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
        def get_project(self, **kwargs: Any) -> ProjectDetails: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-11-15-preview', params_added_on={'2024-11-15-preview': ['api_version', 'project_name', 'top', 'skip', 'maxpagesize', 'accept']}, api_versions_list=['2024-11-15-preview', '2025-05-15-preview'])
        def list_deployment_resources(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AssignedDeploymentResource]: ...

        @distributed_trace
        def list_deployments(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ProjectDeployment]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-11-15-preview', params_added_on={'2024-11-15-preview': ['api_version', 'project_name', 'top', 'skip', 'maxpagesize', 'accept']}, api_versions_list=['2024-11-15-preview', '2025-05-15-preview'])
        def list_exported_models(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ExportedTrainedModel]: ...

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


    class azure.ai.textanalytics.authoring.operations.TrainedModelOperations:

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

        @distributed_trace
        def list_model_evaluation_results(
                self, 
                trained_model_label: str, 
                *, 
                skip: Optional[int] = ..., 
                string_index_type: Union[str, StringIndexType], 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DocumentEvalResult]: ...


```