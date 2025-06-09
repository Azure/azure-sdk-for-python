# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient

from test_tracing_live import ServiceBusTracingTestBase


class TestServiceBusTracingAsync(ServiceBusTracingTestBase):

    @pytest.mark.asyncio
    @pytest.mark.live_test_only
    async def test_servicebus_client_tracing_queue_async(self, config, tracing_helper):

        connection_string = config["servicebus_connection_string"]
        queue_name = config["servicebus_queue_name"]
        client = ServiceBusClient.from_connection_string(connection_string)

        with tracing_helper.tracer.start_as_current_span(name="root"):
            async with client.get_queue_sender(queue_name) as sender:

                # Sending a single message
                await sender.send_messages(ServiceBusMessage("Test foo message"))

                # Sending a batch of messages
                message_batch = await sender.create_message_batch()
                message_batch.add_message(ServiceBusMessage("First batch foo message"))
                message_batch.add_message(ServiceBusMessage("Second batch foo message"))
                await sender.send_messages(message_batch)


            finished_spans = tracing_helper.exporter.get_finished_spans()
            server_address = sender.fully_qualified_namespace

            # We expect 5 spans to have finished: 2 send spans, and 3 message spans.
            assert len(finished_spans) == 5

            # Verify the spans from the first send.
            self._verify_message(span=finished_spans[0], dest=queue_name, server_address=server_address)
            self._verify_send(span=finished_spans[1], dest=queue_name, server_address=server_address, message_count=1)

            # Verify span links from single send.
            link = finished_spans[1].links[0]
            assert link.context.span_id == finished_spans[0].context.span_id
            assert link.context.trace_id == finished_spans[0].context.trace_id

            # Verify the spans from the second send.
            self._verify_message(span=finished_spans[2], dest=queue_name, server_address=server_address)
            self._verify_message(span=finished_spans[3], dest=queue_name, server_address=server_address)
            self._verify_send(span=finished_spans[4], dest=queue_name, server_address=server_address, message_count=2)

            # Verify span links from batch send.
            assert len(finished_spans[4].links) == 2
            link = finished_spans[4].links[0]
            assert link.context.span_id == finished_spans[2].context.span_id
            assert link.context.trace_id == finished_spans[2].context.trace_id

            link = finished_spans[4].links[1]
            assert link.context.span_id == finished_spans[3].context.span_id
            assert link.context.trace_id == finished_spans[3].context.trace_id

            tracing_helper.exporter.clear()

            # Receive all the sent spans.
            async with client.get_queue_receiver(queue_name=queue_name) as receiver:
                received_msgs = await receiver.receive_messages(max_message_count=3, max_wait_time=10)
                for msg in received_msgs:
                    assert "foo" in str(msg)
                    await receiver.complete_message(msg)

            receive_spans = tracing_helper.exporter.get_finished_spans()

            # We expect 4 spans to have finished: 1 receive span, and 3 settlement spans.
            assert len(receive_spans) == 4
            self._verify_receive(span=receive_spans[0], dest=queue_name, server_address=server_address, message_count=3)

            # Verify span links from receive.
            assert len(receive_spans[0].links) == 3
            assert receive_spans[0].links[0].context.span_id == finished_spans[0].context.span_id
            assert receive_spans[0].links[1].context.span_id == finished_spans[2].context.span_id
            assert receive_spans[0].links[2].context.span_id == finished_spans[3].context.span_id

            # Verify settlement spans.
            self._verify_complete(span=receive_spans[1], dest=queue_name, server_address=server_address)
            self._verify_complete(span=receive_spans[2], dest=queue_name, server_address=server_address)
            self._verify_complete(span=receive_spans[3], dest=queue_name, server_address=server_address)

    @pytest.mark.asyncio
    @pytest.mark.live_test_only
    async def test_servicebus_client_tracing_topic_async(self, config, tracing_helper):
        connection_string = config["servicebus_connection_string"]
        topic_name = config["servicebus_topic_name"]
        subscription_name = config["servicebus_subscription_name"]
        client = ServiceBusClient.from_connection_string(connection_string)

        with tracing_helper.tracer.start_as_current_span(name="root"):
            async with client.get_topic_sender(topic_name) as sender:

                # Sending a single message
                await sender.send_messages(ServiceBusMessage("Test foo message"))

                # Sending a batch of messages
                message_batch = await sender.create_message_batch()
                message_batch.add_message(ServiceBusMessage("First batch foo message"))
                message_batch.add_message(ServiceBusMessage("Second batch foo message"))
                await sender.send_messages(message_batch)

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
            async with client.get_subscription_receiver(topic_name, subscription_name) as receiver:
                received_msgs = await receiver.receive_messages(max_message_count=3, max_wait_time=10)
                for msg in received_msgs:
                    assert "foo" in str(msg)
                    await receiver.complete_message(msg)

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
