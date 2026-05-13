```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.schemaregistry.encoder.avroencoder

    class azure.schemaregistry.encoder.avroencoder.AvroEncoder: implements ContextManager 

        def __init__(
                self, 
                *, 
                auto_register: bool = False, 
                client: SchemaRegistryClient, 
                group_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        def decode(
                self, 
                message: Union[MessageContent, MessageType], 
                *, 
                readers_schema: Optional[str] = ..., 
                request_options: Optional[Dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @overload
        def encode(
                self, 
                content: Mapping[str, Any], 
                *, 
                message_type: Type[MessageType], 
                request_options: Optional[Dict[str, Any]] = ..., 
                schema: str, 
                **kwargs: Any
            ) -> MessageType: ...

        @overload
        def encode(
                self, 
                content: Mapping[str, Any], 
                *, 
                message_type: None = ..., 
                request_options: Optional[Dict[str, Any]] = ..., 
                schema: str, 
                **kwargs: Any
            ) -> MessageContent: ...


    class azure.schemaregistry.encoder.avroencoder.InvalidContentError(ValueError):
        details: dict
        message: str

        def __init__(
                self, 
                message: str, 
                *args: Any, 
                *, 
                details: Optional[Dict[str, str]] = ..., 
                error = ..., 
            ) -> None: ...


    class azure.schemaregistry.encoder.avroencoder.InvalidSchemaError(ValueError):
        details: dict
        message: str

        def __init__(
                self, 
                message: str, 
                *args: Any, 
                *, 
                details: Optional[Dict[str, str]] = ..., 
                error = ..., 
            ) -> None: ...


    class azure.schemaregistry.encoder.avroencoder.MessageContent(TypedDict):
        key "content": bytes
        key "content_type": str


    class azure.schemaregistry.encoder.avroencoder.MessageType(Protocol):

        def __message_content__(self) -> MessageContent: ...

        @classmethod
        def from_message_content(
                cls, 
                content: bytes, 
                content_type: str, 
                **kwargs: Any
            ) -> MessageType: ...


namespace azure.schemaregistry.encoder.avroencoder.aio

    class azure.schemaregistry.encoder.avroencoder.aio.AvroEncoder: implements AsyncContextManager 

        def __init__(
                self, 
                *, 
                auto_register: bool = False, 
                client: SchemaRegistryClient, 
                group_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        async def decode(
                self, 
                message: Union[MessageContent, MessageType], 
                *, 
                readers_schema: Optional[str] = ..., 
                request_options: Optional[Dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @overload
        async def encode(
                self, 
                content: Mapping[str, Any], 
                *, 
                message_type: Type[MessageType], 
                request_options: Optional[Dict[str, Any]] = ..., 
                schema: str, 
                **kwargs: Any
            ) -> MessageType: ...

        @overload
        async def encode(
                self, 
                content: Mapping[str, Any], 
                *, 
                message_type: None = ..., 
                request_options: Optional[Dict[str, Any]] = ..., 
                schema: str, 
                **kwargs: Any
            ) -> MessageContent: ...


```