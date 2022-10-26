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
from azure.eventhub.exceptions import ConnectError, AuthenticationError, EventHubError
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
                                             credential=AzureSasCredential(token),
                                             uamqp_transport=uamqp_transport)

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

@pytest.mark.liveTest
@pytest.mark.asyncio
def test_client_invalid_credential(live_eventhub, uamqp_transport):

    def on_event(partition_context, event):
        pass

    def on_error(partition_context, error):
        on_error.err = error

    env_credential = EnvironmentCredential()
    producer_client = EventHubProducerClient(fully_qualified_namespace="fakeeventhub.servicebus.windows.net",
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=env_credential,
                                             user_agent='customized information',
                                             retry_total=1,
                                             retry_mode='exponential',
                                             retry_backoff=0.02,
                                             uamqp_transport=uamqp_transport)
    consumer_client = EventHubConsumerClient(fully_qualified_namespace="fakeeventhub.servicebus.windows.net",
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=env_credential,
                                             user_agent='customized information',
                                             consumer_group='$Default',
                                             retry_total=1,
                                             retry_mode='exponential',
                                             retry_backoff=0.02,
                                             uamqp_transport=uamqp_transport)
    with producer_client:
        with pytest.raises(ConnectError):
            producer_client.create_batch(partition_id='0')

    on_error.err = None
    with consumer_client:
        thread = threading.Thread(target=consumer_client.receive, args=(on_event,),
                                  kwargs={"starting_position": "-1", "on_error": on_error})
        thread.daemon = True
        thread.start()
        time.sleep(15)
    thread.join()
    assert isinstance(on_error.err, ConnectError)

    producer_client = EventHubProducerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name='fakehub',
                                             credential=env_credential,
                                             uamqp_transport=uamqp_transport)

    consumer_client = EventHubConsumerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name='fakehub',
                                             credential=env_credential,
                                             consumer_group='$Default',
                                             retry_total=0,
                                             uamqp_transport=uamqp_transport)

    with producer_client:
        with pytest.raises(ConnectError):
            producer_client.create_batch(partition_id='0')

    on_error.err = None
    with consumer_client:
        thread = threading.Thread(target=consumer_client.receive, args=(on_event,),
                                  kwargs={"starting_position": "-1", "on_error": on_error})
        thread.daemon = True
        thread.start()
        time.sleep(15)
    thread.join()
    assert isinstance(on_error.err, AuthenticationError)
    
    credential = EventHubSharedKeyCredential(live_eventhub['key_name'], live_eventhub['access_key'])
    auth_uri = "sb://{}/{}".format(live_eventhub['hostname'], live_eventhub['event_hub'])
    token = credential.get_token(auth_uri).token
    producer_client = EventHubProducerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=EventHubSASTokenCredential(token, time.time() + 5),
                                             uamqp_transport=uamqp_transport)
    time.sleep(6)
    # expired credential
    with producer_client:
        with pytest.raises(AuthenticationError):
            producer_client.create_batch(partition_id='0')

    consumer_client = EventHubConsumerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=EventHubSASTokenCredential(token, time.time() + 7),
                                             consumer_group='$Default',
                                             retry_total=0,
                                             uamqp_transport=uamqp_transport)
    on_error.err = None
    with consumer_client:
        thread = threading.Thread(target=consumer_client.receive, args=(on_event,),
                                  kwargs={"starting_position": "-1", "on_error": on_error})
        thread.daemon = True
        thread.start()
        time.sleep(15)
    thread.join()

    assert isinstance(on_error.err, AuthenticationError)

    credential = EventHubSharedKeyCredential('fakekey', live_eventhub['access_key'])
    producer_client = EventHubProducerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=credential,
                                             uamqp_transport=uamqp_transport)

    with producer_client:
        with pytest.raises(AuthenticationError):
            producer_client.create_batch(partition_id='0')

    producer_client = EventHubProducerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=env_credential,
                                             connection_verify="cacert.pem",
                                             uamqp_transport=uamqp_transport)
    
    # uamqp: EventHubError
    # pyamqp: ConnectError
    with producer_client:
        with pytest.raises(EventHubError):
            producer_client.create_batch(partition_id='0')

    consumer_client = EventHubConsumerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             consumer_group='$Default',
                                             credential=env_credential,
                                             retry_total=0,
                                             connection_verify="cacert.pem",
                                             uamqp_transport=uamqp_transport)
    with consumer_client:
        thread = threading.Thread(target=consumer_client.receive, args=(on_event,),
                                  kwargs={"starting_position": "-1", "on_error": on_error})
        thread.daemon = True
        thread.start()
        time.sleep(5)
    thread.join()

    # uamqp: FileNotFoundError  TODO: this seems like a bug from uamqp, should be ConnectError?
    # pyamqp: ConnectError
    assert isinstance(on_error.err, FileNotFoundError)

    producer_client = EventHubProducerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             credential=env_credential,
                                             custom_endpoint_address="fakeaddr",
                                             uamqp_transport=uamqp_transport)

    with producer_client:
        with pytest.raises(AuthenticationError):
            producer_client.create_batch(partition_id='0')

    consumer_client = EventHubConsumerClient(fully_qualified_namespace=live_eventhub['hostname'],
                                             eventhub_name=live_eventhub['event_hub'],
                                             consumer_group='$Default',
                                             credential=env_credential,
                                             retry_total=0,
                                             custom_endpoint_address="fakeaddr",
                                             uamqp_transport=uamqp_transport)
    with consumer_client:
        thread = threading.Thread(target=consumer_client.receive, args=(on_event,),
                                  kwargs={"starting_position": "-1", "on_error": on_error})
        thread.daemon = True
        thread.start()
        time.sleep(15)
    thread.join()

    assert isinstance(on_error.err, AuthenticationError)
