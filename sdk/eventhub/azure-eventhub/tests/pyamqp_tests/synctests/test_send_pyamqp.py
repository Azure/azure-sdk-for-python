# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pytest

from azure.eventhub._pyamqp import authentication, SendClient
from azure.eventhub._pyamqp.constants import TransportType
from azure.eventhub._pyamqp.message import Header, Message

def test_event_hubs_client_send(live_eventhub):
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
    
    # message = EventData("Single Message")._to_outgoing_message()
    header = Header()
    message = Message(value="Single Message")

    with SendClient(live_eventhub['hostname'], target, auth=sas_auth, debug=True, transport_type=TransportType.Amqp) as send_client:
        send_client.send_message(message)