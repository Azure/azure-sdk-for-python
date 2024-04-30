# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

import pytest


class TracingTestHelper:
    def __init__(self, tracer, exporter):
        self.tracer = tracer
        self.exporter = exporter


@pytest.fixture(scope="session", autouse=True)
def enable_tracing():
    provider = TracerProvider()
    trace.set_tracer_provider(provider)


@pytest.fixture(scope="function")
def tracing_helper() -> TracingTestHelper:
    span_exporter = InMemorySpanExporter()
    processor = SimpleSpanProcessor(span_exporter)
    trace.get_tracer_provider().add_span_processor(processor)
    return TracingTestHelper(trace.get_tracer(__name__), span_exporter)


@pytest.fixture(scope="session")
def config():
    return {
        "storage_account_name": os.environ.get("AZURE_STORAGE_ACCOUNT_NAME"),
        "storage_account_key": os.environ.get("AZURE_STORAGE_ACCOUNT_KEY"),
        "storage_connection_string": os.environ.get("AZURE_STORAGE_CONNECTION_STRING"),
        "servicebus_connection_string": os.environ.get("AZURE_SERVICEBUS_CONNECTION_STRING"),
        "servicebus_queue_name": os.environ.get("AZURE_SERVICEBUS_QUEUE_NAME"),
        "servicebus_topic_name": os.environ.get("AZURE_SERVICEBUS_TOPIC_NAME"),
        "servicebus_subscription_name": os.environ.get("AZURE_SERVICEBUS_SUBSCRIPTION_NAME"),
        "eventhub_connection_string": os.environ.get("AZURE_EVENTHUB_CONNECTION_STRING"),
        "eventhub_name": os.environ.get("AZURE_EVENTHUB_NAME"),
    }
