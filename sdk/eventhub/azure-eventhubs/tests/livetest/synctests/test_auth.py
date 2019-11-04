#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import pytest
import time
import threading

from azure.eventhub import EventData, EventHubProducerClient, EventHubConsumerClient


@pytest.mark.liveTest
def test_client_secret_credential(aad_credential, live_eventhub):
    try:
        from azure.identity import EnvironmentCredential
    except ImportError:
        pytest.skip("No azure identity library")
    credential = EnvironmentCredential()
    producer_client = EventHubProducerClient(host=live_eventhub['hostname'],
                                             event_hub_path=live_eventhub['event_hub'],
                                             credential=credential,
                                             user_agent='customized information')
    consumer_client = EventHubConsumerClient(host=live_eventhub['hostname'],
                                             event_hub_path=live_eventhub['event_hub'],
                                             credential=credential,
                                             user_agent='customized information')
    with producer_client:
        producer_client.send(EventData(body='A single message'))

    def on_events(partition_context, events):
        assert partition_context.partition_id == '0'
        assert len(events) == 1
        assert list(events[0].body)[0] == 'A single message'.encode('utf-8')
    with consumer_client:
        worker = threading.Thread(target=consumer_client.receive, args=(on_events,),
                                  kwargs={"consumer_group": '$default',
                                          "partition_id": '0'})
        worker.start()
        time.sleep(2)
