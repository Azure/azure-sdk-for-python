```py
namespace azure.mgmt.serialconsole

    class azure.mgmt.serialconsole.MicrosoftSerialConsoleClient(_MicrosoftSerialConsoleClientOperationsMixin): implements ContextManager 
        serial_ports: SerialPortsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def disable_console(
                self, 
                default: str, 
                **kwargs: Any
            ) -> DisableSerialConsoleResult: ...

        @distributed_trace
        def enable_console(
                self, 
                default: str, 
                **kwargs: Any
            ) -> EnableSerialConsoleResult: ...

        @distributed_trace
        def get_console_status(
                self, 
                default: str, 
                **kwargs: Any
            ) -> SerialConsoleStatus: ...

        @distributed_trace
        def list_operations(self, **kwargs: Any) -> SerialConsoleOperations: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.serialconsole.aio

    class azure.mgmt.serialconsole.aio.MicrosoftSerialConsoleClient(_MicrosoftSerialConsoleClientOperationsMixin): implements AsyncContextManager 
        serial_ports: SerialPortsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def disable_console(
                self, 
                default: str, 
                **kwargs: Any
            ) -> DisableSerialConsoleResult: ...

        @distributed_trace_async
        async def enable_console(
                self, 
                default: str, 
                **kwargs: Any
            ) -> EnableSerialConsoleResult: ...

        @distributed_trace_async
        async def get_console_status(
                self, 
                default: str, 
                **kwargs: Any
            ) -> SerialConsoleStatus: ...

        @distributed_trace_async
        async def list_operations(self, **kwargs: Any) -> SerialConsoleOperations: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.serialconsole.aio.operations

    class azure.mgmt.serialconsole.aio.operations.SerialPortsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def connect(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource: str, 
                serial_port: str, 
                **kwargs: Any
            ) -> SerialPortConnectResult: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource: str, 
                serial_port: str, 
                parameters: SerialPort, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SerialPort: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource: str, 
                serial_port: str, 
                parameters: SerialPort, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SerialPort: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource: str, 
                serial_port: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SerialPort: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource: str, 
                serial_port: str, 
                **kwargs: Any
            ) -> SerialPort: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource: str, 
                **kwargs: Any
            ) -> SerialPortListResult: ...

        @distributed_trace_async
        async def list_by_subscriptions(self, **kwargs: Any) -> SerialPortListResult: ...


namespace azure.mgmt.serialconsole.models

    class azure.mgmt.serialconsole.models.CloudError(_Model):
        error: Optional[CloudErrorBody]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[CloudErrorBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.serialconsole.models.CloudErrorBody(_Model):
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


    class azure.mgmt.serialconsole.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.serialconsole.models.DisableSerialConsoleResult(_Model):
        properties: Optional[DisableSerialConsoleResultProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DisableSerialConsoleResultProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.serialconsole.models.DisableSerialConsoleResultProperties(_Model):
        disabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                disabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.serialconsole.models.EnableSerialConsoleResult(_Model):
        properties: Optional[EnableSerialConsoleResultProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EnableSerialConsoleResultProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.serialconsole.models.EnableSerialConsoleResultProperties(_Model):
        disabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                disabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.serialconsole.models.GetSerialConsoleSubscriptionNotFound(_Model):
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


    class azure.mgmt.serialconsole.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.serialconsole.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.serialconsole.models.SerialConsoleOperations(_Model):
        value: Optional[list[SerialConsoleOperationsValueItem]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[SerialConsoleOperationsValueItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.serialconsole.models.SerialConsoleOperationsValueItem(_Model):
        display: Optional[SerialConsoleOperationsValueItemDisplay]
        is_data_action: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[SerialConsoleOperationsValueItemDisplay] = ..., 
                is_data_action: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.serialconsole.models.SerialConsoleOperationsValueItemDisplay(_Model):
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


    class azure.mgmt.serialconsole.models.SerialConsoleStatus(_Model):
        properties: Optional[SerialConsoleStatusProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SerialConsoleStatusProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.serialconsole.models.SerialConsoleStatusProperties(_Model):
        disabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                disabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.serialconsole.models.SerialPort(ProxyResource):
        id: str
        name: str
        properties: Optional[SerialPortProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SerialPortProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.serialconsole.models.SerialPortConnectResult(_Model):
        connection_string: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                connection_string: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.serialconsole.models.SerialPortConnectionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        INACTIVE = "inactive"


    class azure.mgmt.serialconsole.models.SerialPortListResult(_Model):
        value: Optional[list[SerialPort]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[SerialPort]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.serialconsole.models.SerialPortProperties(_Model):
        connection_state: Optional[Union[str, SerialPortConnectionState]]
        state: Optional[Union[str, SerialPortState]]

        @overload
        def __init__(
                self, 
                *, 
                connection_state: Optional[Union[str, SerialPortConnectionState]] = ..., 
                state: Optional[Union[str, SerialPortState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.serialconsole.models.SerialPortState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.mgmt.serialconsole.models.SystemData(_Model):
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


namespace azure.mgmt.serialconsole.operations

    class azure.mgmt.serialconsole.operations.SerialPortsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def connect(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource: str, 
                serial_port: str, 
                **kwargs: Any
            ) -> SerialPortConnectResult: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource: str, 
                serial_port: str, 
                parameters: SerialPort, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SerialPort: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource: str, 
                serial_port: str, 
                parameters: SerialPort, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SerialPort: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource: str, 
                serial_port: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SerialPort: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource: str, 
                serial_port: str, 
                **kwargs: Any
            ) -> SerialPort: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource: str, 
                **kwargs: Any
            ) -> SerialPortListResult: ...

        @distributed_trace
        def list_by_subscriptions(self, **kwargs: Any) -> SerialPortListResult: ...


namespace azure.mgmt.serialconsole.types

    class azure.mgmt.serialconsole.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.serialconsole.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.serialconsole.types.SerialPort(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SerialPortProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SerialPortProperties
        system_data: SystemData
        type: str


    class azure.mgmt.serialconsole.types.SerialPortProperties(TypedDict, total=False):
        key "connectionState": Union[str, SerialPortConnectionState]
        key "state": Union[str, SerialPortState]
        connection_state: Union[str, SerialPortConnectionState]
        state: Union[str, SerialPortState]


    class azure.mgmt.serialconsole.types.SystemData(TypedDict, total=False):
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


```