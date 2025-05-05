# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import asyncio
import time
import ssl
import certifi

from azure.core.credentials import AzureSasCredential, AzureNamedKeyCredential
from azure.identity.aio import EnvironmentCredential
from azure.eventhub import EventData
from azure.eventhub.exceptions import ConnectError
from azure.eventhub.aio import (
    EventHubConsumerClient,
    EventHubProducerClient,
    EventHubSharedKeyCredential,
)
from azure.eventhub.aio._client_base_async import EventHubSASTokenCredential


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_client_token_credential_async(live_eventhub, get_credential_async, uamqp_transport, client_args):
    credential = get_credential_async()
    producer_client = EventHubProducerClient(
        fully_qualified_namespace=live_eventhub["hostname"],
        eventhub_name=live_eventhub["event_hub"],
        credential=credential,
        user_agent="customized information",
        auth_timeout=30,
        uamqp_transport=uamqp_transport,
        **client_args
    )
    consumer_client = EventHubConsumerClient(
        fully_qualified_namespace=live_eventhub["hostname"],
        eventhub_name=live_eventhub["event_hub"],
        consumer_group="$default",
        credential=credential,
        user_agent="customized information",
        auth_timeout=30,
        uamqp_transport=uamqp_transport,
        **client_args
    )

    async with producer_client:
        batch = await producer_client.create_batch(partition_id="0")
        batch.add(EventData(body="A single message"))
        await producer_client.send_batch(batch)

    async def on_event(partition_context, event):
        on_event.called = True
        on_event.partition_id = partition_context.partition_id
        on_event.event = event

    on_event.called = False
    async with consumer_client:
        task = asyncio.ensure_future(consumer_client.receive(on_event, partition_id="0", starting_position="-1"))
        await asyncio.sleep(15)
    await task
    assert on_event.called is True
    assert on_event.partition_id == "0"
    assert list(on_event.event.body)[0] == "A single message".encode("utf-8")


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_client_sas_credential_async(live_eventhub, uamqp_transport, client_args):
    # This should "just work" to validate known-good.
    hostname = live_eventhub["hostname"]
    producer_client = EventHubProducerClient.from_connection_string(
        live_eventhub["connection_str"],
        eventhub_name=live_eventhub["event_hub"],
        uamqp_transport=uamqp_transport,
        **client_args
    )

    async with producer_client:
        batch = await producer_client.create_batch(partition_id="0")
        batch.add(EventData(body="A single message"))
        await producer_client.send_batch(batch)

    # This should also work, but now using SAS tokens.
    credential = EventHubSharedKeyCredential(live_eventhub["key_name"], live_eventhub["access_key"])
    auth_uri = "sb://{}/{}".format(hostname, live_eventhub["event_hub"])
    token = (await credential.get_token(auth_uri)).token
    producer_client = EventHubProducerClient(
        fully_qualified_namespace=hostname,
        eventhub_name=live_eventhub["event_hub"],
        credential=EventHubSASTokenCredential(token, time.time() + 3000),
        uamqp_transport=uamqp_transport,
        **client_args
    )

    async with producer_client:
        batch = await producer_client.create_batch(partition_id="0")
        batch.add(EventData(body="A single message"))
        await producer_client.send_batch(batch)

    # Finally let's do it with SAS token + conn str
    token_conn_str = "Endpoint=sb://{}/;SharedAccessSignature={};".format(hostname, token)
    conn_str_producer_client = EventHubProducerClient.from_connection_string(
        token_conn_str,
        eventhub_name=live_eventhub["event_hub"],
        uamqp_transport=uamqp_transport,
        **client_args
    )

    async with conn_str_producer_client:
        batch = await conn_str_producer_client.create_batch(partition_id="0")
        batch.add(EventData(body="A single message"))
        await conn_str_producer_client.send_batch(batch)


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_client_azure_sas_credential_async(live_eventhub, uamqp_transport, client_args):
    # This should "just work" to validate known-good.
    hostname = live_eventhub["hostname"]
    producer_client = EventHubProducerClient.from_connection_string(
        live_eventhub["connection_str"],
        eventhub_name=live_eventhub["event_hub"],
        uamqp_transport=uamqp_transport,
        **client_args
    )

    async with producer_client:
        batch = await producer_client.create_batch(partition_id="0")
        batch.add(EventData(body="A single message"))
        await producer_client.send_batch(batch)

    credential = EventHubSharedKeyCredential(live_eventhub["key_name"], live_eventhub["access_key"])
    auth_uri = "sb://{}/{}".format(hostname, live_eventhub["event_hub"])
    token = (await credential.get_token(auth_uri)).token
    producer_client = EventHubProducerClient(
        fully_qualified_namespace=hostname,
        eventhub_name=live_eventhub["event_hub"],
        auth_timeout=30,
        credential=AzureSasCredential(token),
        uamqp_transport=uamqp_transport,
        **client_args
    )

    async with producer_client:
        batch = await producer_client.create_batch(partition_id="0")
        batch.add(EventData(body="A single message"))
        await producer_client.send_batch(batch)

    assert (await producer_client.get_eventhub_properties()) is not None


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_client_azure_named_key_credential_async(live_eventhub, uamqp_transport, client_args):

    credential = AzureNamedKeyCredential(live_eventhub["key_name"], live_eventhub["access_key"])
    consumer_client = EventHubConsumerClient(
        fully_qualified_namespace=live_eventhub["hostname"],
        eventhub_name=live_eventhub["event_hub"],
        consumer_group="$default",
        credential=credential,
        auth_timeout=30,
        user_agent="customized information",
        uamqp_transport=uamqp_transport,
        **client_args
    )

    assert (await consumer_client.get_eventhub_properties()) is not None

    credential.update("foo", "bar")

    with pytest.raises(Exception):
        await consumer_client.get_eventhub_properties()

    credential.update(live_eventhub["key_name"], live_eventhub["access_key"])
    assert (await consumer_client.get_eventhub_properties()) is not None


# New feature only for Pure Python AMQP, not uamqp.
@pytest.mark.liveTest
@pytest.mark.asyncio
@pytest.mark.no_amqpproxy # testing ssl_context
async def test_client_with_ssl_context_async(auth_credentials_async, socket_transport):
    fully_qualified_namespace, eventhub_name, credential = auth_credentials_async

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
    async with producer:
        with pytest.raises(ConnectError):
            batch = await producer.create_batch()

    async def on_event(partition_context, event):
        on_event.called = True
        on_event.partition_id = partition_context.partition_id
        on_event.event = event

    async def on_error(partition_context, error):
        on_error.error = error
        await consumer.close()

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
    async with consumer:
        task = asyncio.ensure_future(consumer.receive(on_event, on_error=on_error, starting_position="-1"))
        await asyncio.sleep(15)
    await task
    assert isinstance(on_error.error, ConnectError)

    # Check that SSLContext with valid cert file doesn't raise an error
    async def verify_context_async():
        # asyncio.to_thread only available in Python 3.9+
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        await asyncio.to_thread(context.load_verify_locations, certifi.where())
        purpose = ssl.Purpose.SERVER_AUTH
        await asyncio.to_thread(context.load_default_certs, purpose=purpose)
        return context

    def verify_context():  # for Python 3.8
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations(certifi.where())
        purpose = ssl.Purpose.SERVER_AUTH
        context.load_default_certs(purpose=purpose)
        return context

    if hasattr(asyncio, "to_thread"):
        context = await verify_context_async()
    else:
        context = verify_context()

    producer = EventHubProducerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=credential(),
        transport_type=socket_transport,
        ssl_context=context,
    )
    async with producer:
        batch = await producer.create_batch()
        batch.add(EventData(body="A single message"))
        batch.add(EventData(body="A second message"))
        await producer.send_batch(batch)

    async def on_event(partition_context, event):
        on_event.total += 1

    async def on_error(partition_context, error):
        on_error.error = error
        await consumer.close()

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

    async with consumer:
        task = asyncio.ensure_future(consumer.receive(on_event, on_error=on_error, starting_position="-1"))
        await asyncio.sleep(15)
    await task
    assert on_event.total == 2
    assert on_error.error is None
