# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import asyncio
import uuid

import conftest

from azure.servicebus.aio import ServiceBusClient, Message
from azure.servicebus.common.constants import NEXT_AVAILABLE
from azure.servicebus.common.errors import NoActiveSession


async def message_processing(queue_client):
    while True:
        try:
            async with queue_client.get_receiver(session=NEXT_AVAILABLE, idle_timeout=1) as session:
                await session.set_session_state("OPEN")
                async for message in session:
                    print("Message: {}".format(message))
                    print("Time to live: {}".format(message.header.time_to_live))
                    print("Sequence number: {}".format(message.sequence_number))
                    print("Enqueue Sequence numger: {}".format(message.enqueue_sequence_number))
                    print("Partition ID: {}".format(message.partition_id))
                    print("Partition Key: {}".format(message.partition_key))
                    print("Locked until: {}".format(message.locked_until))
                    print("Lock Token: {}".format(message.lock_token))
                    print("Enqueued time: {}".format(message.enqueued_time))
                    await message.complete()
                    if str(message) == 'shutdown':
                        await session.set_session_state("CLOSED")
                        break
        except NoActiveSession:
            return


async def sample_session_send_receive_with_pool_async(sb_config, queue):

    concurrent_receivers = 5
    sessions = [str(uuid.uuid4()) for i in range(concurrent_receivers)]
    client = ServiceBusClient(
        service_namespace=sb_config['hostname'],
        shared_access_key_name=sb_config['key_name'],
        shared_access_key_value=sb_config['access_key'])

    queue_client = client.get_queue(queue)
    for session_id in sessions:
        async with queue_client.get_sender(session=session_id) as sender:
            await asyncio.gather(*[sender.send(Message("Sample message no. {}".format(i))) for i in range(20)])
            await sender.send(Message("shutdown"))

    receive_sessions = [message_processing(queue_client) for _ in range(concurrent_receivers)]
    await asyncio.gather(*receive_sessions)


if __name__ == '__main__':
    live_config = conftest.get_live_servicebus_config()
    queue_name = conftest.create_session_queue(live_config)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(sample_session_send_receive_with_pool_async(live_config, queue_name))
    finally:
        conftest.cleanup_queue(live_config, queue_name)
