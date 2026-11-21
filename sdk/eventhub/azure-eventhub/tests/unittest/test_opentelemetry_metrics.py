# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import logging
from unittest.mock import AsyncMock, Mock

import pytest
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader

from azure.eventhub import EventData, EventDataBatch, EventHubConsumerClient, EventHubProducerClient
from azure.eventhub.aio import EventHubConsumerClient as AsyncConsumer
from azure.eventhub.aio import EventHubProducerClient as AsyncProducer
from azure.eventhub._constants import ALL_PARTITIONS
from azure.eventhub._pyamqp.message import Message
from azure.eventhub.exceptions import EventHubError


@pytest.fixture
def amqpproxy():
    """These tests substitute AMQP network I/O and do not need the service fixture."""


@pytest.fixture
def metrics():
    reader = InMemoryMetricReader()
    provider = MeterProvider(metric_readers=[reader])
    yield provider, reader
    provider.shutdown()


def points(reader, instrument):
    data = reader.get_metrics_data()
    for resource in data.resource_metrics:
        for scope in resource.scope_metrics:
            for metric in scope.metrics:
                if metric.name == "az.eventhubs." + instrument:
                    return metric.data.data_points
    return []


def counts(reader, instrument):
    return {(p.attributes["operation"], p.attributes["outcome"]): p.value for p in points(reader, instrument)}


def test_send_counts_recovery_batches_and_failed_preparation(metrics, monkeypatch):
    provider, reader = metrics
    client = EventHubProducerClient("namespace", "hub", None, meter_provider=provider)
    producer = client._producers[ALL_PARTITIONS]
    send = Mock(side_effect=[EventHubError("transient"), None, None])
    monkeypatch.setattr(producer, "_send_event_data_with_retry", send)
    monkeypatch.setattr(client, "_start_producer", Mock())
    client.send_event(EventData("one"))
    batch = EventDataBatch()
    batch.add(EventData("two"))
    batch.add(EventData("three"))
    client.send_batch(batch)
    with pytest.raises(TypeError):
        client.send_batch(batch, partition_key="invalid")
    assert send.call_count == 3
    assert counts(reader, "operations") == {("send", "success"): 2, ("send", "error"): 1}
    assert counts(reader, "events") == {("send", "success"): 3}
    success = next(p for p in points(reader, "operation.duration") if p.attributes["outcome"] == "success")
    assert success.count == 2
    assert success.attributes["messaging.destination.name"] == "hub"
    assert success.attributes["server.address"] == "namespace"


@pytest.mark.asyncio
async def test_async_send_records_cancellation(metrics, monkeypatch):
    provider, reader = metrics
    client = AsyncProducer("namespace", "hub", None, meter_provider=provider)
    sender = client._producers[ALL_PARTITIONS]
    monkeypatch.setattr(sender, "_send_event_data_with_retry", AsyncMock(side_effect=[None, asyncio.CancelledError()]))
    await client.send_event(EventData("payload"))
    with pytest.raises(asyncio.CancelledError):
        await client.send_event(EventData("payload"))
    assert counts(reader, "operations") == {("send", "success"): 1, ("send", "cancelled"): 1}
    assert counts(reader, "events") == {("send", "success"): 1}


def test_receive_counts_delivery_before_callback(metrics, monkeypatch):
    provider, reader = metrics
    client = EventHubConsumerClient("namespace", "hub", "group", None, meter_provider=provider)
    callback = Mock(side_effect=ValueError("application error"))
    receiver = client._create_consumer("group", "0", "-1", callback)
    receiver._message_buffer.extend([Message(data=[b"one"]), Message(data=[b"two"])])
    with pytest.raises(ValueError, match="application error"):
        receiver.receive(batch=True, max_batch_size=2)
    monkeypatch.setattr(receiver, "_open", Mock(side_effect=ImportError("test open failure")))
    with pytest.raises(ImportError):
        receiver.receive()
    assert counts(reader, "operations") == {("receive", "success"): 1, ("receive", "error"): 1}
    assert counts(reader, "events") == {("receive", "success"): 2}


@pytest.mark.asyncio
async def test_async_receive_measures_each_delivery(metrics, monkeypatch):
    provider, reader = metrics
    client = AsyncConsumer("namespace", "hub", "group", None, meter_provider=provider)
    callback = AsyncMock()
    receiver = client._create_consumer("group", "0", "-1", callback)

    async def receive(consumer, *_):
        await consumer._on_event_received([EventData("one"), EventData("two")])
        await consumer._on_event_received([])
        raise asyncio.CancelledError()

    monkeypatch.setattr(receiver._amqp_transport, "receive_messages_async", receive)
    with pytest.raises(asyncio.CancelledError):
        await receiver.receive(batch=True)
    assert callback.await_count == 2
    assert counts(reader, "operations") == {("receive", "success"): 2, ("receive", "cancelled"): 1}
    assert counts(reader, "events") == {("receive", "success"): 2}


def test_failed_open_records_link_lifecycle(metrics, caplog, monkeypatch):
    provider, reader = metrics
    client = EventHubProducerClient("namespace", "hub", None, meter_provider=provider)
    sender = client._producers[ALL_PARTITIONS]
    monkeypatch.setattr(client, "_create_auth", Mock(side_effect=ValueError("broker detail")))
    with caplog.at_level(logging.DEBUG, logger="azure.eventhub"), pytest.raises(ValueError):
        sender._open()
    (transition,) = points(reader, "amqp.lifecycle")
    assert transition.value == 1
    assert dict(transition.attributes) == {"component": "sender", "outcome": "error"}
    assert caplog.records[-1].outcome == "error"
    assert "broker detail" not in caplog.text


def test_buffered_send_counts_at_flush(metrics, monkeypatch):
    provider, reader = metrics
    success = Mock()
    with EventHubProducerClient(
        "namespace", "hub", None, meter_provider=provider, buffered_mode=True, on_success=success, on_error=Mock()
    ) as client:
        client._partition_ids = ["0"]
        client._max_message_size_on_link = 65536
        # Disable timed flushing to drive the real worker deterministically.
        client._max_wait_time = 0
        sender = client._create_producer("0")
        monkeypatch.setattr(client, "_create_producer", Mock(return_value=sender))
        monkeypatch.setattr(sender, "_send_event_data_with_retry", Mock())
        client.send_event(EventData("one"))
        client.send_event(EventData("two"))
        assert reader.get_metrics_data() is None
        client.flush()
        assert counts(reader, "operations") == {("send", "success"): 1}
        assert counts(reader, "events") == {("send", "success"): 2}
        success.assert_called_once()
