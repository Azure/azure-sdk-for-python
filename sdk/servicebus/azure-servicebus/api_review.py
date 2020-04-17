## APIs:
class ServiceBusClient:
    def __init__(
        self,
        fully_qualified_namespace : str,
        credential : TokenCredential,
        logging_enable: bool = False,
        http_proxy: dict = None,
        transport_type: TransportType = TransportType.Amqp,
    ):

    def __enter__(self):
    def __exit__(self, *kwargs):
    def close(self):

    @classmethod
    def from_connection_string(cls, conn_str, **kwargs):

    def get_queue_sender(self, queue_name, **kwargs) -> ServiceBusSender:
    def get_queue_receiver(self, queue_name, **kwargs) -> ServiceBusReceiver:
    def get_topic_sender(self, topic_name, **kwargs) -> ServiceBusSender:
    def get_subscription_receiver(self, topic_name, subscription_name, **kwargs) -> ServiceBusReceiver:

    def get_queue_session_receiver(self, queue_name, session_id, **kwargs) -> ServiceBusSessionReceiver:
    def get_subscription_session_receiver(self, topic_name, subscription_name, session_id, **kwargs) -> ServiceBusSessionReceiver:

    def get_subscription_rule_manager(self, topic_name, subscription_name) -> SubscriptionRuleManager:

class ServiceBusSender:
    def __init__(
        self,
        fully_qualified_namespace : str,
        credential: TokenCredential,
        queue_name: str = None,
        topic_name: str = None,
        logging_enable: bool = False,
        http_proxy: dict = None,
        transport_type: TransportType = TransportType.Amqp,
        retry_total : int = 3,
        retry_backoff_factor : float = 30,
        retry_backoff_maximum : int = 120  # cur_retry_backoff = retry_backoff_factor * (2^cur_retry_time)
    ) -> None:
    @classmethod
    def from_connection_string(
        cls,
        conn_str : str,
        queue_name: str = None,
        topic_name: str = None,
        **kwargs
    ) -> ServiceBusSender:

    def __enter__(self):
    def __exit__(self):

    def close(self) -> None:

    def create_batch(
        self,
        max_size_in_bytes : int = None
    ) -> BatchMessage:

    def send(
        self,
        message : Union[Message, BatchMessage],
        message_timeout : float = None
    ) -> None:
    def schedule(
        self,
        message : Union[Message, BatchMessage],
        schedule_time_utc : datetime,
    ) -> List[int]:

    def cancel_scheduled_messages(self, sequence_number : Union[int, List[int]]) -> None:


class ServiceBusReceiver:
    def __init__(
        self,
        fully_qualified_namespace : str,
        credential: TokenCredential,
        queue_name: str = None,
        topic_name: str = None,
        subscription_name : str = None,
        session_id : str = None,
        mode : ReceiveSettleMode = ReceiveSettleMode.PeekLock
        logging_enable: bool = False,
        http_proxy: dict = None,
        transport_type: TransportType = TransportType.Amqp,
        retry_total : int = 3,
        retry_backoff_factor: float = 30,
        retry_backoff_maximum: int = 120  # cur_retry_backoff = retry_backoff_factor * (2^cur_retry_time)
    ) -> None:
    @classmethod
    def from_connection_string(
        cls,
        conn_str : str,
        queue_name: str = None,
        topic_name: str = None,
        subscription_name : str = None,
        session_id: str = None,
        mode : ReceiveSettleMode = ReceiveSettleMode.PeekLock
        **kwargs
    )-> ServiceBusReceiver:

    def __enter__(self):
    def __exit__(self):

    def close(self) -> None:

    def __iter__(self):
    def __next__(self):
    def next(self):

    def peek(
        self,
        message_count : int = 1,
        sequence_number : int = None
    ) -> List[PeekMessage]:
    def receive_deferred_messages(
        self,
        sequence_numbers : List[int],
    ) -> List[DeferredMessage]:
    def receive(
        self,
        max_batch_size : int = None,
        timeout : float = None,
    ) -> List[ReceivedMessage]:  # Pull mode receive


class ServiceBusSessionReceiver(ServiceBusReceiver):
    @property
    def session(self) -> ServiceBusSession:


class ServiceBusSession:
    @property
    def get_session_state(self) -> str:  # This can be made to property if property is more pythonic way
    def set_session_state(self, state : str) -> None:  # This can be made to property if property is more pythonic way
    def renew_lock(self) -> None:
    @property
    def session_id(self) -> str:
    def expired(self) -> bool:


class Message:
    def __init__(self, body : str, encoding : str = 'UTF-8', **kwargs) -> None:
    def __str__(self):

    # @properties
    def body(self) -> Union[bytes, Generator[bytes]]:  # read-only
    def partition_key(self, value : str):
    def partition_key(self) -> str:
    def via_partition_key(self, value: str):
    def via_partition_key(self) -> str:
    def time_to_live(self, value : Union[float, timedelta]):
    def time_to_live(self) -> datetime.timedelta:
    def annotations(self, value : dict[str, Any]):
    def annotations(self) -> dict[str, Any]:
    def user_properties(self, value : dict[str, Any]):
    def user_properties(self) -> dict[str, Any]:
    def enqueue_sequence_number(self, value : int):
    def enqueue_sequence_number(self) -> int:

    # Methods
    def schedule(self, schedule_time_utc : datetime) -> None:


class BatchMessage(Message):
# inherited from Message
    def add(self, message: Message) -> None:


class PeekMessage(Message):
    def enqueued_time(self) -> datetime:  # read-only
    def scheduled_enqueue_time(self) -> datetime:  # read-only
    def sequence_number(self) -> int:  # read-only
    def partition_id(self) -> str:  # read-only
    def session_id(self) -> str:  # read-only

class ReceivedMessage(Message):

    # @properties
    def settled(self) -> bool:  # read-only
    def enqueued_time(self) -> datetime:  # read-only
    def scheduled_enqueue_time(self) -> datetime:  # read-only
    def sequence_number(self) -> int:  # read-only
    def partition_id(self) -> str:  # read-only
    def locked_until(self) -> datetime:  # read-only
    def expired(self) -> bool:  # read-only
    def lock_token(self) -> str:  # read-only
    def session_id(self) -> str:  # read-only

    # methods
    def renew_lock(self) -> None:
    def complete(self) -> None:
    def dead_letter(self, description : str = None) -> None:
    def abandon(self) -> None:
    def defer(self) -> None:


class ReceiveSettleMode:
    PeekLock
    ReceiveAndDelete


class TransportType(Enum):
    Amqp
    AmqpOverWebsocket


class ServiceBusSharedKeyCredential:
    def __init__(self, policy, key):
    def get_token(self, *scopes, **kwargs):


class SubscriptionRuleManager:
    def __init__(
        self,
        fully_qualified_namespace: str,
        topic_name: str,
        subscription_name: str,
        credential: TokenCredential,
        logging_enable: bool = False,
        http_proxy: dict = None,
        transport_type: TransportType = TransportType.Amqp
    ) -> SubscriptionRuleManager

    @classmethod
    def from_connection_string(cls, conn_str, subscription_name, topic_name=None, **kwargs) -> SubscriptionRuleManager:

    def get_rules(self, timeout: float = None) -> list[RuleDescription]:
    def add_rule(self, rule_name: str, filter: Union(bool, str, CorrelationFilter), sql_rule_action_expression: str, timeout: float = None):
    def remove_rule(self, rule_name: str, timeout: float = None):


class RuleDescription:
    #TODO: is it necessary to make it separate class or just a list[dict]?
    def __init__(self):
    @property
    def filter(self) -> Union(str, CorrelationFilter):  # TODO: return multiple types OK?
    def action(self) -> str:
    def name(self) -> str:


class CorrelationFilter:
    # TODO: is it necessary to make it separate class, depending on the fact that there're so many fields,
    #  and how people would use this, I personally prefer it being a class
    def __init__(self):

    @property
    def correlation_id(self, val : str):
    def correlation_id(self) -> str:
    def message_id(self, val : str):
    def message_id(self) -> str:
    def to(self, val: str):
    def to(self) -> str:
    def reply_to(self, val : str):
    def reply_to(self) -> str:
    def label(self, val: str):
    def label(self) -> str:
    def session_id(self, val: str):
    def session_id(self) -> str:
    def reply_to_session_id(self, val: str):
    def reply_to_session_id(self) -> str:
    def content_type(self, val: str):
    def content_type(self) -> str:
    def user_properties(self, val: dict):
    def user_properties(self) -> dict:
