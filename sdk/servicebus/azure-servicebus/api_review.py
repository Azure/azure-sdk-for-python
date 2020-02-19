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

    def list_session_ids(self) -> List[str]:

    def send(
        self,
        messages,
        session : str = None,
        message_timeout : float = None
    ) -> None:
    def schedule(
        self,
        messages,
        schedule_time : datetime,
        session : str = None
    ) -> List[int]:
    def cancel_scheduled_messages(self, sequence_numbers : List[int]) -> None:


class ServiceBusReceiverClient:
    def __init__(
        self,
        fully_qualified_namespace : str,
        entity_name : str,
        subscription_name : str = None,
        session : str = None,
        credential : TokenCredential,
        logging_enable: bool = False,
        http_proxy: dict = None,
        transport_type: TransportType = None,
        retry_total : int = 3,
    ) -> None:
    @classmethod
    def from_queue(
        cls,
        fully_qualified_namespace : str,
        queue_name : str,
        credential : TokenCredential,
        session: str = None,
        **kwargs
    ) -> ServiceBusReceiverClient:
    @classmethod
    def from_topic_subscription(
        cls,
        fully_qualified_namespace : str,
        topic_name : str,
        subscription_name : str,
        credential: TokenCredential,
        session: str = None,
        **kwargs
    ) -> ServiceBusReceiverClient:
    @classmethod
    def from_connection_string(
        cls,
        conn_str : str,
        entity_name : str = None,
        subscription_name : str = None,
        session: str = None,
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
        mode : ReceiveSettleMode =ReceiveSettleMode.PeekLock
    ) -> List[DeferredMessage]:
    def receive(
        self,
        max_batch_size : int = None,
        timeout : float = None,
        mode : ReceiveSettleMode =ReceiveSettleMode.PeekLock
    ) -> List[Message]:  # Pull mode receive
    def settle_deferred_messages(
        self,
        settlement : str,  # TODO: In T1 settlement is just string like 'completed', 'suspended', 'abandoned', can we improve this parameter to be Enum or remove this method?
        messages : List[DeferredMessage],
        **kwargs
    ) -> None:  # Batch settle deferred messages

    def list_sessions(self) -> List[str]:
    def get_session(self) -> Session:  # raise Error when called on non-session entity

    # Rule APIs, raise Error when called on Queue
    def add_rule(self, rule_name : str, filter : str) -> None: # TODO: figure out what filter is
    def remove_rule(self, rule_name : str) -> None:
    def get_rules(self) -> List[str] -> Dict[str, Any]:


class Session:
    def get_session_id(self) -> str:
    def get_session_state(self) -> str:  # This can be made to property if property is more pythonic way
    def set_session_state(self, state : str) -> None:  # This can be made to property if property is more pythonic way
    def renew_lock(self) -> None:
    @property
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
    def settled(self) -> bool:  # read-only
    def enqueued_time(self) -> datetime:  # read-only
    def scheduled_enqueue_time(self) -> datetime:  # read-only
    def sequence_number(self) -> int:  # read-only
    def partition_id(self) -> str:  # read-only
    def locked_until(self) -> datetime:  # read-only
    def expired(self) -> bool:  # read-only
    def lock_token(self) -> str:  # read-only
    def body(self) -> Union[bytes, Generator[bytes]]:  # read-only
    def partition_key(self, value : str):
    def partition_key(self) -> str:
    def via_partition_key(self, value: str):
    def via_partition_key(self) -> str:
    def sessio_id(self, value : str):
    def sessio_id(self) -> str:
    def time_to_live(self, value : Union[float, timedelta]):
    def time_to_live(self) -> datetime.timedelta:
    def annotations(self, value : dict[str, Any]):
    def annotations(self) -> dict[str, Any]:
    def user_properties(self, value : dict[str, Any]):
    def user_properties(self) -> dict[str, Any]:
    def enqueue_sequence_number(self, value : int):
    def enqueue_sequence_number(self) -> int:

    # Methods
    def schedule(self, schedule_time : datetime) -> None:
    def renew_lock(self) -> None:
    def complete(self) -> None:
    def dead_letter(self, description : str = None) -> None:
    def abandon(self) -> None:
    def defer(self) -> None:


class BatchMessage(Message):
# inherited from Message


class PeekMessage(Message):
# inherited from Message, and cannot settle/lock the message


class DeferredMessage(Message):
    # interited from Message
    # its own @properties
    def settled(self) -> bool:  # read-only


class ReceiveSettleMode:
    PeekLock
    ReceiveAndDelete


class TransportType(Enum):
    Amqp
    AmqpOverWebsocket


class ServiceBusSharedKeyCredential:
    def __init__(self, policy, key):
    def get_token(self, *scopes, **kwargs):


################################################### Split Line ###################################################

## Sampe Code:

### creation of differen entity clients

# Queue Sender
queue_sender = SeviceBusSenderClient.from_queue(
    fully_qualified_namepsace="fully_qualified_namepsace",
    queue_name="queue_name",
    credential=ServiceBusSharedKeyCredential("policy", "key")
)

queue_sender = SeviceBusSenderClient.from_connection_string(
    conn_str="conn_str",
    entity_name="queue_name"
)

queue_sender = SeviceBusSenderClient(
    fully_qualified_namepsace="fully_qualified_namepsace",
    entity_name="queue_name",
    ServiceBusSharedKeyCredential("policy", "key")
)

# Queue Receiver
queue_receiver = SeviceBusReceiverClient.from_queue(
    fully_qualified_namepsace="fully_qualified_namepsace",
    queue_name="queue_name",
    credential=ServiceBusSharedKeyCredential("policy", "key")
)

queue_receiver = SeviceBusReceiverClient.from_connection_string(
    conn_str="conn_str",
    entity_name="queue_name"
)

queue_receiver = SeviceBusReceiverClient(
    fully_qualified_namepsace="fully_qualified_namepsace",
    entity_name="queue_name",
    credential=ServiceBusSharedKeyCredential("policy", "key"),
    session="test_session"
)

# Topic Sender
topic_sender = SeviceBusSenderClient.from_topic(
    fully_qualified_namepsace="fully_qualified_namepsace",
    topic_name="topic_name",
    credential=ServiceBusSharedKeyCredential("policy", "key")
)

topic_sender = SeviceBusSenderClient.from_connection_string(
    conn_str="conn_str",
    entity_name="topic_name"
)

topic_sender = SeviceBusSenderClient(
    fully_qualified_namepsace="fully_qualified_namepsace",
    entity_name="topic_name",
    credential=ServiceBusSharedKeyCredential("policy", "key")
)

# Subscription Receiver
subscription_receiver = SeviceBusReceiverClient.from_topic_subscription(
    fully_qualified_namepsace="fully_qualified_namespace",
    topic_name="topic_name",
    subscription_name="subscription_name",
    credential=ServiceBusSharedKeyCredential("policy", "key")
)

subscription_receiver = SeviceBusReceiverClient.from_connection_string(
    conn_str="conn_str",
    entity_name="topic_name",
    subscription_name="subscription_name"
)

subscription_receiver = SeviceBusReceiverClient(
    fully_qualified_namepsace="fully_qualified_namespace",
    entity_name="topic_name",
    subscription_name="subcription_name",
    credential=ServiceBusSharedKeyCredential("policy", "key"),
    session="test_session"
)


### Send and receive
# 1 Send

queue_sender = SeviceBusSenderClient.from_queue(
    fully_qualified_namepsace="fully_qualified_namepsace",
    queue_name="queue_name",
    credential=ServiceBusSharedKeyCredential("policy", "key")
)

'''
topic_sender = SeviceBusSenderClient.from_queue(
    fully_qualified_namepsace="fully_qualified_namepsace",
    topic_name="topic_name",
    credential=ServiceBusSharedKeyCredential("policy", "key")
)
'''

with queue_sender:
    # 1.1 send single
    message = Message("Test message")
    queue_sender.send(message)

    # 1.2 send list
    messages = [Message("Test message {}".format(i)) for i in range(10)]
    queue_sender.send(messages)

    # 1.3 schedule
    schedule_message = Message("scheduled_message")
    enqueue_time = datetime.utcnow() + timedelta(minutes=10)
    sequence_number = queue_sender.schedule(schedule_message, enqueue_time)

    # 1.4 cancel schedule
    queue_sender.cancel_scheduled_messages(*sequence_number)

# 2 Receive

queue_receiver = ServiceBusReceiverClient.from_queue(
    fully_qualified_namespace="fully_qualified_namespace",
    queue_name="queue_name",
    credential=ServiceBusSharedKeyCredential("policy", "key")
)

'''
subscription_receiver = ServiceBusReceiverClient.from_queue(
    fully_qualified_namespace="fully_qualified_namespace",
    topic_name="topic_name",
    subscription_name="subscription_name"
    credential=ServiceBusSharedKeyCredential("policy", "key")
)
'''

# 2.1 peek
with queue_receiver:
    msgs = queue_receiver.peek(count=10)

# 2.2 iterator receive
with queue_receiver:
    for msg in queue_receiver:
        print(message)
        msg.complete()
        # msg.renew_lock()
        # msg.abondon()
        # msg.defer()
        # msg.dead_letter()

# 2.3 pull mode receive
with queue_receiver:
    msgs = queue_receiver.receive(max_batch_size=10)
    for msg in msgs:
        msg.complete()

# 2.4 receive deferred letter
with queue_receiver:
    defered_sequence_numbers = [xxxx]
    deferred = queue_receiver.receive_deferred_messages(defered_sequence_numbers)
    queue_receiver.settle_deferred_messages('completed', deferred)


### Session operation


# 1 Send
topic_sender = SeviceBusSenderClient.from_topic
(
    fully_qualified_namespace="fully_qualified_namepsace",
    topic_name="topic_name",
    credential=ServiceBusSharedKeyCredential("policy", "key")
)

with topic_sender:
    # 1.1 send single
    message = Message("Test message")
    # message.session_id = "test_session"
    topic_sender.send(message, session="test_session")

    # 1.2 send list
    messages = [Message("Test message {}".format(i)) for i in range(10)]
    topic_sender.send(messages, session="test_session")

    # 1.3 schedule
    schedule_message = Message("scheduled_message")
    enqueue_time = datetime.utcnow() + timedelta(minutes=10)
    sequence_number = topic_sender.schedule(schedule_message, enqueue_time, session="test_session")

    # 1.4 cancel schedule
    topic_sender.cancel_scheduled_messages(*sequence_number)

# 2 Receive
subscription_receiver = ServiceBusReceiverClient.from_topic_subscription
(
    fully_qualified_namespace="fully_qualified_namespace",
    topic_name="topic_name",
    subscription_name="subscription_name",
    credential=ServiceBusSharedKeyCredential("policy", "key"),
    session="test_session"
)

# 2.1 peek
with subscription_receiver:
    msgs = subscription_receiver.peek(count=10)

# 2.2 iterator receive
with subscription_receiver:
    session = subscription_receiver.get_session()
    session.set_session_state("START")
    for msg in subscription_receiver:
        print(message)
        msg.complete()
        session.renew_lock()
        if str(msg) == "shutdown":
            session.set_session_state("STOP")
            break

# 2.3 pull mode receive
with subscription_receiver:
    session = subscription_receiver.get_session()
    msgs = subscription_receiver.receive(max_batch_size=10)
    session.set_session_state("BEGIN")
    for msg in msgs:
        msg.complete()
        session.renew_lock()
    session.set_session_state("END")

# 2.4 receive deferred letter
with subscription_receiver:
    session = subscription_receiver.get_session()
    if session.get_session_state() == "DONE":
        defered_sequence_numbers = [xxxx]
        deferred = subscription_receiver.receive_deferred_messages(defered_sequence_numbers)
        subscription_receiver.settle_deferred_messages('completed', deferred)

### Rule operations

subscription_receiver = ServiceBusReceiverClient.from_topic_subscription
(
    fully_qualified_namespace="fully_qualified_namespace",
    topic_name="topic_name",
    subscription_name="subscription_name",
    credential=ServiceBusSharedKeyCredential("policy", "key"))

with subscription_receiver:
    subscription_receiver.get_rules()
    subscription_receiver.add_rule("test_rule", "1=1")
    subscription_receiver.remove_rule("test_rule")

### Transaction operations

subscription_receiver = ServiceBusReceiverClient.from_topic_subscription
(
    fully_qualified_namespace="fully_qualified_namespace",
    topic_name="topic_name",
    subscription_name="subscription_name",
    credential=ServiceBusSharedKeyCredential("policy", "key")
)

with subscription_receiver:
    transaction = subscription_receiver.get_transaction()  # TODO, no idea on how to get a transaction for now
    with transaction:
        try:
            subscription_receiver.add_rule("test_rule", "1=1")
            msgs = subscription_receiver.receive(max_batch_size=1000)
            for msg in msgs:
                msg.abandon()
            subscription_receiver.remove_rule("test_rule")
            session_msgs = subscription_receiver.receive(max_batch_size=1000)
            for msg in session_msgs:
                msg.complete()
        except:
            transaction.abort()

################################################### Split Line ###################################################

# Approach for Session APIs - Option 1
## APIs
### Put session methods on ServiceBusReceiverClient
class ServiceBusReceiverClient:
    def list_sessions(self):
    def set_session_state(self, session_state):
    def get_session_state(self):
    def renew_lock(self):
    @property
    def expired(self):


## Sample Code:
# iterator receive
with subscription_receiver:
    subscription_receiver.set_session_state(session_state="START")
    for msg in subscription_receiver:
        print(message)
        msg.complete()
        subscription_receiver.renew_lock()
        if str(msg) == "shutdown":
            subscription_receiver.set_session_state(session_state="STOP")
            break

# pull mode receive
with subscription_receiver:
    session_id = "test_session"
    msgs = subscription_receiver.receive(max_batch_size=10)
    subscription_receiver.set_session_state(session_state="BEGIN")
    for msg in msgs:
        msg.complete()
        subscription_receiver.renew_lock()
    subscription_receiver.set_session_state(session_state="END")

# receive deferred letter
with subscription_receiver:
    if subscription_receiver.get_session_state() == "DONE":
        defered_sequence_numbers = [xxxx]
        deferred = subscription_receiver.receive_deferred_messages(defered_sequence_numbers)
        subscription_receiver.settle_deferred_messages('completed', deferred)


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
    def get_subscription_rule_manager(self):  # raise Error when called on Queue

class SubscriptionRuleManager:
    def add_rule(self, rule_name, filter):
    def remove_rule(self, rule_name):
    def get_rules(self):


################################################### Split Line ###################################################

# Approach for Rule APIs - Option 3
## APIs
class SubscriptionRuleManager:
    def from_receiver_client_for_subscription(receiver_client):
    def add_rule(self, rule_name, filter):
    def remove_rule(self, rule_name):
    def get_rules(self):
