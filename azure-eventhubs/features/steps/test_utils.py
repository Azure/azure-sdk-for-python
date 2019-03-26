# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid
import time
import asyncio

def create_mgmt_client(credentials, subscription, location='westus'):
    from azure.mgmt.resource import ResourceManagementClient
    from azure.mgmt.eventhub import EventHubManagementClient

    resource_client = ResourceManagementClient(credentials, subscription)
    rg_name = 'pytest-{}'.format(uuid.uuid4())
    resource_group = resource_client.resource_groups.create_or_update(
                rg_name, {'location': location})

    eh_client = EventHubManagementClient(credentials, subscription)
    namespace = 'pytest-{}'.format(uuid.uuid4())
    creator = eh_client.namespaces.create_or_update(
        resource_group.name,
        namespace)
    create.wait()
    return resource_group, eh_client


def get_eventhub_config():
    config = {}
    config['hostname'] = os.environ['EVENT_HUB_HOSTNAME']
    config['event_hub'] = os.environ['EVENT_HUB_NAME']
    config['key_name'] = os.environ['EVENT_HUB_SAS_POLICY']
    config['access_key'] = os.environ['EVENT_HUB_SAS_KEY']
    config['consumer_group'] = "$Default"
    config['partition'] = "0"
    return config


def get_eventhub_100TU_config():
    config = {}
    config['hostname'] = os.environ['EVENT_HUB_100TU_HOSTNAME']
    config['event_hub'] = os.environ['EVENT_HUB_100TU_NAME']
    config['key_name'] = os.environ['EVENT_HUB_100TU_SAS_POLICY']
    config['access_key'] = os.environ['EVENT_HUB_100TU_SAS_KEY']
    config['consumer_group'] = "$Default"
    config['partition'] = "0"
    return config


def send_constant_messages(sender, timeout, payload=1024):
    deadline = time.time()
    total = 0
    while time.time() < deadline:
        data = EventData(body=b"D" * payload)
        sender.send(data)
        total += 1
    return total


def send_constant_async_messages(sender, timeout, batch_size=10000, payload=1024):
    deadline = time.time()
    total = 0
    while time.time() < deadline:
        data = EventData(body=b"D" * args.payload)
        sender.transfer(data)
        total += 1
        if total % 10000 == 0:
            sender.wait()
    return total


def send_constant_async_messages(sender, timeout, batch_size=1, payload=1024):
    deadline = time.time()
    while time.time() < deadline:
        if batch_size > 1:
            data = EventData(batch=data_generator())
        else:
            data = EventData(body=b"D" * payload)


async def receive_pump(receiver, timeout, validation=True):
    total = 0
    deadline = time.time() + timeout
    sequence = 0
    offset = None
    while time.time() < deadline:
        batch = await receiver.receive(timeout=5)
        total += len(batch)
        if validation:
            assert receiver.offset
            for event in batch:
                next_sequence = event.sequence_number
                assert next_sequence > sequence, "Received Event with lower sequence number than previous."
                assert (next_sequence - sequence) == 1, "Sequence number skipped by a value great than 1."
                sequence = next_sequence
                msg_data = b"".join([b for b in event.body]).decode('UTF-8')
                assert json.loads(msg_data), "Unable to deserialize Event data."
