```py
namespace azure.mgmt.anyscale

    class azure.mgmt.anyscale.PlatformClient: implements ContextManager 
        agreements: AgreementsOperations
        cloud_resources: CloudResourcesOperations
        clouds: CloudsOperations
        compute_configs: ComputeConfigsOperations
        container_images: ContainerImagesOperations
        jobs: JobsOperations
        operation_statuses: OperationStatusesOperations
        operations: Operations
        projects: ProjectsOperations
        services: ServicesOperations
        workspaces: WorkspacesOperations

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


namespace azure.mgmt.anyscale.aio

    class azure.mgmt.anyscale.aio.PlatformClient: implements AsyncContextManager 
        agreements: AgreementsOperations
        cloud_resources: CloudResourcesOperations
        clouds: CloudsOperations
        compute_configs: ComputeConfigsOperations
        container_images: ContainerImagesOperations
        jobs: JobsOperations
        operation_statuses: OperationStatusesOperations
        operations: Operations
        projects: ProjectsOperations
        services: ServicesOperations
        workspaces: WorkspacesOperations

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


namespace azure.mgmt.anyscale.aio.operations

    class azure.mgmt.anyscale.aio.operations.AgreementsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                agreement_name: str, 
                resource: Agreement, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agreement: ...

        @overload
        async def create_or_update(
                self, 
                agreement_name: str, 
                resource: Agreement, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agreement: ...

        @overload
        async def create_or_update(
                self, 
                agreement_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agreement: ...

        @distributed_trace_async
        async def delete(
                self, 
                agreement_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                agreement_name: str, 
                **kwargs: Any
            ) -> Agreement: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Agreement]: ...


    class azure.mgmt.anyscale.aio.operations.CloudResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                cloud_resource_name: str, 
                resource: CloudResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                cloud_resource_name: str, 
                resource: CloudResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                cloud_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                cloud_resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                cloud_resource_name: str, 
                **kwargs: Any
            ) -> CloudResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CloudResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                cloud_resource_name: str, 
                properties: CloudResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CloudResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                cloud_resource_name: str, 
                properties: CloudResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CloudResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                cloud_resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CloudResource: ...


    class azure.mgmt.anyscale.aio.operations.CloudsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                resource: Cloud, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cloud]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                resource: Cloud, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cloud]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cloud]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                **kwargs: Any
            ) -> Cloud: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Cloud]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Cloud]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                properties: CloudUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Cloud: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                properties: CloudUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Cloud: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Cloud: ...


    class azure.mgmt.anyscale.aio.operations.ComputeConfigsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                compute_config_name: str, 
                resource: ComputeConfig, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ComputeConfig]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                compute_config_name: str, 
                resource: ComputeConfig, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ComputeConfig]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                compute_config_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ComputeConfig]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                compute_config_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                compute_config_name: str, 
                **kwargs: Any
            ) -> ComputeConfig: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ComputeConfig]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                compute_config_name: str, 
                properties: ComputeConfigUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComputeConfig: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                compute_config_name: str, 
                properties: ComputeConfigUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComputeConfig: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                compute_config_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComputeConfig: ...


    class azure.mgmt.anyscale.aio.operations.ContainerImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                container_image_name: str, 
                resource: ContainerImage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ContainerImage]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                container_image_name: str, 
                resource: ContainerImage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ContainerImage]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                container_image_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ContainerImage]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                container_image_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                container_image_name: str, 
                **kwargs: Any
            ) -> ContainerImage: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ContainerImage]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                container_image_name: str, 
                properties: ContainerImageUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerImage: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                container_image_name: str, 
                properties: ContainerImageUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerImage: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                container_image_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerImage: ...


    class azure.mgmt.anyscale.aio.operations.JobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                job_name: str, 
                resource: Job, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Job]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                job_name: str, 
                resource: Job, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Job]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                job_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Job]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> Job: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Job]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                job_name: str, 
                properties: JobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Job: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                job_name: str, 
                properties: JobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Job: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                job_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Job: ...


    class azure.mgmt.anyscale.aio.operations.OperationStatusesOperations:

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


    class azure.mgmt.anyscale.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.anyscale.aio.operations.ProjectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                resource: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Project]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                resource: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Project]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Project]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Project: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Project]: ...


    class azure.mgmt.anyscale.aio.operations.ServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                service_name: str, 
                resource: Service, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Service]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                service_name: str, 
                resource: Service, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Service]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                service_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Service]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> Service: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Service]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                service_name: str, 
                properties: ServiceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Service: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                service_name: str, 
                properties: ServiceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Service: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                service_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Service: ...


    class azure.mgmt.anyscale.aio.operations.WorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                workspace_name: str, 
                resource: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                workspace_name: str, 
                resource: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                workspace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> Workspace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Workspace]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                workspace_name: str, 
                properties: WorkspaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                workspace_name: str, 
                properties: WorkspaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                workspace_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...


namespace azure.mgmt.anyscale.models

    class azure.mgmt.anyscale.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.anyscale.models.Agreement(ProxyResource):
        id: str
        name: str
        properties: Optional[AgreementProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AgreementProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.AgreementProperties(_Model):
        agreement_link: Optional[str]
        display_name: Optional[str]
        effective_date: Optional[datetime]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: Optional[Union[str, AgreementStatus]]


    class azure.mgmt.anyscale.models.AgreementStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        PENDING = "Pending"


    class azure.mgmt.anyscale.models.Cloud(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[CloudProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[CloudProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.CloudProperties(_Model):
        acr_resource_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        sso_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                acr_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.CloudResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[CloudResourceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[CloudResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.CloudResourceProperties(_Model):
        anyscale_operator_iam_identity: Optional[str]
        cloud_resource_id: Optional[str]
        cloud_storage_bucket_endpoint: str
        cloud_storage_bucket_name: str
        cloud_storage_bucket_region: Optional[str]
        compute_stack: Union[str, ComputeStack]
        provider: Union[str, Provider]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        region: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                anyscale_operator_iam_identity: Optional[str] = ..., 
                cloud_storage_bucket_endpoint: str, 
                cloud_storage_bucket_name: str, 
                cloud_storage_bucket_region: Optional[str] = ..., 
                compute_stack: Union[str, ComputeStack], 
                provider: Union[str, Provider], 
                region: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.CloudResourceUpdate(_Model):
        properties: Optional[CloudResourceUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CloudResourceUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.CloudResourceUpdateProperties(_Model):
        anyscale_operator_iam_identity: Optional[str]
        cloud_storage_bucket_endpoint: Optional[str]
        cloud_storage_bucket_name: Optional[str]
        compute_stack: Optional[Union[str, ComputeStack]]
        provider: Optional[Union[str, Provider]]

        @overload
        def __init__(
                self, 
                *, 
                anyscale_operator_iam_identity: Optional[str] = ..., 
                cloud_storage_bucket_endpoint: Optional[str] = ..., 
                cloud_storage_bucket_name: Optional[str] = ..., 
                compute_stack: Optional[Union[str, ComputeStack]] = ..., 
                provider: Optional[Union[str, Provider]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.CloudUpdate(_Model):
        properties: Optional[CloudUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CloudUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.CloudUpdateProperties(_Model):
        acr_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                acr_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.ComputeConfig(ProxyResource):
        id: str
        name: str
        properties: Optional[ComputeConfigProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ComputeConfigProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.ComputeConfigProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        revision: Optional[int]
        spec: ComputeConfigSpec
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                spec: ComputeConfigSpec
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.ComputeConfigSpec(_Model):
        options: Optional[list[ComputeConfigSpecOption]]

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[list[ComputeConfigSpecOption]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.ComputeConfigSpecOption(_Model):
        advanced_instance_config: Optional[str]
        cloud_resource_names: Optional[list[str]]
        flags: Optional[Any]
        head_node: NodeType
        worker_nodes: Optional[list[WorkerNode]]
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                advanced_instance_config: Optional[str] = ..., 
                cloud_resource_names: Optional[list[str]] = ..., 
                flags: Optional[Any] = ..., 
                head_node: NodeType, 
                worker_nodes: Optional[list[WorkerNode]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.ComputeConfigSpecOrReference(_Model):
        compute_config_name: Optional[str]
        spec: Optional[ComputeConfigSpec]

        @overload
        def __init__(
                self, 
                *, 
                compute_config_name: Optional[str] = ..., 
                spec: Optional[ComputeConfigSpec] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.ComputeConfigUpdate(_Model):
        properties: Optional[ComputeConfigUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ComputeConfigUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.ComputeConfigUpdateProperties(_Model):
        spec: Optional[ComputeConfigSpec]

        @overload
        def __init__(
                self, 
                *, 
                spec: Optional[ComputeConfigSpec] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.ComputeStack(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        K8_S = "K8S"


    class azure.mgmt.anyscale.models.ContainerImage(ProxyResource):
        id: str
        name: str
        properties: Optional[ContainerImageProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ContainerImageProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.ContainerImageBuildState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILD_FAILED = "BuildFailed"
        BUILD_IN_PROGRESS = "BuildInProgress"
        BUILD_PENDING = "BuildPending"
        BUILD_SUCCEEDED = "BuildSucceeded"


    class azure.mgmt.anyscale.models.ContainerImageProperties(_Model):
        build_state: Optional[Union[str, ContainerImageBuildState]]
        container_image_uri: Optional[str]
        containerfile: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        revision: Optional[int]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                container_image_uri: Optional[str] = ..., 
                containerfile: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.ContainerImageUpdate(_Model):
        properties: Optional[ContainerImageUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ContainerImageUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.ContainerImageUpdateProperties(_Model):
        container_image_uri: Optional[str]
        containerfile: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                container_image_uri: Optional[str] = ..., 
                containerfile: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.CpuArchitecture(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARM64 = "arm64"
        X86_64 = "x86_64"


    class azure.mgmt.anyscale.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.anyscale.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.anyscale.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.anyscale.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.Job(ProxyResource):
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


    class azure.mgmt.anyscale.models.JobConfig(_Model):
        compute_config: Optional[ComputeConfigSpecOrReference]
        entrypoint: Optional[str]
        env_vars: Optional[Any]
        image_uri: Optional[str]
        max_retries: Optional[int]
        pip_requirements: Optional[list[str]]
        py_modules: Optional[list[str]]
        timeout: Optional[timedelta]
        working_dir: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                compute_config: Optional[ComputeConfigSpecOrReference] = ..., 
                entrypoint: Optional[str] = ..., 
                env_vars: Optional[Any] = ..., 
                image_uri: Optional[str] = ..., 
                max_retries: Optional[int] = ..., 
                pip_requirements: Optional[list[str]] = ..., 
                py_modules: Optional[list[str]] = ..., 
                timeout: Optional[timedelta] = ..., 
                working_dir: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.JobProperties(_Model):
        config: JobConfig
        provisioning_state: Optional[Union[str, ProvisioningState]]
        state: Optional[Union[str, JobState]]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                config: JobConfig
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.JobState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        RUNNING = "Running"
        STARTING = "Starting"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.anyscale.models.JobUpdate(_Model):
        properties: Optional[JobUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[JobUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.JobUpdateProperties(_Model):
        config: Optional[JobConfig]

        @overload
        def __init__(
                self, 
                *, 
                config: Optional[JobConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.LogicalResources(_Model):
        cpu: Optional[int]
        custom_resources: Optional[Any]
        gpu: Optional[int]
        memory: Optional[int]
        object_store_memory: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cpu: Optional[int] = ..., 
                custom_resources: Optional[Any] = ..., 
                gpu: Optional[int] = ..., 
                memory: Optional[int] = ..., 
                object_store_memory: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.MarketType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ON_DEMAND = "ON_DEMAND"
        PREFER_SPOT = "PREFER_SPOT"
        SPOT = "SPOT"


    class azure.mgmt.anyscale.models.NodeType(_Model):
        advanced_instance_config: Optional[str]
        flags: Optional[Any]
        instance_type: Optional[str]
        labels: Optional[Any]
        name: str
        required_labels: Optional[Any]
        required_resources: Optional[PhysicalResources]
        resources: Optional[LogicalResources]

        @overload
        def __init__(
                self, 
                *, 
                advanced_instance_config: Optional[str] = ..., 
                flags: Optional[Any] = ..., 
                instance_type: Optional[str] = ..., 
                labels: Optional[Any] = ..., 
                name: str, 
                required_labels: Optional[Any] = ..., 
                required_resources: Optional[PhysicalResources] = ..., 
                resources: Optional[LogicalResources] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.Operation(_Model):
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


    class azure.mgmt.anyscale.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.anyscale.models.OperationStatusResult(_Model):
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


    class azure.mgmt.anyscale.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.anyscale.models.PhysicalResources(_Model):
        accelerator: Optional[str]
        cpu: Optional[int]
        cpu_architecture: Optional[Union[str, CpuArchitecture]]
        gpu: Optional[int]
        memory: Optional[int]
        tpu: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                accelerator: Optional[str] = ..., 
                cpu: Optional[int] = ..., 
                cpu_architecture: Optional[Union[str, CpuArchitecture]] = ..., 
                gpu: Optional[int] = ..., 
                memory: Optional[int] = ..., 
                tpu: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.Project(ProxyResource):
        id: str
        name: str
        properties: Optional[ProjectProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ProjectProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.ProjectProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        url: Optional[str]


    class azure.mgmt.anyscale.models.Provider(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWS = "AWS"
        AZURE = "Azure"
        GCP = "GCP"
        GENERIC = "Generic"


    class azure.mgmt.anyscale.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.anyscale.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.anyscale.models.RayGcsExternalStorageConfig(_Model):
        address: Optional[str]
        certificate_path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                address: Optional[str] = ..., 
                certificate_path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.anyscale.models.RolloutStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IN_PLACE = "InPlace"
        MULTI_VERSION = "MultiVersion"
        ROLLOUT = "Rollout"


    class azure.mgmt.anyscale.models.Service(ProxyResource):
        id: str
        name: str
        properties: Optional[ServiceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ServiceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.ServiceCurrentState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ROLLING_BACK = "RollingBack"
        ROLLING_OUT = "RollingOut"
        RUNNING = "Running"
        STARTING = "Starting"
        SYSTEM_FAILURE = "SystemFailure"
        TERMINATED = "Terminated"
        TERMINATING = "Terminating"
        UNHEALTHY = "Unhealthy"
        UPDATING = "Updating"
        USER_ERROR_FAILURE = "UserErrorFailure"


    class azure.mgmt.anyscale.models.ServiceDeploymentConfig(_Model):
        applications: Optional[list[Any]]
        auto_complete_rollout: Optional[bool]
        canary_percent: Optional[int]
        compute_config: Optional[ComputeConfigSpecOrReference]
        connection_ids: Optional[list[str]]
        description: Optional[str]
        env_vars: Optional[Any]
        grpc_config: Optional[Any]
        http_config: Optional[Any]
        image_uri: Optional[str]
        max_surge_percent: Optional[int]
        max_uptime_timeout_sec: Optional[int]
        ray_gcs_external_storage_config: Optional[RayGcsExternalStorageConfig]
        rollout_strategy: Optional[Union[str, RolloutStrategy]]
        tracing_config: Optional[TracingConfig]
        traffic_percent: Optional[int]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                applications: Optional[list[Any]] = ..., 
                auto_complete_rollout: Optional[bool] = ..., 
                canary_percent: Optional[int] = ..., 
                compute_config: Optional[ComputeConfigSpecOrReference] = ..., 
                connection_ids: Optional[list[str]] = ..., 
                description: Optional[str] = ..., 
                env_vars: Optional[Any] = ..., 
                grpc_config: Optional[Any] = ..., 
                http_config: Optional[Any] = ..., 
                image_uri: Optional[str] = ..., 
                max_surge_percent: Optional[int] = ..., 
                max_uptime_timeout_sec: Optional[int] = ..., 
                ray_gcs_external_storage_config: Optional[RayGcsExternalStorageConfig] = ..., 
                rollout_strategy: Optional[Union[str, RolloutStrategy]] = ..., 
                tracing_config: Optional[TracingConfig] = ..., 
                traffic_percent: Optional[int] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.ServiceProperties(_Model):
        auto_rollout_enabled: Optional[bool]
        base_url: Optional[str]
        canary_version: Optional[ServiceVersionDetail]
        current_state: Optional[Union[str, ServiceCurrentState]]
        deployment_config: Optional[ServiceDeploymentConfig]
        hostname: Optional[str]
        primary_version: Optional[ServiceVersionDetail]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                deployment_config: Optional[ServiceDeploymentConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.ServiceUpdate(_Model):
        properties: Optional[ServiceUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ServiceUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.ServiceUpdateProperties(_Model):
        deployment_config: Optional[ServiceDeploymentConfig]

        @overload
        def __init__(
                self, 
                *, 
                deployment_config: Optional[ServiceDeploymentConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.ServiceVersionDetail(_Model):
        applications: Optional[list[Any]]
        compute_config: ComputeConfigSpecOrReference
        created_at: Optional[datetime]
        current_state: Union[str, ServiceVersionState]
        current_weight: Optional[int]
        image_uri: str
        ray_gcs_external_storage_config: Optional[RayGcsExternalStorageConfig]
        tracing_config: Optional[TracingConfig]
        version: str
        weight: int

        @overload
        def __init__(
                self, 
                *, 
                applications: Optional[list[Any]] = ..., 
                compute_config: ComputeConfigSpecOrReference, 
                created_at: Optional[datetime] = ..., 
                current_state: Union[str, ServiceVersionState], 
                current_weight: Optional[int] = ..., 
                image_uri: str, 
                ray_gcs_external_storage_config: Optional[RayGcsExternalStorageConfig] = ..., 
                tracing_config: Optional[TracingConfig] = ..., 
                version: str, 
                weight: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.ServiceVersionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RUNNING = "Running"
        STARTING = "Starting"
        SYSTEM_FAILURE = "SystemFailure"
        TERMINATED = "Terminated"
        TERMINATING = "Terminating"
        UNHEALTHY = "Unhealthy"
        UNKNOWN = "Unknown"
        UPDATING = "Updating"


    class azure.mgmt.anyscale.models.SystemData(_Model):
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


    class azure.mgmt.anyscale.models.TracingConfig(_Model):
        enabled: Optional[bool]
        exporter_import_path: Optional[str]
        sampling_ratio: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                exporter_import_path: Optional[str] = ..., 
                sampling_ratio: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.TrackedResource(Resource):
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


    class azure.mgmt.anyscale.models.WorkerNode(NodeType):
        advanced_instance_config: str
        flags: any
        instance_type: str
        labels: any
        market_type: Optional[Union[str, MarketType]]
        max_nodes: Optional[int]
        min_nodes: Optional[int]
        name: str
        required_labels: any
        required_resources: PhysicalResources
        resources: LogicalResources

        @overload
        def __init__(
                self, 
                *, 
                advanced_instance_config: Optional[str] = ..., 
                flags: Optional[Any] = ..., 
                instance_type: Optional[str] = ..., 
                labels: Optional[Any] = ..., 
                market_type: Optional[Union[str, MarketType]] = ..., 
                max_nodes: Optional[int] = ..., 
                min_nodes: Optional[int] = ..., 
                name: str, 
                required_labels: Optional[Any] = ..., 
                required_resources: Optional[PhysicalResources] = ..., 
                resources: Optional[LogicalResources] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.Workspace(ProxyResource):
        id: str
        name: str
        properties: Optional[WorkspaceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkspaceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.WorkspaceProperties(_Model):
        compute_config: ComputeConfigSpecOrReference
        current_status: Optional[Union[str, WorkspaceState]]
        idle_termination_minutes: Optional[int]
        image_uri: str
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                compute_config: ComputeConfigSpecOrReference, 
                idle_termination_minutes: Optional[int] = ..., 
                image_uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.WorkspaceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERRORED = "Errored"
        RUNNING = "Running"
        STARTING = "Starting"
        TERMINATED = "Terminated"
        TERMINATING = "Terminating"
        UPDATING = "Updating"


    class azure.mgmt.anyscale.models.WorkspaceUpdate(_Model):
        properties: Optional[WorkspaceUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkspaceUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.anyscale.models.WorkspaceUpdateProperties(_Model):
        compute_config: Optional[ComputeConfigSpecOrReference]
        idle_termination_minutes: Optional[int]
        image_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                compute_config: Optional[ComputeConfigSpecOrReference] = ..., 
                idle_termination_minutes: Optional[int] = ..., 
                image_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.anyscale.operations

    class azure.mgmt.anyscale.operations.AgreementsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                agreement_name: str, 
                resource: Agreement, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agreement: ...

        @overload
        def create_or_update(
                self, 
                agreement_name: str, 
                resource: Agreement, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agreement: ...

        @overload
        def create_or_update(
                self, 
                agreement_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agreement: ...

        @distributed_trace
        def delete(
                self, 
                agreement_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                agreement_name: str, 
                **kwargs: Any
            ) -> Agreement: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Agreement]: ...


    class azure.mgmt.anyscale.operations.CloudResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                cloud_resource_name: str, 
                resource: CloudResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                cloud_resource_name: str, 
                resource: CloudResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                cloud_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                cloud_resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                cloud_resource_name: str, 
                **kwargs: Any
            ) -> CloudResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CloudResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                cloud_resource_name: str, 
                properties: CloudResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CloudResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                cloud_resource_name: str, 
                properties: CloudResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CloudResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                cloud_resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CloudResource: ...


    class azure.mgmt.anyscale.operations.CloudsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                resource: Cloud, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cloud]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                resource: Cloud, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cloud]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cloud]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                **kwargs: Any
            ) -> Cloud: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Cloud]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Cloud]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                properties: CloudUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Cloud: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                properties: CloudUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Cloud: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Cloud: ...


    class azure.mgmt.anyscale.operations.ComputeConfigsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                compute_config_name: str, 
                resource: ComputeConfig, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ComputeConfig]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                compute_config_name: str, 
                resource: ComputeConfig, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ComputeConfig]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                compute_config_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ComputeConfig]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                compute_config_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                compute_config_name: str, 
                **kwargs: Any
            ) -> ComputeConfig: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ComputeConfig]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                compute_config_name: str, 
                properties: ComputeConfigUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComputeConfig: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                compute_config_name: str, 
                properties: ComputeConfigUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComputeConfig: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                compute_config_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ComputeConfig: ...


    class azure.mgmt.anyscale.operations.ContainerImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                container_image_name: str, 
                resource: ContainerImage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ContainerImage]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                container_image_name: str, 
                resource: ContainerImage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ContainerImage]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                container_image_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ContainerImage]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                container_image_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                container_image_name: str, 
                **kwargs: Any
            ) -> ContainerImage: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ContainerImage]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                container_image_name: str, 
                properties: ContainerImageUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerImage: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                container_image_name: str, 
                properties: ContainerImageUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerImage: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                container_image_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerImage: ...


    class azure.mgmt.anyscale.operations.JobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                job_name: str, 
                resource: Job, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Job]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                job_name: str, 
                resource: Job, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Job]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                job_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Job]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> Job: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Job]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                job_name: str, 
                properties: JobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Job: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                job_name: str, 
                properties: JobUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Job: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                job_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Job: ...


    class azure.mgmt.anyscale.operations.OperationStatusesOperations:

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


    class azure.mgmt.anyscale.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.anyscale.operations.ProjectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                resource: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Project]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                resource: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Project]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Project]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Project: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Project]: ...


    class azure.mgmt.anyscale.operations.ServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                service_name: str, 
                resource: Service, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Service]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                service_name: str, 
                resource: Service, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Service]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                service_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Service]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> Service: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Service]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                service_name: str, 
                properties: ServiceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Service: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                service_name: str, 
                properties: ServiceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Service: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                service_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Service: ...


    class azure.mgmt.anyscale.operations.WorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                workspace_name: str, 
                resource: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                workspace_name: str, 
                resource: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                workspace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> Workspace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Workspace]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                workspace_name: str, 
                properties: WorkspaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                workspace_name: str, 
                properties: WorkspaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cloud_name: str, 
                project_name: str, 
                workspace_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...


namespace azure.mgmt.anyscale.types

    class azure.mgmt.anyscale.types.Agreement(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AgreementProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AgreementProperties
        systemData: SystemData
        type: str


    class azure.mgmt.anyscale.types.AgreementProperties(TypedDict, total=False):
        key "agreementLink": str
        key "displayName": str
        key "effectiveDate": str
        key "provisioningState": Union[str, ProvisioningState]
        key "status": Union[str, AgreementStatus]
        agreementLink: str
        displayName: str
        effectiveDate: str
        provisioningState: Union[str, ProvisioningState]
        status: Union[str, AgreementStatus]


    class azure.mgmt.anyscale.types.Cloud(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('CloudProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: CloudProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.anyscale.types.CloudProperties(TypedDict, total=False):
        key "acrResourceId": str
        key "provisioningState": Union[str, ProvisioningState]
        key "ssoUrl": str
        acrResourceId: str
        provisioningState: Union[str, ProvisioningState]
        ssoUrl: str


    class azure.mgmt.anyscale.types.CloudResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('CloudResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: CloudResourceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.anyscale.types.CloudResourceProperties(TypedDict, total=False):
        key "anyscaleOperatorIamIdentity": str
        key "cloudResourceId": str
        key "cloudStorageBucketEndpoint": Required[str]
        key "cloudStorageBucketName": Required[str]
        key "cloudStorageBucketRegion": str
        key "computeStack": Required[Union[str, ComputeStack]]
        key "provider": Required[Union[str, Provider]]
        key "provisioningState": Union[str, ProvisioningState]
        key "region": str
        anyscaleOperatorIamIdentity: str
        cloudResourceId: str
        cloudStorageBucketEndpoint: str
        cloudStorageBucketName: str
        cloudStorageBucketRegion: str
        computeStack: Union[str, ComputeStack]
        provider: Union[str, Provider]
        provisioningState: Union[str, ProvisioningState]
        region: str


    class azure.mgmt.anyscale.types.CloudResourceUpdate(TypedDict, total=False):
        key "properties": ForwardRef('CloudResourceUpdateProperties', module='types')
        properties: CloudResourceUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.anyscale.types.CloudResourceUpdateProperties(TypedDict, total=False):
        key "anyscaleOperatorIamIdentity": str
        key "cloudStorageBucketEndpoint": str
        key "cloudStorageBucketName": str
        key "computeStack": Union[str, ComputeStack]
        key "provider": Union[str, Provider]
        anyscaleOperatorIamIdentity: str
        cloudStorageBucketEndpoint: str
        cloudStorageBucketName: str
        computeStack: Union[str, ComputeStack]
        provider: Union[str, Provider]


    class azure.mgmt.anyscale.types.CloudUpdate(TypedDict, total=False):
        key "properties": ForwardRef('CloudUpdateProperties', module='types')
        properties: CloudUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.anyscale.types.CloudUpdateProperties(TypedDict, total=False):
        key "acrResourceId": str
        acrResourceId: str


    class azure.mgmt.anyscale.types.ComputeConfig(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ComputeConfigProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ComputeConfigProperties
        systemData: SystemData
        type: str


    class azure.mgmt.anyscale.types.ComputeConfigProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "revision": int
        key "spec": Required[ComputeConfigSpec]
        key "url": str
        provisioningState: Union[str, ProvisioningState]
        revision: int
        spec: ComputeConfigSpec
        url: str


    class azure.mgmt.anyscale.types.ComputeConfigSpec(TypedDict, total=False):
        options: list[ComputeConfigSpecOption]


    class azure.mgmt.anyscale.types.ComputeConfigSpecOption(TypedDict, total=False):
        key "advancedInstanceConfig": str
        key "flags": Any
        key "headNode": Required[NodeType]
        advancedInstanceConfig: str
        cloudResourceNames: list[str]
        flags: Any
        headNode: NodeType
        workerNodes: list[WorkerNode]
        zones: list[str]


    class azure.mgmt.anyscale.types.ComputeConfigSpecOrReference(TypedDict, total=False):
        key "computeConfigName": str
        key "spec": ForwardRef('ComputeConfigSpec', module='types')
        computeConfigName: str
        spec: ComputeConfigSpec


    class azure.mgmt.anyscale.types.ComputeConfigUpdate(TypedDict, total=False):
        key "properties": ForwardRef('ComputeConfigUpdateProperties', module='types')
        properties: ComputeConfigUpdateProperties


    class azure.mgmt.anyscale.types.ComputeConfigUpdateProperties(TypedDict, total=False):
        key "spec": ForwardRef('ComputeConfigSpec', module='types')
        spec: ComputeConfigSpec


    class azure.mgmt.anyscale.types.ContainerImage(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ContainerImageProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ContainerImageProperties
        systemData: SystemData
        type: str


    class azure.mgmt.anyscale.types.ContainerImageProperties(TypedDict, total=False):
        key "buildState": Union[str, ContainerImageBuildState]
        key "containerImageUri": str
        key "containerfile": str
        key "provisioningState": Union[str, ProvisioningState]
        key "revision": int
        key "url": str
        buildState: Union[str, ContainerImageBuildState]
        containerImageUri: str
        containerfile: str
        provisioningState: Union[str, ProvisioningState]
        revision: int
        url: str


    class azure.mgmt.anyscale.types.ContainerImageUpdate(TypedDict, total=False):
        key "properties": ForwardRef('ContainerImageUpdateProperties', module='types')
        properties: ContainerImageUpdateProperties


    class azure.mgmt.anyscale.types.ContainerImageUpdateProperties(TypedDict, total=False):
        key "containerImageUri": str
        key "containerfile": str
        containerImageUri: str
        containerfile: str


    class azure.mgmt.anyscale.types.Job(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('JobProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: JobProperties
        systemData: SystemData
        type: str


    class azure.mgmt.anyscale.types.JobConfig(TypedDict, total=False):
        key "computeConfig": ForwardRef('ComputeConfigSpecOrReference', module='types')
        key "entrypoint": str
        key "envVars": Any
        key "imageUri": str
        key "maxRetries": int
        key "timeout": str
        key "workingDir": str
        computeConfig: ComputeConfigSpecOrReference
        entrypoint: str
        envVars: Any
        imageUri: str
        maxRetries: int
        pipRequirements: list[str]
        pyModules: list[str]
        timeout: str
        workingDir: str


    class azure.mgmt.anyscale.types.JobProperties(TypedDict, total=False):
        key "config": Required[JobConfig]
        key "provisioningState": Union[str, ProvisioningState]
        key "state": Union[str, JobState]
        key "url": str
        config: JobConfig
        provisioningState: Union[str, ProvisioningState]
        state: Union[str, JobState]
        url: str


    class azure.mgmt.anyscale.types.JobUpdate(TypedDict, total=False):
        key "properties": ForwardRef('JobUpdateProperties', module='types')
        properties: JobUpdateProperties


    class azure.mgmt.anyscale.types.JobUpdateProperties(TypedDict, total=False):
        key "config": ForwardRef('JobConfig', module='types')
        config: JobConfig


    class azure.mgmt.anyscale.types.LogicalResources(TypedDict, total=False):
        key "cpu": int
        key "customResources": Any
        key "gpu": int
        key "memory": int
        key "objectStoreMemory": int
        cpu: int
        customResources: Any
        gpu: int
        memory: int
        objectStoreMemory: int


    class azure.mgmt.anyscale.types.NodeType(TypedDict, total=False):
        key "advancedInstanceConfig": str
        key "flags": Any
        key "instanceType": str
        key "labels": Any
        key "name": Required[str]
        key "requiredLabels": Any
        key "requiredResources": ForwardRef('PhysicalResources', module='types')
        key "resources": ForwardRef('LogicalResources', module='types')
        advancedInstanceConfig: str
        flags: Any
        instanceType: str
        labels: Any
        name: str
        requiredLabels: Any
        requiredResources: PhysicalResources
        resources: LogicalResources


    class azure.mgmt.anyscale.types.PhysicalResources(TypedDict, total=False):
        key "accelerator": str
        key "cpu": int
        key "cpuArchitecture": Union[str, CpuArchitecture]
        key "gpu": int
        key "memory": int
        key "tpu": int
        accelerator: str
        cpu: int
        cpuArchitecture: Union[str, CpuArchitecture]
        gpu: int
        memory: int
        tpu: int


    class azure.mgmt.anyscale.types.Project(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ProjectProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ProjectProperties
        systemData: SystemData
        type: str


    class azure.mgmt.anyscale.types.ProjectProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "url": str
        provisioningState: Union[str, ProvisioningState]
        url: str


    class azure.mgmt.anyscale.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.anyscale.types.RayGcsExternalStorageConfig(TypedDict, total=False):
        key "address": str
        key "certificatePath": str
        address: str
        certificatePath: str


    class azure.mgmt.anyscale.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.anyscale.types.Service(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ServiceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ServiceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.anyscale.types.ServiceDeploymentConfig(TypedDict, total=False):
        key "autoCompleteRollout": bool
        key "canaryPercent": int
        key "computeConfig": ForwardRef('ComputeConfigSpecOrReference', module='types')
        key "description": str
        key "envVars": Any
        key "grpcConfig": Any
        key "httpConfig": Any
        key "imageUri": str
        key "maxSurgePercent": int
        key "maxUptimeTimeoutSec": int
        key "rayGcsExternalStorageConfig": ForwardRef('RayGcsExternalStorageConfig', module='types')
        key "rolloutStrategy": Union[str, RolloutStrategy]
        key "tracingConfig": ForwardRef('TracingConfig', module='types')
        key "trafficPercent": int
        key "version": str
        applications: list[Any]
        autoCompleteRollout: bool
        canaryPercent: int
        computeConfig: ComputeConfigSpecOrReference
        connectionIds: list[str]
        description: str
        envVars: Any
        grpcConfig: Any
        httpConfig: Any
        imageUri: str
        maxSurgePercent: int
        maxUptimeTimeoutSec: int
        rayGcsExternalStorageConfig: RayGcsExternalStorageConfig
        rolloutStrategy: Union[str, RolloutStrategy]
        tracingConfig: TracingConfig
        trafficPercent: int
        version: str


    class azure.mgmt.anyscale.types.ServiceProperties(TypedDict, total=False):
        key "autoRolloutEnabled": bool
        key "baseUrl": str
        key "canaryVersion": ForwardRef('ServiceVersionDetail', module='types')
        key "currentState": Union[str, ServiceCurrentState]
        key "deploymentConfig": ForwardRef('ServiceDeploymentConfig', module='types')
        key "hostname": str
        key "primaryVersion": ForwardRef('ServiceVersionDetail', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "url": str
        autoRolloutEnabled: bool
        baseUrl: str
        canaryVersion: ServiceVersionDetail
        currentState: Union[str, ServiceCurrentState]
        deploymentConfig: ServiceDeploymentConfig
        hostname: str
        primaryVersion: ServiceVersionDetail
        provisioningState: Union[str, ProvisioningState]
        url: str


    class azure.mgmt.anyscale.types.ServiceUpdate(TypedDict, total=False):
        key "properties": ForwardRef('ServiceUpdateProperties', module='types')
        properties: ServiceUpdateProperties


    class azure.mgmt.anyscale.types.ServiceUpdateProperties(TypedDict, total=False):
        key "deploymentConfig": ForwardRef('ServiceDeploymentConfig', module='types')
        deploymentConfig: ServiceDeploymentConfig


    class azure.mgmt.anyscale.types.ServiceVersionDetail(TypedDict, total=False):
        key "computeConfig": Required[ComputeConfigSpecOrReference]
        key "createdAt": str
        key "currentState": Required[Union[str, ServiceVersionState]]
        key "currentWeight": int
        key "imageUri": Required[str]
        key "rayGcsExternalStorageConfig": ForwardRef('RayGcsExternalStorageConfig', module='types')
        key "tracingConfig": ForwardRef('TracingConfig', module='types')
        key "version": Required[str]
        key "weight": Required[int]
        applications: list[Any]
        computeConfig: ComputeConfigSpecOrReference
        createdAt: str
        currentState: Union[str, ServiceVersionState]
        currentWeight: int
        imageUri: str
        rayGcsExternalStorageConfig: RayGcsExternalStorageConfig
        tracingConfig: TracingConfig
        version: str
        weight: int


    class azure.mgmt.anyscale.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.anyscale.types.TracingConfig(TypedDict, total=False):
        key "enabled": bool
        key "exporterImportPath": str
        key "samplingRatio": float
        enabled: bool
        exporterImportPath: str
        samplingRatio: float


    class azure.mgmt.anyscale.types.TrackedResource(Resource):
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


    class azure.mgmt.anyscale.types.WorkerNode(NodeType):
        key "advancedInstanceConfig": str
        key "flags": Any
        key "instanceType": str
        key "labels": Any
        key "marketType": Union[str, MarketType]
        key "maxNodes": int
        key "minNodes": int
        key "name": Required[str]
        key "requiredLabels": Any
        key "requiredResources": ForwardRef('PhysicalResources', module='types')
        key "resources": ForwardRef('LogicalResources', module='types')
        advancedInstanceConfig: str
        flags: Any
        instanceType: str
        labels: Any
        marketType: Union[str, MarketType]
        maxNodes: int
        minNodes: int
        name: str
        requiredLabels: Any
        requiredResources: PhysicalResources
        resources: LogicalResources


    class azure.mgmt.anyscale.types.Workspace(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('WorkspaceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: WorkspaceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.anyscale.types.WorkspaceProperties(TypedDict, total=False):
        key "computeConfig": Required[ComputeConfigSpecOrReference]
        key "currentStatus": Union[str, WorkspaceState]
        key "idleTerminationMinutes": int
        key "imageUri": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        computeConfig: ComputeConfigSpecOrReference
        currentStatus: Union[str, WorkspaceState]
        idleTerminationMinutes: int
        imageUri: str
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.anyscale.types.WorkspaceUpdate(TypedDict, total=False):
        key "properties": ForwardRef('WorkspaceUpdateProperties', module='types')
        properties: WorkspaceUpdateProperties


    class azure.mgmt.anyscale.types.WorkspaceUpdateProperties(TypedDict, total=False):
        key "computeConfig": ForwardRef('ComputeConfigSpecOrReference', module='types')
        key "idleTerminationMinutes": int
        key "imageUri": str
        computeConfig: ComputeConfigSpecOrReference
        idleTerminationMinutes: int
        imageUri: str


```