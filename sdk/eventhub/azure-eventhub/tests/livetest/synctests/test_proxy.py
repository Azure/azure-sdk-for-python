# -- coding: utf-8 --
#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest
import time
import sys

import proxy
from azure.eventhub import EventData, TransportType
from azure.eventhub.exceptions import EventHubError
from azure.eventhub import EventHubProducerClient

@pytest.mark.liveTest
def test_send_with_proxy(connstr_receivers):
    if sys.version_info < (3, 6):
        pytest.skip("proxy test only works on python 3.6+")
    connection_str, receivers = connstr_receivers
    with proxy.start(
            [
                '--hostname', "127.0.0.1",
                '--port', '9946'
            ]
    ):
        client = EventHubProducerClient.from_connection_string(
            connection_str,
            transport_type=TransportType.AmqpOverWebsocket,
            http_proxy={
                "proxy_hostname": "127.0.0.1",
                "proxy_port": 9946
            }
        )
        with client:
            batch = client.create_batch(partition_id="0")
            batch.add(EventData("Event Data"))
            client.send_batch(batch)

        time.sleep(1)
        received = []
        received.extend(receivers[0].receive_message_batch(max_batch_size=5, timeout=10000))
        assert len(received) == 1


@pytest.mark.liveTest
def test_send_with_wrong_proxy(connstr_receivers):
    if sys.version_info < (3, 6):
        pytest.skip("proxy test only works on python 3.6+")
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(
        connection_str,
        transport_type=TransportType.AmqpOverWebsocket,
        http_proxy={
            "proxy_hostname": "127.0.0.1",
            "proxy_port": 8898
        }
    )
    with client:
        with pytest.raises(EventHubError):
            batch = client.create_batch(partition_id="0")
            batch.add(EventData("Event Data"))
            client.send_batch(batch)
