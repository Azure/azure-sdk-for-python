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


def test_failed_open_records_link_lifecycle(metrics, spans, caplog, monkeypatch):
    from opentelemetry.trace import StatusCode

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
    (link,) = spans.get_finished_spans()
    assert link.status.status_code == StatusCode.ERROR
    assert "broker detail" not in link.to_json()


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


@pytest.fixture
def spans(monkeypatch):
    from azure.core.settings import settings
    from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    provider = TracerProvider()
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    monkeypatch.setattr(trace, "get_tracer", provider.get_tracer)
    previous = settings.tracing_implementation()
    settings.tracing_implementation.set_value(OpenTelemetrySpan)
    try:
        yield exporter
    finally:
        settings.tracing_implementation.set_value(previous)
        provider.shutdown()


def current_span_id():
    from opentelemetry import trace

    return trace.get_current_span().get_span_context().span_id


def metric_if_recorded(reader, instrument):
    return points(reader, instrument) if reader.get_metrics_data() else []


@pytest.mark.parametrize("fail_attach", [False, True])
def test_sync_receive_waits_for_link_and_times_only_its_polls(metrics, spans, monkeypatch, fail_attach):
    from opentelemetry.trace import StatusCode

    provider, reader = metrics
    client = EventHubConsumerClient("namespace", "hub", "group", None, meter_provider=provider)
    callback_contexts = []
    receiver = client._create_consumer("group", "0", "-1", lambda _: callback_contexts.append(current_span_id()))
    clock = [0.0]
    monkeypatch.setattr("azure.eventhub._metrics.perf_counter", lambda: clock[0])
    failure = ImportError("private broker information")
    readiness = iter([False, failure if fail_attach else True])

    def client_ready():
        clock[0] += 1.0
        ready = next(readiness)
        if isinstance(ready, Exception):
            raise ready
        return ready

    handler = Mock()
    handler.client_ready.side_effect = client_ready
    handler.do_work.side_effect = lambda **_: receiver._message_buffer.append(Message(data=[b"one"]))
    monkeypatch.setattr(client, "_create_auth", Mock())
    monkeypatch.setattr(receiver, "_create_handler", lambda _: setattr(receiver, "_handler", handler))
    receiver.receive(max_batch_size=1)
    assert not spans.get_finished_spans()
    assert not metric_if_recorded(reader, "amqp.lifecycle")
    assert current_span_id() == 0
    # Another partition receives and runs application code between the two readiness polls.
    clock[0] += 80.0
    if fail_attach:
        with pytest.raises(ImportError) as original:
            receiver.receive(max_batch_size=1)
        assert original.value is failure
    else:
        receiver.receive(max_batch_size=1)
        assert callback_contexts == [0]
    (receive,) = [s for s in spans.get_finished_spans() if s.name == "EventHubs.receive.operation"]
    (link,) = [s for s in spans.get_finished_spans() if s.name == "EventHubs.amqp.open"]
    assert link.parent.span_id == receive.context.span_id
    assert link.attributes["outcome"] == ("error" if fail_attach else "success")
    (transition,) = points(reader, "amqp.lifecycle")
    assert transition.value == 1
    assert transition.attributes["outcome"] == link.attributes["outcome"]
    (duration,) = points(reader, "operation.duration")
    assert duration.sum == 2.0
    if fail_attach:
        assert link.status.status_code == StatusCode.ERROR
        assert "private broker" not in link.to_json()


def test_receive_duration_excludes_time_between_polls(metrics, monkeypatch):
    provider, reader = metrics
    client = EventHubConsumerClient("namespace", "hub", "group", None, meter_provider=provider)
    receiver = client._create_consumer("group", "0", "-1", Mock())
    clock = [0.0]
    monkeypatch.setattr("azure.eventhub._metrics.perf_counter", lambda: clock[0])

    def poll():
        clock[0] += 1.0
        return False

    monkeypatch.setattr(receiver, "_open", poll)
    receiver.receive(max_batch_size=1)
    clock[0] += 80.0
    receiver._message_buffer.append(Message(data=[b"one"]))
    receiver.receive(max_batch_size=1)
    (duration,) = points(reader, "operation.duration")
    assert duration.sum == 1.0


def test_cold_batch_send_link_has_operation_parent(spans, monkeypatch):
    callback_contexts = []
    client = EventHubProducerClient(
        "namespace", "hub", None, on_success=lambda *_: callback_contexts.append(current_span_id())
    )
    sender = client._producers[ALL_PARTITIONS]
    handler = Mock()
    handler.client_ready.return_value = True
    monkeypatch.setattr(client, "_create_auth", Mock())
    monkeypatch.setattr(sender, "_create_handler", lambda _: setattr(sender, "_handler", handler))
    monkeypatch.setattr(client._amqp_transport, "get_remote_max_message_size", Mock(return_value=65536))
    monkeypatch.setattr(sender, "_send_event_data_with_retry", Mock())
    client.send_batch([EventData("one")])
    finished = {s.name: s for s in spans.get_finished_spans()}
    assert finished["EventHubs.amqp.open"].parent.span_id == finished["EventHubs.send.operation"].context.span_id
    assert callback_contexts == [0]


@pytest.mark.asyncio
async def test_async_cold_batch_send_link_has_operation_parent(spans, monkeypatch):
    callback_contexts = []

    async def callback(*_):
        callback_contexts.append(current_span_id())

    client = AsyncProducer("namespace", "hub", None, on_success=callback)
    sender = client._producers[ALL_PARTITIONS]
    handler = AsyncMock()
    handler.client_ready_async.return_value = True
    monkeypatch.setattr(client, "_create_auth_async", AsyncMock())
    monkeypatch.setattr(sender, "_create_handler", lambda _: setattr(sender, "_handler", handler))
    monkeypatch.setattr(client._amqp_transport, "get_remote_max_message_size", Mock(return_value=65536))
    monkeypatch.setattr(sender, "_send_event_data_with_retry", AsyncMock())
    await client.send_batch([EventData("one")])
    finished = {s.name: s for s in spans.get_finished_spans()}
    assert finished["EventHubs.amqp.open"].parent.span_id == finished["EventHubs.send.operation"].context.span_id
    assert callback_contexts == [0]


@pytest.mark.asyncio
async def test_async_receive_failure_while_callback_is_waiting(metrics, spans, monkeypatch):
    provider, reader = metrics
    started, release = asyncio.Event(), asyncio.Event()
    callback_tasks = []

    async def callback(_):
        assert current_span_id() == 0
        started.set()
        await release.wait()

    client = AsyncConsumer("namespace", "hub", "group", None, meter_provider=provider)
    receiver = client._create_consumer("group", "0", "-1", callback)
    handler = AsyncMock()
    handler.client_ready_async.return_value = True
    monkeypatch.setattr(client, "_create_auth_async", AsyncMock())
    monkeypatch.setattr(receiver, "_create_handler", lambda _: setattr(receiver, "_handler", handler))
    monkeypatch.setattr(client._amqp_transport, "get_remote_max_message_size", Mock(return_value=65536))

    async def transport(consumer, *_):
        await consumer._open()
        callback_tasks.append(asyncio.create_task(consumer._on_event_received(EventData("one"))))
        await started.wait()
        raise RuntimeError("transport failed with callback outstanding")

    monkeypatch.setattr(receiver._amqp_transport, "receive_messages_async", transport)
    try:
        with pytest.raises(RuntimeError, match="transport failed"):
            await receiver.receive()
    finally:
        release.set()
        await asyncio.gather(*callback_tasks)
    assert receiver._receive_operation is None
    assert counts(reader, "operations") == {("receive", "success"): 1, ("receive", "error"): 1}
    duration = next(p for p in points(reader, "operation.duration") if p.attributes["outcome"] == "error")
    assert duration.sum == 0
    parents = [s for s in spans.get_finished_spans() if s.name == "EventHubs.receive.operation"]
    assert [s.attributes["outcome"] for s in parents] == ["success", "error"]
    (link,) = [s for s in spans.get_finished_spans() if s.name == "EventHubs.amqp.open"]
    assert link.parent.span_id == parents[0].context.span_id
