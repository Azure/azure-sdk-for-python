# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pytest

from azure.eventhub._pyamqp import authentication, ReceiveClient, SendClient
from azure.eventhub._pyamqp.constants import TransportType
from azure.eventhub._pyamqp.message import Message


def send_message(live_eventhub):
    uri = "sb://{}/{}".format(live_eventhub['hostname'], live_eventhub['event_hub'])
    sas_auth = authentication.SASTokenAuth(
        uri=uri,
        audience=uri,
        username=live_eventhub['key_name'],
        password=live_eventhub['access_key']
    )

    target = "amqps://{}/{}/Partitions/{}".format(
        live_eventhub['hostname'],
        live_eventhub['event_hub'],
        live_eventhub['partition'])
    
    message = Message(value="Single Message")

    with SendClient(live_eventhub['hostname'], target, auth=sas_auth, debug=True, transport_type=TransportType.Amqp) as send_client:
        send_client.send_message(message)


def test_event_hubs_client_web_socket(live_eventhub):
    uri = "sb://{}/{}".format(live_eventhub['hostname'], live_eventhub['event_hub'])
    sas_auth = authentication.SASTokenAuth(
        uri=uri,
        audience=uri,
        username=live_eventhub['key_name'],
        password=live_eventhub['access_key']
    )

    source = "amqps://{}/{}/ConsumerGroups/{}/Partitions/{}".format(
        live_eventhub['hostname'],
        live_eventhub['event_hub'],
        live_eventhub['consumer_group'],
        live_eventhub['partition'])

    send_message(live_eventhub=live_eventhub)

    with ReceiveClient(live_eventhub['hostname'] + '/$servicebus/websocket/', source, auth=sas_auth, debug=False, timeout=500, prefetch=1, transport_type=TransportType.AmqpOverWebsocket) as receive_client:
        messages = receive_client.receive_message_batch(max_batch_size=1)
        assert len(messages) > 0
