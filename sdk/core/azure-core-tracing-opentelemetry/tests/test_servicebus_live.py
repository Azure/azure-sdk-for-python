# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.servicebus import ServiceBusClient, ServiceBusMessage
from opentelemetry.trace import SpanKind


class TestServiceBusTracing:
    def _verify_span_attributes(self, *, span):
        # Ensure all attributes are set and have a value.
        for attr in span.attributes:
            assert span.attributes[attr] is not None and span.attributes[attr] != ""

    def _verify_message(self, *, span, dest, server_address):
        assert span.name == "ServiceBus.message"
        assert span.kind == SpanKind.PRODUCER
        self._verify_span_attributes(span=span)
        assert span.attributes["az.namespace"] == "Microsoft.ServiceBus"
        assert span.attributes["messaging.system"] == "servicebus"
        assert span.attributes["messaging.destination.name"] == dest
        assert span.attributes["server.address"] == server_address

    def _verify_send(self, *, span, dest, server_address, message_count):
        assert span.name == "ServiceBus.send"
        assert span.kind == SpanKind.CLIENT
        self._verify_span_attributes(span=span)
        assert span.attributes["az.namespace"] == "Microsoft.ServiceBus"
        assert span.attributes["messaging.system"] == "servicebus"
        assert span.attributes["messaging.destination.name"] == dest
        assert span.attributes["messaging.operation"] == "publish"
        assert span.attributes["server.address"] == server_address
        if message_count > 1:
            assert span.attributes["messaging.batch.message_count"] == message_count

    def _verify_receive(self, *, span, dest, server_address, message_count):
        assert span.name == "ServiceBus.receive"
        assert span.kind == SpanKind.CLIENT
        self._verify_span_attributes(span=span)
        assert span.attributes["az.namespace"] == "Microsoft.ServiceBus"
        assert span.attributes["messaging.system"] == "servicebus"
        assert span.attributes["messaging.destination.name"] == dest
        assert span.attributes["messaging.operation"] == "receive"
        assert span.attributes["server.address"] == server_address
        for link in span.links:
            assert "enqueuedTime" in link.attributes
        if message_count > 1:
            assert span.attributes["messaging.batch.message_count"] == message_count

    def _verify_complete(self, *, span, dest, server_address):
        assert span.name == "ServiceBus.complete"
        assert span.kind == SpanKind.CLIENT
        self._verify_span_attributes(span=span)
        assert span.attributes["az.namespace"] == "Microsoft.ServiceBus"
        assert span.attributes["messaging.system"] == "servicebus"
        assert span.attributes["messaging.operation"] == "settle"
        assert span.attributes["server.address"] == server_address
        assert span.attributes["messaging.destination.name"] == dest

    @pytest.mark.live_test_only
    def test_servicebus_client_tracing_queue(self, config, tracing_helper):
        connection_string = config["servicebus_connection_string"]
        queue_name = config["servicebus_queue_name"]
        client = ServiceBusClient.from_connection_string(connection_string)

        with tracing_helper.tracer.start_as_current_span(name="root"):
            with client.get_queue_sender(queue_name) as sender:

                # Sending a single message
                sender.send_messages(ServiceBusMessage("Test foo message"))

                # Sending a batch of messages
                message_batch = sender.create_message_batch()
                message_batch.add_message(ServiceBusMessage("First batch foo message"))
                message_batch.add_message(ServiceBusMessage("Second batch foo message"))
                sender.send_messages(message_batch)

            send_spans = tracing_helper.exporter.get_finished_spans()
            server_address = sender.fully_qualified_namespace

            # We expect 5 spans to have finished: 2 send spans, and 3 message spans.
            assert len(send_spans) == 5

            # Verify the spans from the first send.
            self._verify_message(span=send_spans[0], dest=queue_name, server_address=server_address)
            self._verify_send(span=send_spans[1], dest=queue_name, server_address=server_address, message_count=1)

            # Verify span links from single send.
            link = send_spans[1].links[0]
            assert link.context.span_id == send_spans[0].context.span_id
            assert link.context.trace_id == send_spans[0].context.trace_id

            # Verify the spans from the second send.
            self._verify_message(span=send_spans[2], dest=queue_name, server_address=server_address)
            self._verify_message(span=send_spans[3], dest=queue_name, server_address=server_address)
            self._verify_send(span=send_spans[4], dest=queue_name, server_address=server_address, message_count=2)

            # Verify span links from batch send.
            assert len(send_spans[4].links) == 2
            link = send_spans[4].links[0]
            assert link.context.span_id == send_spans[2].context.span_id
            assert link.context.trace_id == send_spans[2].context.trace_id

            link = send_spans[4].links[1]
            assert link.context.span_id == send_spans[3].context.span_id
            assert link.context.trace_id == send_spans[3].context.trace_id

            tracing_helper.exporter.clear()

            # Receive all the sent spans.
            receiver = client.get_queue_receiver(queue_name=queue_name)
            with receiver:
                received_msgs = receiver.receive_messages(max_message_count=3, max_wait_time=10)
                for msg in received_msgs:
                    assert "foo" in str(msg)
                    receiver.complete_message(msg)

            receive_spans = tracing_helper.exporter.get_finished_spans()

            # We expect 4 spans to have finished: 1 receive span, and 3 settlement spans.
            assert len(receive_spans) == 4
            self._verify_receive(span=receive_spans[0], dest=queue_name, server_address=server_address, message_count=3)

            # Verify span links from receive.
            assert len(receive_spans[0].links) == 3
            assert receive_spans[0].links[0].context.span_id == send_spans[0].context.span_id
            assert receive_spans[0].links[1].context.span_id == send_spans[2].context.span_id
            assert receive_spans[0].links[2].context.span_id == send_spans[3].context.span_id

            # Verify settlement spans.
            self._verify_complete(span=receive_spans[1], dest=queue_name, server_address=server_address)
            self._verify_complete(span=receive_spans[2], dest=queue_name, server_address=server_address)
            self._verify_complete(span=receive_spans[3], dest=queue_name, server_address=server_address)

    @pytest.mark.live_test_only
    def test_servicebus_client_tracing_topic(self, config, tracing_helper):
        connection_string = config["servicebus_connection_string"]
        topic_name = config["servicebus_topic_name"]
        subscription_name = config["servicebus_subscription_name"]
        client = ServiceBusClient.from_connection_string(connection_string)

        with tracing_helper.tracer.start_as_current_span(name="root"):
            with client.get_topic_sender(topic_name) as sender:

                # Sending a single message
                sender.send_messages(ServiceBusMessage("Test foo message"))

                # Sending a batch of messages
                message_batch = sender.create_message_batch()
                message_batch.add_message(ServiceBusMessage("First batch foo message"))
                message_batch.add_message(ServiceBusMessage("Second batch foo message"))
                sender.send_messages(message_batch)

            send_spans = tracing_helper.exporter.get_finished_spans()
            server_address = sender.fully_qualified_namespace

            # We expect 5 spans to have finished: 2 send spans, and 3 message spans.
            assert len(send_spans) == 5

            # Verify the spans from the first send.
            self._verify_message(span=send_spans[0], dest=topic_name, server_address=server_address)
            self._verify_send(span=send_spans[1], dest=topic_name, server_address=server_address, message_count=1)

            # Verify span links from single send.
            link = send_spans[1].links[0]
            assert link.context.span_id == send_spans[0].context.span_id
            assert link.context.trace_id == send_spans[0].context.trace_id

            # Verify the spans from the second send.
            self._verify_message(span=send_spans[2], dest=topic_name, server_address=server_address)
            self._verify_message(span=send_spans[3], dest=topic_name, server_address=server_address)
            self._verify_send(span=send_spans[4], dest=topic_name, server_address=server_address, message_count=2)

            # Verify span links from batch send.
            assert len(send_spans[4].links) == 2
            link = send_spans[4].links[0]
            assert link.context.span_id == send_spans[2].context.span_id
            assert link.context.trace_id == send_spans[2].context.trace_id

            link = send_spans[4].links[1]
            assert link.context.span_id == send_spans[3].context.span_id
            assert link.context.trace_id == send_spans[3].context.trace_id

            tracing_helper.exporter.clear()

            # Receive all the sent spans.
            receiver = client.get_subscription_receiver(topic_name, subscription_name)
            with receiver:
                received_msgs = receiver.receive_messages(max_message_count=3, max_wait_time=10)
                for msg in received_msgs:
                    assert "foo" in str(msg)
                    receiver.complete_message(msg)

            receive_spans = tracing_helper.exporter.get_finished_spans()

            # We expect 4 spans to have finished: 1 receive span, and 3 settlement spans.
            assert len(receive_spans) == 4
            self._verify_receive(span=receive_spans[0], dest=topic_name, server_address=server_address, message_count=3)

            assert len(receive_spans[0].links) == 3
            assert receive_spans[0].links[0].context.span_id == send_spans[0].context.span_id
            assert receive_spans[0].links[1].context.span_id == send_spans[2].context.span_id
            assert receive_spans[0].links[2].context.span_id == send_spans[3].context.span_id

            # Verify settlement spans.
            self._verify_complete(span=receive_spans[1], dest=topic_name, server_address=server_address)
            self._verify_complete(span=receive_spans[2], dest=topic_name, server_address=server_address)
            self._verify_complete(span=receive_spans[3], dest=topic_name, server_address=server_address)
