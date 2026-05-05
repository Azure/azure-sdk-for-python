```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.schemaregistry

    class azure.schemaregistry.InboundMessageContent(Protocol):

        def __message_content__(self) -> MessageContent: ...


    class azure.schemaregistry.MessageContent(TypedDict):
        key "content": ForwardRef('bytes', module='_patch')
        key "content_type": ForwardRef('str', module='_patch')


    class azure.schemaregistry.OutboundMessageContent(Protocol):

        @classmethod
        def from_message_content(
                cls, 
                content: bytes, 
                content_type: str, 
                **kwargs: Any
            ) -> Self: ...


    class azure.schemaregistry.Schema:
        definition: str
        properties: SchemaProperties

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...


    class azure.schemaregistry.SchemaContentValidate(Protocol):

        def __call__(
                self, 
                schema: Mapping[str, Any], 
                content: Mapping[str, Any]
            ) -> None: ...


    class azure.schemaregistry.SchemaFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVRO = "Avro"
        CUSTOM = "Custom"
        JSON = "Json"


    class azure.schemaregistry.SchemaProperties:
        format: SchemaFormat
        group_name: str
        id: str
        name: str
        version: int

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...


    class azure.schemaregistry.SchemaRegistryClient: implements ContextManager 

        def __init__(
                self, 
                fully_qualified_namespace: str, 
                credential: TokenCredential, 
                *, 
                api_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @overload
        def get_schema(
                self, 
                schema_id: str, 
                **kwargs: Any
            ) -> Schema: ...

        @overload
        def get_schema(
                self, 
                *, 
                group_name: str, 
                name: str, 
                version: int, 
                **kwargs: Any
            ) -> Schema: ...

        @distributed_trace
        def get_schema_properties(
                self, 
                group_name: str, 
                name: str, 
                definition: str, 
                format: Union[str, SchemaFormat], 
                **kwargs: Any
            ) -> SchemaProperties: ...

        @distributed_trace
        def register_schema(
                self, 
                group_name: str, 
                name: str, 
                definition: str, 
                format: Union[str, SchemaFormat], 
                **kwargs: Any
            ) -> SchemaProperties: ...


namespace azure.schemaregistry.aio

    class azure.schemaregistry.aio.SchemaRegistryClient: implements AsyncContextManager 

        def __init__(
                self, 
                fully_qualified_namespace: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @overload
        async def get_schema(
                self, 
                schema_id: str, 
                **kwargs: Any
            ) -> Schema: ...

        @overload
        async def get_schema(
                self, 
                *, 
                group_name: str, 
                name: str, 
                version: int, 
                **kwargs: Any
            ) -> Schema: ...

        @distributed_trace_async
        async def get_schema_properties(
                self, 
                group_name: str, 
                name: str, 
                definition: str, 
                format: Union[str, SchemaFormat], 
                **kwargs: Any
            ) -> SchemaProperties: ...

        @distributed_trace_async
        async def register_schema(
                self, 
                group_name: str, 
                name: str, 
                definition: str, 
                format: Union[str, SchemaFormat], 
                **kwargs: Any
            ) -> SchemaProperties: ...


namespace azure.schemaregistry.encoder.jsonencoder

    class azure.schemaregistry.encoder.jsonencoder.InvalidContentError(ValueError):
        message: str

        def __init__(
                self, 
                message: str, 
                *args: Any, 
                *, 
                details: Optional[Dict[str, str]] = ..., 
            ) -> None: ...


    class azure.schemaregistry.encoder.jsonencoder.JsonSchemaEncoder: implements ContextManager 

        def __init__(
                self, 
                *, 
                client: SchemaRegistryClient, 
                group_name: Optional[str] = ..., 
                validate: Union[str, SchemaContentValidate]
            ) -> None: ...

        def close(self) -> None: ...

        def decode(
                self, 
                message: Union[MessageContent, InboundMessageContent], 
                *, 
                request_options: Optional[Dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @overload
        def encode(
                self, 
                content: Mapping[str, Any], 
                *, 
                message_type: Type[OutboundMessageContent], 
                request_options: Optional[Dict[str, Any]] = ..., 
                schema: str, 
                **kwargs: Any
            ) -> OutboundMessageContent: ...

        @overload
        def encode(
                self, 
                content: Mapping[str, Any], 
                *, 
                message_type: Type[OutboundMessageContent], 
                request_options: Optional[Dict[str, Any]] = ..., 
                schema_id: str, 
                **kwargs: Any
            ) -> OutboundMessageContent: ...

        @overload
        def encode(
                self, 
                content: Mapping[str, Any], 
                *, 
                request_options: Optional[Dict[str, Any]] = ..., 
                schema: str, 
                **kwargs: Any
            ) -> MessageContent: ...

        @overload
        def encode(
                self, 
                content: Mapping[str, Any], 
                *, 
                request_options: Optional[Dict[str, Any]] = ..., 
                schema_id: str, 
                **kwargs: Any
            ) -> MessageContent: ...


namespace azure.schemaregistry.encoder.jsonencoder.aio

    class azure.schemaregistry.encoder.jsonencoder.aio.JsonSchemaEncoder: implements AsyncContextManager 

        def __init__(
                self, 
                *, 
                client: SchemaRegistryClient, 
                group_name: Optional[str] = ..., 
                validate: Union[str, SchemaContentValidate]
            ) -> None: ...

        async def close(self) -> None: ...

        async def decode(
                self, 
                message: Union[MessageContent, InboundMessageContent], 
                *, 
                request_options: Optional[Dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @overload
        async def encode(
                self, 
                content: Mapping[str, Any], 
                *, 
                message_type: Type[OutboundMessageContent], 
                request_options: Optional[Dict[str, Any]] = ..., 
                schema: str, 
                **kwargs: Any
            ) -> OutboundMessageContent: ...

        @overload
        async def encode(
                self, 
                content: Mapping[str, Any], 
                *, 
                message_type: Type[OutboundMessageContent], 
                request_options: Optional[Dict[str, Any]] = ..., 
                schema_id: str, 
                **kwargs: Any
            ) -> OutboundMessageContent: ...

        @overload
        async def encode(
                self, 
                content: Mapping[str, Any], 
                *, 
                request_options: Optional[Dict[str, Any]] = ..., 
                schema: str, 
                **kwargs: Any
            ) -> MessageContent: ...

        @overload
        async def encode(
                self, 
                content: Mapping[str, Any], 
                *, 
                request_options: Optional[Dict[str, Any]] = ..., 
                schema_id: str, 
                **kwargs: Any
            ) -> MessageContent: ...


namespace azure.schemaregistry.models

    class azure.schemaregistry.models.SchemaContentTypeValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVRO = "application/json; serialization=Avro"
        CUSTOM = "text/plain; charset=utf-8"
        JSON = "application/json; serialization=Json"
        PROTOBUF = "text/vnd.ms.protobuf"


```