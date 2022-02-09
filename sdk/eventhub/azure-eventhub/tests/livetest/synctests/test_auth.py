#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import pytest
import time
import threading

from azure.identity import EnvironmentCredential
from azure.eventhub import EventData, EventHubProducerClient, EventHubConsumerClient, EventHubSharedKeyCredential
from azure.eventhub._client_base import EventHubSASTokenCredential
from azure.core.credentials import AzureSasCredential, AzureNamedKeyCredential


@pytest.mark.liveTest
def test_client_secret_credential(live_eventhub, uamqp_transport):
    credential = EnvironmentCredential()
    producer_client = EventHubProducerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=credential,
                                             user_agent='customized information',
                                             uamqp_transport=uamqp_transport)
    consumer_client = EventHubConsumerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             consumer_group='$default',
                                             credential=credential,
                                             user_agent='customized information',
                                             uamqp_transport=uamqp_transport
                                             )
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


@pytest.mark.liveTest
def test_client_sas_credential(live_eventhub, uamqp_transport):
    # This should "just work" to validate known-good.
    hostname = live_eventhub['hostname']
    producer_client = EventHubProducerClient.from_connection_string(
        live_eventhub['connection_str'], eventhub_name = live_eventhub['event_hub'], uamqp_transport=uamqp_transport
    )

    with producer_client:
        batch = producer_client.create_batch(partition_id='0')
        batch.add(EventData(body='A single message'))
        producer_client.send_batch(batch)

    # This should also work, but now using SAS tokens.
    credential = EventHubSharedKeyCredential(live_eventhub['key_name'], live_eventhub['access_key'])
    auth_uri = "sb://{}/{}".format(hostname, live_eventhub['event_hub'])
    token = credential.get_token(auth_uri).token
    producer_client = EventHubProducerClient(fully_qualified_namespace=hostname,
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=EventHubSASTokenCredential(token, time.time() + 3000),
                                             uamqp_transport=uamqp_transport)

    with producer_client:
        batch = producer_client.create_batch(partition_id='0')
        batch.add(EventData(body='A single message'))
        producer_client.send_batch(batch)

    # Finally let's do it with SAS token + conn str
    token_conn_str = "Endpoint=sb://{}/;SharedAccessSignature={};".format(hostname, token.decode())
    conn_str_producer_client = EventHubProducerClient.from_connection_string(token_conn_str,
                                                                             eventhub_name=live_eventhub['event_hub'],
                                                                             uamqp_transport=uamqp_transport)

    with conn_str_producer_client:
        batch = conn_str_producer_client.create_batch(partition_id='0')
        batch.add(EventData(body='A single message'))
        conn_str_producer_client.send_batch(batch)


@pytest.mark.liveTest
def test_client_azure_sas_credential(live_eventhub, uamqp_transport):
    # This should "just work" to validate known-good.
    hostname = live_eventhub['hostname']
    producer_client = EventHubProducerClient.from_connection_string(
        live_eventhub['connection_str'], eventhub_name = live_eventhub['event_hub'], uamqp_transport=uamqp_transport
    )

    with producer_client:
        batch = producer_client.create_batch(partition_id='0')
        batch.add(EventData(body='A single message'))
        producer_client.send_batch(batch)

    # This should also work, but now using SAS tokens.
    credential = EventHubSharedKeyCredential(live_eventhub['key_name'], live_eventhub['access_key'])
    auth_uri = "sb://{}/{}".format(hostname, live_eventhub['event_hub'])
    token = credential.get_token(auth_uri).token.decode()
    producer_client = EventHubProducerClient(fully_qualified_namespace=hostname,
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=AzureSasCredential(token))

    with producer_client:
        batch = producer_client.create_batch(partition_id='0')
        batch.add(EventData(body='A single message'))
        producer_client.send_batch(batch)


@pytest.mark.liveTest
def test_client_azure_named_key_credential(live_eventhub, uamqp_transport):
    credential = AzureNamedKeyCredential(live_eventhub['key_name'], live_eventhub['access_key'])
    consumer_client = EventHubConsumerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             consumer_group='$default',
                                             credential=credential,
                                             user_agent='customized information',
                                             uamqp_transport=uamqp_transport)

    assert consumer_client.get_eventhub_properties() is not None
    
    credential.update("foo", "bar")

    with pytest.raises(Exception):
        consumer_client.get_eventhub_properties()
    
    credential.update(live_eventhub['key_name'], live_eventhub['access_key'])
    assert consumer_client.get_eventhub_properties() is not None
