
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
    session_id="test_session"
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
    session_id="test_session"
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

    # 1.2 send batch
    batch_message = topic_sender.create_batch(max_size_in_bytes=256 * 1204)
    while True:
        try:
            batch_message.try_add(Message("Test message"))
        except ValueError:
            break

    topic_sender.send(batch_message)

    # 1.3 schedule
    schedule_message = Message("scheduled_message")

    enqueue_time = datetime.utcnow() + timedelta(minutes=10)
    sequence_number = topic_sender.schedule(schedule_message, enqueue_time)

    batch_schedule_message = topic_sender.create_batch(max_size_in_bytes=256 * 1204)
    while True:
        try:
            batch_message.try_add(Message("Test message"))
        except ValueError:
            break

    batch_sequence_numbers = topic_sender.schedule(batch_schedule_message, enqueue_time)

    # 1.4 cancel schedule
    topic_sender.cancel_scheduled_messages(sequence_number)
    topic_sender.cancel_scheduled_messages(batch_sequence_numbers)

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
    topic_sender.send(message, session_id="test_session")

    # 1.2 send batch
    batch_message = topic_sender.create_batch(max_size_in_bytes=256 * 1204, seesion_id="test_session")
    while True:
        try:
            batch_message.try_add(Message("Test message"))
        except ValueError:
            break

    topic_sender.send(batch_message)

    # 1.3 schedule
    schedule_message = Message("scheduled_message")

    enqueue_time = datetime.utcnow() + timedelta(minutes=10)
    sequence_number = topic_sender.schedule(schedule_message, enqueue_time, session_id="test_session")

    batch_schedule_message = topic_sender.create_batch(max_size_in_bytes=256 * 1204)
    while True:
        try:
            batch_message.try_add(Message("Test message"))
        except ValueError:
            break

    batch_sequence_numbers = topic_sender.schedule(batch_schedule_message, enqueue_time)

    # 1.4 cancel schedule
    topic_sender.cancel_scheduled_messages(sequence_number)
    topic_sender.cancel_scheduled_messages(batch_sequence_numbers)

# 2 Receive
subscription_receiver = ServiceBusReceiverClient.from_topic_subscription
(
    fully_qualified_namespace="fully_qualified_namespace",
    topic_name="topic_name",
    subscription_name="subscription_name",
    credential=ServiceBusSharedKeyCredential("policy", "key"),
    session_id="test_session"
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
        defered_sequence_numbers = [1,2,3,4,5]
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