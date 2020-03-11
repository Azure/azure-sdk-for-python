#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import time
import uuid
from datetime import datetime, timedelta
import concurrent

from azure.servicebus import ServiceBusClient
from azure.servicebus.common.message import BatchMessage
from azure.servicebus.common.constants import ReceiveSettleMode


def create_standard_queue(sb_config):
    from azure.servicebus.control_client import ServiceBusService, Queue
    queue_name = str(uuid.uuid4())
    queue_value = Queue(
        lock_duration='PT30S',
        requires_duplicate_detection=False,
        dead_lettering_on_message_expiration=True,
        requires_session=False)
    client = ServiceBusService(
        service_namespace=sb_config['hostname'],
        shared_access_key_name=sb_config['key_name'],
        shared_access_key_value=sb_config['access_key'])
    if client.create_queue(queue_name, queue=queue_value, fail_on_exist=True):
        return queue_name
    raise ValueError("Queue creation failed.")


def cleanup_queue(servicebus_config, queue_name):
    from azure.servicebus.control_client import ServiceBusService
    client = ServiceBusService(
        service_namespace=servicebus_config['hostname'],
        shared_access_key_name=servicebus_config['key_name'],
        shared_access_key_value=servicebus_config['access_key'])
    client.delete_queue(queue_name)


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
            if total % 50 == 0:
                print("Sent {} messages".format(total))
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
        for message in receiver:
            message.complete()
            total += 1
            if total % 50 == 0:
                print("Received {} messages".format(total))
            if endtime <= datetime.now():
                break

    return total


def stress_test_queue_peeklock_send_receive(sb_config, queue):
    starttime = datetime.now()
    endtime = starttime + timedelta(hours=24)
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
    live_config = {}
    live_config['hostname'] = os.environ['SERVICE_BUS_HOSTNAME']
    live_config['key_name'] = os.environ['SERVICE_BUS_SAS_POLICY']
    live_config['access_key'] = os.environ['SERVICE_BUS_SAS_KEY']
    try:
        test_queue = create_standard_queue(live_config)
        print("Created queue {}".format(test_queue))
        stress_test_queue_peeklock_send_receive(live_config, test_queue)
    finally:
        print("Cleaning up queue {}".format(test_queue))
        cleanup_queue(live_config, test_queue)
