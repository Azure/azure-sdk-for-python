#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import pytest
import time
import threading

from azure.identity import EnvironmentCredential
from azure.eventhub import EventData, EventHubProducerClient, EventHubConsumerClient, EventHubSharedKeyCredential, EventHubSASTokenCredential

from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from tests.eventhub_preparer import (
    CachedEventHubNamespacePreparer, 
    CachedEventHubPreparer
)

@pytest.mark.liveTest
def test_client_secret_credential(live_eventhub):
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


from azure.eventhub._client_base import _generate_sas_token as generate_sas_token
import datetime

class EventHubClientTests(AzureMgmtTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='eventhubtest')
    @CachedEventHubNamespacePreparer(name_prefix='eventhubtest')
    @CachedEventHubPreparer(name_prefix='eventhubtest')
    def test_client_sas_credential(self,
                                   eventhub,
                                   eventhub_namespace,
                                   eventhub_namespace_key_name,
                                   eventhub_namespace_primary_key,
                                   eventhub_namespace_connection_string,
                                   **kwargs):
        # This should "just work" to validate known-good.
        hostname = "{}.servicebus.windows.net".format(eventhub_namespace.name)
        producer_client = EventHubProducerClient.from_connection_string(eventhub_namespace_connection_string, eventhub_name = eventhub.name)

        with producer_client:
            batch = producer_client.create_batch(partition_id='0')
            batch.add(EventData(body='A single message'))
            producer_client.send_batch(batch)

        # This should also work, but now using SAS tokens.
        print("This works->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        credential = EventHubSharedKeyCredential(eventhub_namespace_key_name, eventhub_namespace_primary_key)
        hostname = "{}.servicebus.windows.net".format(eventhub_namespace.name)
        auth_uri = "sb://{}/{}".format(hostname, eventhub.name)
        token = credential.get_token(auth_uri).token
        #token = generate_sas_token(auth_uri, eventhub_namespace_key_name, eventhub_namespace_primary_key, datetime.timedelta(seconds=300)).token
        producer_client = EventHubProducerClient(fully_qualified_namespace=hostname,
                                                 eventhub_name=eventhub.name,
                                                 credential=EventHubSASTokenCredential(token, time.time() + 3000))

        with producer_client:
            batch = producer_client.create_batch(partition_id='0')
            batch.add(EventData(body='A single message'))
            producer_client.send_batch(batch)
        
        print("RAWTOKEN===================================================")    
        print(token)
        # Finally let's do it with SAS token + conn str
        token_conn_str = "Endpoint=sb://{}/;SharedAccessToken={};".format(hostname, token)
        conn_str_producer_client = EventHubProducerClient.from_connection_string(token_conn_str,
                                                                                 eventhub_name=eventhub.name)
        
        with conn_str_producer_client:
            batch = conn_str_producer_client.create_batch(partition_id='0')
            batch.add(EventData(body='A single message'))
            conn_str_producer_client.send_batch(batch)
