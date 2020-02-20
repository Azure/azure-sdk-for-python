# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import uuid

import conftest

from azure.servicebus import ServiceBusClient
from azure.servicebus import Message


def sample_session_send_receive_batch(sb_config, queue):
    session_id = str(uuid.uuid4())
    client = ServiceBusClient(
        service_namespace=sb_config['hostname'],
        shared_access_key_name=sb_config['key_name'],
        shared_access_key_value=sb_config['access_key'],
        debug=False)

    queue_client = client.get_queue(queue)
    with queue_client.get_sender(session=session_id) as sender:
        for i in range(100):
            message = Message("Sample message no. {}".format(i))
            sender.send(message)
        sender.send(Message("shutdown"))


    with queue_client.get_receiver(session=session_id) as session:
        session.set_session_state("START")
        for message in session:
            print(message)
            message.complete()
            if str(message) == "shutdown":
                session.set_session_state("END")
                break


if __name__ == '__main__':
    live_config = conftest.get_live_servicebus_config()
    queue_name = conftest.create_session_queue(live_config)
    print("Created queue {}".format(queue_name))
    try:
        sample_session_send_receive_batch(live_config, queue_name)
    finally:
        print("Cleaning up queue {}".format(queue_name))
        conftest.cleanup_queue(live_config, queue_name)
