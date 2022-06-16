# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pytest

from azure.eventhub._pyamqp import authentication, ReceiveClient
from azure.eventhub._pyamqp.constants import TransportType

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

    with ReceiveClient(live_eventhub['hostname'] + '/$servicebus/websocket/', source, auth=sas_auth, debug=False, timeout=10, prefetch=1, transport_type=TransportType.AmqpOverWebsocket) as receive_client:
        begin = receive_client._received_messages.qsize()
        receive_client.receive_message_batch(max_batch_size=1)
        return receive_client._received_messages.qsize() - begin
