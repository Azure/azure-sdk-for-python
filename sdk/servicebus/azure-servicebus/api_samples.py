## Sample Code:

### creation of different entity clients

# Top Level ServiceBusClient
sb_client = ServiceBusClient.from_connection_string(conn_str="conn_str")
sb_client = ServiceBusClient(
    fully_qualified_namespace="fully_qualified_namespace",
    crendetial=ServiceBusSharedKeyCredential("policy", "key")
)

queue_sender = sb_client.get_queue_sender(queue_name="queue_name")
queue_receiver = sb_client.get_queue_receiver(queue_name="queue_name")
topic_sender = sb_client.get_topic_sender(topic_name="topic_name")
subscription_receiver = sb_client.get_subscription_receiver(
    topic_name="topic_name",
    subscription_name="subscription_name"
)

# Queue Sender
queue_sender = ServiceBusSender.from_connection_string(
    conn_str="conn_str",
    queue_name="queue_name"
)

queue_sender = ServiceBusSender(
    fully_qualified_namespace="fully_qualified_namespace",
    queue_name="queue_name",
    ServiceBusSharedKeyCredential("policy", "key")
)

# Queue Receiver
queue_receiver = ServiceBusReceiver.from_connection_string(
    conn_str="conn_str",
    queue_name="queue_name"
)

queue_receiver = ServiceBusReceiver(
    fully_qualified_namespace="fully_qualified_namespace",
    queue_name="queue_name",
    credential=ServiceBusSharedKeyCredential("policy", "key"),
    session_id="test_session"
)

# Topic Sender
topic_sender = ServiceBusSender.from_connection_string(
    conn_str="conn_str",
    topic_name="topic_name"
)

topic_sender = ServiceBusSender(
    fully_qualified_namespace="fully_qualified_namespace",
    topic_name="topic_name",
    credential=ServiceBusSharedKeyCredential("policy", "key")
)

# Subscription Receiver
subscription_receiver = ServiceBusReceiver.from_connection_string(
    conn_str="conn_str",
    topic_name="topic_name",
    subscription_name="subscription_name"
)

subscription_receiver = ServiceBusReceiver(
    fully_qualified_namespace="fully_qualified_namespace",
    topic_name="topic_name",
    subscription_name="subcription_name",
    credential=ServiceBusSharedKeyCredential("policy", "key"),
    session_id="test_session"
)


### Send and receive
# 1 Send
sb_client = ServiceBusClient.from_connection_string(conn_str="conn_str")
queue_sender = sb_client.get_queue_sender(queue_name="queue_name")

with sb_client:
    with queue_sender:
        # 1.1 send single
        message = Message("Test message")
        queue_sender.send(message)

        # 1.2 send batch
        batch_message = topic_sender.create_batch(max_size_in_bytes=256 * 1204)
        while True:
            try:
                batch_message.add(Message("Test message"))
            except ValueError:
                break

        topic_sender.send(batch_message)

        # 1.3 schedule
        schedule_message = Message("scheduled_message")

        schedule_time_utc = datetime.utcnow() + timedelta(minutes=10)
        sequence_number = topic_sender.schedule(schedule_message, schedule_time_utc)

        batch_schedule_message = topic_sender.create_batch(max_size_in_bytes=256 * 1204)

        while True:
            try:
                batch_message.add(Message("Test message"))
            except ValueError:
                break

        batch_sequence_numbers = topic_sender.schedule(batch_schedule_message, schedule_time_utc)

        # 1.4 cancel schedule
        topic_sender.cancel_scheduled_messages(sequence_number)
        topic_sender.cancel_scheduled_messages(batch_sequence_numbers)

# 2 Receive
sb_client = ServiceBusClient.from_connection_string(conn_str="conn_str")
queue_receiver = sb_client.get_queue_receiver(queue_name="queue_name")

# 2.1 peek
with sb_client:
    with queue_receiver:
        msgs = queue_receiver.peek(count=10)
        for msg in msgs:
            print(msg)

# 2.2 iterator receive
with sb_client:
    with queue_receiver:
        for msg in queue_receiver:
            print(message)
            msg.complete()
            # msg.renew_lock()
            # msg.abandon()
            # msg.defer()
            # msg.dead_letter()

# 2.3 pull mode receive
with sb_client:
    with queue_receiver:
        msgs = queue_receiver.receive(max_batch_size=10)
        for msg in msgs:
            msg.complete()

# 2.4 receive deferred letter
with sb_client:
    with queue_receiver:
        defered_sequence_numbers = [1,2,3,4,5,6]
        deferred_messages = queue_receiver.receive_deferred_messages(defered_sequence_numbers)
        for i in deferred_messages:
            deferred_messages.abandon()


### Session operation
# 1 Send
sb_client = ServiceBusClient.from_connection_string(conn_str="conn_str")
topic_sender = sb_client.get_topic_sender(topic_name="topic_name")

with sb_client:
    with topic_sender:
        # 1.1 send single
        message = Message("Test message")
        topic_sender.send(message, session_id="test_session")

        # 1.2 send batch
        batch_message = topic_sender.create_batch()
        while True:
            try:
                batch_message.add(Message("Test message"))
            except ValueError:
                break

        topic_sender.send(batch_message, session_id="test_session")

        # 1.3 schedule
        schedule_message = Message("Scheduled message")
        schedule_time_utc = datetime.utcnow() + timedelta(minutes=10)
        sequence_number = topic_sender.schedule(schedule_message, schedule_time_utc, session_id="test_session")

        batch_schedule_message = topic_sender.create_batch()

        batch_sequence_numbers = topic_sender.schedule(
            message=batch_schedule_message,
            schedule_time_utc=schedule_time_utc,
            session_id="test_session"
        )

        # 1.4 cancel schedule
        topic_sender.cancel_scheduled_messages(sequence_number)
        topic_sender.cancel_scheduled_messages(batch_sequence_numbers)

# 2 Receive
sb_client = ServiceBusClient.from_connection_string(conn_str="conn_str")
subscription_receiver = sb_client.get_subscription_receiver(
    topic_name="topic_name",
    subscription_name="subscription_name",
    session_id="test_session"
)

# 2.1 iterator receive
with sb_client:
    with subscription_receiver:
        session = subscription_receiver.session
        session.set_session_state("START")
        for msg in subscription_receiver:
            if session.expired:
                break
            print(message)
            msg.complete()
            session.renew_lock()

# 2.2 pull mode receive
with sb_client:
    with subscription_receiver:
        session = subscription_receiver.session
        msgs = subscription_receiver.receive(max_batch_size=10)
        session.set_session_state("BEGIN")
        for msg in msgs:
            msg.complete()
            session.renew_lock()
        session.set_session_state("END")

### Rule operation

# 1. get rules
subscription_rule_manager = sb_client.get_subscription_rule_manager("topic_name", "subscription_name")
rules = subscription_rule_manager.get_rules()
for rule in rules:
    print(rule.name)
    print(rule.filter)  # If it's type of correlation, print the detail info
    print(rule.action)

# 2. add rule

# 2.1 add boolean filter rule

subscription_rule_manager.add_rule("rule_name", filter=True, sql_rule_action_expression=None)

# 2.2 add sql filter rule

message = Message("msg")
message.correlation_id = 2
message.user_properties = {"priority" : 2}
subscription_rule_manager.add_rule("rule_name", filter="priority >= 1 AND sys.correlation-id = 2", sql_rule_action_expression=None)

# 2.3 add correlation filter rule

message = Message("msg")
message.correlation_id = 2
message.user_properties = {"key" : "value"}

correlation_filter = CorrelationFilter()
correlation_filter.user_properties = {"key": "value"}
correlation_filter.correlation_id = 2

subscription_rule_manager.add_rule("rule_name", filter=CorrelationFilter, sql_rule_action_expression="SET key = 'new value'")
