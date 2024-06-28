# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
import sys
import threading

import pytest
from azure.core.tracing.common import with_current_context
from azure.eventhub import EventHubConsumerClient, EventHubProducerClient, EventData
from opentelemetry.trace import SpanKind


class TestEventHubsTracing:
    def _verify_span_attributes(self, *, span):
        # Ensure all attributes are set and have a value.
        for attr in span.attributes:
            assert span.attributes[attr] is not None and span.attributes[attr] != ""

    def _verify_message(self, *, span, dest, server_address):
        assert span.name == "EventHubs.message"
        assert span.kind == SpanKind.PRODUCER
        self._verify_span_attributes(span=span)
        assert span.attributes["az.namespace"] == "Microsoft.EventHub"
        assert span.attributes["messaging.system"] == "eventhubs"
        assert span.attributes["messaging.destination.name"] == dest
        assert span.attributes["server.address"] == server_address

    def _verify_send(self, *, span, dest, server_address, message_count):
        assert span.name == "EventHubs.send"
        assert span.kind == SpanKind.CLIENT
        self._verify_span_attributes(span=span)
        assert span.attributes["az.namespace"] == "Microsoft.EventHub"
        assert span.attributes["messaging.system"] == "eventhubs"
        assert span.attributes["messaging.destination.name"] == dest
        assert span.attributes["messaging.operation"] == "publish"
        assert span.attributes["server.address"] == server_address
        if message_count > 1:
            assert span.attributes["messaging.batch.message_count"] == message_count

    def _verify_receive(self, *, span, dest, server_address, message_count):
        assert span.name == "EventHubs.receive"
        assert span.kind == SpanKind.CLIENT
        self._verify_span_attributes(span=span)
        assert span.attributes["az.namespace"] == "Microsoft.EventHub"
        assert span.attributes["messaging.system"] == "eventhubs"
        assert span.attributes["messaging.destination.name"] == dest
        assert span.attributes["messaging.operation"] == "receive"
        assert span.attributes["server.address"] == server_address
        for link in span.links:
            assert "enqueuedTime" in link.attributes
        if message_count > 1:
            assert span.attributes["messaging.batch.message_count"] == message_count

    def _verify_process(self, *, span, dest, server_address, message_count):
        assert span.name == "EventHubs.process"
        assert span.kind == SpanKind.CONSUMER
        self._verify_span_attributes(span=span)
        assert span.attributes["az.namespace"] == "Microsoft.EventHub"
        assert span.attributes["messaging.system"] == "eventhubs"
        assert span.attributes["messaging.destination.name"] == dest
        assert span.attributes["messaging.operation"] == "process"
        assert span.attributes["server.address"] == server_address
        if message_count > 1:
            assert span.attributes["messaging.batch.message_count"] == message_count

    @pytest.mark.live_test_only
    @pytest.mark.skipif(sys.platform.startswith("darwin"), reason="threading issues on mac CI")
    def test_eventhubs_client_tracing(self, config, tracing_helper):

        connection_string = config["eventhub_connection_string"]
        eventhub_name = config["eventhub_name"]

        producer_client = EventHubProducerClient.from_connection_string(
            conn_str=connection_string,
            eventhub_name=eventhub_name,
        )

        consumer_client = EventHubConsumerClient.from_connection_string(
            conn_str=connection_string,
            consumer_group="$Default",
            eventhub_name=eventhub_name,
        )

        with tracing_helper.tracer.start_as_current_span(name="root"):

            current_date = datetime.now()

            with producer_client:

                # Send batch of events
                event_data_batch = producer_client.create_batch()
                event_data_batch.add(EventData("First message inside an EventDataBatch"))
                event_data_batch.add(EventData("Second message inside an EventDataBatch"))
                producer_client.send_batch(event_data_batch)

            send_spans = tracing_helper.exporter.get_finished_spans()

            # We expect 3 spans to have finished: 1 send spans, and 2 message spans.
            assert len(send_spans) == 3

            server_address = producer_client._address.hostname
            dest_name = producer_client._address.path

            # Verify the spans from the batch send.
            self._verify_message(span=send_spans[0], dest=dest_name, server_address=server_address)
            self._verify_message(span=send_spans[1], dest=dest_name, server_address=server_address)
            self._verify_send(span=send_spans[2], dest=dest_name, server_address=server_address, message_count=2)

            # Verify span links from batch send.
            assert len(send_spans[2].links) == 2
            link = send_spans[2].links[0]
            assert link.context.span_id == send_spans[0].context.span_id
            assert link.context.trace_id == send_spans[0].context.trace_id

            link = send_spans[2].links[1]
            assert link.context.span_id == send_spans[1].context.span_id
            assert link.context.trace_id == send_spans[1].context.trace_id

            tracing_helper.exporter.clear()

            def on_event_batch(partition_context, event_batch):
                pass

            # Receive batch of events.
            worker = threading.Thread(
                target=with_current_context(consumer_client.receive_batch),
                args=(on_event_batch,),
                kwargs={"starting_position": current_date},
            )
            worker.daemon = True
            worker.start()
            worker.join(timeout=3)

            receive_spans = tracing_helper.exporter.get_finished_spans()

            # We expect 2 spans to have finished: 1 receive span and 1 process span.
            assert len(receive_spans) == 2

            self._verify_receive(span=receive_spans[0], dest=dest_name, server_address=server_address, message_count=2)
            self._verify_process(span=receive_spans[1], dest=dest_name, server_address=server_address, message_count=2)

            # Verify receive span links.
            assert len(receive_spans[0].links) == 2
            assert receive_spans[0].links[0].context.span_id == send_spans[0].context.span_id
            assert receive_spans[0].links[1].context.span_id == send_spans[1].context.span_id

            # Verify process span links.
            assert len(receive_spans[1].links) == 2
            assert receive_spans[1].links[0].context.span_id == send_spans[0].context.span_id
            assert receive_spans[1].links[1].context.span_id == send_spans[1].context.span_id
