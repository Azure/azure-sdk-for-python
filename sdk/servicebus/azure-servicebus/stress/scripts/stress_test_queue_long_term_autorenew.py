#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import time
from datetime import datetime, timedelta
import concurrent

import conftest
from azure.servicebus import AutoLockRenewer, ServiceBusClient, ServiceBusMessage

def send_message(client, queue_name):
    queue_client = client.get_queue(queue_name)
    msg = ServiceBusMessage(b'Test')
    queue_client.send(msg)
    print('ServiceBusMessage sent')


def process_message(message):
    print('Beginning Processing')
    time.sleep(600)
    print('Done Processing')


def receive_process_and_complete_message(client, queue_name):
    queue_client = client.get_queue(queue_name)
    lock_renewal = AutoLockRenewer(max_workers=4)
    lock_renewal.renew_period = 120
    with queue_client.get_receiver() as queue_receiver:
        for message in queue_receiver:
            print("Received message: ", message)
            lock_renewal.register(queue_receiver, message, max_lock_renewal_duration=10800)
            process_message(message)
            print("Completing message")
            queue_receiver.complete_message(message)
            break


def stress_test_queue_long_term_autorenew(sb_conn_str, queue_name):
    client = ServiceBusClient.from_connection_string(
        sb_conn_str,
        debug=False)

    send_message(client, queue_name)
    receive_process_and_complete_message(client, queue_name)


if __name__ == '__main__':
    live_config = conftest.get_live_servicebus_config()
    queue_name = conftest.create_standard_queue(live_config)
    print("Created queue {}".format(queue_name))
    try:
        stress_test_queue_long_term_autorenew(live_config, queue_name)
    finally:
        print("Cleaning up queue {}".format(queue_name))
        conftest.cleanup_queue(live_config, queue_name)
