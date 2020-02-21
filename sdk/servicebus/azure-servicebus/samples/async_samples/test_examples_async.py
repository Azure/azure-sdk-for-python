#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest
import asyncio
import logging
import sys
import os
import pytest
import time
from datetime import datetime, timedelta

from azure.servicebus.aio import (
    ServiceBusClient,
    QueueClient,
    Message,
    BatchMessage,
    DeferredMessage,
    AutoLockRenew)
from azure.servicebus.common.message import PeekMessage
from azure.servicebus.common.constants import ReceiveSettleMode
from azure.servicebus.common.errors import (
    ServiceBusResourceNotFound,
    ServiceBusError,
    MessageLockExpired,
    InvalidHandlerState,
    MessageAlreadySettled,
    AutoLockRenewTimeout,
    MessageSendFailed,
    MessageSettleFailed)


async def process_message(message):
    print(message)

@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_async_snippet_queues(live_servicebus_config, standard_queue):
    # [START create_async_servicebus_client]
    import os
    from azure.servicebus.aio import ServiceBusClient, Message

    namespace = os.environ['SERVICE_BUS_HOSTNAME']
    shared_access_policy = os.environ['SERVICE_BUS_SAS_POLICY']
    shared_access_key = os.environ['SERVICE_BUS_SAS_KEY']

    client = ServiceBusClient(
        service_namespace=namespace,
        shared_access_key_name=shared_access_policy,
        shared_access_key_value=shared_access_key)
    # [END create_async_servicebus_client]

    # [START create_async_servicebus_client_connstr]
    connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']

    client = ServiceBusClient.from_connection_string(connection_str)
    # [END create_async_servicebus_client_connstr]

    # [START get_async_queue_client]
    from azure.servicebus import ServiceBusResourceNotFound

    try:
        queue_client = client.get_queue("MyQueue")
    except ServiceBusResourceNotFound:
        pass
    # [END get_async_queue_client]
    try:
        # [START create_queue_client]
        import os
        from azure.servicebus.aio import QueueClient

        connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
        queue_client = QueueClient.from_connection_string(connection_str, name="MyQueue")
        queue_properties = queue_client.get_properties()

        # [END create_queue_client]
    except ServiceBusResourceNotFound:
        pass

    queue_client = client.get_queue(standard_queue)

    # [START client_peek_messages]
    peeked_messages = await queue_client.peek(count=5)
    # [END client_peek_messages]

    await queue_client.send(Message("a"))
    try:
        # [START client_defer_messages]
        sequence_numbers = []
        async with queue_client.get_receiver() as receiver:
            async for message in receiver:
                sequence_numbers.append(message.sequence_number)
                await message.defer()
                break

        deferred = await queue_client.receive_deferred_messages(sequence_numbers)
        # [END client_defer_messages]
    except ValueError:
        pass

    await queue_client.send(Message("a"))
    try:
        sequence_numbers = []
        async with queue_client.get_receiver(idle_timeout=2) as receiver:
            async for message in receiver:
                sequence_numbers.append(message.sequence_number)
                await message.defer()
                break
        # [START client_settle_deferred_messages]
        deferred = await queue_client.receive_deferred_messages(sequence_numbers)

        await queue_client.settle_deferred_messages('completed', deferred)
        # [END client_settle_deferred_messages]
    except ValueError:
        pass

    # [START open_close_sender_directly]
    from azure.servicebus.aio import Message

    sender = queue_client.get_sender()
    try:
        await sender.open()
        await sender.send(Message("foobar"))
    finally:
        await sender.close()
    # [END open_close_sender_directly]

    # [START queue_client_send]
    from azure.servicebus.aio import Message

    message = Message("Hello World")
    await queue_client.send(message)
    # [END queue_client_send]

    # [START queue_client_send_multiple]
    from azure.servicebus.aio import Message

    messages = [Message("First"), Message("Second")]
    await queue_client.send(messages, message_timeout=30)
    # [END queue_client_send_multiple]

    # [START open_close_receiver_directly]
    receiver = queue_client.get_receiver()
    async for message in receiver:
        print(message)
        break
    await receiver.close()
    # [END open_close_receiver_directly]

    await queue_client.send(Message("a"))
    # [START open_close_receiver_context]
    async with queue_client.get_receiver() as receiver:
        async for message in receiver:
            await process_message(message)
    # [END open_close_receiver_context]
            break

    # [START open_close_sender_context]
    async with queue_client.get_sender() as sender:

        await sender.send(Message("First"))
        await sender.send(Message("Second"))
    # [END open_close_sender_context]

    # [START queue_sender_messages]
    async with queue_client.get_sender() as sender:

        sender.queue_message(Message("First"))
        sender.queue_message(Message("Second"))
        await sender.send_pending_messages()
    # [END queue_sender_messages]

    # [START schedule_messages]
    async with queue_client.get_sender() as sender:

        enqueue_time = datetime.utcnow() + timedelta(minutes=10)
        await sender.schedule(enqueue_time, Message("First"), Message("Second"))
    # [END schedule_messages]

    # [START cancel_schedule_messages]
    async with queue_client.get_sender() as sender:

        enqueue_time = datetime.utcnow() + timedelta(minutes=10)
        sequence_numbers = await sender.schedule(enqueue_time, Message("First"), Message("Second"))

        await sender.cancel_scheduled_messages(*sequence_numbers)
    # [END cancel_schedule_messages]

    # [START receiver_peek_messages]
    async with queue_client.get_receiver() as receiver:
        pending_messages = await receiver.peek(count=5)
    # [END receiver_peek_messages]

    try:
        await queue_client.send(Message("a"))
        # [START receiver_defer_messages]
        async with queue_client.get_receiver() as receiver:
            async for message in receiver:
                sequence_no = message.sequence_number
                await message.defer()
                break

            message = await receiver.receive_deferred_messages([sequence_no])
        # [END receiver_defer_messages]
    except ServiceBusError:
        pass

    await queue_client.send(Message("a"))
    # [START receiver_deadletter_messages]
    async with queue_client.get_receiver(idle_timeout=5) as receiver:
        async for message in receiver:
            await message.dead_letter()

    async with queue_client.get_deadletter_receiver() as receiver:
        async for message in receiver:
            await message.complete()
    # [END receiver_deadletter_messages]
            break

    # [START receiver_fetch_batch]
    async with queue_client.get_receiver(idle_timeout=5, prefetch=100) as receiver:
        messages = await receiver.fetch_next(timeout=5)
        await asyncio.gather(*[m.complete() for m in messages])
    # [END receiver_fetch_batch]

    # [START auto_lock_renew_async_message]
    from azure.servicebus.aio import AutoLockRenew

    lock_renewal = AutoLockRenew()
    async with queue_client.get_receiver(idle_timeout=3) as queue_receiver:
        async for message in queue_receiver:
            lock_renewal.register(message, timeout=60)
            await process_message(message)

            await message.complete()
    # [END auto_lock_renew_async_message]

@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_async_snippet_sessions(live_servicebus_config, session_queue):
    queue_client = QueueClient.from_connection_string(
        live_servicebus_config['conn_str'],
        name=session_queue)
    queue_client.get_properties()

    # [START open_close_session_sender_context]
    from azure.servicebus.aio import Message

    async with queue_client.get_sender(session="MySessionID") as sender:

        await sender.send(Message("First"))
        await sender.send(Message("Second"))
    # [END open_close_session_sender_context]

    # [START queue_session_sender_messages]
    async with queue_client.get_sender(session="MySessionID") as sender:

        sender.queue_message(Message("First"))
        sender.queue_message(Message("Second"))
        await sender.send_pending_messages()
    # [END queue_session_sender_messages]

    # [START schedule_session_messages]
    async with queue_client.get_sender(session="MySessionID") as sender:

        enqueue_time = datetime.utcnow() + timedelta(minutes=10)
        await sender.schedule(enqueue_time, Message("First"), Message("Second"))
    # [END schedule_session_messages]

    # [START open_close_receiver_session_context]
    async with queue_client.get_receiver(session="MySessionID") as session:
        async for message in session:
            await process_message(message)
    # [END open_close_receiver_session_context]
            break

    # [START open_close_receiver_session_nextavailable]
    from azure.servicebus import NEXT_AVAILABLE, NoActiveSession

    try:
        async with queue_client.get_receiver(session=NEXT_AVAILABLE, idle_timeout=5) as receiver:
            async for message in receiver:
                await process_message(message)
    except NoActiveSession:
        pass
    # [END open_close_receiver_session_nextavailable]

    # [START set_session_state]
    async with queue_client.get_receiver(session="MySessionID", idle_timeout=5) as session:
        current_state = await session.get_session_state()
        if not current_state:
            await session.set_session_state("OPENED")
    # [END set_session_state]

    try:
        # [START receiver_peek_session_messages]
        async with queue_client.get_receiver(session=NEXT_AVAILABLE, idle_timeout=5) as receiver:
            pending_messages = await receiver.peek(count=5)
        # [END receiver_peek_session_messages]
    except NoActiveSession:
        pass

    await queue_client.send([Message("a"), Message("b"), Message("c"),  Message("d"),  Message("e"),  Message("f")], session="MySessionID")
    try:
        # [START receiver_defer_session_messages]
        async with queue_client.get_receiver(session="MySessionID", idle_timeout=5) as receiver:
            sequence_numbers = []
            async for message in receiver:
                sequence_numbers.append(message.sequence_number)
                await message.defer()
                break

            message = await receiver.receive_deferred_messages(sequence_numbers)
        # [END receiver_defer_session_messages]
    except ServiceBusError:
        pass

    # [START receiver_renew_session_lock]
    async with queue_client.get_receiver(session="MySessionID", idle_timeout=5) as session:
        async for message in session:
            await process_message(message)
            await session.renew_lock()
    # [END receiver_renew_session_lock]
            break

    # [START auto_lock_renew_async_session]
    from azure.servicebus.aio import AutoLockRenew

    lock_renewal = AutoLockRenew()
    async with queue_client.get_receiver(session="MySessionID", idle_timeout=3) as session:
        lock_renewal.register(session)

        async for message in session:
            await process_message(message)
            await message.complete()
    # [END auto_lock_renew_async_session]
            break

@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_async_snippet_topics(live_servicebus_config, standard_subscription):
    topic_name, subscription_name = standard_subscription

    import os
    from azure.servicebus.aio import ServiceBusClient

    namespace = os.environ['SERVICE_BUS_HOSTNAME']
    shared_access_policy = os.environ['SERVICE_BUS_SAS_POLICY']
    shared_access_key = os.environ['SERVICE_BUS_SAS_KEY']

    client = ServiceBusClient(
        service_namespace=namespace,
        shared_access_key_name=shared_access_policy,
        shared_access_key_value=shared_access_key)

    # [START get_async_topic_client]
    from azure.servicebus import ServiceBusResourceNotFound

    try:
        topic_client = client.get_topic("MyTopic")
    except ServiceBusResourceNotFound:
        pass
    # [END get_async_topic_client]

    try:
        # [START create_topic_client]
        import os
        from azure.servicebus.aio import TopicClient

        connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
        topic_client = TopicClient.from_connection_string(connection_str, name="MyTopic")
        topic_properties = topic_client.get_properties()
        # [END create_topic_client]
    except ServiceBusResourceNotFound:
        pass

    # [START get_async_subscription_client]
    from azure.servicebus import ServiceBusResourceNotFound

    try:
        subscription_client = client.get_subscription("MyTopic", "MySubscription")
    except ServiceBusResourceNotFound:
        pass
    # [END get_async_subscription_client]

    try:
        # [START create_sub_client]
        import os
        from azure.servicebus.aio import SubscriptionClient

        connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
        subscription_client = SubscriptionClient.from_connection_string(connection_str, name="MySubscription", topic="MyTopic")
        properties = subscription_client.get_properties()
        # [END create_sub_client]
    except ServiceBusResourceNotFound:
        pass

@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_async_sample_queue_send_receive_batch(live_servicebus_config, standard_queue):
    try:
        from samples.async_samples.example_queue_send_receive_batch_async import sample_queue_send_receive_batch_async
    except ImportError:
        pytest.skip("")
    await sample_queue_send_receive_batch_async(live_servicebus_config, standard_queue)

@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_async_sample_session_send_receive_batch(live_servicebus_config, session_queue):
    try:
        from samples.async_samples.example_session_send_receive_batch_async import sample_session_send_receive_batch_async
    except ImportError:
        pytest.skip("")
    await sample_session_send_receive_batch_async(live_servicebus_config, session_queue)

@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_async_sample_session_send_receive_with_pool(live_servicebus_config, session_queue):
    try:
        from samples.async_samples.example_session_send_receive_with_pool_async import sample_session_send_receive_with_pool_async
    except ImportError:
        pytest.skip("")
    await sample_session_send_receive_with_pool_async(live_servicebus_config, session_queue)
