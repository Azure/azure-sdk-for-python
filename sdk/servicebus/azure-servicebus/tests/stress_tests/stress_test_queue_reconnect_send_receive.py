#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import time
from datetime import datetime, timedelta
import concurrent

import conftest
from azure.servicebus import ServiceBusClient, Message


def message_send_process(sb_config, queue, endtime):
    client = ServiceBusClient(
        service_namespace=sb_config['hostname'],
        shared_access_key_name=sb_config['key_name'],
        shared_access_key_value=sb_config['access_key'],
        debug=False)

    total = 0
    queue_client = client.get_queue(queue)
    while endtime > datetime.now():
        queue_client.send(Message("Slow stress test message"))
        total += 1
        time.sleep(3)
    return total


def message_receive_process(sb_config, queue, endtime):
    client = ServiceBusClient(
        service_namespace=sb_config['hostname'],
        shared_access_key_name=sb_config['key_name'],
        shared_access_key_value=sb_config['access_key'],
        debug=False)

    queue_client = client.get_queue(queue)
    total = 0
    while endtime > datetime.now():
        with queue_client.get_receiver() as receiver:
            batch = receiver.fetch_next()
            for message in batch:
                total += 1
                message.complete()

    return total


def stress_test_queue_slow_send_receive(sb_config, queue):
    starttime = datetime.now()
    endtime = starttime + timedelta(seconds=30)
    sent_messages = 0
    received_messages = 0

    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as proc_pool:
        senders = [proc_pool.submit(message_send_process, sb_config, queue, endtime) for i in range(1)]
        receivers = [proc_pool.submit(message_receive_process, sb_config, queue, endtime) for i in range(1)]

        for done in concurrent.futures.as_completed(senders + receivers):
            if done in senders:
                sent_messages += done.result()
            else:
                received_messages += done.result()

    print("Sent {} messages and received {} messages.".format(sent_messages, received_messages))


if __name__ == '__main__':
    live_config = conftest.get_live_servicebus_config()
    queue_name = conftest.create_standard_queue(live_config)
    print("Created queue {}".format(queue_name))
    try:
        stress_test_queue_slow_send_receive(live_config, queue_name)
    finally:
        print("Cleaning up queue {}".format(queue_name))
        conftest.cleanup_queue(live_config, queue_name)
