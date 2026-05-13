```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.servicebus

    def azure.servicebus.parse_connection_string(conn_str: str) -> ServiceBusConnectionStringProperties: ...


    class azure.servicebus.AutoLockRenewer: implements ContextManager 

        def __init__(
                self, 
                max_lock_renewal_duration: float = 300, 
                on_lock_renew_failure: Optional[LockRenewFailureCallback] = None, 
                executor: Optional[ThreadPoolExecutor] = None, 
                max_workers: Optional[int] = None
            ) -> None: ...

        def close(self, wait: bool = True) -> None: ...

        def register(
                self, 
                receiver: ServiceBusReceiver, 
                renewable: Union[ServiceBusReceivedMessage, ServiceBusSession], 
                max_lock_renewal_duration: Optional[float] = None, 
                on_lock_renew_failure: Optional[LockRenewFailureCallback] = None
            ) -> None: ...


    class azure.servicebus.ServiceBusClient: implements ContextManager 
        fully_qualified_namespace: str

        def __init__(
                self, 
                fully_qualified_namespace: str, 
                credential: Union[TokenCredential, AzureSasCredential, AzureNamedKeyCredential], 
                *, 
                connection_verify: Optional[str] = ..., 
                custom_endpoint_address: Optional[str] = ..., 
                http_proxy: Optional[Dict] = ..., 
                logging_enable: Optional[bool] = ..., 
                retry_backoff_factor: float = 0.8, 
                retry_backoff_max: float = 120, 
                retry_mode: str = "exponential", 
                retry_total: int = 3, 
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
                *, 
                connection_verify: Optional[str] = ..., 
                custom_endpoint_address: Optional[str] = ..., 
                http_proxy: Optional[Dict] = ..., 
                logging_enable: Optional[bool] = ..., 
                retry_backoff_factor: float = 0.8, 
                retry_backoff_max: float = 120, 
                retry_mode: str = "exponential", 
                retry_total: int = 3, 
                ssl_context: Union[SSLContext, None] = ..., 
                transport_type: TransportType = ..., 
                uamqp_transport: bool = ..., 
                user_agent: Optional[str] = ..., 
                **kwargs: Any
            ) -> ServiceBusClient: ...

        def close(self) -> None: ...

        def get_queue_receiver(
                self, 
                queue_name: str, 
                *, 
                auto_lock_renewer: Optional[AutoLockRenewer] = ..., 
                client_identifier: Optional[str] = ..., 
                max_wait_time: Optional[float] = ..., 
                prefetch_count: int = 0, 
                receive_mode: Union[ServiceBusReceiveMode, str] = ServiceBusReceiveMode.PEEK_LOCK, 
                session_id: Optional[Union[str, NextAvailableSessionType]] = ..., 
                socket_timeout: Optional[float] = ..., 
                sub_queue: Optional[Union[ServiceBusSubQueue, str]] = ..., 
                **kwargs: Any
            ) -> ServiceBusReceiver: ...

        def get_queue_sender(
                self, 
                queue_name: str, 
                *, 
                client_identifier: Optional[str] = ..., 
                socket_timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> ServiceBusSender: ...

        def get_subscription_receiver(
                self, 
                topic_name: str, 
                subscription_name: str, 
                *, 
                auto_lock_renewer: Optional[AutoLockRenewer] = ..., 
                client_identifier: Optional[str] = ..., 
                max_wait_time: Optional[float] = ..., 
                prefetch_count: int = 0, 
                receive_mode: Union[ServiceBusReceiveMode, str] = ServiceBusReceiveMode.PEEK_LOCK, 
                session_id: Optional[Union[str, NextAvailableSessionType]] = ..., 
                socket_timeout: Optional[float] = ..., 
                sub_queue: Optional[Union[ServiceBusSubQueue, str]] = ..., 
                **kwargs: Any
            ) -> ServiceBusReceiver: ...

        def get_topic_sender(
                self, 
                topic_name: str, 
                *, 
                client_identifier: Optional[str] = ..., 
                socket_timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> ServiceBusSender: ...


    class azure.servicebus.ServiceBusConnectionStringProperties(DictMixin):
        property endpoint: str    # Read-only
        property entity_path: Optional[str]    # Read-only
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
                entity_path: Optional[str] = ..., 
                fully_qualified_namespace: str, 
                shared_access_key: Optional[str] = ..., 
                shared_access_key_name: Optional[str] = ..., 
                shared_access_signature: Optional[str] = ...
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


    class azure.servicebus.ServiceBusMessage:
        property application_properties: Optional[Dict[Union[str, bytes], PrimitiveTypes]]
        property body: Any    # Read-only
        property body_type: AmqpMessageBodyType    # Read-only
        property content_type: Optional[str]
        property correlation_id: Optional[str]
        property message: Union[Message, LegacyMessage]
        property message_id: Optional[str]
        property partition_key: Optional[str]
        property raw_amqp_message: AmqpAnnotatedMessage    # Read-only
        property reply_to: Optional[str]
        property reply_to_session_id: Optional[str]
        property scheduled_enqueue_time_utc: Optional[datetime]
        property session_id: Optional[str]
        property subject: Optional[str]
        property time_to_live: Optional[timedelta]
        property to: Optional[str]

        def __init__(
                self, 
                body: Optional[Union[str, bytes]], 
                *, 
                application_properties: Optional[Dict[Union[str, bytes], PrimitiveTypes]] = ..., 
                content_type: Optional[str] = ..., 
                correlation_id: Optional[str] = ..., 
                message_id: Optional[str] = ..., 
                partition_key: Optional[str] = ..., 
                reply_to: Optional[str] = ..., 
                reply_to_session_id: Optional[str] = ..., 
                scheduled_enqueue_time_utc: Optional[datetime] = ..., 
                session_id: Optional[str] = ..., 
                subject: Optional[str] = ..., 
                time_to_live: Optional[timedelta] = ..., 
                to: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...


    class azure.servicebus.ServiceBusMessageBatch:
        property max_size_in_bytes: int    # Read-only
        property message: Union[BatchMessage, LegacyBatchMessage]
        property size_in_bytes: int    # Read-only

        def __init__(
                self, 
                max_size_in_bytes: Optional[int] = None, 
                **kwargs: Any
            ) -> None: ...

        def __len__(self) -> int: ...

        def __repr__(self) -> str: ...

        def add_message(self, message: Union[ServiceBusMessage, AmqpAnnotatedMessage, Mapping[str, Any]]) -> None: ...


    class azure.servicebus.ServiceBusMessageState(int, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = 0
        DEFERRED = 1
        SCHEDULED = 2


    class azure.servicebus.ServiceBusReceiveMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PEEK_LOCK = "peeklock"
        RECEIVE_AND_DELETE = "receiveanddelete"


    class azure.servicebus.ServiceBusReceivedMessage(ServiceBusMessage):
        property application_properties: Optional[Dict[Union[str, bytes], PrimitiveTypes]]
        property body: Any    # Read-only
        property body_type: AmqpMessageBodyType    # Read-only
        property content_type: Optional[str]
        property correlation_id: Optional[str]
        property dead_letter_error_description: Optional[str]    # Read-only
        property dead_letter_reason: Optional[str]    # Read-only
        property dead_letter_source: Optional[str]    # Read-only
        property delivery_count: Optional[int]    # Read-only
        property enqueued_sequence_number: Optional[int]    # Read-only
        property enqueued_time_utc: Optional[datetime]    # Read-only
        property expires_at_utc: Optional[datetime]    # Read-only
        property lock_token: Optional[Union[uuid.UUID, str]]    # Read-only
        property locked_until_utc: Optional[datetime]    # Read-only
        property message: Union[Message, LegacyMessage]    # Read-only
        property message_id: Optional[str]
        property partition_key: Optional[str]
        property raw_amqp_message: AmqpAnnotatedMessage    # Read-only
        property reply_to: Optional[str]
        property reply_to_session_id: Optional[str]
        property scheduled_enqueue_time_utc: Optional[datetime]
        property sequence_number: Optional[int]    # Read-only
        property session_id: Optional[str]
        property state: ServiceBusMessageState    # Read-only
        property subject: Optional[str]
        property time_to_live: Optional[timedelta]
        property to: Optional[str]
        auto_renew_error: Union[AutoLockRenewTimeout, AutoLockRenewFailed]

        def __getstate__(self) -> Dict[str, Any]: ...

        def __init__(
                self, 
                message: Union[Message, pyamqp_Message], 
                receive_mode: Union[ServiceBusReceiveMode, str] = ServiceBusReceiveMode.PEEK_LOCK, 
                frame: Optional[TransferFrame] = None, 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __setstate__(self, state: Dict[str, Any]) -> None: ...

        def __str__(self) -> str: ...


    class azure.servicebus.ServiceBusReceiver(BaseHandler, ReceiverMixin): implements ContextManager , Iterator 
        property client_identifier: str    # Read-only
        property session: ServiceBusSession    # Read-only
        entity_path: str
        fully_qualified_namespace: str

        def __init__(
                self, 
                fully_qualified_namespace: str, 
                credential: Union[TokenCredential, AzureSasCredential, AzureNamedKeyCredential], 
                *, 
                auto_lock_renewer: Optional[AutoLockRenewer] = ..., 
                client_identifier: Optional[str] = ..., 
                http_proxy: Optional[Dict] = ..., 
                logging_enable: Optional[bool] = ..., 
                max_wait_time: Optional[float] = ..., 
                prefetch_count: int = 0, 
                queue_name: Optional[str] = ..., 
                receive_mode: Union[ServiceBusReceiveMode, str] = ServiceBusReceiveMode.PEEK_LOCK, 
                socket_timeout: Optional[float] = ..., 
                subscription_name: Optional[str] = ..., 
                topic_name: Optional[str] = ..., 
                transport_type: TransportType = ..., 
                user_agent: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def abandon_message(self, message: ServiceBusReceivedMessage) -> None: ...

        def close(self) -> None: ...

        def complete_message(self, message: ServiceBusReceivedMessage) -> None: ...

        def dead_letter_message(
                self, 
                message: ServiceBusReceivedMessage, 
                reason: Optional[str] = None, 
                error_description: Optional[str] = None
            ) -> None: ...

        def defer_message(self, message: ServiceBusReceivedMessage) -> None: ...

        def peek_messages(
                self, 
                max_message_count: int = 1, 
                *, 
                sequence_number: int = 0, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> List[ServiceBusReceivedMessage]: ...

        def receive_deferred_messages(
                self, 
                sequence_numbers: Union[int, List[int]], 
                *, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> List[ServiceBusReceivedMessage]: ...

        def receive_messages(
                self, 
                max_message_count: Optional[int] = 1, 
                max_wait_time: Optional[float] = None
            ) -> List[ServiceBusReceivedMessage]: ...

        def renew_message_lock(
                self, 
                message: ServiceBusReceivedMessage, 
                *, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> datetime: ...


    class azure.servicebus.ServiceBusSender(BaseHandler, SenderMixin): implements ContextManager 
        property client_identifier: str    # Read-only
        entity_name: str
        fully_qualified_namespace: str

        def __init__(
                self, 
                fully_qualified_namespace: str, 
                credential: Union[TokenCredential, AzureSasCredential, AzureNamedKeyCredential], 
                *, 
                client_identifier: Optional[str] = ..., 
                http_proxy: Optional[Dict] = ..., 
                logging_enable: Optional[bool] = ..., 
                queue_name: Optional[str] = ..., 
                socket_timeout: Optional[float] = ..., 
                topic_name: Optional[str] = ..., 
                transport_type: TransportType = ..., 
                user_agent: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def cancel_scheduled_messages(
                self, 
                sequence_numbers: Union[int, List[int]], 
                *, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        def create_message_batch(self, max_size_in_bytes: Optional[int] = None) -> ServiceBusMessageBatch: ...

        def schedule_messages(
                self, 
                messages: MessageTypes, 
                schedule_time_utc: datetime, 
                *, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> List[int]: ...

        def send_messages(
                self, 
                message: Union[MessageTypes, ServiceBusMessageBatch], 
                *, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.servicebus.ServiceBusSession(BaseSession):
        property locked_until_utc: Optional[datetime]    # Read-only
        property session_id: str    # Read-only
        auto_renew_error: Union[AutoLockRenewTimeout, AutoLockRenewFailed]

        def __init__(
                self, 
                session_id: str, 
                receiver: Union[ServiceBusReceiver, ServiceBusReceiverAsync]
            ) -> None: ...

        def get_state(
                self, 
                *, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> bytes: ...

        def renew_lock(
                self, 
                *, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> datetime: ...

        def set_state(
                self, 
                state: Optional[Union[str, bytes, bytearray]], 
                *, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.servicebus.ServiceBusSessionFilter(Enum):
        NEXT_AVAILABLE = 0


    class azure.servicebus.ServiceBusSubQueue(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEAD_LETTER = "deadletter"
        TRANSFER_DEAD_LETTER = "transferdeadletter"


    class azure.servicebus.TransportType(Enum):
        Amqp = 1
        AmqpOverWebsocket = 2


namespace azure.servicebus.aio

    class azure.servicebus.aio.AutoLockRenewer: implements AsyncContextManager 

        def __init__(
                self, 
                max_lock_renewal_duration: float = 300, 
                on_lock_renew_failure: Optional[AsyncLockRenewFailureCallback] = None, 
                loop: Optional[AbstractEventLoop] = None
            ) -> None: ...

        async def close(self) -> None: ...

        def register(
                self, 
                receiver: ServiceBusReceiver, 
                renewable: Union[ServiceBusReceivedMessage, ServiceBusSession], 
                max_lock_renewal_duration: Optional[float] = None, 
                on_lock_renew_failure: Optional[AsyncLockRenewFailureCallback] = None
            ) -> None: ...


    class azure.servicebus.aio.ServiceBusClient: implements AsyncContextManager 
        fully_qualified_namespace: str

        def __init__(
                self, 
                fully_qualified_namespace: str, 
                credential: Union[AsyncTokenCredential, AzureSasCredential, AzureNamedKeyCredential], 
                *, 
                connection_verify: Optional[str] = ..., 
                custom_endpoint_address: Optional[str] = ..., 
                http_proxy: Optional[Dict] = ..., 
                logging_enable: Optional[bool] = ..., 
                retry_backoff_factor: float = 0.8, 
                retry_backoff_max: float = 120, 
                retry_mode: str = "exponential", 
                retry_total: int = 3, 
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
                *, 
                connection_verify: Optional[str] = ..., 
                custom_endpoint_address: Optional[str] = ..., 
                http_proxy: Optional[Dict] = ..., 
                logging_enable: Optional[bool] = ..., 
                retry_backoff_factor: float = 0.8, 
                retry_backoff_max: float = 120, 
                retry_mode: str = "exponential", 
                retry_total: int = 3, 
                ssl_context: Union[SSLContext, None] = ..., 
                transport_type: TransportType = ..., 
                uamqp_transport: bool = ..., 
                user_agent: Optional[str] = ..., 
                **kwargs: Any
            ) -> ServiceBusClient: ...

        async def close(self) -> None: ...

        def get_queue_receiver(
                self, 
                queue_name: str, 
                *, 
                auto_lock_renewer: Optional[AutoLockRenewer] = ..., 
                client_identifier: Optional[str] = ..., 
                max_wait_time: Optional[float] = ..., 
                prefetch_count: int = 0, 
                receive_mode: Union[ServiceBusReceiveMode, str] = ServiceBusReceiveMode.PEEK_LOCK, 
                session_id: Optional[Union[str, NextAvailableSessionType]] = ..., 
                socket_timeout: Optional[float] = ..., 
                sub_queue: Optional[Union[ServiceBusSubQueue, str]] = ..., 
                **kwargs: Any
            ) -> ServiceBusReceiver: ...

        def get_queue_sender(
                self, 
                queue_name: str, 
                *, 
                client_identifier: Optional[str] = ..., 
                socket_timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> ServiceBusSender: ...

        def get_subscription_receiver(
                self, 
                topic_name: str, 
                subscription_name: str, 
                *, 
                auto_lock_renewer: Optional[AutoLockRenewer] = ..., 
                client_identifier: Optional[str] = ..., 
                max_wait_time: Optional[float] = ..., 
                prefetch_count: int = 0, 
                receive_mode: Union[ServiceBusReceiveMode, str] = ServiceBusReceiveMode.PEEK_LOCK, 
                session_id: Optional[Union[str, NextAvailableSessionType]] = ..., 
                socket_timeout: Optional[float] = ..., 
                sub_queue: Optional[Union[ServiceBusSubQueue, str]] = ..., 
                **kwargs: Any
            ) -> ServiceBusReceiver: ...

        def get_topic_sender(
                self, 
                topic_name: str, 
                *, 
                client_identifier: Optional[str] = ..., 
                socket_timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> ServiceBusSender: ...


    class azure.servicebus.aio.ServiceBusReceiver(AsyncIterator, BaseHandler, ReceiverMixin): implements AsyncContextManager , AsyncIterable , AsyncIterator 
        property client_identifier: str    # Read-only
        property session: ServiceBusSession    # Read-only
        entity_path: str
        fully_qualified_namespace: str

        def __init__(
                self, 
                fully_qualified_namespace: str, 
                credential: Union[AsyncTokenCredential, AzureSasCredential, AzureNamedKeyCredential], 
                *, 
                auto_lock_renewer: Optional[AutoLockRenewer] = ..., 
                client_identifier: Optional[str] = ..., 
                http_proxy: Optional[Dict] = ..., 
                logging_enable: Optional[bool] = ..., 
                max_wait_time: Optional[float] = ..., 
                prefetch_count: int = 0, 
                queue_name: Optional[str] = ..., 
                receive_mode: Union[ServiceBusReceiveMode, str] = ServiceBusReceiveMode.PEEK_LOCK, 
                socket_timeout: Optional[float] = ..., 
                subscription_name: Optional[str] = ..., 
                topic_name: Optional[str] = ..., 
                transport_type: TransportType = ..., 
                user_agent: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        async def abandon_message(self, message: ServiceBusReceivedMessage) -> None: ...

        async def close(self) -> None: ...

        async def complete_message(self, message: ServiceBusReceivedMessage) -> None: ...

        async def dead_letter_message(
                self, 
                message: ServiceBusReceivedMessage, 
                reason: Optional[str] = None, 
                error_description: Optional[str] = None
            ) -> None: ...

        async def defer_message(self, message: ServiceBusReceivedMessage) -> None: ...

        async def peek_messages(
                self, 
                max_message_count: int = 1, 
                *, 
                sequence_number: int = 0, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> List[ServiceBusReceivedMessage]: ...

        async def receive_deferred_messages(
                self, 
                sequence_numbers: Union[int, List[int]], 
                *, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> List[ServiceBusReceivedMessage]: ...

        async def receive_messages(
                self, 
                max_message_count: Optional[int] = 1, 
                max_wait_time: Optional[float] = None
            ) -> List[ServiceBusReceivedMessage]: ...

        async def renew_message_lock(
                self, 
                message: ServiceBusReceivedMessage, 
                *, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> datetime: ...


    class azure.servicebus.aio.ServiceBusSender(BaseHandler, SenderMixin): implements AsyncContextManager 
        property client_identifier: str    # Read-only
        entity_name: str
        fully_qualified_namespace: str

        def __init__(
                self, 
                fully_qualified_namespace: str, 
                credential: Union[AsyncTokenCredential, AzureSasCredential, AzureNamedKeyCredential], 
                *, 
                client_identifier: Optional[str] = ..., 
                http_proxy: Optional[Dict] = ..., 
                logging_enable: Optional[bool] = ..., 
                queue_name: Optional[str] = ..., 
                socket_timeout: Optional[float] = ..., 
                topic_name: Optional[str] = ..., 
                transport_type: TransportType = ..., 
                user_agent: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        async def cancel_scheduled_messages(
                self, 
                sequence_numbers: Union[int, List[int]], 
                *, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        async def create_message_batch(self, max_size_in_bytes: Optional[int] = None) -> ServiceBusMessageBatch: ...

        async def schedule_messages(
                self, 
                messages: MessageTypes, 
                schedule_time_utc: datetime, 
                *, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> List[int]: ...

        async def send_messages(
                self, 
                message: Union[MessageTypes, ServiceBusMessageBatch], 
                *, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.servicebus.aio.ServiceBusSession(BaseSession):
        property locked_until_utc: Optional[datetime]    # Read-only
        property session_id: str    # Read-only

        def __init__(
                self, 
                session_id: str, 
                receiver: Union[ServiceBusReceiver, ServiceBusReceiverAsync]
            ) -> None: ...

        async def get_state(
                self, 
                *, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> bytes: ...

        async def renew_lock(
                self, 
                *, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> datetime: ...

        async def set_state(
                self, 
                state: Optional[Union[str, bytes, bytearray]], 
                *, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...


namespace azure.servicebus.aio.management

    class azure.servicebus.aio.management.ServiceBusAdministrationClient: implements AsyncContextManager 

        def __init__(
                self, 
                fully_qualified_namespace: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: Union[str, ApiVersion] = DEFAULT_VERSION, 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                *, 
                api_version: Union[str, ApiVersion] = DEFAULT_VERSION, 
                **kwargs: Any
            ) -> ServiceBusAdministrationClient: ...

        async def close(self) -> None: ...

        async def create_queue(
                self, 
                queue_name: str, 
                *, 
                authorization_rules: Optional[List[AuthorizationRule]] = ..., 
                auto_delete_on_idle: Optional[Union[timedelta, str]] = ..., 
                dead_lettering_on_message_expiration: Optional[bool] = ..., 
                default_message_time_to_live: Optional[Union[timedelta, str]] = ..., 
                duplicate_detection_history_time_window: Optional[Union[timedelta, str]] = ..., 
                enable_batched_operations: Optional[bool] = ..., 
                enable_express: Optional[bool] = ..., 
                enable_partitioning: Optional[bool] = ..., 
                forward_dead_lettered_messages_to: Optional[str] = ..., 
                forward_to: Optional[str] = ..., 
                lock_duration: Optional[Union[timedelta, str]] = ..., 
                max_delivery_count: Optional[int] = ..., 
                max_message_size_in_kilobytes: Optional[int] = ..., 
                max_size_in_megabytes: Optional[int] = ..., 
                requires_duplicate_detection: Optional[bool] = ..., 
                requires_session: Optional[bool] = ..., 
                user_metadata: Optional[str] = ..., 
                **kwargs: Any
            ) -> QueueProperties: ...

        async def create_rule(
                self, 
                topic_name: str, 
                subscription_name: str, 
                rule_name: str, 
                *, 
                action: Optional[SqlRuleAction] = ..., 
                filter: Union[CorrelationRuleFilter, SqlRuleFilter] = TrueRuleFilter(), 
                **kwargs: Any
            ) -> RuleProperties: ...

        async def create_subscription(
                self, 
                topic_name: str, 
                subscription_name: str, 
                *, 
                auto_delete_on_idle: Optional[Union[timedelta, str]] = ..., 
                dead_lettering_on_filter_evaluation_exceptions: Optional[bool] = ..., 
                dead_lettering_on_message_expiration: Optional[bool] = ..., 
                default_message_time_to_live: Optional[Union[timedelta, str]] = ..., 
                enable_batched_operations: Optional[bool] = ..., 
                forward_dead_lettered_messages_to: Optional[str] = ..., 
                forward_to: Optional[str] = ..., 
                lock_duration: Optional[Union[timedelta, str]] = ..., 
                max_delivery_count: Optional[int] = ..., 
                requires_session: Optional[bool] = ..., 
                user_metadata: Optional[str] = ..., 
                **kwargs: Any
            ) -> SubscriptionProperties: ...

        async def create_topic(
                self, 
                topic_name: str, 
                *, 
                authorization_rules: Optional[List[AuthorizationRule]] = ..., 
                auto_delete_on_idle: Optional[Union[timedelta, str]] = ..., 
                default_message_time_to_live: Optional[Union[timedelta, str]] = ..., 
                duplicate_detection_history_time_window: Optional[Union[timedelta, str]] = ..., 
                enable_batched_operations: Optional[bool] = ..., 
                enable_express: Optional[bool] = ..., 
                enable_partitioning: Optional[bool] = ..., 
                filtering_messages_before_publishing: Optional[bool] = ..., 
                max_message_size_in_kilobytes: Optional[int] = ..., 
                max_size_in_megabytes: Optional[int] = ..., 
                requires_duplicate_detection: Optional[bool] = ..., 
                size_in_bytes: Optional[int] = ..., 
                support_ordering: Optional[bool] = ..., 
                user_metadata: Optional[str] = ..., 
                **kwargs: Any
            ) -> TopicProperties: ...

        async def delete_queue(
                self, 
                queue_name: str, 
                **kwargs: Any
            ) -> None: ...

        async def delete_rule(
                self, 
                topic_name: str, 
                subscription_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        async def delete_subscription(
                self, 
                topic_name: str, 
                subscription_name: str, 
                **kwargs: Any
            ) -> None: ...

        async def delete_topic(
                self, 
                topic_name: str, 
                **kwargs: Any
            ) -> None: ...

        async def get_namespace_properties(self, **kwargs: Any) -> NamespaceProperties: ...

        async def get_queue(
                self, 
                queue_name: str, 
                **kwargs: Any
            ) -> QueueProperties: ...

        async def get_queue_runtime_properties(
                self, 
                queue_name: str, 
                **kwargs: Any
            ) -> QueueRuntimeProperties: ...

        async def get_rule(
                self, 
                topic_name: str, 
                subscription_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> RuleProperties: ...

        async def get_subscription(
                self, 
                topic_name: str, 
                subscription_name: str, 
                **kwargs: Any
            ) -> SubscriptionProperties: ...

        async def get_subscription_runtime_properties(
                self, 
                topic_name: str, 
                subscription_name: str, 
                **kwargs: Any
            ) -> SubscriptionRuntimeProperties: ...

        async def get_topic(
                self, 
                topic_name: str, 
                **kwargs: Any
            ) -> TopicProperties: ...

        async def get_topic_runtime_properties(
                self, 
                topic_name: str, 
                **kwargs: Any
            ) -> TopicRuntimeProperties: ...

        def list_queues(self, **kwargs: Any) -> AsyncItemPaged[QueueProperties]: ...

        def list_queues_runtime_properties(self, **kwargs: Any) -> AsyncItemPaged[QueueRuntimeProperties]: ...

        def list_rules(
                self, 
                topic_name: str, 
                subscription_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RuleProperties]: ...

        def list_subscriptions(
                self, 
                topic_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SubscriptionProperties]: ...

        def list_subscriptions_runtime_properties(
                self, 
                topic_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SubscriptionRuntimeProperties]: ...

        def list_topics(self, **kwargs: Any) -> AsyncItemPaged[TopicProperties]: ...

        def list_topics_runtime_properties(self, **kwargs: Any) -> AsyncItemPaged[TopicRuntimeProperties]: ...

        async def update_queue(
                self, 
                queue: Union[QueueProperties, Mapping[str, Any]], 
                **kwargs: Any
            ) -> None: ...

        async def update_rule(
                self, 
                topic_name: str, 
                subscription_name: str, 
                rule: Union[RuleProperties, Mapping[str, Any]], 
                **kwargs: Any
            ) -> None: ...

        async def update_subscription(
                self, 
                topic_name: str, 
                subscription: Union[SubscriptionProperties, Mapping[str, Any]], 
                **kwargs: Any
            ) -> None: ...

        async def update_topic(
                self, 
                topic: Union[TopicProperties, Mapping[str, Any]], 
                **kwargs: Any
            ) -> None: ...


namespace azure.servicebus.amqp

    class azure.servicebus.amqp.AmqpAnnotatedMessage:
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
                annotations: Optional[Dict[str, Any]] = ..., 
                application_properties: Optional[Dict[str, Any]] = ..., 
                data_body: Union[str, bytes, list[str, bytes]] = ..., 
                delivery_annotations: Optional[Dict[str, Any]] = ..., 
                footer: Optional[Dict[str, Any]] = ..., 
                header: Optional[Union[AmqpMessageHeader, Mapping[str, Any]]] = ..., 
                properties: Optional[Union[AmqpMessageProperties, Mapping[str, Any]]] = ..., 
                sequence_body: list[any] = ..., 
                value_body: any = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def __str__(self) -> str: ...


    class azure.servicebus.amqp.AmqpMessageBodyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA = "data"
        SEQUENCE = "sequence"
        VALUE = "value"


    class azure.servicebus.amqp.AmqpMessageHeader(DictMixin):
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
                **kwargs: Any
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


    class azure.servicebus.amqp.AmqpMessageProperties(DictMixin):
        absolute_expiry_time: Optional[int]
        content_encoding: Optional[Union[str, bytes]]
        content_type: Optional[Union[str, bytes]]
        correlation_id: Optional[Union[str, bytes]]
        creation_time: Optional[int]
        group_id: Optional[Union[str, bytes]]
        group_sequence: Optional[int]
        message_id: Optional[Union[str, bytes, uuid.UUID]]
        reply_to: Optional[Union[str, bytes]]
        reply_to_group_id: Optional[Union[str, bytes]]
        subject: Optional[Union[str, bytes]]
        to: Optional[Union[str, bytes]]
        user_id: Optional[Union[str, bytes]]

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
                **kwargs: Any
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


namespace azure.servicebus.exceptions

    class azure.servicebus.exceptions.AutoLockRenewFailed(ServiceBusError):

        def __init__(
                self, 
                message: Optional[Union[str, bytes]], 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.servicebus.exceptions.AutoLockRenewTimeout(ServiceBusError):

        def __init__(
                self, 
                message: Optional[Union[str, bytes]], 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.servicebus.exceptions.MessageAlreadySettled(ValueError):

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.servicebus.exceptions.MessageLockLostError(ServiceBusError):

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.servicebus.exceptions.MessageNotFoundError(ServiceBusError):

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.servicebus.exceptions.MessageSizeExceededError(ServiceBusError, ValueError):

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.servicebus.exceptions.MessagingEntityAlreadyExistsError(ServiceBusError):

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.servicebus.exceptions.MessagingEntityDisabledError(ServiceBusError):

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.servicebus.exceptions.MessagingEntityNotFoundError(ServiceBusError):

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.servicebus.exceptions.OperationTimeoutError(ServiceBusError):

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.servicebus.exceptions.ServiceBusAuthenticationError(ServiceBusError):

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.servicebus.exceptions.ServiceBusAuthorizationError(ServiceBusError):

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.servicebus.exceptions.ServiceBusCommunicationError(ServiceBusError):

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.servicebus.exceptions.ServiceBusConnectionError(ServiceBusError):

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.servicebus.exceptions.ServiceBusError(AzureError):
        exc_msg
        exc_traceback
        exc_type
        exc_value
        message: str

        def __init__(
                self, 
                message: Optional[Union[str, bytes]], 
                *args: Any, 
                *, 
                error: Exception = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.servicebus.exceptions.ServiceBusQuotaExceededError(ServiceBusError):

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.servicebus.exceptions.ServiceBusServerBusyError(ServiceBusError):

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.servicebus.exceptions.SessionCannotBeLockedError(ServiceBusError):

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.servicebus.exceptions.SessionLockLostError(ServiceBusError):

        def __init__(self, **kwargs: Any) -> None: ...


namespace azure.servicebus.management

    class azure.servicebus.management.AccessRights(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LISTEN = "Listen"
        MANAGE = "Manage"
        SEND = "Send"


    class azure.servicebus.management.ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V2017_04 = "2017-04"
        V2021_05 = "2021-05"


    class azure.servicebus.management.AuthorizationRule:

        def __init__(
                self, 
                *, 
                claim_type: Optional[str] = ..., 
                claim_value: Optional[str] = ..., 
                created_at_utc: Optional[datetime] = ..., 
                key_name: Optional[str] = ..., 
                modified_at_utc: Optional[datetime] = ..., 
                primary_key: Optional[str] = ..., 
                rights: Optional[List[Union[str, AccessRights]]] = ..., 
                secondary_key: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...


    class azure.servicebus.management.CorrelationRuleFilter:

        def __init__(
                self, 
                *, 
                content_type: Optional[str] = ..., 
                correlation_id: Optional[str] = ..., 
                label: Optional[str] = ..., 
                message_id: Optional[str] = ..., 
                properties: Optional[Dict[str, Union[str, int, float, bool, datetime, timedelta]]] = ..., 
                reply_to: Optional[str] = ..., 
                reply_to_session_id: Optional[str] = ..., 
                session_id: Optional[str] = ..., 
                to: Optional[str] = ...
            ) -> None: ...


    class azure.servicebus.management.EntityAvailabilityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        LIMITED = "Limited"
        RENAMING = "Renaming"
        RESTORING = "Restoring"
        UNKNOWN = "Unknown"


    class azure.servicebus.management.EntityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CREATING = "Creating"
        DELETING = "Deleting"
        DISABLED = "Disabled"
        RECEIVE_DISABLED = "ReceiveDisabled"
        RENAMING = "Renaming"
        RESTORING = "Restoring"
        SEND_DISABLED = "SendDisabled"
        UNKNOWN = "Unknown"


    class azure.servicebus.management.FalseRuleFilter(SqlRuleFilter):

        def __init__(self) -> None: ...


    class azure.servicebus.management.MessageCountDetails(Model):
        active_message_count: int
        dead_letter_message_count: int
        scheduled_message_count: int
        transfer_dead_letter_message_count: int
        transfer_message_count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                active_message_count: Optional[int] = ..., 
                dead_letter_message_count: Optional[int] = ..., 
                scheduled_message_count: Optional[int] = ..., 
                transfer_dead_letter_message_count: Optional[int] = ..., 
                transfer_message_count: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.servicebus.management.MessagingSku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.servicebus.management.NamespaceProperties(DictMixin):
        alias: str
        created_at_utc: datetime
        messaging_sku: Union[str, MessagingSku]
        messaging_units: int
        modified_at_utc: datetime
        name: str
        namespace_type: Union[str, NamespaceType]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(
                self, 
                name: str, 
                *, 
                alias: Optional[str], 
                created_at_utc: Optional[datetime], 
                messaging_sku: Optional[Union[str, MessagingSku]], 
                messaging_units: Optional[int], 
                modified_at_utc: Optional[datetime], 
                namespace_type: Optional[Union[str, NamespaceType]]
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


    class azure.servicebus.management.NamespaceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVENT_HUB = "EventHub"
        MESSAGING = "Messaging"
        MIXED = "Mixed"
        NOTIFICATION_HUB = "NotificationHub"
        RELAY = "Relay"


    class azure.servicebus.management.QueueProperties(DictMixin):
        authorization_rules: list[AuthorizationRule]
        auto_delete_on_idle: Union[timedelta, str, None]
        availability_status: Union[str, None, EntityAvailabilityStatus]
        dead_lettering_on_message_expiration: Union[bool, None]
        default_message_time_to_live: Union[timedelta, str, None]
        duplicate_detection_history_time_window: Union[timedelta, str, None]
        enable_batched_operations: Union[bool, None]
        enable_express: Union[bool, None]
        enable_partitioning: Union[bool, None]
        forward_dead_lettered_messages_to: Union[str, None]
        forward_to: Union[str, None]
        lock_duration: Union[timedelta, str, None]
        max_delivery_count: Union[int, None]
        max_message_size_in_kilobytes: Union[int, None]
        max_size_in_megabytes: Union[int, None]
        name: Union[str, None]
        requires_duplicate_detection: Union[bool, None]
        requires_session: Union[bool, None]
        status: Union[str, EntityStatus, None]
        user_metadata: Union[str, None]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(
                self, 
                name: str, 
                *, 
                authorization_rules: Optional[List[AuthorizationRule]], 
                auto_delete_on_idle: Optional[Union[timedelta, str]], 
                availability_status: Optional[Union[str, EntityAvailabilityStatus]], 
                dead_lettering_on_message_expiration: Optional[bool], 
                default_message_time_to_live: Optional[Union[timedelta, str]], 
                duplicate_detection_history_time_window: Optional[Union[timedelta, str]], 
                enable_batched_operations: Optional[bool], 
                enable_express: Optional[bool], 
                enable_partitioning: Optional[bool], 
                forward_dead_lettered_messages_to: Optional[str], 
                forward_to: Optional[str], 
                lock_duration: Optional[Union[timedelta, str]], 
                max_delivery_count: Optional[int], 
                max_message_size_in_kilobytes: Optional[int], 
                max_size_in_megabytes: Optional[int], 
                requires_duplicate_detection: Optional[bool], 
                requires_session: Optional[bool], 
                status: Optional[Union[str, EntityStatus]], 
                user_metadata: Optional[str]
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


    class azure.servicebus.management.QueueRuntimeProperties:
        property accessed_at_utc: Optional[datetime]    # Read-only
        property active_message_count: Optional[int]    # Read-only
        property created_at_utc: Optional[datetime]    # Read-only
        property dead_letter_message_count: Optional[int]    # Read-only
        property name: str    # Read-only
        property scheduled_message_count: Optional[int]    # Read-only
        property size_in_bytes: Optional[int]    # Read-only
        property total_message_count: Optional[int]    # Read-only
        property transfer_dead_letter_message_count: Optional[int]    # Read-only
        property transfer_message_count: Optional[int]    # Read-only
        property updated_at_utc: Optional[datetime]    # Read-only

        def __init__(self) -> None: ...


    class azure.servicebus.management.RuleProperties(DictMixin):
        action: Union[SqlRuleAction, None]
        created_at_utc: Union[datetime, None]
        filter: Union[CorrelationRuleFilter, SqlRuleFilter, None]
        name: str

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(
                self, 
                name: str, 
                *, 
                action: Optional[SqlRuleAction], 
                created_at_utc: Optional[datetime], 
                filter: Optional[Union[CorrelationRuleFilter, SqlRuleFilter]]
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


    class azure.servicebus.management.ServiceBusAdministrationClient: implements ContextManager 

        def __init__(
                self, 
                fully_qualified_namespace: str, 
                credential: TokenCredential, 
                *, 
                api_version: Union[str, ApiVersion] = DEFAULT_VERSION, 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                *, 
                api_version: Union[str, ApiVersion] = DEFAULT_VERSION, 
                **kwargs: Any
            ) -> ServiceBusAdministrationClient: ...

        def close(self) -> None: ...

        def create_queue(
                self, 
                queue_name: str, 
                *, 
                authorization_rules: Optional[List[AuthorizationRule]] = ..., 
                auto_delete_on_idle: Optional[Union[timedelta, str]] = ..., 
                dead_lettering_on_message_expiration: Optional[bool] = ..., 
                default_message_time_to_live: Optional[Union[timedelta, str]] = ..., 
                duplicate_detection_history_time_window: Optional[Union[timedelta, str]] = ..., 
                enable_batched_operations: Optional[bool] = ..., 
                enable_express: Optional[bool] = ..., 
                enable_partitioning: Optional[bool] = ..., 
                forward_dead_lettered_messages_to: Optional[str] = ..., 
                forward_to: Optional[str] = ..., 
                lock_duration: Optional[Union[timedelta, str]] = ..., 
                max_delivery_count: Optional[int] = ..., 
                max_message_size_in_kilobytes: Optional[int] = ..., 
                max_size_in_megabytes: Optional[int] = ..., 
                requires_duplicate_detection: Optional[bool] = ..., 
                requires_session: Optional[bool] = ..., 
                user_metadata: Optional[str] = ..., 
                **kwargs: Any
            ) -> QueueProperties: ...

        def create_rule(
                self, 
                topic_name: str, 
                subscription_name: str, 
                rule_name: str, 
                *, 
                action: Optional[SqlRuleAction] = ..., 
                filter: Union[CorrelationRuleFilter, SqlRuleFilter] = TrueRuleFilter(), 
                **kwargs: Any
            ) -> RuleProperties: ...

        def create_subscription(
                self, 
                topic_name: str, 
                subscription_name: str, 
                *, 
                auto_delete_on_idle: Optional[Union[timedelta, str]] = ..., 
                dead_lettering_on_filter_evaluation_exceptions: Optional[bool] = ..., 
                dead_lettering_on_message_expiration: Optional[bool] = ..., 
                default_message_time_to_live: Optional[Union[timedelta, str]] = ..., 
                enable_batched_operations: Optional[bool] = ..., 
                forward_dead_lettered_messages_to: Optional[str] = ..., 
                forward_to: Optional[str] = ..., 
                lock_duration: Optional[Union[timedelta, str]] = ..., 
                max_delivery_count: Optional[int] = ..., 
                requires_session: Optional[bool] = ..., 
                user_metadata: Optional[str] = ..., 
                **kwargs: Any
            ) -> SubscriptionProperties: ...

        def create_topic(
                self, 
                topic_name: str, 
                *, 
                authorization_rules: Optional[List[AuthorizationRule]] = ..., 
                auto_delete_on_idle: Optional[Union[timedelta, str]] = ..., 
                default_message_time_to_live: Optional[Union[timedelta, str]] = ..., 
                duplicate_detection_history_time_window: Optional[Union[timedelta, str]] = ..., 
                enable_batched_operations: Optional[bool] = ..., 
                enable_express: Optional[bool] = ..., 
                enable_partitioning: Optional[bool] = ..., 
                filtering_messages_before_publishing: Optional[bool] = ..., 
                max_message_size_in_kilobytes: Optional[int] = ..., 
                max_size_in_megabytes: Optional[int] = ..., 
                requires_duplicate_detection: Optional[bool] = ..., 
                size_in_bytes: Optional[int] = ..., 
                support_ordering: Optional[bool] = ..., 
                user_metadata: Optional[str] = ..., 
                **kwargs: Any
            ) -> TopicProperties: ...

        def delete_queue(
                self, 
                queue_name: str, 
                **kwargs: Any
            ) -> None: ...

        def delete_rule(
                self, 
                topic_name: str, 
                subscription_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        def delete_subscription(
                self, 
                topic_name: str, 
                subscription_name: str, 
                **kwargs: Any
            ) -> None: ...

        def delete_topic(
                self, 
                topic_name: str, 
                **kwargs: Any
            ) -> None: ...

        def get_namespace_properties(self, **kwargs: Any) -> NamespaceProperties: ...

        def get_queue(
                self, 
                queue_name: str, 
                **kwargs: Any
            ) -> QueueProperties: ...

        def get_queue_runtime_properties(
                self, 
                queue_name: str, 
                **kwargs: Any
            ) -> QueueRuntimeProperties: ...

        def get_rule(
                self, 
                topic_name: str, 
                subscription_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> RuleProperties: ...

        def get_subscription(
                self, 
                topic_name: str, 
                subscription_name: str, 
                **kwargs: Any
            ) -> SubscriptionProperties: ...

        def get_subscription_runtime_properties(
                self, 
                topic_name: str, 
                subscription_name: str, 
                **kwargs: Any
            ) -> SubscriptionRuntimeProperties: ...

        def get_topic(
                self, 
                topic_name: str, 
                **kwargs: Any
            ) -> TopicProperties: ...

        def get_topic_runtime_properties(
                self, 
                topic_name: str, 
                **kwargs: Any
            ) -> TopicRuntimeProperties: ...

        def list_queues(self, **kwargs: Any) -> ItemPaged[QueueProperties]: ...

        def list_queues_runtime_properties(self, **kwargs: Any) -> ItemPaged[QueueRuntimeProperties]: ...

        def list_rules(
                self, 
                topic_name: str, 
                subscription_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RuleProperties]: ...

        def list_subscriptions(
                self, 
                topic_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SubscriptionProperties]: ...

        def list_subscriptions_runtime_properties(
                self, 
                topic_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SubscriptionRuntimeProperties]: ...

        def list_topics(self, **kwargs: Any) -> ItemPaged[TopicProperties]: ...

        def list_topics_runtime_properties(self, **kwargs: Any) -> ItemPaged[TopicRuntimeProperties]: ...

        def update_queue(
                self, 
                queue: Union[QueueProperties, Mapping[str, Any]], 
                **kwargs: Any
            ) -> None: ...

        def update_rule(
                self, 
                topic_name: str, 
                subscription_name: str, 
                rule: Union[RuleProperties, Mapping[str, Any]], 
                **kwargs: Any
            ) -> None: ...

        def update_subscription(
                self, 
                topic_name: str, 
                subscription: Union[SubscriptionProperties, Mapping[str, Any]], 
                **kwargs: Any
            ) -> None: ...

        def update_topic(
                self, 
                topic: Union[TopicProperties, Mapping[str, Any]], 
                **kwargs: Any
            ) -> None: ...


    class azure.servicebus.management.SqlRuleAction:

        def __init__(
                self, 
                sql_expression: Optional[str] = None, 
                parameters: Optional[Dict[str, Union[str, int, float, bool, datetime, timedelta]]] = None
            ) -> None: ...


    class azure.servicebus.management.SqlRuleFilter:

        def __init__(
                self, 
                sql_expression: Optional[str] = None, 
                parameters: Optional[Dict[str, Union[str, int, float, bool, datetime, timedelta]]] = None
            ) -> None: ...


    class azure.servicebus.management.SubscriptionProperties(DictMixin):
        auto_delete_on_idle: Union[timedelta, str, None]
        availability_status: Union[str, None, EntityAvailabilityStatus]
        dead_lettering_on_filter_evaluation_exceptions: Union[bool, None]
        dead_lettering_on_message_expiration: Union[bool, None]
        default_message_time_to_live: Union[timedelta, str, None]
        enable_batched_operations: Union[bool, None]
        forward_dead_lettered_messages_to: Union[str, None]
        forward_to: Union[str, None]
        lock_duration: Union[timedelta, str, None]
        max_delivery_count: Union[int, None]
        name: str
        requires_session: Union[bool, None]
        status: Union[str, EntityStatus, None]
        user_metadata: Union[str, None]

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(
                self, 
                name: str, 
                *, 
                auto_delete_on_idle: Optional[Union[timedelta, str]], 
                availability_status: Optional[Union[str, EntityAvailabilityStatus]], 
                dead_lettering_on_filter_evaluation_exceptions: Optional[bool], 
                dead_lettering_on_message_expiration: Optional[bool], 
                default_message_time_to_live: Optional[Union[timedelta, str]], 
                enable_batched_operations: Optional[bool], 
                forward_dead_lettered_messages_to: Optional[str], 
                forward_to: Optional[str], 
                lock_duration: Optional[Union[timedelta, str]], 
                max_delivery_count: Optional[int], 
                requires_session: Optional[bool], 
                status: Optional[Union[str, EntityStatus]], 
                user_metadata: Optional[str]
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


    class azure.servicebus.management.SubscriptionRuntimeProperties:
        property accessed_at_utc: Optional[datetime]    # Read-only
        property active_message_count: Optional[int]    # Read-only
        property created_at_utc: Optional[datetime]    # Read-only
        property dead_letter_message_count: Optional[int]    # Read-only
        property name: str    # Read-only
        property total_message_count: Optional[int]    # Read-only
        property transfer_dead_letter_message_count: Optional[int]    # Read-only
        property transfer_message_count: Optional[int]    # Read-only
        property updated_at_utc: Optional[datetime]    # Read-only

        def __init__(self) -> None: ...


    class azure.servicebus.management.TopicProperties(DictMixin):
        authorization_rules
        auto_delete_on_idle
        availability_status
        default_message_time_to_live
        duplicate_detection_history_time_window
        enable_batched_operations
        enable_express
        enable_partitioning
        filtering_messages_before_publishing
        max_message_size_in_kilobytes
        max_size_in_megabytes
        name
        requires_duplicate_detection
        size_in_bytes
        status
        support_ordering
        user_metadata

        def __contains__(self, key: str) -> bool: ...

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(
                self, 
                name: str, 
                *, 
                authorization_rules: Optional[List[AuthorizationRule]], 
                auto_delete_on_idle: Optional[Union[timedelta, str]], 
                availability_status: Optional[Union[str, EntityAvailabilityStatus]], 
                default_message_time_to_live: Optional[Union[timedelta, str]], 
                duplicate_detection_history_time_window: Optional[Union[timedelta, str]], 
                enable_batched_operations: Optional[bool], 
                enable_express: Optional[bool], 
                enable_partitioning: Optional[bool], 
                filtering_messages_before_publishing: Optional[bool], 
                max_message_size_in_kilobytes: Optional[int], 
                max_size_in_megabytes: Optional[int], 
                requires_duplicate_detection: Optional[bool], 
                size_in_bytes: Optional[int], 
                status: Optional[Union[str, EntityStatus]], 
                support_ordering: Optional[bool], 
                user_metadata: Optional[str]
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


    class azure.servicebus.management.TopicRuntimeProperties:
        property accessed_at_utc: Optional[datetime]    # Read-only
        property created_at_utc: Optional[datetime]    # Read-only
        property name: str    # Read-only
        property scheduled_message_count: Optional[int]    # Read-only
        property size_in_bytes: Optional[int]    # Read-only
        property subscription_count: Optional[int]    # Read-only
        property updated_at_utc: Optional[datetime]    # Read-only

        def __init__(self) -> None: ...


    class azure.servicebus.management.TrueRuleFilter(SqlRuleFilter):

        def __init__(self) -> None: ...


```