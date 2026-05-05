```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.eventhub

    def azure.eventhub.parse_connection_string(conn_str: str) -> EventHubConnectionStringProperties: ...


    class azure.eventhub.CheckpointStore:

        @abstractmethod
        def claim_ownership(
                self, 
                ownership_list: Iterable[Dict[str, Any]], 
                **kwargs: Any
            ) -> Iterable[Dict[str, Any]]: ...

        @abstractmethod
        def list_checkpoints(
                self, 
                fully_qualified_namespace: str, 
                eventhub_name: str, 
                consumer_group: str, 
                **kwargs: Any
            ) -> Iterable[Dict[str, Any]]: ...

        @abstractmethod
        def list_ownership(
                self, 
                fully_qualified_namespace: str, 
                eventhub_name: str, 
                consumer_group: str, 
                **kwargs: Any
            ) -> Iterable[Dict[str, Any]]: ...

        @abstractmethod
        def update_checkpoint(
                self, 
                checkpoint: Dict[str, Optional[Union[str, int]]], 
                **kwargs: Any
            ) -> None: ...


    class azure.eventhub.CloseReason(Enum):
        OWNERSHIP_LOST = 1
        SHUTDOWN = 0


    class azure.eventhub.EventData:
        property body: PrimitiveTypes    # Read-only
        property body_type: AmqpMessageBodyType    # Read-only
        property content_type: Optional[str]
        property correlation_id: Optional[str]
        property enqueued_time: Optional[datetime]    # Read-only
        property message: Union[Message, LegacyMessage]
        property message_id: Optional[str]
        property offset: Optional[str]    # Read-only
        property partition_key: Optional[bytes]    # Read-only
        property properties: Dict[Union[str, bytes], Any]
        property raw_amqp_message: AmqpAnnotatedMessage    # Read-only
        property sequence_number: Optional[int]    # Read-only
        property system_properties: Dict[bytes, Any]    # Read-only

        def __init__(self, body: Optional[Union[str, bytes, List[AnyStr]]] = None) -> None: ...

        def __message_content__(self) -> MessageContent: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...

        @classmethod
        def from_bytes(cls, message: bytes) -> EventData: ...

        @classmethod
        def from_message_content(
                cls, 
                content: bytes, 
                content_type: str, 
                **kwargs: Any
            ) -> EventData: ...

        def body_as_json(self, encoding: str = "UTF-8") -> Dict[str, Any]: ...

        def body_as_str(self, encoding: str = "UTF-8") -> str: ...


    class azure.eventhub.EventDataBatch:
        property message: Union[BatchMessage, LegacyBatchMessage]
        property size_in_bytes: int    # Read-only

        def __init__(
                self, 
                max_size_in_bytes: Optional[int] = None, 
                partition_id: Optional[str] = None, 
                partition_key: Optional[Union[str, bytes]] = None, 
                **kwargs: Any
            ) -> None: ...

        def __len__(self) -> int: ...

        def __repr__(self) -> str: ...

        def add(self, event_data: Union[EventData, AmqpAnnotatedMessage]) -> None: ...


    class azure.eventhub.EventHubConnectionStringProperties(DictMixin):
        property endpoint: str    # Read-only
        property eventhub_name: Optional[str]    # Read-only
        property fully_qualified_namespace: str    # Read-only
        property shared_access_key: Optional[str]    # Read-only
        property shared_access_key_name: Optional[str]    # Read-only
        property shared_access_signature: Optional[str]    # Read-only

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(
                self, 
                *, 
                endpoint: str, 
                eventhub_name: Optional[str] = ..., 
                fully_qualified_namespace: str, 
                shared_access_key: Optional[str] = ..., 
                shared_access_key_name: Optional[str] = ..., 
                shared_access_signature: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> List[Tuple[str, Any]]: ...

        def keys(self) -> List[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> List[Any]: ...


    class azure.eventhub.EventHubConsumerClient(ClientBase): implements ContextManager 

        def __init__(
                self, 
                fully_qualified_namespace: str, 
                eventhub_name: str, 
                consumer_group: str, 
                credential: CredentialTypes, 
                *, 
                auth_timeout: Optional[float] = ..., 
                checkpoint_store: Union[CheckpointStore, None] = ..., 
                connection_verify: Union[str, None] = ..., 
                custom_endpoint_address: Union[str, None] = ..., 
                idle_timeout: Optional[float] = ..., 
                load_balancing_interval: Optional[float] = ..., 
                load_balancing_strategy: Union[str, LoadBalancingStrategy] = ..., 
                logging_enable: Optional[bool] = ..., 
                partition_ownership_expiration_interval: Optional[float] = ..., 
                retry_backoff_factor: Optional[float] = ..., 
                retry_backoff_max: Optional[float] = ..., 
                retry_mode: str = ..., 
                retry_total: int = ..., 
                socket_timeout: Optional[float] = ..., 
                ssl_context: Union[SSLContext, None] = ..., 
                transport_type: TransportType = ..., 
                uamqp_transport: bool = ..., 
                user_agent: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                consumer_group: str, 
                *, 
                auth_timeout: float = 60, 
                checkpoint_store: Optional[CheckpointStore] = ..., 
                connection_verify: Optional[str] = ..., 
                custom_endpoint_address: Optional[str] = ..., 
                eventhub_name: Optional[str] = ..., 
                http_proxy: Optional[Dict[str, Union[str, int]]] = ..., 
                idle_timeout: Optional[float] = ..., 
                load_balancing_interval: float = 30, 
                load_balancing_strategy: Union[str, LoadBalancingStrategy] = LoadBalancingStrategy.GREEDY, 
                logging_enable: bool = False, 
                partition_ownership_expiration_interval: Optional[float] = ..., 
                retry_backoff_factor: float = 0.8, 
                retry_backoff_max: float = 120, 
                retry_mode: Literal["exponential", "fixed"] = "exponential", 
                retry_total: int = 3, 
                ssl_context: Optional[SSLContext] = ..., 
                transport_type: TransportType = TransportType.Amqp, 
                uamqp_transport: bool = False, 
                user_agent: Optional[str] = ..., 
                **kwargs: Any
            ) -> EventHubConsumerClient: ...

        def close(self) -> None: ...

        def get_eventhub_properties(self) -> Dict[str, Any]: ...

        def get_partition_ids(self) -> List[str]: ...

        def get_partition_properties(self, partition_id: str) -> Dict[str, Any]: ...

        def receive(
                self, 
                on_event: Callable[[PartitionContext, Optional[EventData]], None], 
                *, 
                max_wait_time: Optional[float] = ..., 
                on_error: Optional[Callable[[PartitionContext, Exception], None]] = ..., 
                on_partition_close: Optional[Callable[[PartitionContext, CloseReason], None]] = ..., 
                on_partition_initialize: Optional[Callable[[PartitionContext], None]] = ..., 
                owner_level: Optional[int] = ..., 
                partition_id: Optional[str] = ..., 
                prefetch: int = 300, 
                starting_position: Optional[Union[str, int, datetime, Dict[str, Any]]] = ..., 
                starting_position_inclusive: Union[bool, Dict[str, bool]] = False, 
                track_last_enqueued_event_properties: bool = False, 
                **kwargs: Any
            ) -> None: ...

        def receive_batch(
                self, 
                on_event_batch: Callable[[PartitionContext, List[EventData]], None], 
                *, 
                max_batch_size: int = 300, 
                max_wait_time: Optional[float] = ..., 
                on_error: Optional[Callable[[PartitionContext, Exception], None]] = ..., 
                on_partition_close: Optional[Callable[[PartitionContext, CloseReason], None]] = ..., 
                on_partition_initialize: Optional[Callable[[PartitionContext], None]] = ..., 
                owner_level: Optional[int] = ..., 
                partition_id: Optional[str] = ..., 
                prefetch: int = 300, 
                starting_position: Optional[Union[str, int, datetime, Dict[str, Any]]] = ..., 
                starting_position_inclusive: Union[bool, Dict[str, bool]] = False, 
                track_last_enqueued_event_properties: bool = False, 
                **kwargs: Any
            ) -> None: ...


    class azure.eventhub.EventHubProducerClient(ClientBase): implements ContextManager 
        property total_buffered_event_count: Optional[int]    # Read-only

        @overload
        def __init__(
                self, 
                fully_qualified_namespace: str, 
                eventhub_name: str, 
                credential: CredentialTypes, 
                *, 
                auth_timeout: Optional[float] = ..., 
                buffer_concurrency: Union[ThreadPoolExecutor, int, None] = ..., 
                buffered_mode: Literal[False] = False, 
                connection_verify: Optional[str] = ..., 
                custom_endpoint_address: Optional[str] = ..., 
                http_proxy: Optional[Dict] = ..., 
                idle_timeout: Optional[float] = ..., 
                logging_enable: Optional[bool] = ..., 
                max_buffer_length: Optional[int] = ..., 
                max_wait_time: Optional[float] = ..., 
                on_error: Optional[Callable[[SendEventTypes, Optional[str], Exception], None]] = ..., 
                on_success: Optional[Callable[[SendEventTypes, Optional[str]], None]] = ..., 
                retry_backoff_factor: Optional[float] = ..., 
                retry_backoff_max: Optional[float] = ..., 
                retry_mode: str = ..., 
                retry_total: int = ..., 
                socket_timeout: Optional[float] = ..., 
                ssl_context: Union[SSLContext, None] = ..., 
                transport_type: TransportType = ..., 
                uamqp_transport: bool = ..., 
                user_agent: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def __init__(
                self, 
                fully_qualified_namespace: str, 
                eventhub_name: str, 
                credential: CredentialTypes, 
                *, 
                auth_timeout: Optional[float] = ..., 
                buffer_concurrency: Optional[Union[ThreadPoolExecutor, int]] = ..., 
                buffered_mode: Literal[True], 
                connection_verify: Optional[str] = ..., 
                custom_endpoint_address: Optional[str] = ..., 
                http_proxy: Optional[Dict] = ..., 
                idle_timeout: Optional[float] = ..., 
                logging_enable: Optional[bool] = ..., 
                max_buffer_length: int = 1500, 
                max_wait_time: float = 1, 
                on_error: Callable[[SendEventTypes, Optional[str], Exception], None], 
                on_success: Callable[[SendEventTypes, Optional[str]], None], 
                retry_backoff_factor: Optional[float] = ..., 
                retry_backoff_max: Optional[float] = ..., 
                retry_mode: str = ..., 
                retry_total: int = ..., 
                socket_timeout: Optional[float] = ..., 
                ssl_context: Union[SSLContext, None] = ..., 
                transport_type: TransportType = ..., 
                uamqp_transport: bool = ..., 
                user_agent: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        @overload
        def from_connection_string(
                cls, 
                conn_str: str, 
                *, 
                buffered_mode: Literal[False] = False, 
                eventhub_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> EventHubProducerClient: ...

        @classmethod
        @overload
        def from_connection_string(
                cls, 
                conn_str: str, 
                *, 
                buffer_concurrency: Optional[Union[ThreadPoolExecutor, int]] = ..., 
                buffered_mode: Literal[True], 
                eventhub_name: Optional[str] = ..., 
                max_buffer_length: int = 1500, 
                max_wait_time: float = 1, 
                on_error: Callable[[SendEventTypes, Optional[str], Exception], None], 
                on_success: Callable[[SendEventTypes, Optional[str]], None], 
                **kwargs: Any
            ) -> EventHubProducerClient: ...

        def close(
                self, 
                *, 
                flush: bool = True, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def create_batch(
                self, 
                *, 
                max_size_in_bytes: Optional[int] = ..., 
                partition_id: Optional[str] = ..., 
                partition_key: Optional[str] = ..., 
                **kwargs: Any
            ) -> EventDataBatch: ...

        def flush(
                self, 
                *, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def get_buffered_event_count(self, partition_id: str) -> Optional[int]: ...

        def get_eventhub_properties(self) -> Dict[str, Any]: ...

        def get_partition_ids(self) -> List[str]: ...

        def get_partition_properties(self, partition_id: str) -> Dict[str, Any]: ...

        def send_batch(
                self, 
                event_data_batch: Union[EventDataBatch, SendEventTypes], 
                *, 
                partition_id: Optional[str] = ..., 
                partition_key: Optional[str] = ..., 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def send_event(
                self, 
                event_data: Union[EventData, AmqpAnnotatedMessage], 
                *, 
                partition_id: Optional[str] = ..., 
                partition_key: Optional[str] = ..., 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.eventhub.EventHubSharedKeyCredential:

        def __init__(
                self, 
                policy: str, 
                key: str
            ) -> None: ...

        def get_token(
                self, 
                *scopes: str, 
                **kwargs: Any
            ) -> AccessToken: ...


    class azure.eventhub.LoadBalancingStrategy(Enum):
        BALANCED = "balanced"
        GREEDY = "greedy"


    class azure.eventhub.PartitionContext:
        property last_enqueued_event_properties: Optional[Dict[str, Any]]    # Read-only

        def __init__(
                self, 
                fully_qualified_namespace: str, 
                eventhub_name: str, 
                consumer_group: str, 
                partition_id: str, 
                checkpoint_store: Optional[CheckpointStore] = None
            ) -> None: ...

        def update_checkpoint(
                self, 
                event: Optional[EventData] = None, 
                **kwargs: Any
            ) -> None: ...


    class azure.eventhub.TransportType(Enum):
        Amqp = 1
        AmqpOverWebsocket = 2


namespace azure.eventhub.aio

    class azure.eventhub.aio.CheckpointStore(ABC):

        @abstractmethod
        async def claim_ownership(
                self, 
                ownership_list: Iterable[Dict[str, Any]], 
                **kwargs: Any
            ) -> Iterable[Dict[str, Any]]: ...

        @abstractmethod
        async def list_checkpoints(
                self, 
                fully_qualified_namespace: str, 
                eventhub_name: str, 
                consumer_group: str, 
                **kwargs: Any
            ) -> Iterable[Dict[str, Any]]: ...

        @abstractmethod
        async def list_ownership(
                self, 
                fully_qualified_namespace: str, 
                eventhub_name: str, 
                consumer_group: str, 
                **kwargs: Any
            ) -> Iterable[Dict[str, Any]]: ...

        @abstractmethod
        async def update_checkpoint(
                self, 
                checkpoint: Dict[str, Optional[Union[str, int]]], 
                **kwargs: Any
            ) -> None: ...


    class azure.eventhub.aio.EventHubConsumerClient(ClientBaseAsync): implements AsyncContextManager 

        def __enter__(self) -> None: ...

        def __init__(
                self, 
                fully_qualified_namespace: str, 
                eventhub_name: str, 
                consumer_group: str, 
                credential: CredentialTypes, 
                *, 
                auth_timeout: Optional[float] = ..., 
                checkpoint_store: Optional[CheckpointStore] = ..., 
                connection_verify: Optional[str] = ..., 
                custom_endpoint_address: Optional[str] = ..., 
                http_proxy: Union[dict[str, str], dict[str, int], None] = ..., 
                idle_timeout: Optional[float] = ..., 
                load_balancing_interval: Optional[float] = ..., 
                load_balancing_strategy: Union[str, LoadBalancingStrategy] = ..., 
                logging_enable: Optional[bool] = ..., 
                partition_ownership_expiration_interval: Optional[float] = ..., 
                retry_backoff_factor: Optional[float] = ..., 
                retry_backoff_max: Optional[float] = ..., 
                retry_mode: str = ..., 
                retry_total: int = ..., 
                socket_timeout: Optional[float] = ..., 
                ssl_context: Union[SSLContext, None] = ..., 
                transport_type: TransportType = ..., 
                uamqp_transport: bool = ..., 
                user_agent: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                consumer_group: str, 
                *, 
                auth_timeout: float = 60, 
                checkpoint_store: Optional[CheckpointStore] = ..., 
                connection_verify: Optional[str] = ..., 
                custom_endpoint_address: Optional[str] = ..., 
                eventhub_name: Optional[str] = ..., 
                http_proxy: Optional[Dict[str, Union[str, int]]] = ..., 
                idle_timeout: Optional[float] = ..., 
                load_balancing_interval: float = 30, 
                load_balancing_strategy: Union[str, LoadBalancingStrategy] = LoadBalancingStrategy.GREEDY, 
                logging_enable: bool = False, 
                partition_ownership_expiration_interval: Optional[float] = ..., 
                retry_backoff_factor: float = 0.8, 
                retry_backoff_max: float = 120, 
                retry_mode: Literal["exponential", "fixed"] = "exponential", 
                retry_total: int = 3, 
                ssl_context: Optional[SSLContext] = ..., 
                transport_type: TransportType = TransportType.Amqp, 
                uamqp_transport: bool = False, 
                user_agent: Optional[str] = ..., 
                **kwargs: Any
            ) -> EventHubConsumerClient: ...

        async def close(self) -> None: ...

        async def get_eventhub_properties(self) -> Dict[str, Any]: ...

        async def get_partition_ids(self) -> List[str]: ...

        async def get_partition_properties(self, partition_id: str) -> Dict[str, Any]: ...

        async def receive(
                self, 
                on_event: Callable[[PartitionContext, Optional[EventData]], Awaitable[None]], 
                *, 
                max_wait_time: Optional[float] = ..., 
                on_error: Optional[Callable[[PartitionContext, Exception], Awaitable[None]]] = ..., 
                on_partition_close: Optional[Callable[[PartitionContext, CloseReason], Awaitable[None]]] = ..., 
                on_partition_initialize: Optional[Callable[[PartitionContext], Awaitable[None]]] = ..., 
                owner_level: Optional[int] = ..., 
                partition_id: Optional[str] = ..., 
                prefetch: int = 300, 
                starting_position: Optional[Union[str, int, datetime, Dict[str, Any]]] = ..., 
                starting_position_inclusive: Union[bool, Dict[str, bool]] = False, 
                track_last_enqueued_event_properties: bool = False
            ) -> None: ...

        async def receive_batch(
                self, 
                on_event_batch: Callable[[PartitionContext, List[EventData]], Awaitable[None]], 
                *, 
                max_batch_size: int = 300, 
                max_wait_time: Optional[float] = ..., 
                on_error: Optional[Callable[[PartitionContext, Exception], Awaitable[None]]] = ..., 
                on_partition_close: Optional[Callable[[PartitionContext, CloseReason], Awaitable[None]]] = ..., 
                on_partition_initialize: Optional[Callable[[PartitionContext], Awaitable[None]]] = ..., 
                owner_level: Optional[int] = ..., 
                partition_id: Optional[str] = ..., 
                prefetch: int = 300, 
                starting_position: Optional[Union[str, int, datetime, Dict[str, Any]]] = ..., 
                starting_position_inclusive: Union[bool, Dict[str, bool]] = False, 
                track_last_enqueued_event_properties: bool = False
            ) -> None: ...


    class azure.eventhub.aio.EventHubProducerClient(ClientBaseAsync): implements AsyncContextManager 
        property total_buffered_event_count: Optional[int]    # Read-only

        def __enter__(self) -> None: ...

        @overload
        def __init__(
                self, 
                fully_qualified_namespace: str, 
                eventhub_name: str, 
                credential: CredentialTypes, 
                *, 
                auth_timeout: Optional[float] = ..., 
                buffered_mode: Literal[False] = False, 
                connection_verify: Optional[str] = ..., 
                custom_endpoint_address: Optional[str] = ..., 
                http_proxy: Optional[dict] = ..., 
                idle_timeout: Optional[float] = ..., 
                logging_enable: Optional[bool] = ..., 
                max_buffer_length: Optional[int] = ..., 
                max_wait_time: Optional[float] = ..., 
                on_error: Optional[Callable[[SendEventTypes, Optional[str], Exception], Awaitable[None]]] = ..., 
                on_success: Optional[Callable[[SendEventTypes, Optional[str]], Awaitable[None]]] = ..., 
                retry_backoff_factor: Optional[float] = ..., 
                retry_backoff_max: Optional[float] = ..., 
                retry_mode: str = ..., 
                retry_total: int = ..., 
                socket_timeout: Optional[float] = ..., 
                ssl_context: Union[SSLContext, None] = ..., 
                transport_type: TransportType = ..., 
                uamqp_transport: bool = ..., 
                user_agent: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def __init__(
                self, 
                fully_qualified_namespace: str, 
                eventhub_name: str, 
                credential: CredentialTypes, 
                *, 
                auth_timeout: Optional[float] = ..., 
                buffered_mode: Literal[True], 
                connection_verify: Optional[str] = ..., 
                custom_endpoint_address: Optional[str] = ..., 
                http_proxy: Optional[dict] = ..., 
                idle_timeout: Optional[float] = ..., 
                logging_enable: Optional[bool] = ..., 
                max_buffer_length: int = 1500, 
                max_wait_time: float = 1, 
                on_error: Callable[[SendEventTypes, Optional[str], Exception], Awaitable[None]], 
                on_success: Callable[[SendEventTypes, Optional[str]], Awaitable[None]], 
                retry_backoff_factor: Optional[float] = ..., 
                retry_backoff_max: Optional[float] = ..., 
                retry_mode: str = ..., 
                retry_total: int = ..., 
                socket_timeout: Optional[float] = ..., 
                ssl_context: Union[SSLContext, None] = ..., 
                transport_type: TransportType = ..., 
                uamqp_transport: bool = ..., 
                user_agent: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        @overload
        def from_connection_string(
                cls, 
                conn_str: str, 
                *, 
                buffered_mode: Literal[False] = False, 
                eventhub_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> EventHubProducerClient: ...

        @classmethod
        @overload
        def from_connection_string(
                cls, 
                conn_str: str, 
                *, 
                buffered_mode: Literal[True], 
                eventhub_name: Optional[str] = ..., 
                max_buffer_length: int = 1500, 
                max_wait_time: float = 1, 
                on_error: Callable[[SendEventTypes, Optional[str], Exception], Awaitable[None]], 
                on_success: Callable[[SendEventTypes, Optional[str]], Awaitable[None]], 
                **kwargs: Any
            ) -> EventHubProducerClient: ...

        async def close(
                self, 
                *, 
                flush: bool = True, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def create_batch(
                self, 
                *, 
                max_size_in_bytes: Optional[int] = ..., 
                partition_id: Optional[str] = ..., 
                partition_key: Optional[str] = ...
            ) -> EventDataBatch: ...

        async def flush(
                self, 
                *, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def get_buffered_event_count(self, partition_id: str) -> Optional[int]: ...

        async def get_eventhub_properties(self) -> Dict[str, Any]: ...

        async def get_partition_ids(self) -> List[str]: ...

        async def get_partition_properties(self, partition_id: str) -> Dict[str, Any]: ...

        async def send_batch(
                self, 
                event_data_batch: Union[EventDataBatch, SendEventTypes], 
                *, 
                partition_id: Optional[str] = ..., 
                partition_key: Optional[str] = ..., 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def send_event(
                self, 
                event_data: Union[EventData, AmqpAnnotatedMessage], 
                *, 
                partition_id: Optional[str] = ..., 
                partition_key: Optional[str] = ..., 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.eventhub.aio.EventHubSharedKeyCredential:

        def __init__(
                self, 
                policy: str, 
                key: str
            ): ...

        async def get_token(
                self, 
                *scopes: str, 
                **kwargs: Any
            ) -> AccessToken: ...


    class azure.eventhub.aio.PartitionContext:
        property last_enqueued_event_properties: Optional[Dict[str, Any]]    # Read-only

        def __init__(
                self, 
                fully_qualified_namespace: str, 
                eventhub_name: str, 
                consumer_group: str, 
                partition_id: str, 
                checkpoint_store: Optional[CheckpointStore] = None
            ) -> None: ...

        async def update_checkpoint(
                self, 
                event: Optional[EventData] = None, 
                **kwargs: Any
            ) -> None: ...


namespace azure.eventhub.amqp

    class azure.eventhub.amqp.AmqpAnnotatedMessage:
        property annotations: Optional[Dict[Union[str, bytes], Any]]
        property application_properties: Optional[Dict[Union[str, bytes], Any]]
        property body: Any    # Read-only
        property body_type: AmqpMessageBodyType    # Read-only
        property delivery_annotations: Optional[Dict[Union[str, bytes], Any]]
        property footer: Optional[Dict[Any, Any]]
        property header: Optional[AmqpMessageHeader]
        property properties: Optional[AmqpMessageProperties]

        def __init__(
                self, 
                *, 
                annotations: Optional[Dict] = ..., 
                application_properties: Optional[Dict] = ..., 
                data_body: Union[str, bytes, List[Union[str, bytes]]] = ..., 
                delivery_annotations: Optional[Dict] = ..., 
                footer: Optional[Dict] = ..., 
                header: Optional[AmqpMessageHeader] = ..., 
                properties: Optional[AmqpMessageProperties] = ..., 
                sequence_body: List[Any] = ..., 
                value_body: Any = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...


    class azure.eventhub.amqp.AmqpMessageBodyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA = "data"
        SEQUENCE = "sequence"
        VALUE = "value"


    class azure.eventhub.amqp.AmqpMessageHeader(DictMixin):
        delivery_count: Optional[int]
        durable: Optional[bool]
        first_acquirer: Optional[bool]
        priority: Optional[int]
        time_to_live: Optional[int]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(
                self, 
                *, 
                delivery_count: Optional[int] = ..., 
                durable: Optional[bool] = ..., 
                first_acquirer: Optional[bool] = ..., 
                priority: Optional[int] = ..., 
                time_to_live: Optional[int] = ..., 
                **kwargs
            ): ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> List[Tuple[str, Any]]: ...

        def keys(self) -> List[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> List[Any]: ...


    class azure.eventhub.amqp.AmqpMessageProperties(DictMixin):
        absolute_expiry_time: Optional[int]
        content_encoding: Optional[bytes]
        content_type: Optional[bytes]
        correlation_id: Optional[bytes]
        creation_time: Optional[int]
        group_id: Optional[bytes]
        group_sequence: Optional[int]
        message_id: Optional[bytes]
        reply_to: Optional[bytes]
        reply_to_group_id: Optional[bytes]
        subject: Optional[bytes]
        to: Optional[bytes]
        user_id: Optional[bytes]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(
                self, 
                *, 
                absolute_expiry_time: Optional[int] = ..., 
                content_encoding: Optional[Union[str, bytes]] = ..., 
                content_type: Optional[Union[str, bytes]] = ..., 
                correlation_id: Optional[Union[str, bytes]] = ..., 
                creation_time: Optional[int] = ..., 
                group_id: Optional[Union[str, bytes]] = ..., 
                group_sequence: Optional[int] = ..., 
                message_id: Optional[Union[str, bytes, uuid.UUID]] = ..., 
                reply_to: Optional[Union[str, bytes]] = ..., 
                reply_to_group_id: Optional[Union[str, bytes]] = ..., 
                subject: Optional[Union[str, bytes]] = ..., 
                to: Optional[Union[str, bytes]] = ..., 
                user_id: Optional[Union[str, bytes]] = ..., 
                **kwargs
            ): ...

        def __len__(self) -> int: ...

        def __ne__(self, other: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def get(
                self, 
                key: str, 
                default: Optional[Any] = None
            ) -> Any: ...

        def has_key(self, k: str) -> bool: ...

        def items(self) -> List[Tuple[str, Any]]: ...

        def keys(self) -> List[str]: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def values(self) -> List[Any]: ...


namespace azure.eventhub.exceptions

    class azure.eventhub.exceptions.AuthenticationError(ConnectError):

        def __init__(
                self, 
                message: str, 
                details: Optional[List[str]] = None
            ) -> None: ...


    class azure.eventhub.exceptions.ClientClosedError(EventHubError):

        def __init__(
                self, 
                message: str, 
                details: Optional[List[str]] = None
            ) -> None: ...


    class azure.eventhub.exceptions.ConnectError(EventHubError):

        def __init__(
                self, 
                message: str, 
                details: Optional[List[str]] = None
            ) -> None: ...


    class azure.eventhub.exceptions.ConnectionLostError(EventHubError):

        def __init__(
                self, 
                message: str, 
                details: Optional[List[str]] = None
            ) -> None: ...


    class azure.eventhub.exceptions.EventDataError(EventHubError):

        def __init__(
                self, 
                message: str, 
                details: Optional[List[str]] = None
            ) -> None: ...


    class azure.eventhub.exceptions.EventDataSendError(EventHubError):

        def __init__(
                self, 
                message: str, 
                details: Optional[List[str]] = None
            ) -> None: ...


    class azure.eventhub.exceptions.EventHubError(Exception):
        details: list[str]
        error: str
        message: str

        def __init__(
                self, 
                message: str, 
                details: Optional[List[str]] = None
            ) -> None: ...


    class azure.eventhub.exceptions.OperationTimeoutError(EventHubError):

        def __init__(
                self, 
                message: str, 
                details: Optional[List[str]] = None
            ) -> None: ...


    class azure.eventhub.exceptions.OwnershipLostError(Exception):


```