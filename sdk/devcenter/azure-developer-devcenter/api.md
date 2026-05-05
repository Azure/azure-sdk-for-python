```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.developer.devcenter

    class azure.developer.devcenter.DevCenterClient(DevCenterClientOperationsMixin): implements ContextManager 

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
        def begin_create_dev_box(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                body: DevBox, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevBox]: ...

        @overload
        def begin_create_dev_box(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevBox]: ...

        @overload
        def begin_create_dev_box(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevBox]: ...

        @overload
        def begin_create_or_update_environment(
                self, 
                project_name: str, 
                user_id: str, 
                environment_name: str, 
                body: Environment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Environment]: ...

        @overload
        def begin_create_or_update_environment(
                self, 
                project_name: str, 
                user_id: str, 
                environment_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Environment]: ...

        @overload
        def begin_create_or_update_environment(
                self, 
                project_name: str, 
                user_id: str, 
                environment_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Environment]: ...

        @distributed_trace
        def begin_delete_dev_box(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                **kwargs: Any
            ) -> LROPoller[OperationDetails]: ...

        @distributed_trace
        def begin_delete_environment(
                self, 
                project_name: str, 
                user_id: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> LROPoller[OperationDetails]: ...

        @distributed_trace
        def begin_restart_dev_box(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                **kwargs: Any
            ) -> LROPoller[OperationDetails]: ...

        @distributed_trace
        def begin_start_dev_box(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                **kwargs: Any
            ) -> LROPoller[OperationDetails]: ...

        @distributed_trace
        def begin_stop_dev_box(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                *, 
                hibernate: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationDetails]: ...

        def close(self) -> None: ...

        @distributed_trace
        def delay_all_dev_box_actions(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                *, 
                delay_until: datetime, 
                **kwargs: Any
            ) -> Iterable[DevBoxActionDelayResult]: ...

        @distributed_trace
        def delay_dev_box_action(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                action_name: str, 
                *, 
                delay_until: datetime, 
                **kwargs: Any
            ) -> DevBoxAction: ...

        @distributed_trace
        def get_catalog(
                self, 
                project_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> Catalog: ...

        @distributed_trace
        def get_dev_box(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                **kwargs: Any
            ) -> DevBox: ...

        @distributed_trace
        def get_dev_box_action(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                action_name: str, 
                **kwargs: Any
            ) -> DevBoxAction: ...

        @distributed_trace
        def get_environment(
                self, 
                project_name: str, 
                user_id: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> Environment: ...

        @distributed_trace
        def get_environment_definition(
                self, 
                project_name: str, 
                catalog_name: str, 
                definition_name: str, 
                **kwargs: Any
            ) -> EnvironmentDefinition: ...

        @distributed_trace
        def get_pool(
                self, 
                project_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> Pool: ...

        @distributed_trace
        def get_project(
                self, 
                project_name: str, 
                **kwargs: Any
            ) -> Project: ...

        @distributed_trace
        def get_remote_connection(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                **kwargs: Any
            ) -> RemoteConnection: ...

        @distributed_trace
        def get_schedule(
                self, 
                project_name: str, 
                pool_name: str, 
                schedule_name: str, 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def list_all_dev_boxes(self, **kwargs: Any) -> Iterable[DevBox]: ...

        @distributed_trace
        def list_all_dev_boxes_by_user(
                self, 
                user_id: str, 
                **kwargs: Any
            ) -> Iterable[DevBox]: ...

        @distributed_trace
        def list_all_environments(
                self, 
                project_name: str, 
                **kwargs: Any
            ) -> Iterable[Environment]: ...

        @distributed_trace
        def list_catalogs(
                self, 
                project_name: str, 
                **kwargs: Any
            ) -> Iterable[Catalog]: ...

        @distributed_trace
        def list_dev_box_actions(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                **kwargs: Any
            ) -> Iterable[DevBoxAction]: ...

        @distributed_trace
        def list_dev_boxes(
                self, 
                project_name: str, 
                user_id: str, 
                **kwargs: Any
            ) -> Iterable[DevBox]: ...

        @distributed_trace
        def list_environment_definitions(
                self, 
                project_name: str, 
                **kwargs: Any
            ) -> Iterable[EnvironmentDefinition]: ...

        @distributed_trace
        def list_environment_definitions_by_catalog(
                self, 
                project_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> Iterable[EnvironmentDefinition]: ...

        @distributed_trace
        def list_environment_types(
                self, 
                project_name: str, 
                **kwargs: Any
            ) -> Iterable[EnvironmentType]: ...

        @distributed_trace
        def list_environments(
                self, 
                project_name: str, 
                user_id: str, 
                **kwargs: Any
            ) -> Iterable[Environment]: ...

        @distributed_trace
        def list_pools(
                self, 
                project_name: str, 
                **kwargs: Any
            ) -> Iterable[Pool]: ...

        @distributed_trace
        def list_projects(self, **kwargs: Any) -> Iterable[Project]: ...

        @distributed_trace
        def list_schedules(
                self, 
                project_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> Iterable[Schedule]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        @distributed_trace
        def skip_dev_box_action(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                action_name: str, 
                **kwargs: Any
            ) -> None: ...


namespace azure.developer.devcenter.aio

    class azure.developer.devcenter.aio.DevCenterClient(DevCenterClientOperationsMixin): implements AsyncContextManager 

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
        async def begin_create_dev_box(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                body: DevBox, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevBox]: ...

        @overload
        async def begin_create_dev_box(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevBox]: ...

        @overload
        async def begin_create_dev_box(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevBox]: ...

        @overload
        async def begin_create_or_update_environment(
                self, 
                project_name: str, 
                user_id: str, 
                environment_name: str, 
                body: Environment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Environment]: ...

        @overload
        async def begin_create_or_update_environment(
                self, 
                project_name: str, 
                user_id: str, 
                environment_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Environment]: ...

        @overload
        async def begin_create_or_update_environment(
                self, 
                project_name: str, 
                user_id: str, 
                environment_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Environment]: ...

        @distributed_trace_async
        async def begin_delete_dev_box(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationDetails]: ...

        @distributed_trace_async
        async def begin_delete_environment(
                self, 
                project_name: str, 
                user_id: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationDetails]: ...

        @distributed_trace_async
        async def begin_restart_dev_box(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationDetails]: ...

        @distributed_trace_async
        async def begin_start_dev_box(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationDetails]: ...

        @distributed_trace_async
        async def begin_stop_dev_box(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                *, 
                hibernate: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationDetails]: ...

        async def close(self) -> None: ...

        @distributed_trace
        def delay_all_dev_box_actions(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                *, 
                delay_until: datetime, 
                **kwargs: Any
            ) -> AsyncIterable[DevBoxActionDelayResult]: ...

        @distributed_trace_async
        async def delay_dev_box_action(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                action_name: str, 
                *, 
                delay_until: datetime, 
                **kwargs: Any
            ) -> DevBoxAction: ...

        @distributed_trace_async
        async def get_catalog(
                self, 
                project_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> Catalog: ...

        @distributed_trace_async
        async def get_dev_box(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                **kwargs: Any
            ) -> DevBox: ...

        @distributed_trace_async
        async def get_dev_box_action(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                action_name: str, 
                **kwargs: Any
            ) -> DevBoxAction: ...

        @distributed_trace_async
        async def get_environment(
                self, 
                project_name: str, 
                user_id: str, 
                environment_name: str, 
                **kwargs: Any
            ) -> Environment: ...

        @distributed_trace_async
        async def get_environment_definition(
                self, 
                project_name: str, 
                catalog_name: str, 
                definition_name: str, 
                **kwargs: Any
            ) -> EnvironmentDefinition: ...

        @distributed_trace_async
        async def get_pool(
                self, 
                project_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> Pool: ...

        @distributed_trace_async
        async def get_project(
                self, 
                project_name: str, 
                **kwargs: Any
            ) -> Project: ...

        @distributed_trace_async
        async def get_remote_connection(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                **kwargs: Any
            ) -> RemoteConnection: ...

        @distributed_trace_async
        async def get_schedule(
                self, 
                project_name: str, 
                pool_name: str, 
                schedule_name: str, 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def list_all_dev_boxes(self, **kwargs: Any) -> AsyncIterable[DevBox]: ...

        @distributed_trace
        def list_all_dev_boxes_by_user(
                self, 
                user_id: str, 
                **kwargs: Any
            ) -> AsyncIterable[DevBox]: ...

        @distributed_trace
        def list_all_environments(
                self, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Environment]: ...

        @distributed_trace
        def list_catalogs(
                self, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Catalog]: ...

        @distributed_trace
        def list_dev_box_actions(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[DevBoxAction]: ...

        @distributed_trace
        def list_dev_boxes(
                self, 
                project_name: str, 
                user_id: str, 
                **kwargs: Any
            ) -> AsyncIterable[DevBox]: ...

        @distributed_trace
        def list_environment_definitions(
                self, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[EnvironmentDefinition]: ...

        @distributed_trace
        def list_environment_definitions_by_catalog(
                self, 
                project_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[EnvironmentDefinition]: ...

        @distributed_trace
        def list_environment_types(
                self, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[EnvironmentType]: ...

        @distributed_trace
        def list_environments(
                self, 
                project_name: str, 
                user_id: str, 
                **kwargs: Any
            ) -> AsyncIterable[Environment]: ...

        @distributed_trace
        def list_pools(
                self, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Pool]: ...

        @distributed_trace
        def list_projects(self, **kwargs: Any) -> AsyncIterable[Project]: ...

        @distributed_trace
        def list_schedules(
                self, 
                project_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Schedule]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        @distributed_trace_async
        async def skip_dev_box_action(
                self, 
                project_name: str, 
                user_id: str, 
                dev_box_name: str, 
                action_name: str, 
                **kwargs: Any
            ) -> None: ...


namespace azure.developer.devcenter.models

    class azure.developer.devcenter.models.Catalog(Model):
        name: str


    class azure.developer.devcenter.models.DevBox(Model):
        action_state: Optional[str]
        created_time: Optional[datetime]
        error: Optional[Error]
        hardware_profile: Optional[HardwareProfile]
        hibernate_support: Optional[Union[str, HibernateSupport]]
        image_reference: Optional[ImageReference]
        local_administrator: Optional[Union[str, LocalAdministratorStatus]]
        location: Optional[str]
        name: str
        os_type: Optional[Union[str, OSType]]
        pool_name: str
        power_state: Optional[Union[str, PowerState]]
        project_name: Optional[str]
        provisioning_state: Optional[Union[str, DevBoxProvisioningState]]
        storage_profile: Optional[StorageProfile]
        unique_id: Optional[str]
        user: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                local_administrator: Optional[Union[str, LocalAdministratorStatus]] = ..., 
                pool_name: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.developer.devcenter.models.DevBoxAction(Model):
        action_type: Union[str, DevBoxActionType]
        name: str
        next: Optional[DevBoxNextAction]
        source_id: str
        suspended_until: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                action_type: Union[str, DevBoxActionType], 
                next: Optional[DevBoxNextAction] = ..., 
                source_id: str, 
                suspended_until: Optional[datetime] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.developer.devcenter.models.DevBoxActionDelayResult(Model):
        action: Optional[DevBoxAction]
        error: Optional[Error]
        name: str
        result: Union[str, DevBoxActionDelayStatus]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[DevBoxAction] = ..., 
                error: Optional[Error] = ..., 
                name: str, 
                result: Union[str, DevBoxActionDelayStatus]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.developer.devcenter.models.DevBoxActionDelayStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.developer.devcenter.models.DevBoxActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STOP = "Stop"


    class azure.developer.devcenter.models.DevBoxNextAction(Model):
        scheduled_time: datetime

        @overload
        def __init__(
                self, 
                *, 
                scheduled_time: datetime
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.developer.devcenter.models.DevBoxProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_GRACE_PERIOD = "InGracePeriod"
        NOT_PROVISIONED = "NotProvisioned"
        PROVISIONED_WITH_WARNING = "ProvisionedWithWarning"
        PROVISIONING = "Provisioning"
        STARTING = "Starting"
        STOPPING = "Stopping"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.developer.devcenter.models.Environment(Model):
        catalog_name: str
        environment_definition_name: str
        environment_type: str
        error: Optional[Error]
        name: str
        parameters: Optional[Dict[str, Any]]
        provisioning_state: Optional[Union[str, EnvironmentProvisioningState]]
        resource_group_id: Optional[str]
        user: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                catalog_name: str, 
                environment_definition_name: str, 
                environment_type: str, 
                parameters: Optional[Dict[str, Any]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.developer.devcenter.models.EnvironmentDefinition(Model):
        catalog_name: str
        description: Optional[str]
        id: str
        name: str
        parameters: Optional[List[EnvironmentDefinitionParameter]]
        parameters_schema: Optional[str]
        template_path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                catalog_name: str, 
                description: Optional[str] = ..., 
                id: str, 
                parameters: Optional[List[EnvironmentDefinitionParameter]] = ..., 
                parameters_schema: Optional[str] = ..., 
                template_path: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.developer.devcenter.models.EnvironmentDefinitionParameter(Model):
        allowed: Optional[List[str]]
        default: Optional[str]
        description: Optional[str]
        id: str
        name: Optional[str]
        read_only: Optional[bool]
        required: bool
        type: Union[str, ParameterType]

        @overload
        def __init__(
                self, 
                *, 
                allowed: Optional[List[str]] = ..., 
                default: Optional[str] = ..., 
                description: Optional[str] = ..., 
                id: str, 
                name: Optional[str] = ..., 
                read_only: Optional[bool] = ..., 
                required: bool, 
                type: Union[str, ParameterType]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.developer.devcenter.models.EnvironmentProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        MOVING_RESOURCES = "MovingResources"
        PREPARING = "Preparing"
        RUNNING = "Running"
        STORAGE_PROVISIONING_FAILED = "StorageProvisioningFailed"
        SUCCEEDED = "Succeeded"
        SYNCING = "Syncing"
        TRANSIENT_FAILURE = "TransientFailure"
        UPDATING = "Updating"


    class azure.developer.devcenter.models.EnvironmentType(Model):
        deployment_target_id: str
        name: str
        status: Union[str, EnvironmentTypeStatus]

        @overload
        def __init__(
                self, 
                *, 
                deployment_target_id: str, 
                name: str, 
                status: Union[str, EnvironmentTypeStatus]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.developer.devcenter.models.EnvironmentTypeStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.developer.devcenter.models.Error(Model):
        code: str
        details: Optional[List[Error]]
        innererror: Optional[InnerError]
        message: str
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                details: Optional[List[Error]] = ..., 
                innererror: Optional[InnerError] = ..., 
                message: str, 
                target: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.developer.devcenter.models.HardwareProfile(Model):
        memory_gb: Optional[int]
        sku_name: Optional[Union[str, SkuName]]
        vcpus: Optional[int]


    class azure.developer.devcenter.models.HibernateSupport(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        OS_UNSUPPORTED = "OsUnsupported"


    class azure.developer.devcenter.models.ImageReference(Model):
        name: Optional[str]
        operating_system: Optional[str]
        os_build_number: Optional[str]
        published_date: Optional[datetime]
        version: Optional[str]


    class azure.developer.devcenter.models.InnerError(Model):
        code: Optional[str]
        innererror: Optional[InnerError]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                innererror: Optional[InnerError] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.developer.devcenter.models.LocalAdministratorStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.developer.devcenter.models.OSDisk(Model):
        disk_size_gb: Optional[int]


    class azure.developer.devcenter.models.OSType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WINDOWS = "Windows"


    class azure.developer.devcenter.models.OperationDetails(Model):
        end_time: Optional[datetime]
        error: Optional[Error]
        id: str
        name: str
        percent_complete: Optional[float]
        properties: Optional[Any]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: Union[str, OperationStatus]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[Error] = ..., 
                percent_complete: Optional[float] = ..., 
                properties: Optional[Any] = ..., 
                resource_id: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Union[str, OperationStatus]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.developer.devcenter.models.OperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        NOT_STARTED = "NotStarted"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.developer.devcenter.models.ParameterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARRAY = "array"
        BOOLEAN = "boolean"
        INTEGER = "integer"
        NUMBER = "number"
        OBJECT = "object"
        STRING = "string"


    class azure.developer.devcenter.models.Pool(Model):
        hardware_profile: Optional[HardwareProfile]
        health_status: Union[str, PoolHealthStatus]
        hibernate_support: Optional[Union[str, HibernateSupport]]
        image_reference: Optional[ImageReference]
        local_administrator: Optional[Union[str, LocalAdministratorStatus]]
        location: str
        name: str
        os_type: Optional[Union[str, OSType]]
        stop_on_disconnect: Optional[StopOnDisconnectConfiguration]
        storage_profile: Optional[StorageProfile]

        @overload
        def __init__(
                self, 
                *, 
                hardware_profile: Optional[HardwareProfile] = ..., 
                health_status: Union[str, PoolHealthStatus], 
                hibernate_support: Optional[Union[str, HibernateSupport]] = ..., 
                image_reference: Optional[ImageReference] = ..., 
                local_administrator: Optional[Union[str, LocalAdministratorStatus]] = ..., 
                location: str, 
                os_type: Optional[Union[str, OSType]] = ..., 
                stop_on_disconnect: Optional[StopOnDisconnectConfiguration] = ..., 
                storage_profile: Optional[StorageProfile] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.developer.devcenter.models.PoolHealthStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        PENDING = "Pending"
        UNHEALTHY = "Unhealthy"
        UNKNOWN = "Unknown"
        WARNING = "Warning"


    class azure.developer.devcenter.models.PowerState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEALLOCATED = "Deallocated"
        HIBERNATED = "Hibernated"
        POWERED_OFF = "PoweredOff"
        RUNNING = "Running"
        UNKNOWN = "Unknown"


    class azure.developer.devcenter.models.Project(Model):
        description: Optional[str]
        max_dev_boxes_per_user: Optional[int]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                max_dev_boxes_per_user: Optional[int] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.developer.devcenter.models.RemoteConnection(Model):
        rdp_connection_url: Optional[str]
        web_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                rdp_connection_url: Optional[str] = ..., 
                web_url: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.developer.devcenter.models.Schedule(Model):
        frequency: Union[str, ScheduledFrequency]
        name: str
        time: str
        time_zone: str
        type: Union[str, ScheduledType]

        @overload
        def __init__(
                self, 
                *, 
                frequency: Union[str, ScheduledFrequency], 
                time: str, 
                time_zone: str, 
                type: Union[str, ScheduledType]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.developer.devcenter.models.ScheduledFrequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"


    class azure.developer.devcenter.models.ScheduledType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STOP_DEV_BOX = "StopDevBox"


    class azure.developer.devcenter.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GENERAL_A_16C64GB1024SSD_V2 = "general_a_16c64gb1024ssd_v2"
        GENERAL_A_16C64GB2048SSD_V2 = "general_a_16c64gb2048ssd_v2"
        GENERAL_A_16C64GB256SSD_V2 = "general_a_16c64gb256ssd_v2"
        GENERAL_A_16C64GB512SSD_V2 = "general_a_16c64gb512ssd_v2"
        GENERAL_A_32C128GB1024SSD_V2 = "general_a_32c128gb1024ssd_v2"
        GENERAL_A_32C128GB2048SSD_V2 = "general_a_32c128gb2048ssd_v2"
        GENERAL_A_32C128GB512SSD_V2 = "general_a_32c128gb512ssd_v2"
        GENERAL_A_8C32GB1024SSD_V2 = "general_a_8c32gb1024ssd_v2"
        GENERAL_A_8C32GB2048SSD_V2 = "general_a_8c32gb2048ssd_v2"
        GENERAL_A_8C32GB256SSD_V2 = "general_a_8c32gb256ssd_v2"
        GENERAL_A_8C32GB512SSD_V2 = "general_a_8c32gb512ssd_v2"
        GENERAL_I_16C64GB1024SSD_V2 = "general_i_16c64gb1024ssd_v2"
        GENERAL_I_16C64GB2048SSD_V2 = "general_i_16c64gb2048ssd_v2"
        GENERAL_I_16C64GB256SSD_V2 = "general_i_16c64gb256ssd_v2"
        GENERAL_I_16C64GB512SSD_V2 = "general_i_16c64gb512ssd_v2"
        GENERAL_I_32C128GB1024SSD_V2 = "general_i_32c128gb1024ssd_v2"
        GENERAL_I_32C128GB2048SSD_V2 = "general_i_32c128gb2048ssd_v2"
        GENERAL_I_32C128GB512SSD_V2 = "general_i_32c128gb512ssd_v2"
        GENERAL_I_8C32GB1024SSD_V2 = "general_i_8c32gb1024ssd_v2"
        GENERAL_I_8C32GB2048SSD_V2 = "general_i_8c32gb2048ssd_v2"
        GENERAL_I_8C32GB256SSD_V2 = "general_i_8c32gb256ssd_v2"
        GENERAL_I_8C32GB512SSD_V2 = "general_i_8c32gb512ssd_v2"


    class azure.developer.devcenter.models.StopOnDisconnectConfiguration(Model):
        grace_period_minutes: Optional[int]
        status: Union[str, StopOnDisconnectStatus]

        @overload
        def __init__(
                self, 
                *, 
                grace_period_minutes: Optional[int] = ..., 
                status: Union[str, StopOnDisconnectStatus]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.developer.devcenter.models.StopOnDisconnectStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.developer.devcenter.models.StorageProfile(Model):
        os_disk: Optional[OSDisk]

        @overload
        def __init__(
                self, 
                *, 
                os_disk: Optional[OSDisk] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


```