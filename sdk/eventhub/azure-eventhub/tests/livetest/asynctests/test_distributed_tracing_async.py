import asyncio
import logging
import pytest
from opencensus.trace.tracer import Tracer
from opencensus.trace.samplers import AlwaysOnSampler

from azure.core.settings import settings
from azure.core.tracing.ext.opencensus_span import OpenCensusSpan

settings.tracing_implementation = OpenCensusSpan

from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient, EventHubConsumerClient

logging.basicConfig(level=logging.INFO)


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_open_sensus_async(connection_str):
    consumer_tracer = Tracer(sampler=AlwaysOnSampler())
    with consumer_tracer.span(name="eventhub consumer tracer"):
        async def on_event_batch(partition_context, events):
            print(events)

        consumer_client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group="$Default")
        async with consumer_client:
            task = asyncio.create_task(
                consumer_client.receive(
                    on_event_batch,
                    partition_id="0"
                ),
            )
            producer_tracer = Tracer(sampler=AlwaysOnSampler())
            with producer_tracer.span(name="event hub producer tracer"):
                producer_client = EventHubProducerClient.from_connection_string(connection_str)
                async with producer_client:
                    batch = await producer_client.create_batch(partition_id="0")
                    batch.add(EventData("Test Event1"))
                    batch.add(EventData("Test Event2"))
                    batch.add(EventData("Test Event3"))
                    await producer_client.send_batch(batch)
            await asyncio.sleep(10)
            assert len(consumer_tracer.tracer._spans_list[0].links) == 3
        task.cancel()
