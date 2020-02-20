# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import uuid
import concurrent

import conftest

from azure.servicebus import ServiceBusClient, Message
from azure.servicebus.common.constants import NEXT_AVAILABLE
from azure.servicebus.common.errors import NoActiveSession


def message_processing(queue_client, messages):
    while True:
        try:
            with queue_client.get_receiver(session=NEXT_AVAILABLE, idle_timeout=1) as session:
                session.set_session_state("OPEN")
                for message in session:
                    messages.append(message)
                    print("Message: {}".format(message))
                    print("Time to live: {}".format(message.header.time_to_live))
                    print("Sequence number: {}".format(message.sequence_number))
                    print("Enqueue Sequence numger: {}".format(message.enqueue_sequence_number))
                    print("Partition ID: {}".format(message.partition_id))
                    print("Partition Key: {}".format(message.partition_key))
                    print("Locked until: {}".format(message.locked_until))
                    print("Lock Token: {}".format(message.lock_token))
                    print("Enqueued time: {}".format(message.enqueued_time))
                    message.complete()
                    if str(message) == 'shutdown':
                        session.set_session_state("CLOSED")
        except NoActiveSession:
            return


def sample_session_send_receive_with_pool(sb_config, queue):

    concurrent_receivers = 5
    sessions = [str(uuid.uuid4()) for i in range(2 * concurrent_receivers)]
    client = ServiceBusClient(
        service_namespace=sb_config['hostname'],
        shared_access_key_name=sb_config['key_name'],
        shared_access_key_value=sb_config['access_key'],
        debug=False)

    queue_client = client.get_queue(queue)
    for session_id in sessions:
        with queue_client.get_sender(session=session_id) as sender:
            for i in range(20):
                message = Message("Sample message no. {}".format(i))
                sender.send(message)

    all_messages = []
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_receivers) as thread_pool:
        for _ in range(concurrent_receivers):
            futures.append(thread_pool.submit(message_processing, queue_client, all_messages))
        concurrent.futures.wait(futures)

    print("Received total {} messages across {} sessions.".format(len(all_messages), 2*concurrent_receivers))


if __name__ == '__main__':
    live_config = conftest.get_live_servicebus_config()
    queue_name = conftest.create_session_queue(live_config)
    print("Created queue {}".format(queue_name))
    try:
        sample_session_send_receive_with_pool(live_config, queue_name)
    finally:
        print("Cleaning up queue {}".format(queue_name))
        conftest.cleanup_queue(live_config, queue_name)
