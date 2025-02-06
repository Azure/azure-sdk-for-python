# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import time
import sys
import threading

from azure.eventhub import EventData, EventDataBatch
from azure.eventhub.exceptions import (
    ConnectError,
    AuthenticationError,
    EventHubError,
    OperationTimeoutError,
)
from azure.eventhub import (
    EventHubProducerClient,
    EventHubConsumerClient,
    EventHubSharedKeyCredential,
)
from azure.eventhub._client_base import EventHubSASTokenCredential


@pytest.mark.liveTest
def test_send_batch_with_invalid_hostname(invalid_hostname, uamqp_transport):
    if sys.platform.startswith("darwin"):
        pytest.skip(
            "Skipping on OSX - it keeps reporting 'Unable to set external certificates' " "and blocking other tests"
        )
    client = EventHubProducerClient.from_connection_string(invalid_hostname, uamqp_transport=uamqp_transport)
    with client:
        with pytest.raises(ConnectError):
            batch = EventDataBatch()
            batch.add(EventData("test data"))
            client.send_batch(batch)

    # test setting callback
    def on_error(events, pid, err):
        assert len(events) == 1
        assert not pid
        on_error.err = err

    on_error.err = None
    client = EventHubProducerClient.from_connection_string(
        invalid_hostname, on_error=on_error, uamqp_transport=uamqp_transport
    )
    with client:
        batch = EventDataBatch()
        batch.add(EventData("test data"))
        client.send_batch(batch)
    assert isinstance(on_error.err, ConnectError)

    on_error.err = None
    client = EventHubProducerClient.from_connection_string(
        invalid_hostname, on_error=on_error, uamqp_transport=uamqp_transport
    )
    with client:
        client.send_event(EventData("test data"))
    assert isinstance(on_error.err, ConnectError)


@pytest.mark.liveTest
def test_receive_with_invalid_hostname_sync(invalid_hostname, uamqp_transport):
    def on_event(partition_context, event):
        pass

    client = EventHubConsumerClient.from_connection_string(
        invalid_hostname, consumer_group="$default", uamqp_transport=uamqp_transport
    )
    with client:
        thread = threading.Thread(target=client.receive, args=(on_event,))
        thread.start()
        time.sleep(2)
        assert len(client._event_processors) == 1
    thread.join()


@pytest.mark.liveTest
def test_send_batch_with_invalid_key(invalid_key, uamqp_transport):
    client = EventHubProducerClient.from_connection_string(invalid_key, uamqp_transport=uamqp_transport)
    try:
        with pytest.raises(ConnectError):
            batch = EventDataBatch()
            batch.add(EventData("test data"))
            client.send_batch(batch)
    finally:
        client.close()


@pytest.mark.liveTest
def test_send_batch_to_invalid_partitions(auth_credentials, uamqp_transport):
    fully_qualified_namespace, eventhub_name, credential = auth_credentials
    partitions = ["XYZ", "-1", "1000", "-"]
    for p in partitions:
        client = EventHubProducerClient(
            fully_qualified_namespace=fully_qualified_namespace,
            eventhub_name=eventhub_name,
            credential=credential(),
            uamqp_transport=uamqp_transport,
        )
        try:
            with pytest.raises(ConnectError):
                batch = client.create_batch(partition_id=p)
                batch.add(EventData("test data"))
                client.send_batch(batch)
        finally:
            client.close()


@pytest.mark.liveTest
def test_send_batch_too_large_message(auth_credentials, uamqp_transport):
    if sys.platform.startswith("darwin"):
        pytest.skip("Skipping on OSX - open issue regarding message size")
    fully_qualified_namespace, eventhub_name, credential = auth_credentials
    client = EventHubProducerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=credential(),
        uamqp_transport=uamqp_transport,
    )
    try:
        data = EventData(b"A" * 1100000)
        batch = client.create_batch()
        with pytest.raises(ValueError):
            batch.add(data)
    finally:
        client.close()


@pytest.mark.liveTest
def test_send_batch_null_body(auth_credentials, uamqp_transport):
    fully_qualified_namespace, eventhub_name, credential = auth_credentials
    client = EventHubProducerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=credential(),
        uamqp_transport=uamqp_transport,
    )
    try:
        with pytest.raises(ValueError):
            data = EventData(None)
            batch = client.create_batch()
            batch.add(data)
            client.send_batch(batch)
    finally:
        client.close()


@pytest.mark.liveTest
def test_create_batch_with_invalid_hostname_sync(invalid_hostname, uamqp_transport):
    if sys.platform.startswith("darwin"):
        pytest.skip(
            "Skipping on OSX - it keeps reporting 'Unable to set external certificates' " "and blocking other tests"
        )
    client = EventHubProducerClient.from_connection_string(invalid_hostname, uamqp_transport=uamqp_transport)
    with client:
        with pytest.raises(ConnectError):
            client.create_batch(max_size_in_bytes=300)


@pytest.mark.liveTest
def test_create_batch_with_too_large_size_sync(auth_credentials, uamqp_transport):
    fully_qualified_namespace, eventhub_name, credential = auth_credentials
    client = EventHubProducerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=credential(),
        uamqp_transport=uamqp_transport,
    )
    with client:
        with pytest.raises(ValueError):
            client.create_batch(max_size_in_bytes=5 * 1024 * 1024)


@pytest.mark.liveTest
def test_invalid_proxy_server(auth_credentials, uamqp_transport):
    if sys.platform.startswith("darwin") and uamqp_transport:
        pytest.skip("Skipping on OSX - running forever and blocking other tests")
    fully_qualified_namespace, eventhub_name, credential = auth_credentials
    HTTP_PROXY = {
        "proxy_hostname": "fakeproxy",  # proxy hostname.
        "proxy_port": 3128,  # proxy port.
    }

    client = EventHubProducerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=credential(),
        http_proxy=HTTP_PROXY,
        uamqp_transport=uamqp_transport,
    )
    with client:
        with pytest.raises(EventHubError):
            batch = client.create_batch()


@pytest.mark.liveTest
def test_client_send_timeout(auth_credential_receivers, uamqp_transport):
    fully_qualified_namespace, eventhub_name, credential, receivers = auth_credential_receivers

    def on_success(events, pid):
        pass

    def on_error(events, pid, err):
        pass

    producer = EventHubProducerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=credential(),
        uamqp_transport=uamqp_transport,
    )

    with producer:
        with pytest.raises(OperationTimeoutError):
            producer.send_batch([EventData(b"Data")], timeout=-1)

        with pytest.raises(OperationTimeoutError):
            producer.send_event(EventData(b"Data"), timeout=-1)

    producer = EventHubProducerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=credential(),
        buffered_mode=True,
        on_success=on_success,
        on_error=on_error,
        uamqp_transport=uamqp_transport,
    )

    with producer:
        with pytest.raises(OperationTimeoutError):
            producer.send_batch([EventData(b"Data")], timeout=-1)

        with pytest.raises(OperationTimeoutError):
            producer.send_event(EventData(b"Data"), timeout=-1)


@pytest.mark.liveTest
def test_client_invalid_credential(live_eventhub, get_credential, uamqp_transport):

    def on_event(partition_context, event):
        pass

    def on_error(partition_context, error):
        on_error.err = error

    azure_credential = get_credential()
    # Skipping on OSX - it's raising a ConnectionLostError
    if not sys.platform.startswith("darwin"):
        producer_client = EventHubProducerClient(
            fully_qualified_namespace="fakeeventhub.servicebus.windows.net",
            eventhub_name=live_eventhub["event_hub"],
            credential=azure_credential,
            user_agent="customized information",
            retry_total=1,
            retry_mode="exponential",
            retry_backoff=0.02,
            uamqp_transport=uamqp_transport,
        )
        consumer_client = EventHubConsumerClient(
            fully_qualified_namespace="fakeeventhub.servicebus.windows.net",
            eventhub_name=live_eventhub["event_hub"],
            credential=azure_credential,
            user_agent="customized information",
            consumer_group="$Default",
            retry_total=1,
            retry_mode="exponential",
            retry_backoff=0.02,
            uamqp_transport=uamqp_transport,
        )
        with producer_client:
            with pytest.raises(ConnectError):
                producer_client.create_batch(partition_id="0")

        on_error.err = None
        with consumer_client:
            thread = threading.Thread(
                target=consumer_client.receive,
                args=(on_event,),
                kwargs={"starting_position": "-1", "on_error": on_error},
            )
            thread.daemon = True
            thread.start()
            time.sleep(15)
        thread.join()
        assert isinstance(on_error.err, ConnectError)

    producer_client = EventHubProducerClient(
        fully_qualified_namespace=live_eventhub["hostname"],
        eventhub_name="fakehub",
        credential=azure_credential,
        uamqp_transport=uamqp_transport,
    )

    consumer_client = EventHubConsumerClient(
        fully_qualified_namespace=live_eventhub["hostname"],
        eventhub_name="fakehub",
        credential=azure_credential,
        consumer_group="$Default",
        retry_total=0,
        uamqp_transport=uamqp_transport,
    )

    with producer_client:
        with pytest.raises(ConnectError):
            producer_client.create_batch(partition_id="0")

    on_error.err = None
    with consumer_client:
        thread = threading.Thread(
            target=consumer_client.receive,
            args=(on_event,),
            kwargs={"starting_position": "-1", "on_error": on_error},
        )
        thread.daemon = True
        thread.start()
        time.sleep(15)
    thread.join()
    assert isinstance(on_error.err, AuthenticationError)

    credential = EventHubSharedKeyCredential(live_eventhub["key_name"], live_eventhub["access_key"])
    auth_uri = "sb://{}/{}".format(live_eventhub["hostname"], live_eventhub["event_hub"])
    token = credential.get_token(auth_uri).token
    producer_client = EventHubProducerClient(
        fully_qualified_namespace=live_eventhub["hostname"],
        eventhub_name=live_eventhub["event_hub"],
        credential=EventHubSASTokenCredential(token, time.time() + 5),
        uamqp_transport=uamqp_transport,
    )
    time.sleep(10)
    # expired credential
    with producer_client:
        with pytest.raises(AuthenticationError):
            producer_client.create_batch(partition_id="0")

    consumer_client = EventHubConsumerClient(
        fully_qualified_namespace=live_eventhub["hostname"],
        eventhub_name=live_eventhub["event_hub"],
        credential=EventHubSASTokenCredential(token, time.time() + 7),
        consumer_group="$Default",
        retry_total=0,
        uamqp_transport=uamqp_transport,
    )
    on_error.err = None
    with consumer_client:
        thread = threading.Thread(
            target=consumer_client.receive,
            args=(on_event,),
            kwargs={"starting_position": "-1", "on_error": on_error},
        )
        thread.daemon = True
        thread.start()
        time.sleep(15)
    thread.join()

    assert isinstance(on_error.err, AuthenticationError)

    credential = EventHubSharedKeyCredential("fakekey", live_eventhub["access_key"])
    producer_client = EventHubProducerClient(
        fully_qualified_namespace=live_eventhub["hostname"],
        eventhub_name=live_eventhub["event_hub"],
        credential=credential,
        uamqp_transport=uamqp_transport,
    )
    with producer_client:
        with pytest.raises(AuthenticationError):
            producer_client.create_batch(partition_id="0")

    consumer_client = EventHubConsumerClient(
        fully_qualified_namespace=live_eventhub["hostname"],
        eventhub_name=live_eventhub["event_hub"],
        credential=credential,
        consumer_group="$Default",
        retry_total=0,
        uamqp_transport=uamqp_transport,
    )
    on_error.err = None
    with consumer_client:
        thread = threading.Thread(
            target=consumer_client.receive,
            args=(on_event,),
            kwargs={"starting_position": "-1", "on_error": on_error},
        )
        thread.daemon = True
        thread.start()
        time.sleep(15)
    thread.join()
    assert isinstance(on_error.err, AuthenticationError)

    credential = EventHubSharedKeyCredential(live_eventhub["key_name"], "fakekey")
    producer_client = EventHubProducerClient(
        fully_qualified_namespace=live_eventhub["hostname"],
        eventhub_name=live_eventhub["event_hub"],
        credential=credential,
        uamqp_transport=uamqp_transport,
    )

    with producer_client:
        errors = AuthenticationError
        # TODO: flaky TimeoutError during connect for China region
        if "servicebus.windows.net" not in live_eventhub["hostname"]:
            errors = (AuthenticationError, ConnectError)
        with pytest.raises(errors):
            producer_client.create_batch(partition_id="0")

    consumer_client = EventHubConsumerClient(
        fully_qualified_namespace=live_eventhub["hostname"],
        eventhub_name=live_eventhub["event_hub"],
        credential=credential,
        consumer_group="$Default",
        retry_total=0,
        uamqp_transport=uamqp_transport,
    )
    on_error.err = None
    with consumer_client:
        thread = threading.Thread(
            target=consumer_client.receive,
            args=(on_event,),
            kwargs={"starting_position": "-1", "on_error": on_error},
        )
        thread.daemon = True
        thread.start()
        time.sleep(15)
    thread.join()
    assert isinstance(on_error.err, AuthenticationError)

    producer_client = EventHubProducerClient(
        fully_qualified_namespace=live_eventhub["hostname"],
        eventhub_name=live_eventhub["event_hub"],
        credential=azure_credential,
        connection_verify="cacert.pem",
        uamqp_transport=uamqp_transport,
    )

    # TODO: this seems like a bug from uamqp, should be ConnectError?
    with producer_client:
        with pytest.raises(EventHubError):
            producer_client.create_batch(partition_id="0")

    consumer_client = EventHubConsumerClient(
        fully_qualified_namespace=live_eventhub["hostname"],
        eventhub_name=live_eventhub["event_hub"],
        consumer_group="$Default",
        credential=azure_credential,
        retry_total=0,
        connection_verify="cacert.pem",
        uamqp_transport=uamqp_transport,
    )
    with consumer_client:
        thread = threading.Thread(
            target=consumer_client.receive,
            args=(on_event,),
            kwargs={"starting_position": "-1", "on_error": on_error},
        )
        thread.daemon = True
        thread.start()
        time.sleep(15)
    thread.join()

    # TODO: this seems like a bug from uamqp, should be ConnectError?
    assert isinstance(on_error.err, FileNotFoundError)

    # Skipping on OSX - it's raising a ConnectionLostError
    if not sys.platform.startswith("darwin"):
        producer_client = EventHubProducerClient(
            fully_qualified_namespace=live_eventhub["hostname"],
            eventhub_name=live_eventhub["event_hub"],
            credential=azure_credential,
            custom_endpoint_address="fakeaddr",
            uamqp_transport=uamqp_transport,
        )

        with producer_client:
            with pytest.raises(AuthenticationError):
                producer_client.create_batch(partition_id="0")

        consumer_client = EventHubConsumerClient(
            fully_qualified_namespace=live_eventhub["hostname"],
            eventhub_name=live_eventhub["event_hub"],
            consumer_group="$Default",
            credential=azure_credential,
            retry_total=0,
            custom_endpoint_address="fakeaddr",
            uamqp_transport=uamqp_transport,
        )
        with consumer_client:
            thread = threading.Thread(
                target=consumer_client.receive,
                args=(on_event,),
                kwargs={"starting_position": "-1", "on_error": on_error},
            )
            thread.daemon = True
            thread.start()
            time.sleep(15)
        thread.join()

        assert isinstance(on_error.err, AuthenticationError)
