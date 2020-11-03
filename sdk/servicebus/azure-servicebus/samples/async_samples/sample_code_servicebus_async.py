# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Examples to show basic async use case of python azure-servicebus SDK, including:
    - Create ServiceBusClient
    - Create ServiceBusSender/ServiceBusReceiver
    - Send single message
    - Receive and settle messages
    - Receive and settle deferred messages
"""
import os
import datetime
import asyncio
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage


_RUN_ITERATOR = False


async def process_message(message):
    print(str(message))


def example_create_servicebus_client_async():
    # [START create_sb_client_from_conn_str_async]
    import os
    from azure.servicebus.aio import ServiceBusClient
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
    # [END create_sb_client_from_conn_str_async]

    # [START create_sb_client_async]
    import os
    from azure.servicebus.aio import ServiceBusClient, ServiceBusSharedKeyCredential
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
    # [END create_sb_client_async]
    return servicebus_client


async def example_create_servicebus_sender_async():
    servicebus_client = example_create_servicebus_client_async()
    # [START create_servicebus_sender_from_conn_str_async]
    import os
    from azure.servicebus.aio import ServiceBusSender
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']
    queue_sender = ServiceBusSender.from_connection_string(
        conn_str=servicebus_connection_str,
        queue_name=queue_name
    )
    # [END create_servicebus_sender_from_conn_str_async]

    # [START create_servicebus_sender_async]
    import os
    from azure.servicebus.aio import ServiceBusSender, ServiceBusSharedKeyCredential
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
    # [END create_servicebus_sender_async]

    # [START create_servicebus_sender_from_sb_client_async]
    import os
    from azure.servicebus.aio import ServiceBusClient
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
    async with servicebus_client:
        queue_sender = servicebus_client.get_queue_sender(queue_name=queue_name)
    # [END create_servicebus_sender_from_sb_client_async]

    # [START create_topic_sender_from_sb_client_async]
    import os
    from azure.servicebus import ServiceBusClient
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    topic_name = os.environ['SERVICE_BUS_TOPIC_NAME']
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
    async with servicebus_client:
        topic_sender = servicebus_client.get_topic_sender(topic_name=topic_name)
    # [END create_topic_sender_from_sb_client_async]

    return queue_sender


async def example_create_servicebus_receiver_async():
    servicebus_client = example_create_servicebus_client_async()

    # [START create_servicebus_receiver_from_conn_str_async]
    import os
    from azure.servicebus.aio import ServiceBusReceiver
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']
    queue_receiver = ServiceBusReceiver.from_connection_string(
        conn_str=servicebus_connection_str,
        queue_name=queue_name
    )
    # [END create_servicebus_receiver_from_conn_str_async]

    # [START create_servicebus_receiver_async]
    import os
    from azure.servicebus.aio import ServiceBusReceiver, ServiceBusSharedKeyCredential
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
    # [END create_servicebus_receiver_async]

    # [START create_queue_deadletter_receiver_from_sb_client_async]
    import os
    from azure.servicebus.aio import ServiceBusClient
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
    async with servicebus_client:
        queue_receiver = servicebus_client.get_queue_deadletter_receiver(queue_name=queue_name)
    # [END create_queue_deadletter_receiver_from_sb_client_async]

    # [START create_servicebus_receiver_from_sb_client_async]
    import os
    from azure.servicebus.aio import ServiceBusClient
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
    async with servicebus_client:
        queue_receiver = servicebus_client.get_queue_receiver(queue_name=queue_name)
    # [END create_servicebus_receiver_from_sb_client_async]

    # [START create_subscription_deadletter_receiver_from_sb_client_async]
    import os
    from azure.servicebus import ServiceBusClient
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    topic_name = os.environ["SERVICE_BUS_TOPIC_NAME"]
    subscription_name = os.environ["SERVICE_BUS_SUBSCRIPTION_NAME"]
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
    async with servicebus_client:
        subscription_receiver = servicebus_client.get_subscription_deadletter_receiver(
            topic_name=topic_name,
            subscription_name=subscription_name,
        )
    # [END create_subscription_deadletter_receiver_from_sb_client_async]

    # [START create_subscription_receiver_from_sb_client_async]
    import os
    from azure.servicebus import ServiceBusClient
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    topic_name = os.environ["SERVICE_BUS_TOPIC_NAME"]
    subscription_name = os.environ["SERVICE_BUS_SUBSCRIPTION_NAME"]
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
    async with servicebus_client:
        subscription_receiver = servicebus_client.get_subscription_receiver(
            topic_name=topic_name,
            subscription_name=subscription_name,
        )
    # [END create_subscription_receiver_from_sb_client_async]

    return queue_receiver


async def example_send_and_receive_async():
    servicebus_sender = await example_create_servicebus_sender_async()
    servicebus_receiver = await example_create_servicebus_receiver_async()

    from azure.servicebus import ServiceBusMessage
    # [START send_async]
    async with servicebus_sender:
        message = ServiceBusMessage("Hello World")
        await servicebus_sender.send_messages(message)
    # [END send_async]

    # [START create_batch_async]
    async with servicebus_sender:
        batch_message = await servicebus_sender.create_message_batch()
        batch_message.add_message(ServiceBusMessage("Single message inside batch"))
    # [END create_batch_async]

    # [START peek_messages_async]
    async with servicebus_receiver:
        messages = await servicebus_receiver.peek_messages()
        for message in messages:
            print(str(message))
    # [END peek_messages_async]

    # [START receive_async]
    async with servicebus_receiver:
        messages = await servicebus_receiver.receive_messages(max_wait_time=5)
        for message in messages:
            print(str(message))
            await servicebus_receiver.complete_message(message)
    # [END receive_async]

    # [START receive_forever_async]
    async with servicebus_receiver:
        async for message in servicebus_receiver.get_streaming_message_iter():
            print(str(message))
            await servicebus_receiver.complete_message(message)
    # [END receive_forever_async]

    # [START auto_lock_renew_message_async]
    from azure.servicebus.aio import AutoLockRenewer

    lock_renewal = AutoLockRenewer()
    async with servicebus_receiver:
        async for message in servicebus_receiver:
            lock_renewal.register(message, timeout=60)
            await process_message(message)
            await servicebus_receiver.complete_message(message)
    # [END auto_lock_renew_message_async]


async def example_receive_deferred_async():
    servicebus_sender = await example_create_servicebus_sender_async()
    servicebus_receiver = await example_create_servicebus_receiver_async()
    async with servicebus_sender:
        await servicebus_sender.send_messages(ServiceBusMessage("Hello World"))
    # [START receive_defer_async]
    async with servicebus_receiver:
        deferred_sequenced_numbers = []
        messages = await servicebus_receiver.receive_messages(max_wait_time=5)
        for message in messages:
            deferred_sequenced_numbers.append(message.sequence_number)
            print(str(message))
            await servicebus_receiver.defer_message(message)

        received_deferred_msg = await servicebus_receiver.receive_deferred_messages(
            sequence_numbers=deferred_sequenced_numbers
        )

        for msg in received_deferred_msg:
            await servicebus_receiver.complete_message(message)
    # [END receive_defer_async]


async def example_session_ops_async():
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']
    session_id = "<your session id>"

    async with ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str) as servicebus_client:
        # [START get_session_async]
        async with servicebus_client.get_queue_receiver(queue_name=queue_name, session_id=session_id) as receiver:
            session = receiver.session
        # [END get_session_async]

        # [START get_session_state_async]
        async with servicebus_client.get_queue_receiver(queue_name=queue_name, session_id=session_id) as receiver:
            session = receiver.session
            session_state = await session.get_state()
        # [END get_session_state_async]

        # [START set_session_state_async]
        async with servicebus_client.get_queue_receiver(queue_name=queue_name, session_id=session_id) as receiver:
            session = receiver.session
            session_state = await session.set_state("START")
        # [END set_session_state_async]

        # [START session_renew_lock_async]
        async with servicebus_client.get_queue_receiver(queue_name=queue_name, session_id=session_id) as receiver:
            session = receiver.session
            session_state = await session.renew_lock()
        # [END session_renew_lock_async]

        # [START auto_lock_renew_session_async]
        from azure.servicebus.aio import AutoLockRenewer

        lock_renewal = AutoLockRenewer()
        async with servicebus_client.get_queue_receiver(queue_name=queue_name, session_id=session_id) as receiver:
            session = receiver.session
            # Auto renew session lock for 2 minutes
            lock_renewal.register(session, timeout=120)
            async for message in receiver:
                await process_message(message)
                await receiver.complete_message(message)
        # [END auto_lock_renew_session_async]
                break


async def example_schedule_ops_async():
    servicebus_sender = await example_create_servicebus_sender_async()
    # [START scheduling_messages_async]
    async with servicebus_sender:
        scheduled_time_utc = datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
        scheduled_messages = [ServiceBusMessage("Scheduled message") for _ in range(10)]
        sequence_nums = await servicebus_sender.schedule_messages(scheduled_messages, scheduled_time_utc)
    # [END scheduling_messages_async]

    # [START cancel_scheduled_messages_async]
    async with servicebus_sender:
        await servicebus_sender.cancel_scheduled_messages(sequence_nums)
    # [END cancel_scheduled_messages_async]


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(example_send_and_receive_async())
    loop.run_until_complete(example_receive_deferred_async())
    loop.run_until_complete(example_schedule_ops_async())
    # loop.run_until_complete(example_session_ops_async())
