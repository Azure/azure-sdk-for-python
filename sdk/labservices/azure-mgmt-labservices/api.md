```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.labservices

    class azure.mgmt.labservices.ManagedLabsClient: implements ContextManager 
        images: ImagesOperations
        lab_plans: LabPlansOperations
        labs: LabsOperations
        operation_results: OperationResultsOperations
        operations: Operations
        schedules: SchedulesOperations
        skus: SkusOperations
        usages: UsagesOperations
        users: UsersOperations
        virtual_machines: VirtualMachinesOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.labservices.aio

    class azure.mgmt.labservices.aio.ManagedLabsClient: implements AsyncContextManager 
        images: ImagesOperations
        lab_plans: LabPlansOperations
        labs: LabsOperations
        operation_results: OperationResultsOperations
        operations: Operations
        schedules: SchedulesOperations
        skus: SkusOperations
        usages: UsagesOperations
        users: UsersOperations
        virtual_machines: VirtualMachinesOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


namespace azure.mgmt.labservices.aio.operations

    class azure.mgmt.labservices.aio.operations.ImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                image_name: str, 
                body: Image, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Image: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                image_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Image: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                image_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Image: ...

        @distributed_trace
        def list_by_lab_plan(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Image]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                image_name: str, 
                body: ImageUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Image: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                image_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Image: ...


    class azure.mgmt.labservices.aio.operations.LabPlansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                body: LabPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LabPlan]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LabPlan]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_save_image(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                body: SaveImageBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_save_image(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                body: LabPlanUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LabPlan]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LabPlan]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> LabPlan: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[LabPlan]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[LabPlan]: ...


    class azure.mgmt.labservices.aio.operations.LabsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                body: Lab, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Lab]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Lab]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_publish(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_sync_group(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                body: LabUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Lab]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Lab]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Lab: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Lab]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Lab]: ...


    class azure.mgmt.labservices.aio.operations.OperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                operation_result_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Optional[OperationResult]: ...


    class azure.mgmt.labservices.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Operation]: ...


    class azure.mgmt.labservices.aio.operations.SchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                schedule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                schedule_name: str, 
                body: Schedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                schedule_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                schedule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def list_by_lab(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Schedule]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                schedule_name: str, 
                body: ScheduleUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                schedule_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...


    class azure.mgmt.labservices.aio.operations.SkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[LabServicesSku]: ...


    class azure.mgmt.labservices.aio.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Usage]: ...


    class azure.mgmt.labservices.aio.operations.UsersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                body: User, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[User]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[User]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_invite(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                body: InviteBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_invite(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                body: UserUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[User]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[User]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> User: ...

        @distributed_trace
        def list_by_lab(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[User]: ...


    class azure.mgmt.labservices.aio.operations.VirtualMachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_redeploy(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_reimage(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reset_password(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                body: ResetPasswordBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reset_password(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_stop(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VirtualMachine: ...

        @distributed_trace
        def list_by_lab(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[VirtualMachine]: ...


namespace azure.mgmt.labservices.models

    class azure.mgmt.labservices.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.labservices.models.AutoShutdownProfile(Model):
        disconnect_delay: timedelta
        idle_delay: timedelta
        no_connect_delay: timedelta
        shutdown_on_disconnect: Union[str, EnableState]
        shutdown_on_idle: Union[str, ShutdownOnIdleMode]
        shutdown_when_not_connected: Union[str, EnableState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                disconnect_delay: Optional[timedelta] = ..., 
                idle_delay: Optional[timedelta] = ..., 
                no_connect_delay: Optional[timedelta] = ..., 
                shutdown_on_disconnect: Optional[Union[str, EnableState]] = ..., 
                shutdown_on_idle: Optional[Union[str, ShutdownOnIdleMode]] = ..., 
                shutdown_when_not_connected: Optional[Union[str, EnableState]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.ConnectionProfile(Model):
        client_rdp_access: Union[str, ConnectionType]
        client_ssh_access: Union[str, ConnectionType]
        web_rdp_access: Union[str, ConnectionType]
        web_ssh_access: Union[str, ConnectionType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                client_rdp_access: Optional[Union[str, ConnectionType]] = ..., 
                client_ssh_access: Optional[Union[str, ConnectionType]] = ..., 
                web_rdp_access: Optional[Union[str, ConnectionType]] = ..., 
                web_ssh_access: Optional[Union[str, ConnectionType]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.ConnectionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        PRIVATE = "Private"
        PUBLIC = "Public"


    class azure.mgmt.labservices.models.CreateOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IMAGE = "Image"
        TEMPLATE_VM = "TemplateVM"


    class azure.mgmt.labservices.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.labservices.models.Credentials(Model):
        password: str
        username: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                password: Optional[str] = ..., 
                username: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.EnableState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.labservices.models.ErrorAdditionalInfo(Model):
        info: JSON
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.ErrorDetail(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.ErrorResponse(Model):
        error: ErrorDetail

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.Identity(Model):
        principal_id: str
        tenant_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                type: Optional[Literal[SystemAssigned]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.Image(ProxyResource):
        author: str
        available_regions: list[str]
        description: str
        display_name: str
        enabled_state: Union[str, EnableState]
        icon_url: str
        id: str
        name: str
        offer: str
        os_state: Union[str, OsState]
        os_type: Union[str, OsType]
        plan: str
        provisioning_state: Union[str, ProvisioningState]
        publisher: str
        shared_gallery_id: str
        sku: str
        system_data: SystemData
        terms_status: Union[str, EnableState]
        type: str
        version: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                available_regions: Optional[List[str]] = ..., 
                enabled_state: Optional[Union[str, EnableState]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.ImageProperties(ImageUpdateProperties):
        author: str
        available_regions: list[str]
        description: str
        display_name: str
        enabled_state: Union[str, EnableState]
        icon_url: str
        offer: str
        os_state: Union[str, OsState]
        os_type: Union[str, OsType]
        plan: str
        provisioning_state: Union[str, ProvisioningState]
        publisher: str
        shared_gallery_id: str
        sku: str
        terms_status: Union[str, EnableState]
        version: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                available_regions: Optional[List[str]] = ..., 
                enabled_state: Optional[Union[str, EnableState]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.ImageReference(Model):
        exact_version: str
        id: str
        offer: str
        publisher: str
        sku: str
        version: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                offer: Optional[str] = ..., 
                publisher: Optional[str] = ..., 
                sku: Optional[str] = ..., 
                version: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.ImageUpdate(Model):
        enabled_state: Union[str, EnableState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                enabled_state: Optional[Union[str, EnableState]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.ImageUpdateProperties(Model):
        enabled_state: Union[str, EnableState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                enabled_state: Optional[Union[str, EnableState]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.InvitationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        NOT_SENT = "NotSent"
        SENDING = "Sending"
        SENT = "Sent"


    class azure.mgmt.labservices.models.InviteBody(Model):
        text: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                text: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.Lab(TrackedResource):
        auto_shutdown_profile: AutoShutdownProfile
        connection_profile: ConnectionProfile
        description: str
        id: str
        lab_plan_id: str
        location: str
        name: str
        network_profile: LabNetworkProfile
        provisioning_state: Union[str, ProvisioningState]
        roster_profile: RosterProfile
        security_profile: SecurityProfile
        state: Union[str, LabState]
        system_data: SystemData
        tags: dict[str, str]
        title: str
        type: str
        virtual_machine_profile: VirtualMachineProfile

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                auto_shutdown_profile: Optional[AutoShutdownProfile] = ..., 
                connection_profile: Optional[ConnectionProfile] = ..., 
                description: Optional[str] = ..., 
                lab_plan_id: Optional[str] = ..., 
                location: str, 
                network_profile: Optional[LabNetworkProfile] = ..., 
                roster_profile: Optional[RosterProfile] = ..., 
                security_profile: Optional[SecurityProfile] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                title: Optional[str] = ..., 
                virtual_machine_profile: Optional[VirtualMachineProfile] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.LabNetworkProfile(Model):
        load_balancer_id: str
        public_ip_id: str
        subnet_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                load_balancer_id: Optional[str] = ..., 
                public_ip_id: Optional[str] = ..., 
                subnet_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.LabPlan(TrackedResource):
        allowed_regions: list[str]
        default_auto_shutdown_profile: AutoShutdownProfile
        default_connection_profile: ConnectionProfile
        default_network_profile: LabPlanNetworkProfile
        id: str
        identity: Identity
        linked_lms_instance: str
        location: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        shared_gallery_id: str
        support_info: SupportInfo
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                allowed_regions: Optional[List[str]] = ..., 
                default_auto_shutdown_profile: Optional[AutoShutdownProfile] = ..., 
                default_connection_profile: Optional[ConnectionProfile] = ..., 
                default_network_profile: Optional[LabPlanNetworkProfile] = ..., 
                identity: Optional[Identity] = ..., 
                linked_lms_instance: Optional[str] = ..., 
                location: str, 
                shared_gallery_id: Optional[str] = ..., 
                support_info: Optional[SupportInfo] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.LabPlanNetworkProfile(Model):
        subnet_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                subnet_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.LabPlanProperties(LabPlanUpdateProperties):
        allowed_regions: list[str]
        default_auto_shutdown_profile: AutoShutdownProfile
        default_connection_profile: ConnectionProfile
        default_network_profile: LabPlanNetworkProfile
        linked_lms_instance: str
        provisioning_state: Union[str, ProvisioningState]
        shared_gallery_id: str
        support_info: SupportInfo

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                allowed_regions: Optional[List[str]] = ..., 
                default_auto_shutdown_profile: Optional[AutoShutdownProfile] = ..., 
                default_connection_profile: Optional[ConnectionProfile] = ..., 
                default_network_profile: Optional[LabPlanNetworkProfile] = ..., 
                linked_lms_instance: Optional[str] = ..., 
                shared_gallery_id: Optional[str] = ..., 
                support_info: Optional[SupportInfo] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.LabPlanUpdate(TrackedResourceUpdate):
        allowed_regions: list[str]
        default_auto_shutdown_profile: AutoShutdownProfile
        default_connection_profile: ConnectionProfile
        default_network_profile: LabPlanNetworkProfile
        identity: Identity
        linked_lms_instance: str
        shared_gallery_id: str
        support_info: SupportInfo
        tags: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                allowed_regions: Optional[List[str]] = ..., 
                default_auto_shutdown_profile: Optional[AutoShutdownProfile] = ..., 
                default_connection_profile: Optional[ConnectionProfile] = ..., 
                default_network_profile: Optional[LabPlanNetworkProfile] = ..., 
                identity: Optional[Identity] = ..., 
                linked_lms_instance: Optional[str] = ..., 
                shared_gallery_id: Optional[str] = ..., 
                support_info: Optional[SupportInfo] = ..., 
                tags: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.LabPlanUpdateProperties(Model):
        allowed_regions: list[str]
        default_auto_shutdown_profile: AutoShutdownProfile
        default_connection_profile: ConnectionProfile
        default_network_profile: LabPlanNetworkProfile
        linked_lms_instance: str
        shared_gallery_id: str
        support_info: SupportInfo

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                allowed_regions: Optional[List[str]] = ..., 
                default_auto_shutdown_profile: Optional[AutoShutdownProfile] = ..., 
                default_connection_profile: Optional[ConnectionProfile] = ..., 
                default_network_profile: Optional[LabPlanNetworkProfile] = ..., 
                linked_lms_instance: Optional[str] = ..., 
                shared_gallery_id: Optional[str] = ..., 
                support_info: Optional[SupportInfo] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.LabProperties(LabUpdateProperties):
        auto_shutdown_profile: AutoShutdownProfile
        connection_profile: ConnectionProfile
        description: str
        lab_plan_id: str
        network_profile: LabNetworkProfile
        provisioning_state: Union[str, ProvisioningState]
        roster_profile: RosterProfile
        security_profile: SecurityProfile
        state: Union[str, LabState]
        title: str
        virtual_machine_profile: VirtualMachineProfile

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                auto_shutdown_profile: Optional[AutoShutdownProfile] = ..., 
                connection_profile: Optional[ConnectionProfile] = ..., 
                description: Optional[str] = ..., 
                lab_plan_id: Optional[str] = ..., 
                network_profile: Optional[LabNetworkProfile] = ..., 
                roster_profile: Optional[RosterProfile] = ..., 
                security_profile: Optional[SecurityProfile] = ..., 
                title: Optional[str] = ..., 
                virtual_machine_profile: Optional[VirtualMachineProfile] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.LabServicesSku(Model):
        capabilities: list[LabServicesSkuCapabilities]
        capacity: LabServicesSkuCapacity
        costs: list[LabServicesSkuCost]
        family: str
        locations: list[str]
        name: str
        resource_type: str
        restrictions: list[LabServicesSkuRestrictions]
        size: str
        tier: Union[str, LabServicesSkuTier]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                capacity: Optional[LabServicesSkuCapacity] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.LabServicesSkuCapabilities(Model):
        name: str
        value: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.LabServicesSkuCapacity(Model):
        default: int
        maximum: int
        minimum: int
        scale_type: Union[str, ScaleType]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.LabServicesSkuCost(Model):
        extended_unit: str
        meter_id: str
        quantity: float

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.LabServicesSkuRestrictions(Model):
        reason_code: Union[str, RestrictionReasonCode]
        type: Union[str, RestrictionType]
        values: list[str]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.LabServicesSkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.labservices.models.LabState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DRAFT = "Draft"
        PUBLISHED = "Published"
        PUBLISHING = "Publishing"
        SCALING = "Scaling"
        SYNCING = "Syncing"


    class azure.mgmt.labservices.models.LabUpdate(TrackedResourceUpdate):
        auto_shutdown_profile: AutoShutdownProfile
        connection_profile: ConnectionProfile
        description: str
        lab_plan_id: str
        roster_profile: RosterProfile
        security_profile: SecurityProfile
        tags: list[str]
        title: str
        virtual_machine_profile: VirtualMachineProfile

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                auto_shutdown_profile: Optional[AutoShutdownProfile] = ..., 
                connection_profile: Optional[ConnectionProfile] = ..., 
                description: Optional[str] = ..., 
                lab_plan_id: Optional[str] = ..., 
                roster_profile: Optional[RosterProfile] = ..., 
                security_profile: Optional[SecurityProfile] = ..., 
                tags: Optional[List[str]] = ..., 
                title: Optional[str] = ..., 
                virtual_machine_profile: Optional[VirtualMachineProfile] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.LabUpdateProperties(Model):
        auto_shutdown_profile: AutoShutdownProfile
        connection_profile: ConnectionProfile
        description: str
        lab_plan_id: str
        roster_profile: RosterProfile
        security_profile: SecurityProfile
        title: str
        virtual_machine_profile: VirtualMachineProfile

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                auto_shutdown_profile: Optional[AutoShutdownProfile] = ..., 
                connection_profile: Optional[ConnectionProfile] = ..., 
                description: Optional[str] = ..., 
                lab_plan_id: Optional[str] = ..., 
                roster_profile: Optional[RosterProfile] = ..., 
                security_profile: Optional[SecurityProfile] = ..., 
                title: Optional[str] = ..., 
                virtual_machine_profile: Optional[VirtualMachineProfile] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.ListUsagesResult(Model):
        next_link: str
        value: list[Usage]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Usage]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.Operation(Model):
        action_type: Union[str, ActionType]
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, Origin]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.OperationResult(Model):
        end_time: datetime
        error: ErrorDetail
        id: str
        name: str
        percent_complete: float
        start_time: datetime
        status: Union[str, OperationStatus]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Union[str, OperationStatus], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.OperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NOT_STARTED = "NotStarted"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.labservices.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.labservices.models.OsState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GENERALIZED = "Generalized"
        SPECIALIZED = "Specialized"


    class azure.mgmt.labservices.models.OsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.labservices.models.PagedImages(Model):
        next_link: str
        value: list[Image]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.PagedLabPlans(Model):
        next_link: str
        value: list[LabPlan]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.PagedLabServicesSkus(Model):
        next_link: str
        value: list[LabServicesSku]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.PagedLabs(Model):
        next_link: str
        value: list[Lab]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.PagedSchedules(Model):
        next_link: str
        value: list[Schedule]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.PagedUsers(Model):
        next_link: str
        value: list[User]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.PagedVirtualMachines(Model):
        next_link: str
        value: list[VirtualMachine]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        LOCKED = "Locked"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.labservices.models.ProxyResource(Resource):
        id: str
        name: str
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.RecurrenceFrequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        WEEKLY = "Weekly"


    class azure.mgmt.labservices.models.RecurrencePattern(Model):
        expiration_date: datetime
        frequency: Union[str, RecurrenceFrequency]
        interval: int
        week_days: Union[list[str, WeekDay]]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                expiration_date: datetime, 
                frequency: Union[str, RecurrenceFrequency], 
                interval: Optional[int] = ..., 
                week_days: Optional[List[Union[str, WeekDay]]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.RegistrationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_REGISTERED = "NotRegistered"
        REGISTERED = "Registered"


    class azure.mgmt.labservices.models.ResetPasswordBody(Model):
        password: str
        username: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                password: str, 
                username: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.Resource(Model):
        id: str
        name: str
        type: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.RestrictionReasonCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_AVAILABLE_FOR_SUBSCRIPTION = "NotAvailableForSubscription"
        QUOTA_ID = "QuotaId"


    class azure.mgmt.labservices.models.RestrictionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCATION = "Location"


    class azure.mgmt.labservices.models.RosterProfile(Model):
        active_directory_group_id: str
        lms_instance: str
        lti_client_id: str
        lti_context_id: str
        lti_roster_endpoint: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                active_directory_group_id: Optional[str] = ..., 
                lms_instance: Optional[str] = ..., 
                lti_client_id: Optional[str] = ..., 
                lti_context_id: Optional[str] = ..., 
                lti_roster_endpoint: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.SaveImageBody(Model):
        lab_virtual_machine_id: str
        name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                lab_virtual_machine_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.ScaleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        MANUAL = "Manual"
        NONE = "None"


    class azure.mgmt.labservices.models.Schedule(ProxyResource):
        id: str
        name: str
        notes: str
        provisioning_state: Union[str, ProvisioningState]
        recurrence_pattern: RecurrencePattern
        start_at: datetime
        stop_at: datetime
        system_data: SystemData
        time_zone_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                notes: Optional[str] = ..., 
                recurrence_pattern: Optional[RecurrencePattern] = ..., 
                start_at: Optional[datetime] = ..., 
                stop_at: Optional[datetime] = ..., 
                time_zone_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.ScheduleProperties(ScheduleUpdateProperties):
        notes: str
        provisioning_state: Union[str, ProvisioningState]
        recurrence_pattern: RecurrencePattern
        start_at: datetime
        stop_at: datetime
        time_zone_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                notes: Optional[str] = ..., 
                recurrence_pattern: Optional[RecurrencePattern] = ..., 
                start_at: Optional[datetime] = ..., 
                stop_at: Optional[datetime] = ..., 
                time_zone_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.ScheduleUpdate(Model):
        notes: str
        recurrence_pattern: RecurrencePattern
        start_at: datetime
        stop_at: datetime
        time_zone_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                notes: Optional[str] = ..., 
                recurrence_pattern: Optional[RecurrencePattern] = ..., 
                start_at: Optional[datetime] = ..., 
                stop_at: Optional[datetime] = ..., 
                time_zone_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.ScheduleUpdateProperties(Model):
        notes: str
        recurrence_pattern: RecurrencePattern
        start_at: datetime
        stop_at: datetime
        time_zone_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                notes: Optional[str] = ..., 
                recurrence_pattern: Optional[RecurrencePattern] = ..., 
                start_at: Optional[datetime] = ..., 
                stop_at: Optional[datetime] = ..., 
                time_zone_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.SecurityProfile(Model):
        open_access: Union[str, EnableState]
        registration_code: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                open_access: Optional[Union[str, EnableState]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.ShutdownOnIdleMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOW_USAGE = "LowUsage"
        NONE = "None"
        USER_ABSENCE = "UserAbsence"


    class azure.mgmt.labservices.models.Sku(Model):
        capacity: int
        family: str
        name: str
        size: str
        tier: Union[str, SkuTier]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: str, 
                size: Optional[str] = ..., 
                tier: Optional[Union[str, SkuTier]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        FREE = "Free"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.labservices.models.SupportInfo(Model):
        email: str
        instructions: str
        phone: str
        url: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                email: Optional[str] = ..., 
                instructions: Optional[str] = ..., 
                phone: Optional[str] = ..., 
                url: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.TrackedResourceUpdate(Model):
        tags: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tags: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.Usage(Model):
        current_value: int
        id: str
        limit: int
        name: UsageName
        unit: Union[str, UsageUnit]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                current_value: Optional[int] = ..., 
                id: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                name: Optional[UsageName] = ..., 
                unit: Optional[Union[str, UsageUnit]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.UsageName(Model):
        localized_value: str
        sku_instances: list[str]
        value: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                localized_value: Optional[str] = ..., 
                sku_instances: Optional[List[str]] = ..., 
                value: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.UsageUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNT = "Count"


    class azure.mgmt.labservices.models.User(ProxyResource):
        additional_usage_quota: timedelta
        display_name: str
        email: str
        id: str
        invitation_sent: datetime
        invitation_state: Union[str, InvitationState]
        name: str
        provisioning_state: Union[str, ProvisioningState]
        registration_state: Union[str, RegistrationState]
        system_data: SystemData
        total_usage: timedelta
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                additional_usage_quota: Optional[timedelta] = ..., 
                email: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.UserProperties(UserUpdateProperties):
        additional_usage_quota: timedelta
        display_name: str
        email: str
        invitation_sent: datetime
        invitation_state: Union[str, InvitationState]
        provisioning_state: Union[str, ProvisioningState]
        registration_state: Union[str, RegistrationState]
        total_usage: timedelta

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                additional_usage_quota: Optional[timedelta] = ..., 
                email: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.UserUpdate(Model):
        additional_usage_quota: timedelta

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                additional_usage_quota: Optional[timedelta] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.UserUpdateProperties(Model):
        additional_usage_quota: timedelta

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                additional_usage_quota: Optional[timedelta] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.VirtualMachine(ProxyResource):
        claimed_by_user_id: str
        connection_profile: VirtualMachineConnectionProfile
        id: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        state: Union[str, VirtualMachineState]
        system_data: SystemData
        type: str
        vm_type: Union[str, VirtualMachineType]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.VirtualMachineAdditionalCapabilities(Model):
        install_gpu_drivers: Union[str, EnableState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                install_gpu_drivers: Optional[Union[str, EnableState]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.VirtualMachineConnectionProfile(Model):
        admin_username: str
        non_admin_username: str
        private_ip_address: str
        rdp_authority: str
        rdp_in_browser_url: str
        ssh_authority: str
        ssh_in_browser_url: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.VirtualMachineProfile(Model):
        additional_capabilities: VirtualMachineAdditionalCapabilities
        admin_user: Credentials
        create_option: Union[str, CreateOption]
        image_reference: ImageReference
        non_admin_user: Credentials
        os_type: Union[str, OsType]
        sku: Sku
        usage_quota: timedelta
        use_shared_password: Union[str, EnableState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                additional_capabilities: Optional[VirtualMachineAdditionalCapabilities] = ..., 
                admin_user: Credentials, 
                create_option: Union[str, CreateOption], 
                image_reference: ImageReference, 
                non_admin_user: Optional[Credentials] = ..., 
                sku: Sku, 
                usage_quota: timedelta, 
                use_shared_password: Optional[Union[str, EnableState]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.labservices.models.VirtualMachineState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REDEPLOYING = "Redeploying"
        REIMAGING = "Reimaging"
        RESETTING_PASSWORD = "ResettingPassword"
        RUNNING = "Running"
        STARTING = "Starting"
        STOPPED = "Stopped"
        STOPPING = "Stopping"


    class azure.mgmt.labservices.models.VirtualMachineType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TEMPLATE = "Template"
        USER = "User"


    class azure.mgmt.labservices.models.WeekDay(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


namespace azure.mgmt.labservices.operations

    class azure.mgmt.labservices.operations.ImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                image_name: str, 
                body: Image, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Image: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                image_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Image: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                image_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Image: ...

        @distributed_trace
        def list_by_lab_plan(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Image]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                image_name: str, 
                body: ImageUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Image: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                image_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Image: ...


    class azure.mgmt.labservices.operations.LabPlansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                body: LabPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LabPlan]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LabPlan]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_save_image(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                body: SaveImageBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_save_image(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                body: LabPlanUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LabPlan]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LabPlan]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_plan_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> LabPlan: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[LabPlan]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[LabPlan]: ...


    class azure.mgmt.labservices.operations.LabsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                body: Lab, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Lab]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Lab]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_publish(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_sync_group(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                body: LabUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Lab]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Lab]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Lab: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Lab]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Lab]: ...


    class azure.mgmt.labservices.operations.OperationResultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                operation_result_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Optional[OperationResult]: ...


    class azure.mgmt.labservices.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Operation]: ...


    class azure.mgmt.labservices.operations.SchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                schedule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                schedule_name: str, 
                body: Schedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                schedule_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                schedule_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def list_by_lab(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Schedule]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                schedule_name: str, 
                body: ScheduleUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                schedule_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...


    class azure.mgmt.labservices.operations.SkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[LabServicesSku]: ...


    class azure.mgmt.labservices.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Usage]: ...


    class azure.mgmt.labservices.operations.UsersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                body: User, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[User]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[User]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_invite(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                body: InviteBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_invite(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                body: UserUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[User]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[User]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                user_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> User: ...

        @distributed_trace
        def list_by_lab(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[User]: ...


    class azure.mgmt.labservices.operations.VirtualMachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_redeploy(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_reimage(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reset_password(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                body: ResetPasswordBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reset_password(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_stop(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                virtual_machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VirtualMachine: ...

        @distributed_trace
        def list_by_lab(
                self, 
                resource_group_name: str, 
                lab_name: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[VirtualMachine]: ...


```