#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import asyncio
import uuid

from azure.servicebus.aio import ServiceBusClient, AutoLockRenew
from azure.servicebus import Message
from azure.servicebus.exceptions import NoActiveSession


CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
# Note: This must be a session-enabled queue.
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]


async def message_processing(servicebus_client, queue_name):
    while True:
        try:
            async with servicebus_client.get_queue_session_receiver(queue_name, idle_timeout=1) as receiver:
                renewer = AutoLockRenew()
                renewer.register(receiver.session)
                await receiver.session.set_session_state("OPEN")
                async for message in receiver:
                    print("Message: {}".format(message))
                    print("Time to live: {}".format(message.header.time_to_live))
                    print("Sequence number: {}".format(message.sequence_number))
                    print("Enqueue Sequence number: {}".format(message.enqueue_sequence_number))
                    print("Partition ID: {}".format(message.partition_id))
                    print("Partition Key: {}".format(message.partition_key))
                    print("Locked until: {}".format(message.locked_until_utc))
                    print("Lock Token: {}".format(message.lock_token))
                    print("Enqueued time: {}".format(message.enqueued_time_utc))
                    await message.complete()
                    if str(message) == 'shutdown':
                        await receiver.session.set_session_state("CLOSED")
                        break
                await renewer.shutdown()
        except NoActiveSession:
            print("There are no non-empty sessions remaining; exiting.  This may present as a UserError in the azure portal.")
            return


async def sample_session_send_receive_with_pool_async(connection_string, queue_name):

    concurrent_receivers = 5
    sessions = [str(uuid.uuid4()) for i in range(concurrent_receivers)]
    client = ServiceBusClient.from_connection_string(connection_string)

    for session_id in sessions:
        async with client.get_queue_sender(queue_name) as sender:
            await asyncio.gather(*[sender.send(Message("Sample message no. {}".format(i), session_id=session_id)) for i in range(20)])
            await sender.send(Message("shutdown", session_id=session_id))

    receive_sessions = [message_processing(client, queue_name) for _ in range(concurrent_receivers)]
    await asyncio.gather(*receive_sessions)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sample_session_send_receive_with_pool_async(CONNECTION_STR, QUEUE_NAME))