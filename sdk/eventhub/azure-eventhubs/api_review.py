
class EventHubProducerClient(ClientBaseAsync):

    eh_name  # type: str

    def __init__(
            self,
            host: str,
            event_hub_path: str,
            credential: Union[EventHubSharedKeyCredential, EventHubSASTokenCredential, TokenCredential],
            **kwargs
    ) -> None:

    async def __aenter__(self):

    async def __aexit__(self, *args):

    @classmethod
    def from_connection_string(
        cls, conn_str: str,
        *,
        event_hub_path: str = None,
        logging_enable: bool = False,
        http_proxy: dict = None,
        auth_timeout: float = 60,
        user_agent: str = None,
        retry_total: int = 3,
        transport_type=None) -> EventHubProducerClient:

    async def send(
        self,
        event_data: Union[EventData, EventDataBatch, Iterable[EventData]],
        *,
        partition_key: Union[str, bytes] = None,
        partition_id: str = None,
        timeout: float = None) -> None:

    async def create_batch(self, max_size: int = None) -> EventDataBatch:

    async def get_properties(self) -> Dict[str, Any]:

    async def get_partition_ids(self) -> List[str]:

    async def get_partition_properties(self, partition: str) -> Dict[str, str]:

    async def close(self) -> None:



class EventHubConsumerClient(ClientBaseAsync):

    eh_name  # type: str

    def __init__(
            self,
            host: str,
            event_hub_path: str,
            credential: Union[EventHubSharedKeyCredential, EventHubSASTokenCredential, TokenCredential],
            **kwargs
    ) -> None:

    async def __aenter__(self):

    async def __aexit__(self, *args):

    @classmethod
    def from_connection_string(cls, conn_str: str, **kwargs) -> EventHubConsumerClient:

    async def receive(
            self,
            on_events: Callable[PartitionContext, EventData],
            consumer_group: str,
            *,
            partition_id: str = None,
            owner_level: int = None,
            prefetch: int = 300,
            track_last_enqueued_event_properties: bool = False,
            initial_event_position=None,
            on_error=None,
            on_partition_initialize=None,
            on_partition_close=None
    ) -> None:

    async def get_properties(self) -> Dict[str, Any]:

    async def get_partition_ids(self) -> List[str]:

    async def get_partition_properties(self, partition: str) -> Dict[str, str]:

    async def close(self) -> None:


class PartitionContext(object):

    fully_qualified_namespace  # type: str
    partition_id  # type: str
    eventhub_name  # type: str
    consumer_group_name  # type: str
    owner_id  # type: str

    def __init__(
        self,
        fully_qualified_namespace: str,
        eventhub_name: str,
        consumer_group_name: str,
        partition_id: str,
        owner_id: str,
        partition_manager: PartitionManager =None) -> None:

    async def update_checkpoint(self, event: EventData):


class PartitionManager(ABC):

    async def list_ownership(
        self,
        fully_qualified_namespace: str,
        eventhub_name: str,
        consumer_group_name: str) -> Iterable[Dict[str, Any]]:

    async def claim_ownership(self, ownership_list: Iterable[Dict[str, Any]]) -> Iterable[Dict[str, Any]]:

    async def update_checkpoint(
        self,
        fully_qualified_namespace: str,
        eventhub_name: str,
        consumer_group_name: str,
        partition_id: str,
        offset: str,
        sequence_number: int) -> None:

    async def list_checkpoints(self, fully_qualified_namespace: str, eventhub_name: str, consumer_group_name: str) -> Iterable[Dict[str,Any]]:


class EventData(object):

    message  # type: uamqp.Message

    def __init__(self, body: Union[str, bytes] =None) -> None:

    def __str__(self) -> str:

    @property
    def sequence_number(self) -> int:

    @property
    def offset(self) -> str:

    @property
    def enqueued_time(self) -> datetime.datetime:
    
    @property
    def partition_key(self) -> bytes:

    @property
    def application_properties(self) -> dict[str, Any]:

    @property
    def system_properties(self) -> dict[str, Any]:

    @property
    def body(self) -> Union[bytes, Iterable[bytes]]:

    @property
    def last_enqueued_event_properties(self) -> dict[str, Any]:

    def body_as_str(self, encoding='UTF-8') -> str:

    def body_as_json(self, encoding='UTF-8') -> dict[str, Any]:

    def encode_message(self) -> bytes:


class EventDataBatch(object):

    message  # type: uamqp.BatchMessage
    max_size  # type: int

    def __init__(self, max_size: int=None, partition_key: str=None) -> None:
    
    def __len__(self) -> int:

    @property
    def size(self) -> int:

    def try_add(self, event_data: EventData) -> None:


class EventPosition(object):

    value  # type: Union[str, int, datetime.datetime]
    inclusive  # type: bool

    def __init__(self, value, inclusive=False):

    
class EventHubSASTokenCredential(object):    

    def __init__(self, token: Union[Callable, dict[str, str]]):

    def get_sas_token(self) -> dict[str, str]:


class EventHubSharedKeyCredential(object):

    def __init__(self, policy: str, key: str):


class EventHubError(Exception):


class ConnectionLostError(EventHubError):


class ConnectError(EventHubError):


class AuthenticationError(ConnectError):


class EventDataError(EventHubError):


class EventDataSendError(EventHubError):


class OperationTimeoutError(EventHubError):
