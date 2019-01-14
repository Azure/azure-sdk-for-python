#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest

from azure.servicebus import ServiceBusResourceNotFound

def test_example_create_servicebus_client(live_servicebus_config):

# Create a new service bus client using SAS credentials
# [START create_servicebus_client]
    import os
    from azure.servicebus import ServiceBusClient

    namespace = os.environ['SERVICE_BUS_HOSTNAME']
    shared_access_policy = os.environ['SERVICE_BUS_SAS_POLICY']
    shared_access_key = os.environ['SERVICE_BUS_SAS_KEY']

    client = ServiceBusClient(
        service_namespace=namespace,
        shared_access_key_name=shared_access_policy,
        shared_access_key_value=shared_access_key)

# [END create_servicebus_client]

# [START create_servicebus_client_connstr]
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

    
def _create_servicebus_client(sb_config):

    import os
    from azure.servicebus import ServiceBusClient

    client = ServiceBusClient(
    service_namespace=sb_config['hostname'],
    shared_access_key_name=sb_config['key_name'],
    shared_access_key_value=sb_config['access_key'],
    debug=True)

    return client

def test_example_send_receive_service_bus(live_servicebus_config, standard_queue, session_queue):
    import os
    from azure.servicebus import ServiceBusClient, ServiceBusResourceNotFound
    from azure.servicebus import Message

    client = _create_servicebus_client(live_servicebus_config)

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


 # [START list_sessions_service_bus]
    session_ids = session_client.list_sessions()

    # List sessions updated after specific time
    import datetime
    yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
    session_ids = session_client.list_sessions(updated_since=yesterday)
 # [END list_sessions_service_bus]


# [START receive_deferred_messages_service_bus]
    seq_numbers = []
    with queue_client.get_receiver() as queue_receiver:
        for message in queue_receiver:
            seq_numbers.append(message.sequence_number)
            message.defer()

    # Receive deferred messages - provide sequence numbers of
    # messages which were deferred.
    deferred = queue_client.receive_deferred_messages(sequence_numbers=seq_numbers)
# [END receive_deferred_messages_service_bus]

# [START settle_deferred_messages_service_bus]
    queue_client.settle_deferred_messages('completed', deferred)
# [END settle_deferred_messages_service_bus]


# [START get_dead_letter_receiver]
    # Get dead lettered messages
    with queue_client.get_deadletter_receiver(idle_timeout=1) as dead_letter_receiver:
        # Peek at messages
        message = dead_letter_receiver.peek()
    
        # Receive dead letterted messages in Batch
        messages_batch = dead_letter_receiver.fetch_next()
        for message in messages_batch:
            print(message)

            # Indicate message acceptance
            message.complete()

        # Receive dead lettered message continuously
        for message in dead_letter_receiver:
            print(message)
            message.complete()
# [END get_dead_letter_receiver]


def test_example_receiver_client(live_servicebus_config, standard_queue):
    import os
    import datetime
    from azure.servicebus import ServiceBusClient
    from azure.servicebus import Message
    from azure.servicebus.receive_handler import Receiver, SessionReceiver

    sb_client = _create_servicebus_client(live_servicebus_config)
    queue_client = sb_client.get_queue(standard_queue)

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
    num_unprocessed_msgs = receiver.queue_size()
# [END queue_size]




# [START create_session_receiver_client]

    handler_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    session_receiver_client =  SessionReceiver(
            handler_id,
            recv_config['source'],
            recv_config['auth_config'],
            debug=recv_config['debug'],
            session=session_id,
            timeout=recv_config['timeout'],
            prefetch=int(recv_config['prefetch']),
            mode=recv_config['mode'])

# [END create_session_receiver_client]

# [Session Receivers only operations]

# [START set_session_state]
# Set the session state
    session_receiver_client.set_session_state('START')
# [END set_session_state]

# [START get_session_state]
# Get the session state
    session_state = session_receiver_client.get_session_state()
# [END get_session_state]

# [START renew_lock]
# Renew session lock before it expires
    session_receiver_client.renew_lock()
# [END renew_lock]

# [START list_sessions]
# List sessions
    session_ids = session_receiver_client.list_sessions()

# List sessions updated after specific time
    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)
    session_ids = session_receiver_client.list_sessions(updated_since=yesterday)
# [END list_sessions]

    


def test_example_receiver_message_functions(sb_config,seq_numbers):
    import os
    import datetime
    from azure.servicebus import ServiceBusClient
    from azure.servicebus import Message

# Create a new service bus client using SAS credentials
    session_id = str(uuid.uuid4())
    client = _create_servicebus_client(sb_config)
    receiver_client = client.get_queue().get_receiver(session_id)
    #receiver_client = client.get_subscription().get_receiver(session_id)

# [START peek_messages]
# Peek at specific number of messages
    receiver_client.peek(count=5)
# [END peek_messages]

# [START fetch_next_messages]
# Receive messages in Batch (specify the amount )
    messages = receiver_client.fetch_next(max_batch_size=15, timeout=1)
    for m in messages:
        print(m.message)
# [END fetch_next_messages]

# [START receive_deferred_messages]
# Receive deferred messages 
# Provide sequence numbers of messages which were deferred.
    receiver_client.receive_deferred_messages(sequence_numbers=seq_numbers)
# [END receive_deferred_messages]
    



def test_example_create_sender_send_message(sb_config, queue_name, sender_config):
    import os
    from azure.servicebus import ServiceBusClient
    from azure.servicebus import Message
    from azure.servicebus.send_handler import Sender, SessionSender

    #[START create_sender_client]
    handler_id = str(uuid.uuid4())

    sender = Sender(
                handler_id,
                sender_config['source'],
                sender_config['auth_config'],
                session=sender_config['session'],
                debug=ender_config['debug'],
                msg_timeout=mender_config['message_timeout'])
    #[END create_sender_client]

    #[START create_session_sender_client]
    session_sender = SessionSender(
            handler_id,
            sender_config['source'],
            sender_config['auth_config'],
            session=sender_config['session'],
            debug=ender_config['debug'],
            msg_timeout=mender_config['message_timeout'])

    # [END create_session_sender_client]

# Create a new service bus client using SAS credentials
    sb_client = _create_servicebus_client(sb_config)
# [Alternatively Get the Sender from Service Bus Client]
# Get the queue client
    queue_client = sb_client.get_queue(queue_name)
# Get the sender - a single open Connection with which multiple send operations can be made
    sender2 = queue_client.get_sender()

# [START send_message]
# Send the message via sender
    message = Message("Hello World!")
    sender.send(message)
# [END send_message]

# Get the session receiver - A Receiver represents a single open Connection with which multiple receive operations can be made.
    receiver = queue_client.get_receiver(idle_timeout=1)
#Process the recevied messages
    for message in receiver:
        print(message)
    # Indicate message acceptance
        message.complete()

# [START reconnect]
# Reconnect to the service, if connection error happens.
    sender.reconnect()
# [END reconnect]



def test_example_message_scheduling_descheduling(sb_config, queue_name):
    import os
    import datetime
    from azure.servicebus import ServiceBusClient
    from azure.servicebus import Message

# Create a new service bus client using SAS credentials
# Create_servicebus_client
    session_id = str(uuid.uuid4())
    client = _create_servicebus_client(sb_config)

# Get the queue client
    queue_client = client.get_queue(queue_name)

# [START scheduling_messages]
# Get the sender - a single open Connection with which multiple send operations can be made
    sender = queue_client.get_sender(session_id)
    message = Message("Hello World!")
    today = datetime.datetime.today()
# Schedule the message 5 days from today
    sequence_numbers = sender.schedule(today + datetime.timedelta(days=5),[message])
# [END scheduling_messages]

# [START cancel_scheduled_messages]
# Cancel the scheduled messages
    sender.cancel_scheduled_messages(sequence_numbers)
# [END cancel_scheduled_messages]


    
def test_example_queue_and_send_pending_messages(sb_config, queue_name):
    import os
    from azure.servicebus import ServiceBusClient
    from azure.servicebus import Message
# Create a new service bus client using SAS credentials
# Create_servicebus_client
    session_id = str(uuid.uuid4())
    client = _create_servicebus_client(sb_config)

# Get the queue client
    queue_client = client.get_queue(queue_name)
# Get the sender - a single open Connection with which multiple send operations can be made
    sender = queue_client.get_sender(session_id)
# Prepare messages to queue

# [START queue_messages]
    message = Message("Hello World!")
    message_next = Message("How are you?")
    sender.queue_message(message)
    sender.queue_message(message_next)
# [END queue_messages]

# [START send_pending_messages]
# Send the pending messages
    message_send_status = sender.send_pending_messages()
    i = 0
    for status in message_send_status:
        messageSent = status[0]
        if(not(messageSent)):
            failureReason = status[1].description
            print("Message at Index {} was not sent. Reason: {}".format(i,failureReason))
# [END send_pending_messages]


def test_sample_queue_send_receive_batch(live_servicebus_config, standard_queue):
    try:
        from examples.example_queue_send_receive_batch import sample_queue_send_receive_batch
    except ImportError:
        pytest.skip("")
    sample_queue_send_receive_batch(live_servicebus_config, standard_queue)


def test_sample_session_send_receive_batch(live_servicebus_config, session_queue):
    try:
        from examples.example_session_send_receive_batch import sample_session_send_receive_batch
    except ImportError:
        pytest.skip("")
    sample_session_send_receive_batch(live_servicebus_config, session_queue)


def test_sample_session_send_receive_with_pool(live_servicebus_config, session_queue):
    try:
        from examples.example_session_send_receive_with_pool import sample_session_send_receive_with_pool
    except ImportError:
        pytest.skip("")
    sample_session_send_receive_with_pool(live_servicebus_config, session_queue)
