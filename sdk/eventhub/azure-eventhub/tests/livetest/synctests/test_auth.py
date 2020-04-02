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
    except ImportError as e:
        pytest.skip("No azure identity library")
    credential = EnvironmentCredential()
    producer_client = EventHubProducerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=credential,
                                             user_agent='customized information')
    consumer_client = EventHubConsumerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             consumer_group='$default',
                                             credential=credential,
                                             user_agent='customized information')
    with producer_client:
        batch = producer_client.create_batch(partition_id='0')
        batch.add(EventData(body='A single message'))
        producer_client.send_batch(batch)

    def on_event(partition_context, event):
        on_event.called = True
        on_event.partition_id = partition_context.partition_id
        on_event.event = event
    on_event.called = False
    with consumer_client:
        worker = threading.Thread(target=consumer_client.receive, args=(on_event,),
                                  kwargs={
                                      "partition_id": '0',
                                      "starting_position": '-1'
                                  })
        worker.start()
        time.sleep(13)

    worker.join()
    assert on_event.called is True
    assert on_event.partition_id == "0"
    assert list(on_event.event.body)[0] == 'A single message'.encode('utf-8')
