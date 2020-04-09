import time
import threading
import logging
import pytest
from opencensus.trace.tracer import Tracer
from opencensus.trace.samplers import AlwaysOnSampler

from azure.core.settings import settings
from azure.core.tracing.ext.opencensus_span import OpenCensusSpan

settings.tracing_implementation = OpenCensusSpan

from azure.eventhub import EventData
from azure.eventhub import EventHubProducerClient, EventHubConsumerClient

logging.basicConfig(level=logging.INFO)


@pytest.mark.liveTest
def test_open_sensus_async(connection_str):
    consumer_tracer = Tracer(sampler=AlwaysOnSampler())
    with consumer_tracer.span(name="eventhub consumer tracer"):
        def on_event_batch(partition_context, events):
            print(events)

        consumer_client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group="$Default")
        with consumer_client:
            thread = threading.Thread(
                target=consumer_client.receive,
                args=(on_event_batch,),
                kwargs={"partition_id": "0"}
            )
            thread.start()
            producer_tracer = Tracer(sampler=AlwaysOnSampler())
            with producer_tracer.span(name="event hub producer tracer"):
                producer_client = EventHubProducerClient.from_connection_string(connection_str)
                with producer_client:
                    batch = producer_client.create_batch(partition_id="0")
                    batch.add(EventData("Test Event1"))
                    batch.add(EventData("Test Event2"))
                    batch.add(EventData("Test Event3"))
                    producer_client.send_batch(batch)
            time.sleep(10)
            assert len(consumer_tracer.tracer._spans_list[0].links) == 3
        thread.join()
