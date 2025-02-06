# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import time
import threading
import ssl
import certifi

from azure.eventhub import (
    EventData,
    EventHubProducerClient,
    EventHubConsumerClient,
    EventHubSharedKeyCredential,
)
from azure.eventhub.exceptions import ConnectError
from azure.eventhub._client_base import EventHubSASTokenCredential
from azure.core.credentials import AzureSasCredential, AzureNamedKeyCredential


@pytest.mark.liveTest
def test_client_token_credential(live_eventhub, get_credential, uamqp_transport):
    credential = get_credential()
    producer_client = EventHubProducerClient(
        fully_qualified_namespace=live_eventhub["hostname"],
        eventhub_name=live_eventhub["event_hub"],
        credential=credential,
        user_agent="customized information",
        uamqp_transport=uamqp_transport,
    )
    consumer_client = EventHubConsumerClient(
        fully_qualified_namespace=live_eventhub["hostname"],
        eventhub_name=live_eventhub["event_hub"],
        consumer_group="$default",
        credential=credential,
        user_agent="customized information",
        uamqp_transport=uamqp_transport,
    )
    with producer_client:
        batch = producer_client.create_batch(partition_id="0")
        batch.add(EventData(body="A single message"))
        producer_client.send_batch(batch)

    def on_event(partition_context, event):
        on_event.called = True
        on_event.partition_id = partition_context.partition_id
        on_event.event = event

    on_event.called = False
    with consumer_client:
        worker = threading.Thread(
            target=consumer_client.receive,
            args=(on_event,),
            kwargs={"partition_id": "0", "starting_position": "-1"},
        )
        worker.start()
        time.sleep(15)

    worker.join()
    assert on_event.called is True
    assert on_event.partition_id == "0"
    assert list(on_event.event.body)[0] == "A single message".encode("utf-8")


@pytest.mark.liveTest
def test_client_sas_credential(live_eventhub, uamqp_transport):
    # This should "just work" to validate known-good.
    hostname = live_eventhub["hostname"]
    producer_client = EventHubProducerClient.from_connection_string(
        live_eventhub["connection_str"],
        eventhub_name=live_eventhub["event_hub"],
        uamqp_transport=uamqp_transport,
    )

    with producer_client:
        batch = producer_client.create_batch(partition_id="0")
        batch.add(EventData(body="A single message"))
        producer_client.send_batch(batch)

    # This should also work, but now using SAS tokens.
    credential = EventHubSharedKeyCredential(live_eventhub["key_name"], live_eventhub["access_key"])
    auth_uri = "sb://{}/{}".format(hostname, live_eventhub["event_hub"])
    token = credential.get_token(auth_uri).token
    producer_client = EventHubProducerClient(
        fully_qualified_namespace=hostname,
        eventhub_name=live_eventhub["event_hub"],
        credential=EventHubSASTokenCredential(token, time.time() + 3000),
        uamqp_transport=uamqp_transport,
    )

    with producer_client:
        batch = producer_client.create_batch(partition_id="0")
        batch.add(EventData(body="A single message"))
        producer_client.send_batch(batch)

    # Finally let's do it with SAS token + conn str
    token_conn_str = "Endpoint=sb://{}/;SharedAccessSignature={};".format(hostname, token)
    conn_str_producer_client = EventHubProducerClient.from_connection_string(
        token_conn_str,
        eventhub_name=live_eventhub["event_hub"],
        uamqp_transport=uamqp_transport,
    )

    with conn_str_producer_client:
        batch = conn_str_producer_client.create_batch(partition_id="0")
        batch.add(EventData(body="A single message"))
        conn_str_producer_client.send_batch(batch)


@pytest.mark.liveTest
def test_client_azure_sas_credential(live_eventhub, uamqp_transport):
    # This should "just work" to validate known-good.
    hostname = live_eventhub["hostname"]
    producer_client = EventHubProducerClient.from_connection_string(
        live_eventhub["connection_str"],
        eventhub_name=live_eventhub["event_hub"],
        uamqp_transport=uamqp_transport,
    )

    with producer_client:
        batch = producer_client.create_batch(partition_id="0")
        batch.add(EventData(body="A single message"))
        producer_client.send_batch(batch)

    # This should also work, but now using SAS tokens.
    credential = EventHubSharedKeyCredential(live_eventhub["key_name"], live_eventhub["access_key"])
    auth_uri = "sb://{}/{}".format(hostname, live_eventhub["event_hub"])
    token = credential.get_token(auth_uri).token
    producer_client = EventHubProducerClient(
        fully_qualified_namespace=hostname,
        eventhub_name=live_eventhub["event_hub"],
        credential=AzureSasCredential(token),
        auth_timeout=30,
        uamqp_transport=uamqp_transport,
    )

    with producer_client:
        batch = producer_client.create_batch(partition_id="0")
        batch.add(EventData(body="A single message"))
        producer_client.send_batch(batch)

    assert producer_client.get_eventhub_properties() is not None


@pytest.mark.liveTest
def test_client_azure_named_key_credential(live_eventhub, uamqp_transport):
    credential = AzureNamedKeyCredential(live_eventhub["key_name"], live_eventhub["access_key"])
    consumer_client = EventHubConsumerClient(
        fully_qualified_namespace=live_eventhub["hostname"],
        eventhub_name=live_eventhub["event_hub"],
        consumer_group="$default",
        credential=credential,
        user_agent="customized information",
        auth_timeout=30,
        uamqp_transport=uamqp_transport,
    )

    assert consumer_client.get_eventhub_properties() is not None

    credential.update("foo", "bar")

    with pytest.raises(Exception):
        consumer_client.get_eventhub_properties()

    credential.update(live_eventhub["key_name"], live_eventhub["access_key"])
    assert consumer_client.get_eventhub_properties() is not None


# New feature only for Pure Python AMQP, not uamqp.
@pytest.mark.liveTest
def test_client_with_ssl_context(auth_credentials, socket_transport):
    fully_qualified_namespace, eventhub_name, credential = auth_credentials

    # Check that SSLContext with invalid/nonexistent cert file raises an error
    context = ssl.SSLContext(cafile="fakecert.pem")
    context.verify_mode = ssl.CERT_REQUIRED

    producer = EventHubProducerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=credential(),
        transport_type=socket_transport,
        ssl_context=context,
        retry_total=0,
    )
    with producer:
        with pytest.raises(ConnectError):
            batch = producer.create_batch()

    def on_event(partition_context, event):
        on_event.called = True
        on_event.partition_id = partition_context.partition_id
        on_event.event = event

    def on_error(partition_context, error):
        on_error.error = error
        consumer.close()

    consumer = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=credential(),
        consumer_group="$default",
        transport_type=socket_transport,
        ssl_context=context,
        retry_total=0,
    )
    on_error.error = None
    with consumer:
        thread = threading.Thread(
            target=consumer.receive,
            args=(on_event,),
            kwargs={"on_error": on_error, "starting_position": "-1"},
        )
        thread.daemon = True
        thread.start()
        time.sleep(15)
        assert isinstance(on_error.error, ConnectError)
    thread.join()

    # Check that SSLContext with valid cert file doesn't raise an error
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(certifi.where())
    purpose = ssl.Purpose.SERVER_AUTH
    context.load_default_certs(purpose=purpose)

    producer = EventHubProducerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=credential(),
        transport_type=socket_transport,
        ssl_context=context,
    )
    with producer:
        batch = producer.create_batch()
        batch.add(EventData(body="A single message"))
        batch.add(EventData(body="A second message"))
        producer.send_batch(batch)

    def on_event(partition_context, event):
        on_event.total += 1

    def on_error(partition_context, error):
        on_error.error = error
        consumer.close()

    consumer = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=credential(),
        consumer_group="$default",
        transport_type=socket_transport,
        ssl_context=context,
    )
    on_event.total = 0
    on_error.error = None

    with consumer:
        thread2 = threading.Thread(
            target=consumer.receive,
            args=(on_event,),
            kwargs={"on_error": on_error, "starting_position": "-1"},
        )
        thread2.daemon = True
        thread2.start()
        time.sleep(15)
        assert on_event.total == 2
        assert on_error.error is None

    thread2.join()
