# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import asyncio
import uuid

import conftest

from azure.servicebus.aio import ServiceBusClient, Message


async def sample_session_send_receive_batch_async(sb_config, queue):

    session_id = str(uuid.uuid4())
    client = ServiceBusClient(
        service_namespace=sb_config['hostname'],
        shared_access_key_name=sb_config['key_name'],
        shared_access_key_value=sb_config['access_key'])

    queue_client = client.get_queue(queue)

    async with queue_client.get_sender(session=session_id) as sender:
        for i in range(100):
            message = Message("Sample message no. {}".format(i))
            await sender.send(message)
        await sender.send(Message("shutdown"))

    async with queue_client.get_receiver(session=session_id) as session:
        await session.set_session_state("START")
        async for message in session:
            await message.complete()
            if str(message) == "shutdown":
                await session.set_session_state("END")
                break


if __name__ == '__main__':
    live_config = conftest.get_live_servicebus_config()
    queue_name = conftest.create_session_queue(live_config)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(sample_session_send_receive_batch_async(live_config, queue_name))
    finally:
        conftest.cleanup_queue(live_config, queue_name)
