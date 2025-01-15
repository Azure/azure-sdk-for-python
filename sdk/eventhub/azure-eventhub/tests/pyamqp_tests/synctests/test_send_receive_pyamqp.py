# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pytest

from azure.eventhub.amqp import AmqpAnnotatedMessage
from azure.eventhub._pyamqp import authentication, ReceiveClient, SendClient
from azure.eventhub._pyamqp.constants import TransportType
from azure.eventhub._pyamqp.message import Message


def send_message(live_eventhub):
    uri = "sb://{}/{}".format(live_eventhub["hostname"], live_eventhub["event_hub"])
    sas_auth = authentication.SASTokenAuth(
        uri=uri, audience=uri, username=live_eventhub["key_name"], password=live_eventhub["access_key"]
    )

    target = "amqps://{}/{}/Partitions/{}".format(
        live_eventhub["hostname"], live_eventhub["event_hub"], live_eventhub["partition"]
    )

    message = Message(value="Single Message")
    amqp_annotated_message = AmqpAnnotatedMessage(sequence_body=[{"sequence_number": 1}, {"sequence_number": 2}, {"sequence_number": 3}])

    with SendClient(
        live_eventhub["hostname"], target, auth=sas_auth, debug=True, transport_type=TransportType.Amqp
    ) as send_client:
        send_client.send_message(message)
        send_client.send_message(amqp_annotated_message)


def test_event_hubs_client_amqp(live_eventhub):
    uri = "sb://{}/{}".format(live_eventhub["hostname"], live_eventhub["event_hub"])
    sas_auth = authentication.SASTokenAuth(
        uri=uri, audience=uri, username=live_eventhub["key_name"], password=live_eventhub["access_key"]
    )

    source = "amqps://{}/{}/ConsumerGroups/{}/Partitions/{}".format(
        live_eventhub["hostname"],
        live_eventhub["event_hub"],
        live_eventhub["consumer_group"],
        live_eventhub["partition"],
    )

    send_message(live_eventhub=live_eventhub)

    with ReceiveClient(
        live_eventhub["hostname"],
        source,
        auth=sas_auth,
        debug=False,
        timeout=500,
        prefetch=1,
        transport_type=TransportType.Amqp,
    ) as receive_client:
        messages = receive_client.receive_message_batch(max_batch_size=2)
        assert len(messages) > 1
        assert messages[1].sequence_body == [{"sequence_number": 1}, {"sequence_number": 2}, {"sequence_number": 3}]
