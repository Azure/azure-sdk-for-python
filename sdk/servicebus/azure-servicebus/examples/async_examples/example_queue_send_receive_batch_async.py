# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import asyncio

import conftest

from azure.servicebus.aio import ServiceBusClient, Message
from azure.servicebus.common.constants import ReceiveSettleMode


async def sample_queue_send_receive_batch_async(sb_config, queue):
    client = ServiceBusClient(
        service_namespace=sb_config['hostname'],
        shared_access_key_name=sb_config['key_name'],
        shared_access_key_value=sb_config['access_key'],
        debug=False)

    queue_client = client.get_queue(queue)
    async with queue_client.get_sender() as sender:
        for i in range(100):
            message = Message("Sample message no. {}".format(i))
            await sender.send(message)
        await sender.send(Message("shutdown"))

    async with queue_client.get_receiver(idle_timeout=1, mode=ReceiveSettleMode.PeekLock, prefetch=10) as receiver:
        # Receive list of messages as a batch
        batch = await receiver.fetch_next(max_batch_size=10)
        await asyncio.gather(*[m.complete() for m in batch])

        # Receive messages as a continuous generator
        async for message in receiver:
            print("Message: {}".format(message))
            print("Sequence number: {}".format(message.sequence_number))
            await message.complete()


if __name__ == '__main__':
    live_config = conftest.get_live_servicebus_config()
    queue_name = conftest.create_standard_queue(live_config)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(sample_queue_send_receive_batch_async(live_config, queue_name))
    finally:
        conftest.cleanup_queue(live_config, queue_name)
