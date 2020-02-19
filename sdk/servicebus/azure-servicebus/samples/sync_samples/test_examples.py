#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest
import datetime
import os

from azure.servicebus import ServiceBusResourceNotFound, ServiceBusError

def create_servicebus_client():
    # [START create_servicebus_client]
    import os
    from azure.servicebus import ServiceBusClient

    namespace = os.environ['SERVICE_BUS_HOSTNAME']
    shared_access_policy = os.environ['SERVICE_BUS_SAS_POLICY']
    shared_access_key = os.environ['SERVICE_BUS_SAS_KEY']

    # Create a new Service Bus client using SAS credentials
    client = ServiceBusClient(
        service_namespace=namespace,
        shared_access_key_name=shared_access_policy,
        shared_access_key_value=shared_access_key)

    # [END create_servicebus_client]
    return client


def process_message(message):
    print(message)

# TODO: Prior to Track2 release, these should be converted to console-runnable.  See EventHubs.
@pytest.mark.liveTest
def test_example_create_servicebus_client(live_servicebus_config):

    client = create_servicebus_client()

    # [START create_servicebus_client_connstr]
    from azure.servicebus import ServiceBusClient
    connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']

    client = ServiceBusClient.from_connection_string(connection_str)
    # [END create_servicebus_client_connstr]

    try:
        # [START get_queue_client]
        # Queue Client can be used to send and receive messages
        # from an Azure ServiceBus Service
        queue_name = 'MyQueue'
        queue_client = client.get_queue(queue_name)
        # [END get_queue_client]
    except ServiceBusResourceNotFound:
        pass

    # [START list_queues]
    queues = client.list_queues()
    # Process the queues
    for queue_client in queues:
        print(queue_client.name)
    # [END list_queues]

    try:
        # [START get_topic_client]
        # Topic Client can be used to send messages to an Azure ServiceBus Service
        topic_name = 'MyTopic'
        topic_client = client.get_topic(topic_name)
        # [END get_topic_client]
    except ServiceBusResourceNotFound:
        pass

    # [START list_topics]
    topics = client.list_topics()
    # Process topics
    for topic_client in topics:
        print(topic_client.name)
    # [END list_topics]

    try:
        # [START get_subscription_client]
        # Subscription client can receivce messages from Azure Service Bus subscription
        subscription_name = 'MySubscription'
        subscription_client = client.get_subscription(topic_name, subscription_name)
        # [END get_subscription_client]
    except ServiceBusResourceNotFound:
        pass

    # [START list_subscriptions]
    subscriptions = client.list_subscriptions(topic_name)
    # Process subscriptions
    for sub_client in subscriptions:
        print(sub_client.name)
    # [END list_subscriptions]

@pytest.mark.liveTest
def test_example_send_receive_service_bus(live_servicebus_config, standard_queue, session_queue):
    import os
    import datetime
    from azure.servicebus import ServiceBusClient, ServiceBusResourceNotFound
    from azure.servicebus import Message

    client = create_servicebus_client()

    try:
        # [START create_queue_client_directly]
        import os
        from azure.servicebus import QueueClient

        connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
        queue_client = QueueClient.from_connection_string(connection_str, name="MyQueue")
        queue_properties = queue_client.get_properties()

        # [END create_queue_client_directly]
    except ServiceBusResourceNotFound:
        pass

    try:
        # [START create_topic_client_directly]
        import os
        from azure.servicebus import TopicClient

        connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
        topic_client = TopicClient.from_connection_string(connection_str, name="MyTopic")
        properties = topic_client.get_properties()

        # [END create_topic_client_directly]
    except ServiceBusResourceNotFound:
        pass

    try:
        # [START create_sub_client_directly]
        import os
        from azure.servicebus import SubscriptionClient

        connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
        subscription_client = SubscriptionClient.from_connection_string(
            connection_str, name="MySub", topic="MyTopic")
        properties = subscription_client.get_properties()

        # [END create_sub_client_directly]
    except ServiceBusResourceNotFound:
        pass

    queue_client = client.get_queue(standard_queue)
    session_client = client.get_queue(session_queue)

    # [START get_sender]
    with queue_client.get_sender() as queue_sender:

        queue_sender.send(Message("First"))
        queue_sender.send(Message("Second"))
    # [END get_sender]

    # [START send_message_service_bus_multiple]
    from azure.servicebus import Message

    message1 = Message("Hello World!")
    message2 = Message("How are you?")
    queue_client.send([message1, message2])
    # [END send_message_service_bus_multiple]

    # [START send_complex_message]
    message = Message("Hello World!")
    message.session_id = "MySessionID"
    message.partition_key = "UsingSpecificPartition"
    message.user_properties = {'data': 'custom_data'}
    message.time_to_live = datetime.timedelta(seconds=30)

    queue_client.send(message)
    # [END send_complex_message]

    # [START send_batch_message]
    from azure.servicebus import BatchMessage

    def batched_data():
        for i in range(100):
            yield "Batched Message no. {}".format(i)

    message = BatchMessage(batched_data())
    results = queue_client.send(message)
    # [END send_batch_message]

    # [START send_message_service_bus]
    from azure.servicebus import Message

    message = Message("Hello World!")
    queue_client.send(message)
    # [END send_message_service_bus]

    # [START get_receiver]
    with queue_client.get_receiver() as queue_receiver:
        messages = queue_receiver.fetch_next(timeout=3)
    # [END get_receiver]

    # [START peek_messages_service_bus]
    # Specify the number of messages to peek at.
    pending_messages = queue_client.peek(count=5)
    # [END peek_messages_service_bus]

    # [START auto_lock_renew_message]
    from azure.servicebus import AutoLockRenew

    lock_renewal = AutoLockRenew(max_workers=4)
    with queue_client.get_receiver(idle_timeout=3) as queue_receiver:
        for message in queue_receiver:
            # Auto renew message for 1 minute.
            lock_renewal.register(message, timeout=60)
            process_message(message)

            message.complete()
    # [END auto_lock_renew_message]

    # [START auto_lock_renew_session]
    from azure.servicebus import AutoLockRenew

    lock_renewal = AutoLockRenew(max_workers=4)
    with session_client.get_receiver(session="MySessionID", idle_timeout=3) as session:
        # Auto renew session lock for 2 minutes
        lock_renewal.register(session, timeout=120)

        for message in session:
            process_message(message)
            message.complete()
    # [END auto_lock_renew_session]

    # [START list_sessions_service_bus]
    session_ids = session_client.list_sessions()

    # List sessions updated after specific time
    import datetime
    yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
    session_ids = session_client.list_sessions(updated_since=yesterday)
    # [END list_sessions_service_bus]

    try:
        # [START receive_deferred_messages_service_bus]
        seq_numbers = []
        with queue_client.get_receiver(idle_timeout=3) as queue_receiver:
            for message in queue_receiver:
                seq_numbers.append(message.sequence_number)
                message.defer()

        # Receive deferred messages - provide sequence numbers of
        # messages which were deferred.
        deferred = queue_client.receive_deferred_messages(sequence_numbers=seq_numbers)
        # [END receive_deferred_messages_service_bus]
    except ValueError:
        pass
    deferred = []
    try:
        # [START settle_deferred_messages_service_bus]
        queue_client.settle_deferred_messages('completed', deferred)
        # [END settle_deferred_messages_service_bus]
    except ValueError:
        pass

    # [START get_dead_letter_receiver]
    # Get dead lettered messages
    with queue_client.get_deadletter_receiver(idle_timeout=1) as dead_letter_receiver:

        # Receive dead lettered message continuously
        for message in dead_letter_receiver:
            print(message)
            message.complete()
    # [END get_dead_letter_receiver]

@pytest.mark.liveTest
def test_example_receiver_client(live_servicebus_config, standard_queue, session_queue):
    import os
    import datetime
    from azure.servicebus import ServiceBusClient
    from azure.servicebus import Message
    from azure.servicebus.receive_handler import Receiver, SessionReceiver

    sb_client = create_servicebus_client()
    queue_client = sb_client.get_queue(standard_queue)
    session_client = sb_client.get_queue(session_queue)
    queue_client.send([Message("a"), Message("b"), Message("c"),  Message("d"),  Message("e"),  Message("f")])
    session_client.send([Message("a"), Message("b"), Message("c"),  Message("d"),  Message("e"),  Message("f")], session="MySessionID")

    # [START open_close_receiver_connection]
    receiver = queue_client.get_receiver()
    for message in receiver:
        print(message)
        break
    receiver.close()
    # [END open_close_receiver_connection]

    # [START create_receiver_client]
    with queue_client.get_receiver() as receiver:
        for message in receiver:
            process_message(message)
    # [END create_receiver_client]
            break

    # [START queue_size]
    # Get the number of unprocessed messages in queue
    num_unprocessed_msgs = receiver.queue_size
    # [END queue_size]

    # [START peek_messages]
    # Peek at specific number of messages
    with queue_client.get_receiver() as receiver:
        receiver.peek(count=5)
    # [END peek_messages]

    # [START receive_complex_message]
    with queue_client.get_receiver(idle_timeout=3) as receiver:
        for message in receiver:
            print("Receiving: {}".format(message))
            print("Time to live: {}".format(message.time_to_live))
            print("Sequence number: {}".format(message.sequence_number))
            print("Enqueue Sequence numger: {}".format(message.enqueue_sequence_number))
            print("Partition ID: {}".format(message.partition_id))
            print("Partition Key: {}".format(message.partition_key))
            print("User Properties: {}".format(message.user_properties))
            print("Annotations: {}".format(message.annotations))
            print("Delivery count: {}".format(message.header.delivery_count))
            print("Message ID: {}".format(message.properties.message_id))
            print("Locked until: {}".format(message.locked_until))
            print("Lock Token: {}".format(message.lock_token))
            print("Enqueued time: {}".format(message.enqueued_time))
    # [END receive_complex_message]

    try:
        # [START receive_deferred_messages]
        seq_numbers = []
        with queue_client.get_receiver(idle_timeout=3) as queue_receiver:
            for message in queue_receiver:
                seq_numbers.append(message.sequence_number)
                message.defer()

        # Receive deferred messages - provide sequence numbers of
        # messages which were deferred.
        with queue_client.get_receiver() as queue_receiver:
            deferred = queue_receiver.receive_deferred_messages(sequence_numbers=seq_numbers)
        # [END receive_deferred_messages]
    except ValueError:
        pass

    # [START fetch_next_messages]
    with queue_client.get_receiver(prefetch=200) as queue_receiver:
        # Receive messages in Batch (specify the amount )
        messages = queue_receiver.fetch_next(max_batch_size=15, timeout=1)
        for m in messages:
            print(m.message)
    # [END fetch_next_messages]


    # [START create_session_receiver_client]
    with session_client.get_receiver(session="MySessionID") as session:
        for message in session:
            process_message(message)
    # [END create_session_receiver_client]
            break

    # [START create_receiver_session_nextavailable]
    from azure.servicebus import NEXT_AVAILABLE, NoActiveSession

    try:
        with session_client.get_receiver(session=NEXT_AVAILABLE, idle_timeout=5) as receiver:
            for message in receiver:
                process_message(message)
    except NoActiveSession:
        pass
    # [END create_receiver_session_nextavailable]

    # [START set_session_state]
    # Set the session state
    with session_client.get_receiver(session="MySessionID") as receiver:
        receiver.set_session_state('START')
    # [END set_session_state]

    # [START get_session_state]
    # Get the session state
    with session_client.get_receiver(session="MySessionID") as receiver:
        session_state = receiver.get_session_state()
    # [END get_session_state]

    # [START renew_lock]
    # Renew session lock before it expires
    with session_client.get_receiver(session="MySessionID") as session:
        messages = session.fetch_next(timeout=3)
        session.renew_lock()
    # [END renew_lock]

    # [START list_sessions]
    # List sessions
    with session_client.get_receiver(session="MySessionID") as receiver:
        session_ids = receiver.list_sessions()

        # List sessions updated after specific time
        today = datetime.datetime.today()
        yesterday = today - datetime.timedelta(days=1)
        session_ids = receiver.list_sessions(updated_since=yesterday)
    # [END list_sessions]

@pytest.mark.liveTest
def test_example_create_sender_send_message(live_servicebus_config, standard_queue, session_queue):
    import os
    from azure.servicebus import ServiceBusClient
    from azure.servicebus import Message
    from azure.servicebus.send_handler import Sender, SessionSender

    sb_client = create_servicebus_client()
    queue_client = sb_client.get_queue(standard_queue)
    session_client = sb_client.get_queue(session_queue)

    # [START create_sender_client]
    from azure.servicebus import Message

    with queue_client.get_sender() as sender:
        sender.send(Message("Hello World!"))

    # [END create_sender_client]

    # [START create_session_sender_client]
    from azure.servicebus import Message

    with session_client.get_sender(session="MySessionID") as sender:
        sender.send(Message("Hello World!"))

    with session_client.get_sender() as sender:
        message = Message("Hello World!")
        message.session_id = "MySessionID"
        sender.send(message)
    # [END create_session_sender_client]

    # [START send_message]
    # Send the message via sender
    with queue_client.get_sender() as sender:
        message = Message("Hello World!")
        sender.send(message)
    # [END send_message]

    # [START scheduling_messages]
    with queue_client.get_sender() as sender:
        message = Message("Hello World!")
        today = datetime.datetime.today()

        # Schedule the message 5 days from today
        sequence_numbers = sender.schedule(today + datetime.timedelta(days=5), message)
    # [END scheduling_messages]

    # [START cancel_scheduled_messages]
    with queue_client.get_sender() as sender:
        message = Message("Hello World!")
        today = datetime.datetime.today()

        # Schedule the message 5 days from today
        sequence_numbers = sender.schedule(today + datetime.timedelta(days=5), message)

        # Cancel scheduled messages
        sender.cancel_scheduled_messages(*sequence_numbers)
    # [END cancel_scheduled_messages]

    # [START queue_and_send_messages]
    with queue_client.get_sender() as sender:
        message1 = Message("Hello World!")
        message2 = Message("How are you?")
        sender.queue_message(message1)
        sender.queue_message(message2)

        message_status = sender.send_pending_messages()
        for status in message_status:
            if not status[0]:
                print("Message send failed: {}".format(status[1]))
    # [END queue_and_send_messages]

    # [START queue_and_send_session_messages]
    with queue_client.get_sender(session="MySessionID") as sender:
        message1 = Message("Hello World!")
        message2 = Message("How are you?")
        sender.queue_message(message1)
        sender.queue_message(message2)

        message_status = sender.send_pending_messages()
        for status in message_status:
            if not status[0]:
                print("Message send failed: {}".format(status[1]))
    # [END queue_and_send_session_messages]

@pytest.mark.liveTest
def test_sample_queue_send_receive_batch(live_servicebus_config, standard_queue):
    try:
        from samples.sync_samples.example_queue_send_receive_batch import sample_queue_send_receive_batch
    except ImportError:
        pytest.skip("")
    sample_queue_send_receive_batch(live_servicebus_config, standard_queue)

@pytest.mark.liveTest
def test_sample_session_send_receive_batch(live_servicebus_config, session_queue):
    try:
        from samples.sync_samples.example_session_send_receive_batch import sample_session_send_receive_batch
    except ImportError:
        pytest.skip("")
    sample_session_send_receive_batch(live_servicebus_config, session_queue)

@pytest.mark.liveTest
def test_sample_session_send_receive_with_pool(live_servicebus_config, session_queue):
    try:
        from samples.sync_samples.example_session_send_receive_with_pool import sample_session_send_receive_with_pool
    except ImportError:
        pytest.skip("")
    sample_session_send_receive_with_pool(live_servicebus_config, session_queue)
