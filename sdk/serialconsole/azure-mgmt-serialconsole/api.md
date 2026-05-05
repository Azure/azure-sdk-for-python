```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.serialconsole

    class azure.mgmt.serialconsole.MicrosoftSerialConsoleClient(MicrosoftSerialConsoleClientOperationsMixin): implements ContextManager 
        serial_ports: SerialPortsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def disable_console(
                self, 
                default: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Union[DisableSerialConsoleResult, GetSerialConsoleSubscriptionNotFound]: ...

        @distributed_trace
        def enable_console(
                self, 
                default: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Union[EnableSerialConsoleResult, GetSerialConsoleSubscriptionNotFound]: ...

        @distributed_trace
        def get_console_status(
                self, 
                default: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Union[SerialConsoleStatus, GetSerialConsoleSubscriptionNotFound]: ...

        @distributed_trace
        def list_operations(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SerialConsoleOperations: ...


namespace azure.mgmt.serialconsole.aio

    class azure.mgmt.serialconsole.aio.MicrosoftSerialConsoleClient(MicrosoftSerialConsoleClientOperationsMixin): implements AsyncContextManager 
        serial_ports: SerialPortsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def disable_console(
                self, 
                default: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Union[DisableSerialConsoleResult, GetSerialConsoleSubscriptionNotFound]: ...

        @distributed_trace_async
        async def enable_console(
                self, 
                default: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Union[EnableSerialConsoleResult, GetSerialConsoleSubscriptionNotFound]: ...

        @distributed_trace_async
        async def get_console_status(
                self, 
                default: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Union[SerialConsoleStatus, GetSerialConsoleSubscriptionNotFound]: ...

        @distributed_trace_async
        async def list_operations(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SerialConsoleOperations: ...


namespace azure.mgmt.serialconsole.aio.operations

    class azure.mgmt.serialconsole.aio.operations.MicrosoftSerialConsoleClientOperationsMixin(MicrosoftSerialConsoleClientMixinABC):

        @distributed_trace_async
        async def disable_console(
                self, 
                default: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Union[DisableSerialConsoleResult, GetSerialConsoleSubscriptionNotFound]: ...

        @distributed_trace_async
        async def enable_console(
                self, 
                default: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Union[EnableSerialConsoleResult, GetSerialConsoleSubscriptionNotFound]: ...

        @distributed_trace_async
        async def get_console_status(
                self, 
                default: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Union[SerialConsoleStatus, GetSerialConsoleSubscriptionNotFound]: ...

        @distributed_trace_async
        async def list_operations(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SerialConsoleOperations: ...


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
                *, 
                cls: Optional[callable] = ..., 
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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SerialPort: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource: str, 
                serial_port: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource: str, 
                serial_port: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SerialPort: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SerialPortListResult: ...

        @distributed_trace_async
        async def list_by_subscriptions(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SerialPortListResult: ...


namespace azure.mgmt.serialconsole.models

    class azure.mgmt.serialconsole.models.CloudErrorBody(Model):
        code: str
        details: list[CloudErrorBody]
        message: str
        target: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[List[CloudErrorBody]] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ..., 
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


    class azure.mgmt.serialconsole.models.DisableSerialConsoleResult(Model):
        disabled: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                disabled: Optional[bool] = ..., 
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


    class azure.mgmt.serialconsole.models.EnableSerialConsoleResult(Model):
        disabled: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                disabled: Optional[bool] = ..., 
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


    class azure.mgmt.serialconsole.models.GetSerialConsoleSubscriptionNotFound(Model):
        code: str
        message: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
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


    class azure.mgmt.serialconsole.models.ProxyResource(Resource):
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


    class azure.mgmt.serialconsole.models.Resource(Model):
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


    class azure.mgmt.serialconsole.models.SerialConsoleOperations(Model):
        value: list[SerialConsoleOperationsValueItem]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[SerialConsoleOperationsValueItem]] = ..., 
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


    class azure.mgmt.serialconsole.models.SerialConsoleOperationsValueItem(Model):
        display: SerialConsoleOperationsValueItemDisplay
        is_data_action: str
        name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display: Optional[SerialConsoleOperationsValueItemDisplay] = ..., 
                is_data_action: Optional[str] = ..., 
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


    class azure.mgmt.serialconsole.models.SerialConsoleOperationsValueItemDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
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


    class azure.mgmt.serialconsole.models.SerialConsoleStatus(Model):
        disabled: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                disabled: Optional[bool] = ..., 
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


    class azure.mgmt.serialconsole.models.SerialPort(ProxyResource):
        id: str
        name: str
        state: Union[str, SerialPortState]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                state: Optional[Union[str, SerialPortState]] = ..., 
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


    class azure.mgmt.serialconsole.models.SerialPortConnectResult(Model):
        connection_string: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                connection_string: Optional[str] = ..., 
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


    class azure.mgmt.serialconsole.models.SerialPortListResult(Model):
        value: list[SerialPort]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[SerialPort]] = ..., 
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


    class azure.mgmt.serialconsole.models.SerialPortState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


namespace azure.mgmt.serialconsole.operations

    class azure.mgmt.serialconsole.operations.MicrosoftSerialConsoleClientOperationsMixin(MicrosoftSerialConsoleClientMixinABC):

        @distributed_trace
        def disable_console(
                self, 
                default: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Union[DisableSerialConsoleResult, GetSerialConsoleSubscriptionNotFound]: ...

        @distributed_trace
        def enable_console(
                self, 
                default: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Union[EnableSerialConsoleResult, GetSerialConsoleSubscriptionNotFound]: ...

        @distributed_trace
        def get_console_status(
                self, 
                default: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Union[SerialConsoleStatus, GetSerialConsoleSubscriptionNotFound]: ...

        @distributed_trace
        def list_operations(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SerialConsoleOperations: ...


    class azure.mgmt.serialconsole.operations.SerialPortsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def connect(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource: str, 
                serial_port: str, 
                *, 
                cls: Optional[callable] = ..., 
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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SerialPort: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource: str, 
                serial_port: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource: str, 
                serial_port: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SerialPort: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_type: str, 
                parent_resource: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SerialPortListResult: ...

        @distributed_trace
        def list_by_subscriptions(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SerialPortListResult: ...


```