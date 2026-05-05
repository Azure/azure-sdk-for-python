```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.containerregistrytasks

    class azure.mgmt.containerregistrytasks.ContainerRegistryTasksMgmtClient: implements ContextManager 
        agent_pools: AgentPoolsOperations
        registries: RegistriesOperations
        runs: RunsOperations
        task_runs: TaskRunsOperations
        tasks: TasksOperations

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


namespace azure.mgmt.containerregistrytasks.aio

    class azure.mgmt.containerregistrytasks.aio.ContainerRegistryTasksMgmtClient: implements AsyncContextManager 
        agent_pools: AgentPoolsOperations
        registries: RegistriesOperations
        runs: RunsOperations
        task_runs: TaskRunsOperations
        tasks: TasksOperations

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


namespace azure.mgmt.containerregistrytasks.aio.operations

    class azure.mgmt.containerregistrytasks.aio.operations.AgentPoolsOperations:

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
                agent_pool_name: str, 
                agent_pool: AgentPool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentPool]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                agent_pool_name: str, 
                agent_pool: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentPool]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                agent_pool_name: str, 
                agent_pool: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentPool]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                agent_pool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                agent_pool_name: str, 
                update_parameters: AgentPoolUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentPool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                agent_pool_name: str, 
                update_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentPool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                agent_pool_name: str, 
                update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentPool]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                agent_pool_name: str, 
                **kwargs: Any
            ) -> AgentPool: ...

        @distributed_trace_async
        async def get_queue_status(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                agent_pool_name: str, 
                **kwargs: Any
            ) -> AgentPoolQueueStatus: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AgentPool]: ...


    class azure.mgmt.containerregistrytasks.aio.operations.RegistriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_build_source_upload_url(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> SourceUploadDefinition: ...

        @overload
        async def schedule_run(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                run_request: RunRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Run: ...

        @overload
        async def schedule_run(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                run_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Run: ...

        @overload
        async def schedule_run(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                run_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Run: ...


    class azure.mgmt.containerregistrytasks.aio.operations.RunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def cancel(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                run_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                run_id: str, 
                **kwargs: Any
            ) -> Run: ...

        @distributed_trace_async
        async def get_log_sas_url(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                run_id: str, 
                **kwargs: Any
            ) -> RunGetLogResult: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Run]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                run_id: str, 
                run_update_parameters: RunUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Run: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                run_id: str, 
                run_update_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Run: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                run_id: str, 
                run_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Run: ...


    class azure.mgmt.containerregistrytasks.aio.operations.TaskRunsOperations:

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
                task_run_name: str, 
                task_run: TaskRun, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TaskRun]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_run_name: str, 
                task_run: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TaskRun]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_run_name: str, 
                task_run: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TaskRun]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_run_name: str, 
                update_parameters: TaskRunUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TaskRun]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_run_name: str, 
                update_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TaskRun]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_run_name: str, 
                update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TaskRun]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_run_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_run_name: str, 
                **kwargs: Any
            ) -> TaskRun: ...

        @distributed_trace_async
        async def get_details(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_run_name: str, 
                **kwargs: Any
            ) -> TaskRun: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TaskRun]: ...


    class azure.mgmt.containerregistrytasks.aio.operations.TasksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_name: str, 
                task_create_parameters: Task, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_name: str, 
                task_create_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_name: str, 
                task_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_name: str, 
                **kwargs: Any
            ) -> Task: ...

        @distributed_trace_async
        async def get_details(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_name: str, 
                **kwargs: Any
            ) -> Task: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Task]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_name: str, 
                task_update_parameters: TaskUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_name: str, 
                task_update_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_name: str, 
                task_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...


namespace azure.mgmt.containerregistrytasks.models

    class azure.mgmt.containerregistrytasks.models.AgentPool(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[AgentPoolProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[AgentPoolProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistrytasks.models.AgentPoolProperties(_Model):
        count: Optional[int]
        os: Optional[Union[str, _models.OS]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        tier: Optional[str]
        virtual_network_subnet_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                os: Optional[Union[str, _models.OS]] = ..., 
                tier: Optional[str] = ..., 
                virtual_network_subnet_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.AgentPoolPropertiesUpdateParameters(_Model):
        count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.AgentPoolQueueStatus(_Model):
        count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.AgentPoolUpdateParameters(_Model):
        properties: Optional[AgentPoolPropertiesUpdateParameters]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AgentPoolPropertiesUpdateParameters] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistrytasks.models.AgentProperties(_Model):
        cpu: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cpu: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.Architecture(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AMD64 = "amd64"
        ARM = "arm"
        ARM64 = "arm64"
        THREE_HUNDRED_EIGHTY_SIX = "386"
        X86 = "x86"


    class azure.mgmt.containerregistrytasks.models.Argument(_Model):
        is_secret: Optional[bool]
        name: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                is_secret: Optional[bool] = ..., 
                name: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.AuthInfo(_Model):
        expires_in: Optional[int]
        refresh_token: Optional[str]
        scope: Optional[str]
        token: str
        token_type: Union[str, TokenType]

        @overload
        def __init__(
                self, 
                *, 
                expires_in: Optional[int] = ..., 
                refresh_token: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                token: str, 
                token_type: Union[str, TokenType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.AuthInfoUpdateParameters(_Model):
        expires_in: Optional[int]
        refresh_token: Optional[str]
        scope: Optional[str]
        token: Optional[str]
        token_type: Optional[Union[str, TokenType]]

        @overload
        def __init__(
                self, 
                *, 
                expires_in: Optional[int] = ..., 
                refresh_token: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                token: Optional[str] = ..., 
                token_type: Optional[Union[str, TokenType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.BaseImageDependency(_Model):
        digest: Optional[str]
        registry: Optional[str]
        repository: Optional[str]
        tag: Optional[str]
        type: Optional[Union[str, BaseImageDependencyType]]

        @overload
        def __init__(
                self, 
                *, 
                digest: Optional[str] = ..., 
                registry: Optional[str] = ..., 
                repository: Optional[str] = ..., 
                tag: Optional[str] = ..., 
                type: Optional[Union[str, BaseImageDependencyType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.BaseImageDependencyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILD_TIME = "BuildTime"
        RUN_TIME = "RunTime"


    class azure.mgmt.containerregistrytasks.models.BaseImageTrigger(_Model):
        base_image_trigger_type: Union[str, BaseImageTriggerType]
        name: str
        status: Optional[Union[str, TriggerStatus]]
        update_trigger_endpoint: Optional[str]
        update_trigger_payload_type: Optional[Union[str, UpdateTriggerPayloadType]]

        @overload
        def __init__(
                self, 
                *, 
                base_image_trigger_type: Union[str, BaseImageTriggerType], 
                name: str, 
                status: Optional[Union[str, TriggerStatus]] = ..., 
                update_trigger_endpoint: Optional[str] = ..., 
                update_trigger_payload_type: Optional[Union[str, UpdateTriggerPayloadType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.BaseImageTriggerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        RUNTIME = "Runtime"


    class azure.mgmt.containerregistrytasks.models.BaseImageTriggerUpdateParameters(_Model):
        base_image_trigger_type: Optional[Union[str, BaseImageTriggerType]]
        name: str
        status: Optional[Union[str, TriggerStatus]]
        update_trigger_endpoint: Optional[str]
        update_trigger_payload_type: Optional[Union[str, UpdateTriggerPayloadType]]

        @overload
        def __init__(
                self, 
                *, 
                base_image_trigger_type: Optional[Union[str, BaseImageTriggerType]] = ..., 
                name: str, 
                status: Optional[Union[str, TriggerStatus]] = ..., 
                update_trigger_endpoint: Optional[str] = ..., 
                update_trigger_payload_type: Optional[Union[str, UpdateTriggerPayloadType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.containerregistrytasks.models.Credentials(_Model):
        custom_registries: Optional[dict[str, CustomRegistryCredentials]]
        source_registry: Optional[SourceRegistryCredentials]

        @overload
        def __init__(
                self, 
                *, 
                custom_registries: Optional[dict[str, CustomRegistryCredentials]] = ..., 
                source_registry: Optional[SourceRegistryCredentials] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.CustomRegistryCredentials(_Model):
        identity: Optional[str]
        password: Optional[SecretObject]
        user_name: Optional[SecretObject]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[str] = ..., 
                password: Optional[SecretObject] = ..., 
                user_name: Optional[SecretObject] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.DockerBuildRequest(RunRequest, discriminator='DockerBuildRequest'):
        agent_configuration: Optional[AgentProperties]
        agent_pool_name: str
        arguments: Optional[list[Argument]]
        credentials: Optional[Credentials]
        docker_file_path: str
        image_names: Optional[list[str]]
        is_archive_enabled: bool
        is_push_enabled: Optional[bool]
        log_template: str
        no_cache: Optional[bool]
        platform: PlatformProperties
        source_location: Optional[str]
        target: Optional[str]
        timeout: Optional[int]
        type: Literal["DockerBuildRequest"]

        @overload
        def __init__(
                self, 
                *, 
                agent_configuration: Optional[AgentProperties] = ..., 
                agent_pool_name: Optional[str] = ..., 
                arguments: Optional[list[Argument]] = ..., 
                credentials: Optional[Credentials] = ..., 
                docker_file_path: str, 
                image_names: Optional[list[str]] = ..., 
                is_archive_enabled: Optional[bool] = ..., 
                is_push_enabled: Optional[bool] = ..., 
                log_template: Optional[str] = ..., 
                no_cache: Optional[bool] = ..., 
                platform: PlatformProperties, 
                source_location: Optional[str] = ..., 
                target: Optional[str] = ..., 
                timeout: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.DockerBuildStep(TaskStepProperties, discriminator='Docker'):
        arguments: Optional[list[Argument]]
        base_image_dependencies: list[BaseImageDependency]
        context_access_token: str
        context_path: str
        docker_file_path: str
        image_names: Optional[list[str]]
        is_push_enabled: Optional[bool]
        no_cache: Optional[bool]
        target: Optional[str]
        type: Literal[StepType.DOCKER]

        @overload
        def __init__(
                self, 
                *, 
                arguments: Optional[list[Argument]] = ..., 
                context_access_token: Optional[str] = ..., 
                context_path: Optional[str] = ..., 
                docker_file_path: str, 
                image_names: Optional[list[str]] = ..., 
                is_push_enabled: Optional[bool] = ..., 
                no_cache: Optional[bool] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.DockerBuildStepUpdateParameters(TaskStepUpdateParameters, discriminator='Docker'):
        arguments: Optional[list[Argument]]
        context_access_token: str
        context_path: str
        docker_file_path: Optional[str]
        image_names: Optional[list[str]]
        is_push_enabled: Optional[bool]
        no_cache: Optional[bool]
        target: Optional[str]
        type: Literal[StepType.DOCKER]

        @overload
        def __init__(
                self, 
                *, 
                arguments: Optional[list[Argument]] = ..., 
                context_access_token: Optional[str] = ..., 
                context_path: Optional[str] = ..., 
                docker_file_path: Optional[str] = ..., 
                image_names: Optional[list[str]] = ..., 
                is_push_enabled: Optional[bool] = ..., 
                no_cache: Optional[bool] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.EncodedTaskRunRequest(RunRequest, discriminator='EncodedTaskRunRequest'):
        agent_configuration: Optional[AgentProperties]
        agent_pool_name: str
        credentials: Optional[Credentials]
        encoded_task_content: str
        encoded_values_content: Optional[str]
        is_archive_enabled: bool
        log_template: str
        platform: PlatformProperties
        source_location: Optional[str]
        timeout: Optional[int]
        type: Literal["EncodedTaskRunRequest"]
        values_property: Optional[list[SetValue]]

        @overload
        def __init__(
                self, 
                *, 
                agent_configuration: Optional[AgentProperties] = ..., 
                agent_pool_name: Optional[str] = ..., 
                credentials: Optional[Credentials] = ..., 
                encoded_task_content: str, 
                encoded_values_content: Optional[str] = ..., 
                is_archive_enabled: Optional[bool] = ..., 
                log_template: Optional[str] = ..., 
                platform: PlatformProperties, 
                source_location: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                values_property: Optional[list[SetValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.EncodedTaskStep(TaskStepProperties, discriminator='EncodedTask'):
        base_image_dependencies: list[BaseImageDependency]
        context_access_token: str
        context_path: str
        encoded_task_content: str
        encoded_values_content: Optional[str]
        type: Literal[StepType.ENCODED_TASK]
        values_property: Optional[list[SetValue]]

        @overload
        def __init__(
                self, 
                *, 
                context_access_token: Optional[str] = ..., 
                context_path: Optional[str] = ..., 
                encoded_task_content: str, 
                encoded_values_content: Optional[str] = ..., 
                values_property: Optional[list[SetValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.EncodedTaskStepUpdateParameters(TaskStepUpdateParameters, discriminator='EncodedTask'):
        context_access_token: str
        context_path: str
        encoded_task_content: Optional[str]
        encoded_values_content: Optional[str]
        type: Literal[StepType.ENCODED_TASK]
        values_property: Optional[list[SetValue]]

        @overload
        def __init__(
                self, 
                *, 
                context_access_token: Optional[str] = ..., 
                context_path: Optional[str] = ..., 
                encoded_task_content: Optional[str] = ..., 
                encoded_values_content: Optional[str] = ..., 
                values_property: Optional[list[SetValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.containerregistrytasks.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.containerregistrytasks.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.FileTaskRunRequest(RunRequest, discriminator='FileTaskRunRequest'):
        agent_configuration: Optional[AgentProperties]
        agent_pool_name: str
        credentials: Optional[Credentials]
        is_archive_enabled: bool
        log_template: str
        platform: PlatformProperties
        source_location: Optional[str]
        task_file_path: str
        timeout: Optional[int]
        type: Literal["FileTaskRunRequest"]
        values_file_path: Optional[str]
        values_property: Optional[list[SetValue]]

        @overload
        def __init__(
                self, 
                *, 
                agent_configuration: Optional[AgentProperties] = ..., 
                agent_pool_name: Optional[str] = ..., 
                credentials: Optional[Credentials] = ..., 
                is_archive_enabled: Optional[bool] = ..., 
                log_template: Optional[str] = ..., 
                platform: PlatformProperties, 
                source_location: Optional[str] = ..., 
                task_file_path: str, 
                timeout: Optional[int] = ..., 
                values_file_path: Optional[str] = ..., 
                values_property: Optional[list[SetValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.FileTaskStep(TaskStepProperties, discriminator='FileTask'):
        base_image_dependencies: list[BaseImageDependency]
        context_access_token: str
        context_path: str
        task_file_path: str
        type: Literal[StepType.FILE_TASK]
        values_file_path: Optional[str]
        values_property: Optional[list[SetValue]]

        @overload
        def __init__(
                self, 
                *, 
                context_access_token: Optional[str] = ..., 
                context_path: Optional[str] = ..., 
                task_file_path: str, 
                values_file_path: Optional[str] = ..., 
                values_property: Optional[list[SetValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.FileTaskStepUpdateParameters(TaskStepUpdateParameters, discriminator='FileTask'):
        context_access_token: str
        context_path: str
        task_file_path: Optional[str]
        type: Literal[StepType.FILE_TASK]
        values_file_path: Optional[str]
        values_property: Optional[list[SetValue]]

        @overload
        def __init__(
                self, 
                *, 
                context_access_token: Optional[str] = ..., 
                context_path: Optional[str] = ..., 
                task_file_path: Optional[str] = ..., 
                values_file_path: Optional[str] = ..., 
                values_property: Optional[list[SetValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.IdentityProperties(_Model):
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


    class azure.mgmt.containerregistrytasks.models.ImageDescriptor(_Model):
        digest: Optional[str]
        registry: Optional[str]
        repository: Optional[str]
        tag: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                digest: Optional[str] = ..., 
                registry: Optional[str] = ..., 
                repository: Optional[str] = ..., 
                tag: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.ImageUpdateTrigger(_Model):
        id: Optional[str]
        images: Optional[list[ImageDescriptor]]
        timestamp: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                images: Optional[list[ImageDescriptor]] = ..., 
                timestamp: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.OS(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.containerregistrytasks.models.OverrideTaskStepProperties(_Model):
        arguments: Optional[list[Argument]]
        context_path: Optional[str]
        file: Optional[str]
        target: Optional[str]
        update_trigger_token: Optional[str]
        values_property: Optional[list[SetValue]]

        @overload
        def __init__(
                self, 
                *, 
                arguments: Optional[list[Argument]] = ..., 
                context_path: Optional[str] = ..., 
                file: Optional[str] = ..., 
                target: Optional[str] = ..., 
                update_trigger_token: Optional[str] = ..., 
                values_property: Optional[list[SetValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.PlatformProperties(_Model):
        architecture: Optional[Union[str, Architecture]]
        os: Union[str, _models.OS]
        variant: Optional[Union[str, Variant]]

        @overload
        def __init__(
                self, 
                *, 
                architecture: Optional[Union[str, Architecture]] = ..., 
                os: Union[str, _models.OS], 
                variant: Optional[Union[str, Variant]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.PlatformUpdateParameters(_Model):
        architecture: Optional[Union[str, Architecture]]
        os: Optional[Union[str, _models.OS]]
        variant: Optional[Union[str, Variant]]

        @overload
        def __init__(
                self, 
                *, 
                architecture: Optional[Union[str, Architecture]] = ..., 
                os: Optional[Union[str, _models.OS]] = ..., 
                variant: Optional[Union[str, Variant]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.containerregistrytasks.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.containerregistrytasks.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.containerregistrytasks.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.containerregistrytasks.models.Run(ProxyResource):
        id: str
        name: str
        properties: Optional[RunProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RunProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistrytasks.models.RunGetLogResult(_Model):
        log_artifact_link: Optional[str]
        log_link: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                log_artifact_link: Optional[str] = ..., 
                log_link: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.RunProperties(_Model):
        agent_configuration: Optional[AgentProperties]
        agent_pool_name: Optional[str]
        create_time: Optional[datetime]
        custom_registries: Optional[list[str]]
        finish_time: Optional[datetime]
        image_update_trigger: Optional[ImageUpdateTrigger]
        is_archive_enabled: Optional[bool]
        last_updated_time: Optional[datetime]
        log_artifact: Optional[ImageDescriptor]
        output_images: Optional[list[ImageDescriptor]]
        platform: Optional[PlatformProperties]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        run_error_message: Optional[str]
        run_id: Optional[str]
        run_type: Optional[Union[str, RunType]]
        source_registry_auth: Optional[str]
        source_trigger: Optional[SourceTriggerDescriptor]
        start_time: Optional[datetime]
        status: Optional[Union[str, RunStatus]]
        task: Optional[str]
        timer_trigger: Optional[TimerTriggerDescriptor]
        update_trigger_token: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_configuration: Optional[AgentProperties] = ..., 
                agent_pool_name: Optional[str] = ..., 
                create_time: Optional[datetime] = ..., 
                custom_registries: Optional[list[str]] = ..., 
                finish_time: Optional[datetime] = ..., 
                image_update_trigger: Optional[ImageUpdateTrigger] = ..., 
                is_archive_enabled: Optional[bool] = ..., 
                last_updated_time: Optional[datetime] = ..., 
                output_images: Optional[list[ImageDescriptor]] = ..., 
                platform: Optional[PlatformProperties] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                run_id: Optional[str] = ..., 
                run_type: Optional[Union[str, RunType]] = ..., 
                source_registry_auth: Optional[str] = ..., 
                source_trigger: Optional[SourceTriggerDescriptor] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[Union[str, RunStatus]] = ..., 
                task: Optional[str] = ..., 
                timer_trigger: Optional[TimerTriggerDescriptor] = ..., 
                update_trigger_token: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.RunRequest(_Model):
        agent_pool_name: Optional[str]
        is_archive_enabled: Optional[bool]
        log_template: Optional[str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                agent_pool_name: Optional[str] = ..., 
                is_archive_enabled: Optional[bool] = ..., 
                log_template: Optional[str] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.RunStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        ERROR = "Error"
        FAILED = "Failed"
        QUEUED = "Queued"
        RUNNING = "Running"
        STARTED = "Started"
        SUCCEEDED = "Succeeded"
        TIMEOUT = "Timeout"


    class azure.mgmt.containerregistrytasks.models.RunType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_BUILD = "AutoBuild"
        AUTO_RUN = "AutoRun"
        QUICK_BUILD = "QuickBuild"
        QUICK_RUN = "QuickRun"


    class azure.mgmt.containerregistrytasks.models.RunUpdateParameters(_Model):
        is_archive_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                is_archive_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.SecretObject(_Model):
        type: Optional[Union[str, SecretObjectType]]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, SecretObjectType]] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.SecretObjectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OPAQUE = "Opaque"
        VAULTSECRET = "Vaultsecret"


    class azure.mgmt.containerregistrytasks.models.SetValue(_Model):
        is_secret: Optional[bool]
        name: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                is_secret: Optional[bool] = ..., 
                name: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.SourceControlType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GITHUB = "Github"
        VISUAL_STUDIO_TEAM_SERVICE = "VisualStudioTeamService"


    class azure.mgmt.containerregistrytasks.models.SourceProperties(_Model):
        branch: Optional[str]
        repository_url: str
        source_control_auth_properties: Optional[AuthInfo]
        source_control_type: Union[str, SourceControlType]

        @overload
        def __init__(
                self, 
                *, 
                branch: Optional[str] = ..., 
                repository_url: str, 
                source_control_auth_properties: Optional[AuthInfo] = ..., 
                source_control_type: Union[str, SourceControlType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.SourceRegistryCredentials(_Model):
        identity: Optional[str]
        login_mode: Optional[Union[str, SourceRegistryLoginMode]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[str] = ..., 
                login_mode: Optional[Union[str, SourceRegistryLoginMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.SourceRegistryLoginMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        NONE = "None"


    class azure.mgmt.containerregistrytasks.models.SourceTrigger(_Model):
        name: str
        source_repository: SourceProperties
        source_trigger_events: list[Union[str, SourceTriggerEvent]]
        status: Optional[Union[str, TriggerStatus]]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                source_repository: SourceProperties, 
                source_trigger_events: list[Union[str, SourceTriggerEvent]], 
                status: Optional[Union[str, TriggerStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.SourceTriggerDescriptor(_Model):
        branch_name: Optional[str]
        commit_id: Optional[str]
        event_type: Optional[str]
        id: Optional[str]
        provider_type: Optional[str]
        pull_request_id: Optional[str]
        repository_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                branch_name: Optional[str] = ..., 
                commit_id: Optional[str] = ..., 
                event_type: Optional[str] = ..., 
                id: Optional[str] = ..., 
                provider_type: Optional[str] = ..., 
                pull_request_id: Optional[str] = ..., 
                repository_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.SourceTriggerEvent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMMIT = "commit"
        PULLREQUEST = "pullrequest"


    class azure.mgmt.containerregistrytasks.models.SourceTriggerUpdateParameters(_Model):
        name: str
        source_repository: Optional[SourceUpdateParameters]
        source_trigger_events: Optional[list[Union[str, SourceTriggerEvent]]]
        status: Optional[Union[str, TriggerStatus]]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                source_repository: Optional[SourceUpdateParameters] = ..., 
                source_trigger_events: Optional[list[Union[str, SourceTriggerEvent]]] = ..., 
                status: Optional[Union[str, TriggerStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.SourceUpdateParameters(_Model):
        branch: Optional[str]
        repository_url: Optional[str]
        source_control_auth_properties: Optional[AuthInfoUpdateParameters]
        source_control_type: Optional[Union[str, SourceControlType]]

        @overload
        def __init__(
                self, 
                *, 
                branch: Optional[str] = ..., 
                repository_url: Optional[str] = ..., 
                source_control_auth_properties: Optional[AuthInfoUpdateParameters] = ..., 
                source_control_type: Optional[Union[str, SourceControlType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.SourceUploadDefinition(_Model):
        relative_path: Optional[str]
        upload_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                relative_path: Optional[str] = ..., 
                upload_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.StepType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOCKER = "Docker"
        ENCODED_TASK = "EncodedTask"
        FILE_TASK = "FileTask"


    class azure.mgmt.containerregistrytasks.models.SystemData(_Model):
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


    class azure.mgmt.containerregistrytasks.models.Task(TrackedResource):
        id: str
        identity: Optional[IdentityProperties]
        location: str
        name: str
        properties: Optional[TaskProperties]
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
                properties: Optional[TaskProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistrytasks.models.TaskProperties(_Model):
        agent_configuration: Optional[AgentProperties]
        agent_pool_name: Optional[str]
        creation_date: Optional[datetime]
        credentials: Optional[Credentials]
        is_system_task: Optional[bool]
        log_template: Optional[str]
        platform: Optional[PlatformProperties]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: Optional[Union[str, TaskStatus]]
        step: Optional[TaskStepProperties]
        timeout: Optional[int]
        trigger: Optional[TriggerProperties]

        @overload
        def __init__(
                self, 
                *, 
                agent_configuration: Optional[AgentProperties] = ..., 
                agent_pool_name: Optional[str] = ..., 
                credentials: Optional[Credentials] = ..., 
                is_system_task: Optional[bool] = ..., 
                log_template: Optional[str] = ..., 
                platform: Optional[PlatformProperties] = ..., 
                status: Optional[Union[str, TaskStatus]] = ..., 
                step: Optional[TaskStepProperties] = ..., 
                timeout: Optional[int] = ..., 
                trigger: Optional[TriggerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.TaskPropertiesUpdateParameters(_Model):
        agent_configuration: Optional[AgentProperties]
        agent_pool_name: Optional[str]
        credentials: Optional[Credentials]
        log_template: Optional[str]
        platform: Optional[PlatformUpdateParameters]
        status: Optional[Union[str, TaskStatus]]
        step: Optional[TaskStepUpdateParameters]
        timeout: Optional[int]
        trigger: Optional[TriggerUpdateParameters]

        @overload
        def __init__(
                self, 
                *, 
                agent_configuration: Optional[AgentProperties] = ..., 
                agent_pool_name: Optional[str] = ..., 
                credentials: Optional[Credentials] = ..., 
                log_template: Optional[str] = ..., 
                platform: Optional[PlatformUpdateParameters] = ..., 
                status: Optional[Union[str, TaskStatus]] = ..., 
                step: Optional[TaskStepUpdateParameters] = ..., 
                timeout: Optional[int] = ..., 
                trigger: Optional[TriggerUpdateParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.TaskRun(ProxyResource):
        id: str
        identity: Optional[IdentityProperties]
        location: Optional[str]
        name: str
        properties: Optional[TaskRunProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityProperties] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[TaskRunProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistrytasks.models.TaskRunProperties(_Model):
        force_update_tag: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        run_request: Optional[RunRequest]
        run_result: Optional[Run]

        @overload
        def __init__(
                self, 
                *, 
                force_update_tag: Optional[str] = ..., 
                run_request: Optional[RunRequest] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.TaskRunPropertiesUpdateParameters(_Model):
        force_update_tag: Optional[str]
        run_request: Optional[RunRequest]

        @overload
        def __init__(
                self, 
                *, 
                force_update_tag: Optional[str] = ..., 
                run_request: Optional[RunRequest] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.TaskRunRequest(RunRequest, discriminator='TaskRunRequest'):
        agent_pool_name: str
        is_archive_enabled: bool
        log_template: str
        override_task_step_properties: Optional[OverrideTaskStepProperties]
        task_id: str
        type: Literal["TaskRunRequest"]

        @overload
        def __init__(
                self, 
                *, 
                agent_pool_name: Optional[str] = ..., 
                is_archive_enabled: Optional[bool] = ..., 
                log_template: Optional[str] = ..., 
                override_task_step_properties: Optional[OverrideTaskStepProperties] = ..., 
                task_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.TaskRunUpdateParameters(_Model):
        identity: Optional[IdentityProperties]
        location: Optional[str]
        properties: Optional[TaskRunPropertiesUpdateParameters]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityProperties] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[TaskRunPropertiesUpdateParameters] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistrytasks.models.TaskStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.containerregistrytasks.models.TaskStepProperties(_Model):
        base_image_dependencies: Optional[list[BaseImageDependency]]
        context_access_token: Optional[str]
        context_path: Optional[str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                context_access_token: Optional[str] = ..., 
                context_path: Optional[str] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.TaskStepUpdateParameters(_Model):
        context_access_token: Optional[str]
        context_path: Optional[str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                context_access_token: Optional[str] = ..., 
                context_path: Optional[str] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.TaskUpdateParameters(_Model):
        identity: Optional[IdentityProperties]
        properties: Optional[TaskPropertiesUpdateParameters]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityProperties] = ..., 
                properties: Optional[TaskPropertiesUpdateParameters] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerregistrytasks.models.TimerTrigger(_Model):
        name: str
        schedule: str
        status: Optional[Union[str, TriggerStatus]]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                schedule: str, 
                status: Optional[Union[str, TriggerStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.TimerTriggerDescriptor(_Model):
        schedule_occurrence: Optional[str]
        timer_trigger_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                schedule_occurrence: Optional[str] = ..., 
                timer_trigger_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.TimerTriggerUpdateParameters(_Model):
        name: str
        schedule: Optional[str]
        status: Optional[Union[str, TriggerStatus]]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                schedule: Optional[str] = ..., 
                status: Optional[Union[str, TriggerStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.TokenType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        O_AUTH = "OAuth"
        PAT = "PAT"


    class azure.mgmt.containerregistrytasks.models.TrackedResource(Resource):
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


    class azure.mgmt.containerregistrytasks.models.TriggerProperties(_Model):
        base_image_trigger: Optional[BaseImageTrigger]
        source_triggers: Optional[list[SourceTrigger]]
        timer_triggers: Optional[list[TimerTrigger]]

        @overload
        def __init__(
                self, 
                *, 
                base_image_trigger: Optional[BaseImageTrigger] = ..., 
                source_triggers: Optional[list[SourceTrigger]] = ..., 
                timer_triggers: Optional[list[TimerTrigger]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.TriggerStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.containerregistrytasks.models.TriggerUpdateParameters(_Model):
        base_image_trigger: Optional[BaseImageTriggerUpdateParameters]
        source_triggers: Optional[list[SourceTriggerUpdateParameters]]
        timer_triggers: Optional[list[TimerTriggerUpdateParameters]]

        @overload
        def __init__(
                self, 
                *, 
                base_image_trigger: Optional[BaseImageTriggerUpdateParameters] = ..., 
                source_triggers: Optional[list[SourceTriggerUpdateParameters]] = ..., 
                timer_triggers: Optional[list[TimerTriggerUpdateParameters]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerregistrytasks.models.UpdateTriggerPayloadType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        TOKEN = "Token"


    class azure.mgmt.containerregistrytasks.models.UserIdentityProperties(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.containerregistrytasks.models.Variant(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V6 = "v6"
        V7 = "v7"
        V8 = "v8"


namespace azure.mgmt.containerregistrytasks.operations

    class azure.mgmt.containerregistrytasks.operations.AgentPoolsOperations:

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
                agent_pool_name: str, 
                agent_pool: AgentPool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentPool]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                agent_pool_name: str, 
                agent_pool: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentPool]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                agent_pool_name: str, 
                agent_pool: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentPool]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                agent_pool_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                agent_pool_name: str, 
                update_parameters: AgentPoolUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentPool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                agent_pool_name: str, 
                update_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentPool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                agent_pool_name: str, 
                update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentPool]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                agent_pool_name: str, 
                **kwargs: Any
            ) -> AgentPool: ...

        @distributed_trace
        def get_queue_status(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                agent_pool_name: str, 
                **kwargs: Any
            ) -> AgentPoolQueueStatus: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AgentPool]: ...


    class azure.mgmt.containerregistrytasks.operations.RegistriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_build_source_upload_url(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> SourceUploadDefinition: ...

        @overload
        def schedule_run(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                run_request: RunRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Run: ...

        @overload
        def schedule_run(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                run_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Run: ...

        @overload
        def schedule_run(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                run_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Run: ...


    class azure.mgmt.containerregistrytasks.operations.RunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def cancel(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                run_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                run_id: str, 
                **kwargs: Any
            ) -> Run: ...

        @distributed_trace
        def get_log_sas_url(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                run_id: str, 
                **kwargs: Any
            ) -> RunGetLogResult: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                *, 
                filter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Run]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                run_id: str, 
                run_update_parameters: RunUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Run: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                run_id: str, 
                run_update_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Run: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                run_id: str, 
                run_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Run: ...


    class azure.mgmt.containerregistrytasks.operations.TaskRunsOperations:

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
                task_run_name: str, 
                task_run: TaskRun, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TaskRun]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_run_name: str, 
                task_run: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TaskRun]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_run_name: str, 
                task_run: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TaskRun]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_run_name: str, 
                update_parameters: TaskRunUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TaskRun]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_run_name: str, 
                update_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TaskRun]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_run_name: str, 
                update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TaskRun]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_run_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_run_name: str, 
                **kwargs: Any
            ) -> TaskRun: ...

        @distributed_trace
        def get_details(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_run_name: str, 
                **kwargs: Any
            ) -> TaskRun: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TaskRun]: ...


    class azure.mgmt.containerregistrytasks.operations.TasksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_name: str, 
                task_create_parameters: Task, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_name: str, 
                task_create_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_name: str, 
                task_create_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_name: str, 
                **kwargs: Any
            ) -> Task: ...

        @distributed_trace
        def get_details(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_name: str, 
                **kwargs: Any
            ) -> Task: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Task]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_name: str, 
                task_update_parameters: TaskUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_name: str, 
                task_update_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                registry_name: str, 
                task_name: str, 
                task_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...


```