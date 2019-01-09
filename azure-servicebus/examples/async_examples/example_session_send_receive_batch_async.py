#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import asyncio
import logging
import sys
import uuid
import pytest

import conftest

from azure.servicebus.aio import ServiceBusClient, Message


def get_logger(level):
    azure_logger = logging.getLogger("azure")
    if not azure_logger.handlers:
        azure_logger.setLevel(level)
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s'))
        azure_logger.addHandler(handler)

    uamqp_logger = logging.getLogger("uamqp")
    if not uamqp_logger.handlers:
        uamqp_logger.setLevel(logging.INFO)
        uamqp_logger.addHandler(handler)
    return azure_logger


logger = get_logger(logging.INFO)


async def sample_session_send_receive_batch(sb_config, queue):

    session_id = str(uuid.uuid4())
    client = ServiceBusClient(
        service_namespace=sb_config['hostname'],
        shared_access_key_name=sb_config['key_name'],
        shared_access_key_value=sb_config['access_key'],
        debug=True)

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


@pytest.mark.asyncio
async def test_async_sample_session_send_receive_batch(live_servicebus_config, session_queue):
    await sample_session_send_receive_batch(live_servicebus_config, session_queue)


if __name__ == '__main__':
    live_config = conftest.get_live_servicebus_config()
    queue_name = conftest.create_session_queue(live_config)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(sample_session_send_receive_batch(live_config, queue_name))
    finally:
        conftest.cleanup_queue(live_config, queue_name)
