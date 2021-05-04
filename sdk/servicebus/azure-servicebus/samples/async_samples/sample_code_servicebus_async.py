# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Examples to show basic async use case of python azure-servicebus SDK, including:
    - Create ServiceBusClient
    - Create ServiceBusSender/ServiceBusReceiver
    - Send single message and batch messages
    - Peek, receive and settle messages
    - Receive and settle dead-lettered messages
    - Receive and settle deferred messages
    - Schedule and cancel scheduled messages
    - Session related operations
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
    from azure.identity.aio import DefaultAzureCredential
    from azure.servicebus.aio import ServiceBusClient
    fully_qualified_namespace = os.environ['SERVICE_BUS_FULLY_QUALIFIED_NAMESPACE']
    servicebus_client = ServiceBusClient(
        fully_qualified_namespace=fully_qualified_namespace,
        credential=DefaultAzureCredential()
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
    queue_sender = ServiceBusSender._from_connection_string(
        conn_str=servicebus_connection_str,
        queue_name=queue_name
    )
    # [END create_servicebus_sender_from_conn_str_async]

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
    from azure.servicebus.aio import ServiceBusClient
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    topic_name = os.environ['SERVICE_BUS_TOPIC_NAME']
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
    async with servicebus_client:
        topic_sender = servicebus_client.get_topic_sender(topic_name=topic_name)
    # [END create_topic_sender_from_sb_client_async]

    queue_sender = servicebus_client.get_queue_sender(queue_name=queue_name)
    return queue_sender


async def example_create_servicebus_receiver_async():
    servicebus_client = example_create_servicebus_client_async()

    # [START create_servicebus_receiver_from_conn_str_async]
    import os
    from azure.servicebus.aio import ServiceBusReceiver
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']
    queue_receiver = ServiceBusReceiver._from_connection_string(
        conn_str=servicebus_connection_str,
        queue_name=queue_name
    )
    # [END create_servicebus_receiver_from_conn_str_async]

    # [START create_queue_deadletter_receiver_from_sb_client_async]
    import os
    from azure.servicebus import ServiceBusSubQueue
    from azure.servicebus.aio import ServiceBusClient
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
    async with servicebus_client:
        queue_receiver = servicebus_client.get_queue_receiver(queue_name=queue_name, sub_queue=ServiceBusSubQueue.DEAD_LETTER)
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
    from azure.servicebus import ServiceBusSubQueue
    from azure.servicebus.aio import ServiceBusClient
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    topic_name = os.environ["SERVICE_BUS_TOPIC_NAME"]
    subscription_name = os.environ["SERVICE_BUS_SUBSCRIPTION_NAME"]
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str)
    async with servicebus_client:
        subscription_receiver = servicebus_client.get_subscription_receiver(
            topic_name=topic_name,
            subscription_name=subscription_name,
            sub_queue=ServiceBusSubQueue.DEAD_LETTER
        )
    # [END create_subscription_deadletter_receiver_from_sb_client_async]

    # [START create_subscription_receiver_from_sb_client_async]
    import os
    from azure.servicebus.aio import ServiceBusClient
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

    queue_receiver = servicebus_client.get_queue_receiver(queue_name=queue_name)
    return queue_receiver


async def example_send_and_receive_async():
    from azure.servicebus import ServiceBusMessage
    servicebus_sender = await example_create_servicebus_sender_async()
    # [START send_async]
    async with servicebus_sender:
        message = ServiceBusMessage("Hello World")
        await servicebus_sender.send_messages(message)
    # [END send_async]
        await servicebus_sender.send_messages([ServiceBusMessage("Hello World")] * 5)

    servicebus_sender = await example_create_servicebus_sender_async()
    # [START create_batch_async]
    async with servicebus_sender:
        batch_message = await servicebus_sender.create_message_batch()
        batch_message.add_message(ServiceBusMessage("Single message inside batch"))
    # [END create_batch_async]

    servicebus_receiver = await example_create_servicebus_receiver_async()
    # [START peek_messages_async]
    async with servicebus_receiver:
        messages = await servicebus_receiver.peek_messages()
        for message in messages:
            print(str(message))
    # [END peek_messages_async]

    servicebus_receiver = await example_create_servicebus_receiver_async()
    # [START receive_async]
    async with servicebus_receiver:
        messages = await servicebus_receiver.receive_messages(max_wait_time=5)
        for message in messages:
            print(str(message))
            await servicebus_receiver.complete_message(message)
    # [END receive_async]

    servicebus_receiver = await example_create_servicebus_receiver_async()
    # [START receive_forever_async]
    async with servicebus_receiver:
        async for message in servicebus_receiver:
            print(str(message))
            await servicebus_receiver.complete_message(message)
    # [END receive_forever_async]
            break

        # [START abandon_message_async]
        messages = await servicebus_receiver.receive_messages(max_wait_time=5)
        for message in messages:
            await servicebus_receiver.abandon_message(message)
        # [END abandon_message_async]

        # [START complete_message_async]
        messages = await servicebus_receiver.receive_messages(max_wait_time=5)
        for message in messages:
            await servicebus_receiver.complete_message(message)
        # [END complete_message_async]

        # [START defer_message_async]
        messages = await servicebus_receiver.receive_messages(max_wait_time=5)
        for message in messages:
            await servicebus_receiver.defer_message(message)
        # [END defer_message_async]

        # [START dead_letter_message_async]
        messages = await servicebus_receiver.receive_messages(max_wait_time=5)
        for message in messages:
            await servicebus_receiver.dead_letter_message(message)
        # [END dead_letter_message_async]

        # [START renew_message_lock_async]
        messages = await servicebus_receiver.receive_messages(max_wait_time=5)
        for message in messages:
            await servicebus_receiver.renew_message_lock(message)
        # [END renew_message_lock_async]

    servicebus_receiver = await example_create_servicebus_receiver_async()
    # [START auto_lock_renew_message_async]
    from azure.servicebus.aio import AutoLockRenewer

    lock_renewal = AutoLockRenewer()
    async with servicebus_receiver:
        async for message in servicebus_receiver:
            lock_renewal.register(servicebus_receiver, message, max_lock_renewal_duration=60)
            await process_message(message)
            await servicebus_receiver.complete_message(message)
    # [END auto_lock_renew_message_async]
            break
    await lock_renewal.close()


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

        for message in received_deferred_msg:
            await servicebus_receiver.complete_message(message)
    # [END receive_defer_async]


async def example_receive_deadletter_async():
    from azure.servicebus import ServiceBusSubQueue
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']

    async with ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str) as servicebus_client:
        async with servicebus_client.get_queue_sender(queue_name) as servicebus_sender:
            await servicebus_sender.send_messages(ServiceBusMessage("Hello World"))
        # [START receive_deadletter_async]
        async with servicebus_client.get_queue_receiver(queue_name) as servicebus_receiver:
            messages = await servicebus_receiver.receive_messages(max_wait_time=5)
            for message in messages:
                await servicebus_receiver.dead_letter_message(
                    message,
                    reason='reason for dead lettering',
                    error_description='description for dead lettering'
                )

        async with servicebus_client.get_queue_receiver(queue_name, sub_queue=ServiceBusSubQueue.DEAD_LETTER) as servicebus_deadletter_receiver:
            messages = await servicebus_deadletter_receiver.receive_messages(max_wait_time=5)
            for message in messages:
                await servicebus_deadletter_receiver.complete_message(message)
        # [END receive_deadletter_async]


async def example_session_ops_async():
    servicebus_connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
    queue_name = os.environ['SERVICE_BUS_SESSION_QUEUE_NAME']
    session_id = "<your session id>"

    async with ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str) as servicebus_client:

        async with servicebus_client.get_queue_sender(queue_name=queue_name) as sender:
            await sender.send_messages(ServiceBusMessage('msg', session_id=session_id))

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
            await session.set_state("START")
        # [END set_session_state_async]

        # [START session_renew_lock_async]
        async with servicebus_client.get_queue_receiver(queue_name=queue_name, session_id=session_id) as receiver:
            session = receiver.session
            await session.renew_lock()
        # [END session_renew_lock_async]

        # [START auto_lock_renew_session_async]
        from azure.servicebus.aio import AutoLockRenewer

        lock_renewal = AutoLockRenewer()
        async with servicebus_client.get_queue_receiver(queue_name=queue_name, session_id=session_id) as receiver:
            session = receiver.session
            # Auto renew session lock for 2 minutes
            lock_renewal.register(receiver, session, max_lock_renewal_duration=120)
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

    servicebus_sender = await example_create_servicebus_sender_async()
    # [START cancel_scheduled_messages_async]
    async with servicebus_sender:
        await servicebus_sender.cancel_scheduled_messages(sequence_nums)
    # [END cancel_scheduled_messages_async]


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(example_send_and_receive_async())
    loop.run_until_complete(example_receive_deferred_async())
    loop.run_until_complete(example_schedule_ops_async())
    loop.run_until_complete(example_receive_deadletter_async())
    loop.run_until_complete(example_session_ops_async())
