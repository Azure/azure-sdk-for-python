# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
from typing import Generator

import pytest
from azure.core.settings import settings
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from devtools_testutils.sanitizers import (
    add_remove_header_sanitizer,
    add_general_regex_sanitizer,
    add_oauth_response_sanitizer,
)

collect_ignore = []


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    add_remove_header_sanitizer(headers="aeg-sas-key")
    add_remove_header_sanitizer(headers="aeg-sas-token")
    add_remove_header_sanitizer(headers="ServiceBusSupplementaryAuthorization")
    add_remove_header_sanitizer(headers="ServiceBusDlqSupplementaryAuthorization")
    add_general_regex_sanitizer(value="fakeresource", regex="(?<=\\/\\/)[a-z-]+(?=\\.servicebus\\.windows\\.net)")
    add_oauth_response_sanitizer()


# Note: This is duplicated between here and the basic conftest, so that it does not throw warnings if you're
# running locally to this SDK. (Everything works properly, pytest just makes a bit of noise.)
def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line("markers", "liveTest: mark test to be a live test only")
    config.addinivalue_line("markers", "live_test_only: mark test to be a live test only")
    config.addinivalue_line("markers", "playback_test_only: mark test to be a playback test only")


class TracingTestHelper:
    def __init__(self, tracer, exporter):
        self.tracer = tracer
        self.exporter = exporter


@pytest.fixture(scope="session", autouse=True)
def enable_otel_tracing():
    provider = TracerProvider()
    trace.set_tracer_provider(provider)


@pytest.fixture(scope="function")
def tracing_helper() -> Generator[TracingTestHelper, None, None]:
    settings.tracing_enabled = True
    settings.tracing_implementation = None
    span_exporter = InMemorySpanExporter()
    processor = SimpleSpanProcessor(span_exporter)
    trace.get_tracer_provider().add_span_processor(processor)
    yield TracingTestHelper(trace.get_tracer(__name__), span_exporter)
    settings.tracing_enabled = None


@pytest.fixture(scope="session")
def config():
    return {
        "servicebus_connection_string": os.environ.get("SERVICEBUS_CONNECTION_STR"),
        "servicebus_queue_name": os.environ.get("SERVICEBUS_QUEUE_NAME"),
        "servicebus_topic_name": os.environ.get("SERVICEBUS_TOPIC_NAME"),
        "servicebus_subscription_name": os.environ.get("SERVICEBUS_SUBSCRIPTION_NAME"),
    }
