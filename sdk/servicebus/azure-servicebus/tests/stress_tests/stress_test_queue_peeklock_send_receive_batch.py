#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import time
from datetime import datetime, timedelta
import concurrent

import conftest
from azure.servicebus import ServiceBusClient
from azure.servicebus.common.message import BatchMessage
from azure.servicebus.common.constants import ReceiveSettleMode


def message_send_process(sb_config, queue, endtime):

    def message_batch():
        for i in range(5):
            yield "Stress Test message no. {}".format(i)

    client = ServiceBusClient(
        service_namespace=sb_config['hostname'],
        shared_access_key_name=sb_config['key_name'],
        shared_access_key_value=sb_config['access_key'],
        debug=False)

    total = 0
    queue_client = client.get_queue(queue)
    with queue_client.get_sender() as sender:
        while endtime > datetime.now():
            message = BatchMessage(message_batch())
            sender.send(message)
            total += 5
            time.sleep(0.01)
    return total


def message_receive_process(sb_config, queue, endtime):
    client = ServiceBusClient(
        service_namespace=sb_config['hostname'],
        shared_access_key_name=sb_config['key_name'],
        shared_access_key_value=sb_config['access_key'],
        debug=False)

    queue_client = client.get_queue(queue)
    with queue_client.get_receiver(idle_timeout=10, mode=ReceiveSettleMode.PeekLock, prefetch=10) as receiver:
        total = 0
        batch = receiver.fetch_next()
        while batch:
            for message in batch:
                message.complete()
                total += 1
                if endtime <= datetime.now():
                    break
            batch = receiver.fetch_next()

    return total


def stress_test_queue_peeklock_send_receive_batch(sb_config, queue):
    starttime = datetime.now()
    endtime = starttime + timedelta(seconds=30)
    sent_messages = 0
    received_messages = 0

    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as proc_pool:
        senders = [proc_pool.submit(message_send_process, sb_config, queue, endtime) for i in range(2)]
        receivers = [proc_pool.submit(message_receive_process, sb_config, queue, endtime) for i in range(2)]

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
        stress_test_queue_peeklock_send_receive_batch(live_config, queue_name)
    finally:
        print("Cleaning up queue {}".format(queue_name))
        conftest.cleanup_queue(live_config, queue_name)
