```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.messaging.webpubsubclient

    class azure.messaging.webpubsubclient.WebPubSubClient(WebPubSubClientBase): implements ContextManager 

        def __init__(
                self, 
                credential: Union[WebPubSubClientCredential, str], 
                *, 
                ack_timeout: float = _ACK_TIMEOUT, 
                auto_rejoin_groups: bool = True, 
                logging_enable: bool = False, 
                message_retry_backoff_factor: float = _RETRY_BACKOFF_FACTOR, 
                message_retry_backoff_max: float = _RETRY_BACKOFF_MAX, 
                message_retry_mode: RetryMode = RetryMode.Exponential, 
                message_retry_total: int = _RETRY_TOTAL, 
                protocol_type: WebPubSubProtocolType = WebPubSubProtocolType.JSON_RELIABLE, 
                reconnect_retry_backoff_factor: float = _RETRY_BACKOFF_FACTOR, 
                reconnect_retry_backoff_max: float = _RETRY_BACKOFF_MAX, 
                reconnect_retry_mode: RetryMode = RetryMode.Exponential, 
                reconnect_retry_total: int = _RETRY_TOTAL, 
                start_timeout: float = _START_TIMEOUT, 
                user_agent: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        def is_connected(self) -> bool: ...

        def join_group(
                self, 
                group_name: str, 
                *, 
                ack_id: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def leave_group(
                self, 
                group_name: str, 
                *, 
                ack_id: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def open(self) -> None: ...

        @overload
        def send_event(
                self, 
                event_name: str, 
                content: str, 
                data_type: Literal[WebPubSubDataType.TEXT], 
                **kwargs: Any
            ) -> None: ...

        @overload
        def send_event(
                self, 
                event_name: str, 
                content: memoryview, 
                data_type: Literal[WebPubSubDataType.BINARY, WebPubSubDataType.PROTOBUF], 
                **kwargs: Any
            ) -> None: ...

        @overload
        def send_event(
                self, 
                event_name: str, 
                content: Dict[str, Any], 
                data_type: Literal[WebPubSubDataType.JSON], 
                **kwargs: Any
            ) -> None: ...

        @overload
        def send_to_group(
                self, 
                group_name: str, 
                content: str, 
                data_type: Literal[WebPubSubDataType.TEXT], 
                **kwargs: Any
            ) -> None: ...

        @overload
        def send_to_group(
                self, 
                group_name: str, 
                content: Dict[str, Any], 
                data_type: Literal[WebPubSubDataType.JSON], 
                **kwargs: Any
            ) -> None: ...

        @overload
        def send_to_group(
                self, 
                group_name: str, 
                content: memoryview, 
                data_type: Literal[WebPubSubDataType.BINARY, WebPubSubDataType.PROTOBUF], 
                **kwargs: Any
            ) -> None: ...

        @overload
        def subscribe(
                self, 
                event: Literal[CallbackType.CONNECTED], 
                listener: Callable[[OnConnectedArgs], None]
            ) -> None: ...

        @overload
        def subscribe(
                self, 
                event: Literal[CallbackType.DISCONNECTED], 
                listener: Callable[[OnDisconnectedArgs], None]
            ) -> None: ...

        @overload
        def subscribe(
                self, 
                event: Literal[CallbackType.STOPPED], 
                listener: Callable[[], None]
            ) -> None: ...

        @overload
        def subscribe(
                self, 
                event: Literal[CallbackType.SERVER_MESSAGE], 
                listener: Callable[[OnServerDataMessageArgs], None]
            ) -> None: ...

        @overload
        def subscribe(
                self, 
                event: Literal[CallbackType.GROUP_MESSAGE], 
                listener: Callable[[OnGroupDataMessageArgs], None]
            ) -> None: ...

        @overload
        def subscribe(
                self, 
                event: Literal[CallbackType.REJOIN_GROUP_FAILED], 
                listener: Callable[[OnRejoinGroupFailedArgs], None]
            ) -> None: ...

        @overload
        def unsubscribe(
                self, 
                event: Literal[CallbackType.CONNECTED], 
                listener: Callable[[OnConnectedArgs], None]
            ) -> None: ...

        @overload
        def unsubscribe(
                self, 
                event: Literal[CallbackType.DISCONNECTED], 
                listener: Callable[[OnDisconnectedArgs], None]
            ) -> None: ...

        @overload
        def unsubscribe(
                self, 
                event: Literal[CallbackType.STOPPED], 
                listener: Callable[[], None]
            ) -> None: ...

        @overload
        def unsubscribe(
                self, 
                event: Literal[CallbackType.SERVER_MESSAGE], 
                listener: Callable[[OnServerDataMessageArgs], None]
            ) -> None: ...

        @overload
        def unsubscribe(
                self, 
                event: Literal[CallbackType.GROUP_MESSAGE], 
                listener: Callable[[OnGroupDataMessageArgs], None]
            ) -> None: ...

        @overload
        def unsubscribe(
                self, 
                event: Literal[CallbackType.REJOIN_GROUP_FAILED], 
                listener: Callable[[OnRejoinGroupFailedArgs], None]
            ) -> None: ...


    class azure.messaging.webpubsubclient.WebPubSubClientCredential:

        def __init__(self, client_access_url_provider: Union[str, Callable]) -> None: ...

        def get_client_access_url(self) -> str: ...


namespace azure.messaging.webpubsubclient.aio

    class azure.messaging.webpubsubclient.aio.WebPubSubClient(WebPubSubClientBase): implements AsyncContextManager 

        def __init__(
                self, 
                credential: Union[WebPubSubClientCredential, str], 
                *, 
                ack_timeout: float = _ACK_TIMEOUT, 
                auto_rejoin_groups: bool = True, 
                logging_enable: bool = False, 
                message_retry_backoff_factor: float = _RETRY_BACKOFF_FACTOR, 
                message_retry_backoff_max: float = _RETRY_BACKOFF_MAX, 
                message_retry_mode: RetryMode = RetryMode.Exponential, 
                message_retry_total: int = _RETRY_TOTAL, 
                protocol_type: WebPubSubProtocolType = WebPubSubProtocolType.JSON_RELIABLE, 
                reconnect_retry_backoff_factor: float = _RETRY_BACKOFF_FACTOR, 
                reconnect_retry_backoff_max: float = _RETRY_BACKOFF_MAX, 
                reconnect_retry_mode: RetryMode = RetryMode.Exponential, 
                reconnect_retry_total: int = _RETRY_TOTAL, 
                start_timeout: float = _START_TIMEOUT, 
                user_agent: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        def is_connected(self) -> bool: ...

        async def join_group(
                self, 
                group_name: str, 
                *, 
                ack_id: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def leave_group(
                self, 
                group_name: str, 
                *, 
                ack_id: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def open(self) -> None: ...

        @overload
        async def send_event(
                self, 
                event_name: str, 
                content: str, 
                data_type: Literal[WebPubSubDataType.TEXT], 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def send_event(
                self, 
                event_name: str, 
                content: memoryview, 
                data_type: Literal[WebPubSubDataType.BINARY, WebPubSubDataType.PROTOBUF], 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def send_event(
                self, 
                event_name: str, 
                content: Dict[str, Any], 
                data_type: Literal[WebPubSubDataType.JSON], 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def send_to_group(
                self, 
                group_name: str, 
                content: str, 
                data_type: Literal[WebPubSubDataType.TEXT], 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def send_to_group(
                self, 
                group_name: str, 
                content: Dict[str, Any], 
                data_type: Literal[WebPubSubDataType.JSON], 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def send_to_group(
                self, 
                group_name: str, 
                content: memoryview, 
                data_type: Literal[WebPubSubDataType.BINARY, WebPubSubDataType.PROTOBUF], 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def subscribe(
                self, 
                event: Literal[CallbackType.CONNECTED], 
                listener: Callable[[OnConnectedArgs], Awaitable[None]]
            ) -> None: ...

        @overload
        async def subscribe(
                self, 
                event: Literal[CallbackType.DISCONNECTED], 
                listener: Callable[[OnDisconnectedArgs], Awaitable[None]]
            ) -> None: ...

        @overload
        async def subscribe(
                self, 
                event: Literal[CallbackType.STOPPED], 
                listener: Callable[[], Awaitable[None]]
            ) -> None: ...

        @overload
        async def subscribe(
                self, 
                event: Literal[CallbackType.SERVER_MESSAGE], 
                listener: Callable[[OnServerDataMessageArgs], Awaitable[None]]
            ) -> None: ...

        @overload
        async def subscribe(
                self, 
                event: Literal[CallbackType.GROUP_MESSAGE], 
                listener: Callable[[OnGroupDataMessageArgs], Awaitable[None]]
            ) -> None: ...

        @overload
        async def subscribe(
                self, 
                event: Literal[CallbackType.REJOIN_GROUP_FAILED], 
                listener: Callable[[OnRejoinGroupFailedArgs], Awaitable[None]]
            ) -> None: ...

        @overload
        async def unsubscribe(
                self, 
                event: Literal[CallbackType.CONNECTED], 
                listener: Callable[[OnConnectedArgs], Awaitable[None]]
            ) -> None: ...

        @overload
        async def unsubscribe(
                self, 
                event: Literal[CallbackType.DISCONNECTED], 
                listener: Callable[[OnDisconnectedArgs], Awaitable[None]]
            ) -> None: ...

        @overload
        async def unsubscribe(
                self, 
                event: Literal[CallbackType.STOPPED], 
                listener: Callable[[], Awaitable[None]]
            ) -> None: ...

        @overload
        async def unsubscribe(
                self, 
                event: Literal[CallbackType.SERVER_MESSAGE], 
                listener: Callable[[OnServerDataMessageArgs], Awaitable[None]]
            ) -> None: ...

        @overload
        async def unsubscribe(
                self, 
                event: Literal[CallbackType.GROUP_MESSAGE], 
                listener: Callable[[OnGroupDataMessageArgs], Awaitable[None]]
            ) -> None: ...

        @overload
        async def unsubscribe(
                self, 
                event: Literal[CallbackType.REJOIN_GROUP_FAILED], 
                listener: Callable[[OnRejoinGroupFailedArgs], Awaitable[None]]
            ) -> None: ...


    class azure.messaging.webpubsubclient.aio.WebPubSubClientCredential:

        def __init__(self, client_access_url_provider: Union[str, Callable[[], Coroutine[Any, Any, str]]]) -> None: ...

        async def get_client_access_url(self) -> str: ...


namespace azure.messaging.webpubsubclient.models

    class azure.messaging.webpubsubclient.models.AckMessageError:
        message: str
        name: str

        def __init__(
                self, 
                *, 
                message: str, 
                name: str
            ): ...


    class azure.messaging.webpubsubclient.models.CallbackType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTED = "connected"
        DISCONNECTED = "disconnected"
        GROUP_MESSAGE = "group-message"
        REJOIN_GROUP_FAILED = "rejoin-group-failed"
        SERVER_MESSAGE = "server-message"
        STOPPED = "stopped"


    class azure.messaging.webpubsubclient.models.OnConnectedArgs:
        connection_id: str
        user_id: str

        def __init__(
                self, 
                connection_id: str, 
                user_id: Optional[str] = None
            ) -> None: ...


    class azure.messaging.webpubsubclient.models.OnDisconnectedArgs:
        connection_id: str
        message: str

        def __init__(
                self, 
                connection_id: Optional[str] = None, 
                message: Optional[str] = None
            ) -> None: ...


    class azure.messaging.webpubsubclient.models.OnGroupDataMessageArgs:
        data: Any
        data_type: Union[WebPubSubDataType, str]
        from_user_id: str
        group: str
        sequence_id: int

        def __init__(
                self, 
                *, 
                data: Any, 
                data_type: WebPubSubDataType, 
                from_user_id: Optional[str] = ..., 
                group: str, 
                sequence_id: Optional[int] = ...
            ) -> None: ...


    class azure.messaging.webpubsubclient.models.OnRejoinGroupFailedArgs:
        error: Exception
        group: str

        def __init__(
                self, 
                group: str, 
                error: Exception
            ) -> None: ...


    class azure.messaging.webpubsubclient.models.OnServerDataMessageArgs:
        data: Any
        data_type: Union[WebPubSubDataType, str]
        sequence_id: int

        def __init__(
                self, 
                data_type: WebPubSubDataType, 
                data: Any, 
                sequence_id: Optional[int] = None
            ) -> None: ...


    class azure.messaging.webpubsubclient.models.OpenClientError(AzureError):


    class azure.messaging.webpubsubclient.models.SendMessageError(AzureError):
        ack_id: int
        error_detail: AckMessageError
        message: str

        def __init__(
                self, 
                message: str, 
                ack_id: Optional[int] = None, 
                error_detail: Optional[AckMessageError] = None
            ) -> None: ...


    class azure.messaging.webpubsubclient.models.WebPubSubDataType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BINARY = "binary"
        JSON = "json"
        PROTOBUF = "protobuf"
        TEXT = "text"


    class azure.messaging.webpubsubclient.models.WebPubSubProtocolType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JSON = "json.webpubsub.azure.v1"
        JSON_RELIABLE = "json.reliable.webpubsub.azure.v1"


```