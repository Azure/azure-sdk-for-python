# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pytest
import asyncio

from azure.eventhub._pyamqp.aio import _authentication_async, SendClientAsync as SendClient
from azure.eventhub._pyamqp.constants import TransportType
from azure.eventhub._pyamqp.message import Message

@pytest.mark.asyncio
async def test_event_hubs_client_send_async(live_eventhub):
    uri = "sb://{}/{}".format(live_eventhub['hostname'], live_eventhub['event_hub'])
    sas_auth = _authentication_async.SASTokenAuthAsync(
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

    async with SendClient(live_eventhub['hostname'], target, auth=sas_auth, debug=True, transport_type=TransportType.Amqp) as send_client:
        await send_client.send_message_async(message)