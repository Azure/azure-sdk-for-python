# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Examples to show basic use case of python azure-servicebus SDK, including:
    - Create ServiceBusClient
    - Create ServiceBusSender/ServiceBusReceiver
    - Send single message
    - Receive and settle messages
    - Receive and settle deferred messages
"""

import os
import datetime
from azure.servicebus import ServiceBusClient, ServiceBusMessage


def process_message(message):
    print(str(message))


def example_create_servicebus_client_sync():
    # [START create_sb_client_from_conn_str_sync]
    import os
    from azure.servicebus import ServiceBusClient
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
    # [END create_sb_client_from_conn_str_sync]

    # [START create_sb_client_sync]
    import os
    from azure.servicebus import ServiceBusClient, ServiceBusSharedKeyCredential
    fully_qualified_namespace = os.environ['SERVICE_BUS_FULLY_QUALIFIED_NAMESPACE']
    shared_access_policy = os.environ['SERVICE_BUS_SAS_POLICY']
    shared_access_key = os.environ['SERVICE_BUS_SAS_KEY']
    servicebus_client = ServiceBusClient(
        fully_qualified_namespace=fully_qualified_namespace,
        credential=ServiceBusSharedKeyCredential(
            shared_access_policy,
            shared_access_key
        )
    )
    # [END create_sb_client_sync]
    return servicebus_client


def example_create_servicebus_sender_sync():
    servicebus_client = example_create_servicebus_client_sync()
    # [START create_servicebus_sender_from_conn_str_sync]
    import os
    from azure.servicebus import ServiceBusSender
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']
    queue_sender = ServiceBusSender.from_connection_string(
        conn_str=servicebus_connection_str,
        queue_name=queue_name
    )
    # [END create_servicebus_sender_from_conn_str_sync]

    # [START create_servicebus_sender_sync]
    import os
    from azure.servicebus import ServiceBusSender, ServiceBusSharedKeyCredential
    fully_qualified_namespace = os.environ['SERVICE_BUS_FULLY_QUALIFIED_NAMESPACE']
    shared_access_policy = os.environ['SERVICE_BUS_SAS_POLICY']
    shared_access_key = os.environ['SERVICE_BUS_SAS_KEY']
    queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']
    queue_sender = ServiceBusSender(
        fully_qualified_namespace=fully_qualified_namespace,
        credential=ServiceBusSharedKeyCredential(
            shared_access_policy,
            shared_access_key
        ),
        queue_name=queue_name
    )
    # [END create_servicebus_sender_sync]

    # [START create_servicebus_sender_from_sb_client_sync]
    import os
    from azure.servicebus import ServiceBusClient
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
    with servicebus_client:
        queue_sender = servicebus_client.get_queue_sender(queue_name=queue_name)
    # [END create_servicebus_sender_from_sb_client_sync]

    # [START create_topic_sender_from_sb_client_sync]
    import os
    from azure.servicebus import ServiceBusClient
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    topic_name = os.environ['SERVICE_BUS_TOPIC_NAME']
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
    with servicebus_client:
        topic_sender = servicebus_client.get_topic_sender(topic_name=topic_name)
    # [END create_topic_sender_from_sb_client_sync]

    return queue_sender


def example_create_servicebus_receiver_sync():
    servicebus_client = example_create_servicebus_client_sync()

    # [START create_servicebus_receiver_from_conn_str_sync]
    import os
    from azure.servicebus import ServiceBusReceiver
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']
    queue_receiver = ServiceBusReceiver.from_connection_string(
        conn_str=servicebus_connection_str,
        queue_name=queue_name
    )
    # [END create_servicebus_receiver_from_conn_str_sync]

    # [START create_servicebus_receiver_sync]
    import os
    from azure.servicebus import ServiceBusReceiver, ServiceBusSharedKeyCredential
    fully_qualified_namespace = os.environ['SERVICE_BUS_FULLY_QUALIFIED_NAMESPACE']
    shared_access_policy = os.environ['SERVICE_BUS_SAS_POLICY']
    shared_access_key = os.environ['SERVICE_BUS_SAS_KEY']
    queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']
    queue_receiver = ServiceBusReceiver(
        fully_qualified_namespace=fully_qualified_namespace,
        credential=ServiceBusSharedKeyCredential(
            shared_access_policy,
            shared_access_key
        ),
        queue_name=queue_name
    )
    # [END create_servicebus_receiver_sync]

    # [START create_queue_deadletter_receiver_from_sb_client_sync]
    import os
    from azure.servicebus import ServiceBusClient
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
    with servicebus_client:
        queue_receiver = servicebus_client.get_queue_deadletter_receiver(queue_name=queue_name)
    # [END create_queue_deadletter_receiver_from_sb_client_sync]

    # [START create_servicebus_receiver_from_sb_client_sync]
    import os
    from azure.servicebus import ServiceBusClient
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
    with servicebus_client:
        queue_receiver = servicebus_client.get_queue_receiver(queue_name=queue_name)
    # [END create_servicebus_receiver_from_sb_client_sync]

    # [START create_subscription_receiver_from_sb_client_sync]
    import os
    from azure.servicebus import ServiceBusClient
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    topic_name = os.environ["SERVICE_BUS_TOPIC_NAME"]
    subscription_name = os.environ["SERVICE_BUS_SUBSCRIPTION_NAME"]
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
    with servicebus_client:
        subscription_receiver = servicebus_client.get_subscription_receiver(
            topic_name=topic_name,
            subscription_name=subscription_name,
        )
    # [END create_subscription_receiver_from_sb_client_sync]

    # [START create_subscription_deadletter_receiver_from_sb_client_sync]
    import os
    from azure.servicebus import ServiceBusClient
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    topic_name = os.environ["SERVICE_BUS_TOPIC_NAME"]
    subscription_name = os.environ["SERVICE_BUS_SUBSCRIPTION_NAME"]
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
    with servicebus_client:
        subscription_receiver = servicebus_client.get_subscription_deadletter_receiver(
            topic_name=topic_name,
            subscription_name=subscription_name,
        )
    # [END create_subscription_deadletter_receiver_from_sb_client_sync]

    return queue_receiver


def example_send_and_receive_sync():
    servicebus_sender = example_create_servicebus_sender_sync()
    servicebus_receiver = example_create_servicebus_receiver_sync()

    from azure.servicebus import ServiceBusMessage
    # [START send_sync]
    with servicebus_sender:
        message = ServiceBusMessage("Hello World")
        servicebus_sender.send_messages(message)
    # [END send_sync]

    # [START create_batch_sync]
    with servicebus_sender:
        batch_message = servicebus_sender.create_message_batch()
        batch_message.add_message(ServiceBusMessage("Single message inside batch"))
    # [END create_batch_sync]

    # [START send_complex_message]
    message = ServiceBusMessage(
        "Hello World!!",
        session_id="MySessionID",
        partition_key="UsingSpecificPartition",
        user_properties={'data': 'custom_data'},
        time_to_live=datetime.timedelta(seconds=30),
        label='MyLabel'
    )
    # [END send_complex_message]

    # [START peek_messages_sync]
    with servicebus_receiver:
        messages = servicebus_receiver.peek_messages()
        for message in messages:
            print(str(message))
    # [END peek_messages_sync]

    # [START auto_lock_renew_message_sync]
    from azure.servicebus import AutoLockRenewer
    lock_renewal = AutoLockRenewer(max_workers=4)
    with servicebus_receiver:
        for message in servicebus_receiver:
            # Auto renew message for 1 minute.
            lock_renewal.register(message, timeout=60)
            process_message(message)
            servicebus_receiver.complete_message(message)
    # [END auto_lock_renew_message_sync]
            break

    # [START receive_sync]
    with servicebus_receiver:
        messages = servicebus_receiver.receive_messages(max_wait_time=5)
        for message in messages:
            print(str(message))
            servicebus_receiver.complete_message(message)
    # [END receive_sync]

        # [START receive_complex_message]
        messages = servicebus_receiver.receive_messages(max_wait_time=5)
        for message in messages:
            print("Receiving: {}".format(message))
            print("Time to live: {}".format(message.time_to_live))
            print("Sequence number: {}".format(message.sequence_number))
            print("Enqueued Sequence numger: {}".format(message.enqueued_sequence_number))
            print("Partition Key: {}".format(message.partition_key))
            print("Properties: {}".format(message.properties))
            print("Delivery count: {}".format(message.delivery_count))
            print("Message ID: {}".format(message.message_id))
            print("Locked until: {}".format(message.locked_until_utc))
            print("Lock Token: {}".format(message.lock_token))
            print("Enqueued time: {}".format(message.enqueued_time_utc))
        # [END receive_complex_message]

        # [START abandon_message]
        messages = servicebus_receiver.receive_messages(max_wait_time=5)
        for message in messages:
            servicebus_receiver.abandon_message(message)
        # [END abandon_message]

    # [START receive_forever]
    with servicebus_receiver:
        for message in servicebus_receiver.get_streaming_message_iter():
            print(str(message))
            servicebus_receiver.complete_message(message)
    # [END receive_forever]
            break


def example_receive_deferred_sync():
    servicebus_sender = example_create_servicebus_sender_sync()
    servicebus_receiver = example_create_servicebus_receiver_sync()
    with servicebus_sender:
        servicebus_sender.send_messages(ServiceBusMessage("Hello World"))
    # [START receive_defer_sync]
    with servicebus_receiver:
        deferred_sequenced_numbers = []
        messages = servicebus_receiver.receive_messages(max_wait_time=5)
        for message in messages:
            deferred_sequenced_numbers.append(message.sequence_number)
            print(str(message))
            servicebus_receiver.defer_message(message)

        received_deferred_msg = servicebus_receiver.receive_deferred_messages(
            sequence_numbers=deferred_sequenced_numbers
        )

        for msg in received_deferred_msg:
            servicebus_receiver.complete_message(msg)
    # [END receive_defer_sync]


def example_receive_deadletter_sync():
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']

    with ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str) as servicebus_client:
        with servicebus_client.get_queue_sender(queue_name) as servicebus_sender:
            servicebus_sender.send_messages(ServiceBusMessage("Hello World"))
        # [START receive_deadletter_sync]
        with servicebus_client.get_queue_receiver(queue_name) as servicebus_receiver:
            messages = servicebus_receiver.receive_messages(max_wait_time=5)
            for message in messages:
                servicebus_receiver.dead_letter_message(message, reason='reason for dead lettering', description='description for dead lettering')

        with servicebus_client.get_queue_deadletter_receiver(queue_name) as servicebus_deadletter_receiver:
            messages = servicebus_deadletter_receiver.receive_messages(max_wait_time=5)
            for message in messages:
                servicebus_receiver.complete_message(message)
        # [END receive_deadletter_sync]


def example_session_ops_sync():
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']
    session_id = "<your session id>"

    with ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str) as servicebus_client:
        # [START get_session_sync]
        with servicebus_client.get_queue_receiver(queue_name=queue_name, session_id=session_id) as receiver:
            session = receiver.session
        # [END get_session_sync]

        # [START get_session_state_sync]
        with servicebus_client.get_queue_receiver(queue_name=queue_name, session_id=session_id) as receiver:
            session = receiver.session
            session_state = session.get_state()
        # [END get_session_state_sync]

        # [START set_session_state_sync]
        with servicebus_client.get_queue_receiver(queue_name=queue_name, session_id=session_id) as receiver:
            session = receiver.session
            session_state = session.set_state("START")
        # [END set_session_state_sync]

        # [START session_renew_lock_sync]
        with servicebus_client.get_queue_receiver(queue_name=queue_name, session_id=session_id) as receiver:
            session = receiver.session
            session_state = session.renew_lock()
        # [END session_renew_lock_sync]

        # [START auto_lock_renew_session_sync]
        from azure.servicebus import AutoLockRenewer

        lock_renewal = AutoLockRenewer(max_workers=4)
        with servicebus_client.get_queue_receiver(queue_name=queue_name, session_id=session_id) as receiver:
            session = receiver.session
            # Auto renew session lock for 2 minutes
            lock_renewal.register(receiver, session, timeout=120)
            for message in receiver:
                process_message(message)
                receiver.complete_message(message)
        # [END auto_lock_renew_session_sync]
                break


def example_schedule_ops_sync():
    servicebus_sender = example_create_servicebus_sender_sync()
    # [START scheduling_messages]
    with servicebus_sender:
        scheduled_time_utc = datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
        scheduled_messages = [ServiceBusMessage("Scheduled message") for _ in range(10)]
        sequence_nums = servicebus_sender.schedule_messages(scheduled_messages, scheduled_time_utc)
    # [END scheduling_messages]

    # [START cancel_scheduled_messages]
    with servicebus_sender:
        servicebus_sender.cancel_scheduled_messages(sequence_nums)
    # [END cancel_scheduled_messages]


example_send_and_receive_sync()
example_receive_deferred_sync()
example_schedule_ops_sync()
# example_session_ops_sync()
