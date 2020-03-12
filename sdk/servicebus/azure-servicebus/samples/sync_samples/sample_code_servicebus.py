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
import datetime
from azure.servicebus import Message


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
    fully_qualified_namespace = os.environ['SERVICE_BUS_CONNECTION_STR']
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
    fully_qualified_namespace = os.environ['SERVICE_BUS_CONNECTION_STR']
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
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str, logging_enable=True)
    with servicebus_client:
        queue_sender = servicebus_client.get_queue_sender(queue_name=queue_name)
    # [END create_servicebus_sender_from_sb_client_sync]
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
    fully_qualified_namespace = os.environ['SERVICE_BUS_CONNECTION_STR']
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

    # [START create_servicebus_receiver_from_sb_client_sync]
    import os
    from azure.servicebus import ServiceBusClient
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str, logging_enable=True)
    with servicebus_client:
        queue_receiver = servicebus_client.get_queue_receiver(queue_name=queue_name)
    # [END create_servicebus_receiver_from_sb_client_sync]

    return queue_receiver


def example_send_and_receive_sync():
    servicebus_sender = example_create_servicebus_sender_sync()
    servicebus_receiver = example_create_servicebus_receiver_sync()

    from azure.servicebus import Message
    # [START servicebus_sender_send_sync]
    with servicebus_sender:
        message = Message("Hello World")
        servicebus_sender.send(message)
    # [END servicebus_sender_send_sync]

    # [START send_complex_message]
    message = Message("Hello World!!")
    message.session_id = "MySessionID"
    message.partition_key = "UsingSpecificPartition"
    message.user_properties = {'data': 'custom_data'}
    message.time_to_live = datetime.timedelta(seconds=30)
    # [END send_complex_message]

    # [START servicebus_receiver_receive_sync]
    with servicebus_receiver:
        messages = servicebus_receiver.receive(timeout=5)
        for message in messages:
            print(message)
            message.complete()
    # [END servicebus_receiver_receive_sync]

        # [START receive_complex_message]
        messages = servicebus_receiver.receive(timeout=5)
        for message in messages:
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


def example_receive_deferred_sync():
    servicebus_sender = example_create_servicebus_sender_sync()
    servicebus_receiver = example_create_servicebus_receiver_sync()
    with servicebus_sender:
        servicebus_sender.send(Message("Hello World"))
    # [START servicebus_receiver_receive_defer_sync]
    with servicebus_receiver:
        deferred_sequenced_numbers = []
        messages = servicebus_receiver.receive(max_batch_size=10, timeout=5)
        for message in messages:
            deferred_sequenced_numbers.append(message.sequence_number)
            print(message)
            message.defer()

        received_deferred_msg = servicebus_receiver.receive_deferred_messages(
            sequence_numbers=deferred_sequenced_numbers
        )

        for msg in received_deferred_msg:
            msg.complete()
    # [END servicebus_receiver_receive_defer_sync]


example_send_and_receive_sync()
example_receive_deferred_sync()
