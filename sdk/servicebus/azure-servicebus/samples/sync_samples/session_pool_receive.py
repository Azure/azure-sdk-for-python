#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import uuid
import concurrent

from azure.servicebus import ServiceBusClient, ServiceBusMessage, AutoLockRenewer, NEXT_AVAILABLE_SESSION
from azure.servicebus.exceptions import OperationTimeoutError

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
# Note: This must be a session-enabled queue.
SESSION_QUEUE_NAME = os.environ["SERVICE_BUS_SESSION_QUEUE_NAME"]


def message_processing(sb_client, queue_name, messages):
    while True:
        try:
            with sb_client.get_queue_receiver(queue_name, max_wait_time=1, session_id=NEXT_AVAILABLE_SESSION) as receiver:
                renewer = AutoLockRenewer()
                renewer.register(receiver, receiver.session)
                receiver.session.set_state("OPEN")
                for message in receiver:
                    messages.append(message)
                    print("Message: {}".format(message))
                    print("Time to live: {}".format(message.time_to_live))
                    print("Sequence number: {}".format(message.sequence_number))
                    print("Enqueue Sequence number: {}".format(message.enqueued_sequence_number))
                    print("Partition Key: {}".format(message.partition_key))
                    print("Locked until: {}".format(message.locked_until_utc))
                    print("Lock Token: {}".format(message.lock_token))
                    print("Enqueued time: {}".format(message.enqueued_time_utc))
                    receiver.complete_message(message)
                    if str(message) == 'shutdown':
                        receiver.session.set_state("CLOSED")
                renewer.close()
        except OperationTimeoutError:
            print("If timeout occurs during connecting to a session,"
                  "It indicates that there might be no non-empty sessions remaining; exiting."
                  "This may present as a UserError in the azure portal metric.")
            return


def sample_session_send_receive_with_pool(connection_string, queue_name):

    concurrent_receivers = 5
    sessions = [str(uuid.uuid4()) for i in range(2 * concurrent_receivers)]
    with ServiceBusClient.from_connection_string(connection_string) as client:
    
        with client.get_queue_sender(queue_name) as sender:
            for session_id in sessions:
                for i in range(20):
                    message = ServiceBusMessage("Sample message no. {}".format(i), session_id=session_id)
                    sender.send_messages(message)

        all_messages = []
        futures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_receivers) as thread_pool:
            for _ in range(concurrent_receivers):
                futures.append(thread_pool.submit(message_processing, client, queue_name, all_messages))
            concurrent.futures.wait(futures)

        print("Received total {} messages across {} sessions.".format(len(all_messages), len(sessions)))


if __name__ == '__main__':
    sample_session_send_receive_with_pool(CONNECTION_STR, SESSION_QUEUE_NAME)
