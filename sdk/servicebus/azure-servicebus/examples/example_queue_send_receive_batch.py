# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import conftest

from azure.servicebus import ServiceBusClient
from azure.servicebus import Message
from azure.servicebus.common.constants import ReceiveSettleMode


def sample_queue_send_receive_batch(sb_config, queue):

    client = ServiceBusClient(
        service_namespace=sb_config['hostname'],
        shared_access_key_name=sb_config['key_name'],
        shared_access_key_value=sb_config['access_key'],
        debug=False)

    queue_client = client.get_queue(queue)
    with queue_client.get_sender() as sender:
        for i in range(100):
            message = Message("Sample message no. {}".format(i))
            sender.send(message)

    with queue_client.get_receiver(idle_timeout=1, mode=ReceiveSettleMode.PeekLock, prefetch=10) as receiver:

        total = 0
        # Receive list of messages as a batch
        batch = receiver.fetch_next(max_batch_size=10)
        for message in batch:
            print("Message: {}".format(message))
            print("Sequence number: {}".format(message.sequence_number))
            message.complete()
            total += 1

        # Receive messages as a continuous generator
        for message in receiver:
            print("Message: {}".format(message))
            print("Sequence number: {}".format(message.sequence_number))
            message.complete()
            total += 1

    print("Received total {} messages".format(total))


if __name__ == '__main__':
    live_config = conftest.get_live_servicebus_config()
    queue_name = conftest.create_standard_queue(live_config)
    print("Created queue {}".format(queue_name))
    try:
        sample_queue_send_receive_batch(live_config, queue_name)
    finally:
        print("Cleaning up queue {}".format(queue_name))
        conftest.cleanup_queue(live_config, queue_name)
