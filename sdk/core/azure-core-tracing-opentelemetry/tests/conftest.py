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


span_exporter = InMemorySpanExporter()


@pytest.fixture(scope="session")
def tracer():
    processor = SimpleSpanProcessor(span_exporter)
    provider = TracerProvider()
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    return provider.get_tracer(__name__)


@pytest.fixture(scope="function")
def exporter():
    span_exporter.clear()
    return span_exporter


@pytest.fixture(scope="session")
def config():
    return {
        "storage_account_name": os.environ["AZURE_STORAGE_ACCOUNT_NAME"],
        "storage_account_key": os.environ["AZURE_STORAGE_ACCOUNT_KEY"],
        "storage_connection_string": os.environ["AZURE_STORAGE_CONNECTION_STRING"],
    }
