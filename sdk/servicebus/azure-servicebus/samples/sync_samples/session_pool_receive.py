#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid
import concurrent

from azure.servicebus import ServiceBusClient, Message, AutoLockRenew
from azure.servicebus import NoActiveSession

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
# Note: This must be a session-enabled queue.
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]

def message_processing(sb_client, queue_name, messages):
    while True:
        try:
            with sb_client.get_queue_session_receiver(queue_name, idle_timeout=1) as receiver:
                renewer = AutoLockRenew()
                renewer.register(receiver.session, timeout=None)
                receiver.session.set_session_state("OPEN")
                for message in receiver:
                    messages.append(message)
                    print("Message: {}".format(message))
                    print("Time to live: {}".format(message.header.time_to_live))
                    print("Sequence number: {}".format(message.sequence_number))
                    print("Enqueue Sequence numger: {}".format(message.enqueue_sequence_number))
                    print("Partition ID: {}".format(message.partition_id))
                    print("Partition Key: {}".format(message.partition_key))
                    print("Locked until: {}".format(message.locked_until_utc))
                    print("Lock Token: {}".format(message.lock_token))
                    print("Enqueued time: {}".format(message.enqueued_time_utc))
                    message.complete()
                    if str(message) == 'shutdown':
                        receiver.session.set_session_state("CLOSED")
                renewer.shutdown()
        except NoActiveSession:
            print("There are no non-empty sessions remaining; exiting.  This may present as a UserError in the azure portal.")
            return


def sample_session_send_receive_with_pool(connection_string, queue_name):

    concurrent_receivers = 5
    sessions = [str(uuid.uuid4()) for i in range(2 * concurrent_receivers)]
    with ServiceBusClient.from_connection_string(connection_string) as client:
    
        with client.get_queue_sender(queue_name) as sender:
            for session_id in sessions:
                for i in range(20):
                    message = Message("Sample message no. {}".format(i), session_id=session_id)
                    sender.send(message)

        all_messages = []
        futures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_receivers) as thread_pool:
            for _ in range(concurrent_receivers):
                futures.append(thread_pool.submit(message_processing, client, queue_name, all_messages))
            concurrent.futures.wait(futures)

        print("Received total {} messages across {} sessions.".format(len(all_messages), len(sessions)))


if __name__ == '__main__':
    sample_session_send_receive_with_pool(CONNECTION_STR, QUEUE_NAME)
