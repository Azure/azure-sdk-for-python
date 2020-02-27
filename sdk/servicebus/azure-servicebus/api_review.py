# Two-Clients Approach

## APIs:
class SeviceBusSenderClient:
    def __init__(
        self,
        fully_qualified_namespace : str,
        entity_name : str,
        credential : TokenCredential,
        logging_enable: bool = False,
        http_proxy: dict = None,
        transport_type: TransportType = None,
        retry_total : int = 3,
        retry_backoff_factor : float = 30,
        retry_backoff_maximum : int = 120  # cur_retry_backoff = retry_backoff_factor * (2^cur_retry_time)
        connection : ServiceBusConnection = None
    ) -> None:
    @classmethod
    def from_queue(
        cls,
        fully_qualified_namepsace : str,
        queue_name : str,
        credential : TokenCredential,
        **kwargs
    ) -> SeviceBusSenderClient:
    @classmethod
    def from_topic(
        cls,
        fully_qualified_namespace : str,
        topic_name : str,
        credential : TokenCredential,
        **kwargs
    ) -> SeviceBusSenderClient:
    @classmethod
    def from_connection_string(
        cls,
        conn_str : str,
        entity_name : str = None,
        **kwargs
    ) -> SeviceBusSenderClient:

    def __enter__(self):
    def __exit__(self):

    def close(self) -> None:

    def get_properties(self) -> Dict[str, Any]:

    def create_batch(
        self,
        session_id : str = None,
        max_size_in_bytes : int = None
    ) -> BatchMessage:

    def send(
        self,
        message : Union[Message, BatchMessage],
        session_id : str = None,
        message_timeout : float = None
    ) -> None:
    def schedule(
        self,
        message : Union[Message, BatchMessage],
        schedule_time_utc : datetime,
        session_id : str = None
    ) -> List[int]:

    def cancel_scheduled_messages(self, sequence_number : Union[int, List[int]]) -> None:


class ServiceBusReceiverClient:
    def __init__(
        self,
        fully_qualified_namespace : str,
        entity_name : str,
        credential: TokenCredential,
        subscription_name : str = None,
        session_id : str = None,
        mode : ReceiveSettleMode = ReceiveSettleMode.PeekLock
        logging_enable: bool = False,
        http_proxy: dict = None,
        transport_type: TransportType = None,
        retry_total : int = 3,
        retry_backoff_factor: float = 30,
        retry_backoff_maximum: int = 120  # cur_retry_backoff = retry_backoff_factor * (2^cur_retry_time)
        connection: Connection = None
    ) -> None:
    @classmethod
    def from_queue(
        cls,
        fully_qualified_namespace : str,
        queue_name : str,
        credential : TokenCredential,
        session_id: str = None,
        mode : ReceiveSettleMode = ReceiveSettleMode.PeekLock
        **kwargs
    ) -> ServiceBusReceiverClient:
    @classmethod
    def from_topic_subscription(
        cls,
        fully_qualified_namespace : str,
        topic_name : str,
        subscription_name : str,
        credential: TokenCredential,
        session_id: str = None,
        mode : ReceiveSettleMode = ReceiveSettleMode.PeekLock
        **kwargs
    ) -> ServiceBusReceiverClient:
    @classmethod
    def from_connection_string(
        cls,
        conn_str : str,
        entity_name : str = None,
        subscription_name : str = None,
        session_id: str = None,
        mode : ReceiveSettleMode = ReceiveSettleMode.PeekLock
        **kwargs
    )-> ServiceBusReceiverClient:

    def __enter__(self):
    def __exit__(self):

    def close(self) -> None:

    def get_properties(self) -> Dict[str, any]:

    def __iter__(self):
    def __next__(self):
    def next(self):

    def peek(
        self,
        count : int = 1,
        start_from : int = None
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


    @property
    def session(self) -> ServiceBusSession:


    # Rule APIs, raise Error when called on Queue
    def add_rule(self, rule_name : str, filter : str) -> None: # TODO: figure out what filter is
    def remove_rule(self, rule_name : str) -> None:
    def get_rules(self) -> List[str] -> Dict[str, Any]:


class ServiceBusSession:
    @property
    def get_session_state(self) -> str:  # This can be made to property if property is more pythonic way
    def set_session_state(self, state : str) -> None:  # This can be made to property if property is more pythonic way
    def renew_lock(self) -> None:
    @property
    def session_id(self) -> str:
    def expired(self) -> bool:


class Transaction:
    def __init__(self) -> None:
    def __enter__(self):
    def __exit__(self):
    def begin(self) -> None:
    def commit(self) -> None:
    def abort(self) -> None:


class Message:
    def __init__(self, body : str, encoding : str = 'UTF-8', **kwargs) -> None:
    def __str__(self):

    # @properties
    def body(self) -> Union[bytes, Generator[bytes]]:  # read-only
    def partition_key(self, value : str):
    def partition_key(self) -> str:
    def via_partition_key(self, value: str):
    def via_partition_key(self) -> str:
    def session_id(self, value : str):
    def session_id(self) -> str:
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

    # methods
    def renew_lock(self) -> None:
    def complete(self) -> None:
    def dead_letter(self, description : str = None) -> None:
    def abandon(self) -> None:
    def defer(self) -> None:


class PeekMessage(ReceivedMessage):
# inherited from ReceivedMessage, and cannot settle/lock the message


class DeferredMessage(ReceivedMessage):
# interited from ReceivedMessage


class ReceiveSettleMode:
    PeekLock
    ReceiveAndDelete


class TransportType(Enum):
    Amqp
    AmqpOverWebsocket


class ServiceBusConnection:
    def __int__(
        self,
        fully_qualified_namespace,
        entity_name,
        token_credential
    ) -> None:
    def from_connection_string(
        self,
        conn_str,
        entity_name=None
    ) -> ServiceBusConnection:

class ServiceBusSharedKeyCredential:
    def __init__(self, policy, key):
    def get_token(self, *scopes, **kwargs):

class ServiceBusError(Exception):

class ServiceBusClient:  # MGMT APIs
    def __init__(
        self,
        fully_qualified_namespace : str,
        credential : TokenCredential,
        **kwargs
    ):

    @classmethod
    def from_connection_string(cls, conn_str, **kwargs):

    def create_queue(self, queue_name, **kwargs):
    def delete_queue(self, queue_name, fail_not_exist=False):
    def list_queues(self) -> List[str]:
    def get_queue_sender(self, queue_name, **kwargs) -> ServiceBusSenderClient:
    def get_queue_receiver(self, queue_name, **kwargs) -> ServiceBusReceiverClient:

    def create_topic(self, topic_name, **kwargs):
    def delete_topic(self, topic_name, fail_not_exist=False):
    def list_topics(self):
    def get_topic_sender(self, topic_name) -> ServiceBusSenderClient:

    def create_subscription(self, topic_name, subscription_name):
    def delete_subscription(self, topic_name, subscription_name, fail_not_exist=False):
    def list_subscriptions(self, topic_name):
    def get_subscription_receiver(self, topic_name, subscription_name) -> ServiceBusReceiverClient:

    def list_session_ids_of_queue(self, queue_name):
    def list_session_ids_of_subscription(self, topic_name, subscription_name):

################################################### Split Line ###################################################

# Approach for Rule APIs - Option 1
## APIs
### 3-Clients approach

class ServiceBusSenderClient:
class QueueReceiverClient:
class SubscriptionReceiverClient:
    def add_rule(self, rule_name, filter):
    def remove_rule(self, rule_name):
    def get_rules(self):


################################################### Split Line ###################################################

# Approach for Rule APIs - Option 2
## APIs
class ServiceBusReceiverClient:
    @property
    def subscription_rule_manager(self):  # raise Error when called on Queue

class SubscriptionRuleManager:
    def add_rule(self, rule_name, filter):
    def remove_rule(self, rule_name):
    def get_rules(self):


################################################### Split Line ###################################################

# Approach for Rule APIs - Option 3
## APIs
class SubscriptionRuleManager:
    @classmethod
    def from_receiver_client_for_subscription(cls, receiver_client):
    def add_rule(self, rule_name, filter):
    def remove_rule(self, rule_name):
    def get_rules(self):
