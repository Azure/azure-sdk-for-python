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
    ServiceBusError,
    MessageLockExpired,
    InvalidHandlerState,
    MessageAlreadySettled,
    AutoLockRenewTimeout,
    MessageSendFailed,
    MessageSettleFailed)

from examples.async_examples.example_queue_send_receive_batch_async import sample_queue_send_receive_batch_async
from examples.async_examples.example_session_send_receive_batch_async import sample_session_send_receive_batch_async
from examples.async_examples.example_session_send_receive_with_pool_async import sample_session_send_receive_with_pool_async


async def process_message(message):
    print(message)


@pytest.mark.asyncio
async def test_async_snippet_queues(live_servicebus_config, standard_queue):

# [START create_servicebus_client]
    import os
    from azure.servicebus.aio import ServiceBusClient

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

# [START get_queue_client]
    from azure.servicebus import ServiceBusResourceNotFound

    try:
        queue_client = client.get_queue("MyQueue")
    except ServiceBusResourceNotFound:
        pass
# [END get_queue_client]


    # queue_client = QueueClient.from_connection_string(
    #     live_servicebus_config['conn_str'],
    #     name=standard_queue,
    #     debug=True)
    queue_client = client.get_queue(standard_queue)

# [START client_peek_messages]
    peeked_messages = await queue_client.peek(count=5)
# [END client_peek_messages]

# [START client_defer_messages]
    sequence_numbers = []
    async with queue_client.get_receiver() as receiver:
        async for message in receiver:
            sequence_numbers.append(message.sequence_number)
            await message.defer()

    deferred = await queue_client.receive_deferred_messages(sequence_numbers)
# [END client_defer_messages]

# [START client_settle_deferred_messages]
    deferred = await queue_client.receive_deferred_messages(sequence_numbers)

    await queue_client.settle_deferred_messages('completed', deferred)
# [END client_settle_deferred_messages]

# [START open_close_sender_directly]
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
    queue_client.send(message)
# [END queue_client_send]

# [START queue_client_send_multiple]
    from azure.servicebus.aio import Message

    messages = [Message("First"), Message("Second")]
    queue_client.send(messages, message_timeout=30)
# [END queue_client_send_multiple]

# [START open_close_receiver_directly]
    receiver = queue_client.get_receiver()
    async for message in receiver:
        print(message)
        break
    await receiver.close()
# [END open_close_receiver_directly]

# [START open_close_receiver_context]
    async with queue_client.get_receiver() as receiver:
        async for message in receiver:
            await process_message(message)
# [END open_close_receiver_context]

# [START receiver_peek_messages]
    async with queue_client.get_receiver() as receiver:
        pending_messages = await receiver.peek(count=5)
# [END receiver_peek_messages]

# [START receiver_defer_messages]
    async with queue_client.get_receiver() as receiver:
        async for message in receiver:
            sequence_no = message.sequence_number
            await message.defer()
            break

        message = await receiver.receive_deferred_messages([sequence_no])
# [END receiver_defer_messages]

# [START receiver_fetch_batch]
    async with queue_client.get_receiver(prefetch=100) as receiver:
        messages = await receiver.fetch_batch(timeout=5)
        await asyncio.gather(*[m.complete() for m in messages])
# [END receiver_fetch_batch]


@pytest.mark.asyncio
async def test_async_snippet_sessions(live_servicebus_config, session_queue):
    queue_client = QueueClient.from_connection_string(
        live_servicebus_config['conn_str'],
        name=session_queue,
        debug=True)
    queue_client.get_properties()

# [START open_close_receiver_session_context]
    async with queue_client.get_receiver(session="MySession") as session:
        async for message in session:
            await process_message(message)
# [END open_close_receiver_session_context]

# [START open_close_receiver_session_nextavailable]
    from azure.servicebus import NEXT_AVAILABLE, NoActiveSession

    try:
        async with queue_client.get_receiver(session=NEXT_AVAILABLE) as receiver:
            async for message in receiver:
                await process_message(message)
    except NoActiveSession:
        pass
# [END open_close_receiver_session_nextavailable]

# [START set_session_state]
    async with queue_client.get_receiver(session="MySession") as session:
        current_state = await session.get_session_state()
        if not current_state:
            await session.set_session_state("OPENED")
# [START set_session_state]

# [START receiver_peek_session_messages]
    async with queue_client.get_receiver(session=NEXT_AVAILABLE) as receiver:
        pending_messages = await receiver.peek(count=5)
# [END receiver_peek_session_messages]

# [START receiver_defer_session_messages]
    async with queue_client.get_receiver(session="MySession") as receiver:
        async for message in receiver:
            sequence_no = message.sequence_number
            await message.defer()
            break

        message = await receiver.receive_deferred_messages([sequence_no])
# [END receiver_defer_session_messages]

# [START receiver_renew_session_lock]
    async with queue_client.get_receiver(session="MySession") as session:
        async for message in session:
            await process_message(message)
            await session.renew_lock()
# [END receiver_renew_session_lock]


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

# [START get_topic_client]
    from azure.servicebus import ServiceBusResourceNotFound

    try:
        topic_client = client.get_topic("MyTopic")
    except ServiceBusResourceNotFound:
        pass
# [END get_topic_client]

# [START get_subscription_client]
    from azure.servicebus import ServiceBusResourceNotFound

    try:
        subscription_client = client.get_subscription("MyTopic", "MySubscription")
    except ServiceBusResourceNotFound:
        pass
# [END get_subscription_client]




@pytest.mark.asyncio
async def test_async_sample_queue_send_receive_batch(live_servicebus_config, standard_queue):
    await sample_queue_send_receive_batch_async(live_servicebus_config, standard_queue)


@pytest.mark.asyncio
async def test_async_sample_session_send_receive_batch(live_servicebus_config, session_queue):
    await sample_session_send_receive_batch_async(live_servicebus_config, session_queue)


@pytest.mark.asyncio
async def test_async_sample_session_send_receive_with_pool(live_servicebus_config, session_queue):
    await sample_session_send_receive_with_pool_async(live_servicebus_config, session_queue)
