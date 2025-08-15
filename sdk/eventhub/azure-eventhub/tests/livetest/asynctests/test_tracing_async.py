# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import datetime
import sys
import asyncio

import pytest
from azure.core.tracing.common import with_current_context
from azure.eventhub import EventData
from azure.eventhub.aio import EventHubConsumerClient, EventHubProducerClient

from tracing_common import  EventHubsTracingTestBase


class TestEventHubsTracingAsync(EventHubsTracingTestBase):

    @pytest.mark.asyncio
    @pytest.mark.live_test_only
    @pytest.mark.skipif(sys.platform.startswith("darwin"), reason="threading issues on mac CI")
    async def test_eventhubs_client_tracing(self, test_resources_config, tracing_helper):

        connection_string = test_resources_config["eventhub_connection_string"]
        eventhub_name = test_resources_config["eventhub_name"]

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

            async with producer_client:

                # Send batch of events
                event_data_batch = await producer_client.create_batch()
                event_data_batch.add(EventData("First message inside an EventDataBatch"))
                event_data_batch.add(EventData("Second message inside an EventDataBatch"))
                await producer_client.send_batch(event_data_batch)

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

            async def on_event_batch(partition_context, event_batch):
                pass

            async with consumer_client:
                # Receive batch of events.
                task = asyncio.ensure_future(
                    consumer_client.receive_batch(on_event_batch, starting_position=current_date)
                )
                await asyncio.sleep(3)
            task.cancel()

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
