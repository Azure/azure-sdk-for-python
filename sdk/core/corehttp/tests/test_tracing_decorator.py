# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Tests for the distributed_trace decorator."""
import time

from corehttp.settings import settings
from corehttp.instrumentation.tracing import distributed_trace

from opentelemetry.trace import StatusCode as OtelStatusCode


class MockClient:

    _instrumentation_config = {
        "library_name": "mylibrary",
        "library_version": "1.0.0",
        "schema_url": "https://test.schema",
        "attributes": {"namespace": "Sample.Namespace"},
    }

    @distributed_trace
    def nested_calls(self):
        time.sleep(0.001)
        self.get_foo()
        self.method_with_kwargs()

    @distributed_trace
    def get_foo(self):
        time.sleep(0.001)
        return 5

    @distributed_trace
    def raising_exception(self, **kwargs):
        raise ValueError("Something went horribly wrong here")

    @distributed_trace
    def method_with_kwargs(self, **kwargs):
        time.sleep(0.001)


def test_decorator_raise_exception(tracing_helper):
    """Test that an exception is recorded as an error event."""
    client = MockClient()
    with tracing_helper.tracer.start_as_current_span("Root"):
        try:
            client.raising_exception()
        except ValueError:
            pass
        client.get_foo()

        finished_spans = tracing_helper.exporter.get_finished_spans()
        assert len(finished_spans) == 2
        assert finished_spans[0].name == "MockClient.raising_exception"
        assert finished_spans[0].status.status_code == OtelStatusCode.ERROR
        assert "Something went horribly wrong here" in finished_spans[0].status.description
        assert finished_spans[0].attributes.get("error.type") == "ValueError"

        assert finished_spans[1].name == "MockClient.get_foo"
        assert finished_spans[1].status.status_code == OtelStatusCode.UNSET


def test_decorator_nested_calls(tracing_helper):
    """Test that only a span corresponding to the outermost method is created."""
    client = MockClient()
    with tracing_helper.tracer.start_as_current_span("Root"):
        client.nested_calls()

        finished_spans = tracing_helper.exporter.get_finished_spans()
        assert len(finished_spans) == 1
        assert finished_spans[0].name == "MockClient.nested_calls"


def test_decorator_instrumentation_config(tracing_helper):
    """Test that the instrumentation config is respected."""
    client = MockClient()
    with tracing_helper.tracer.start_as_current_span("Root"):
        client.get_foo()

        finished_spans = tracing_helper.exporter.get_finished_spans()
        assert len(finished_spans) == 1
        assert finished_spans[0].name == "MockClient.get_foo"
        assert finished_spans[0].instrumentation_scope.schema_url == "https://test.schema"
        assert finished_spans[0].instrumentation_scope.name == "mylibrary"
        assert finished_spans[0].instrumentation_scope.version == "1.0.0"
        assert finished_spans[0].instrumentation_scope.attributes.get("namespace") == "Sample.Namespace"


def test_decorated_method_with_tracing_options(tracing_helper):
    """Test that a decorated method can respect tracing options."""
    client = MockClient()
    settings.tracing_enabled = False
    with tracing_helper.tracer.start_as_current_span("Root"):
        client.method_with_kwargs(tracing_options={"enabled": True, "attributes": {"custom_key": "custom_value"}})

        finished_spans = tracing_helper.exporter.get_finished_spans()
        assert len(finished_spans) == 1
        assert finished_spans[0].name == "MockClient.method_with_kwargs"
        assert finished_spans[0].attributes.get("custom_key") == "custom_value"


def test_decorated_method_with_tracing_disabled(tracing_helper):
    """Test that a decorated method isn't traced if tracing is disabled on a per-operation basis."""
    client = MockClient()
    with tracing_helper.tracer.start_as_current_span("Root"):
        client.method_with_kwargs(tracing_options={"enabled": False, "attributes": {"custom_key": "custom_value"}})

        finished_spans = tracing_helper.exporter.get_finished_spans()
        assert len(finished_spans) == 0


def test_decorated_method_with_tracing_disabled_globally(tracing_helper):
    """Test that a decorated method isn't traced if tracing is disabled globally."""
    client = MockClient()
    settings.tracing_enabled = False
    with tracing_helper.tracer.start_as_current_span("Root"):
        client.method_with_kwargs()

        finished_spans = tracing_helper.exporter.get_finished_spans()
        assert len(finished_spans) == 0
