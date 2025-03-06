# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""The tests for decorators_async.py"""

try:
    from unittest import mock
except ImportError:
    import mock

import time

import pytest
from azure.core.pipeline import Pipeline, PipelineResponse
from azure.core.pipeline.policies import HTTPPolicy
from azure.core.pipeline.transport import HttpTransport
from azure.core.settings import settings
from azure.core.tracing import SpanKind
from azure.core.tracing.decorator_async import distributed_trace_async
from opentelemetry.trace import StatusCode as OtelStatusCode

from tracing_common import FakeSpan
from utils import HTTP_REQUESTS


class MockClient:

    _instrumentation_config = {
        "library_name": "my-library",
        "library_version": "1.0.0",
        "schema_url": "https://test.schema",
        "attributes": {"az.namespace": "Sample.Namespace"},
    }

    def __init__(self, http_request, policies=None, assert_current_span=False):
        time.sleep(0.001)
        self.request = http_request("GET", "http://localhost")
        if policies is None:
            policies = []
        policies.append(mock.Mock(spec=HTTPPolicy, send=self.verify_request))
        self.policies = policies
        self.transport = mock.Mock(spec=HttpTransport)
        self.pipeline = Pipeline(self.transport, policies=policies)

        self.expected_response = mock.Mock(spec=PipelineResponse)
        self.assert_current_span = assert_current_span

    def verify_request(self, request):
        if self.assert_current_span:
            assert execution_context.get_current_span() is not None
        return self.expected_response

    @distributed_trace_async
    async def make_request(self, numb_times, **kwargs):
        time.sleep(0.001)
        if numb_times < 1:
            return None
        response = self.pipeline.run(self.request, **kwargs)
        await self.get_foo(merge_span=True)
        kwargs["merge_span"] = True
        await self.make_request(numb_times - 1, **kwargs)
        return response

    @distributed_trace_async
    async def merge_span_method(self):
        return await self.get_foo(merge_span=True)

    @distributed_trace_async
    async def no_merge_span_method(self):
        return await self.get_foo()

    @distributed_trace_async
    async def get_foo(self):
        time.sleep(0.001)
        return 5

    @distributed_trace_async(name_of_span="different name")
    async def check_name_is_different(self):
        time.sleep(0.001)

    @distributed_trace_async(tracing_attributes={"foo": "bar"})
    async def tracing_attr(self, **kwargs):
        time.sleep(0.001)

    @distributed_trace_async(kind=SpanKind.PRODUCER)
    async def kind_override(self):
        time.sleep(0.001)

    @distributed_trace_async
    async def raising_exception(self, **kwargs):
        raise ValueError("Something went horribly wrong here")

    @distributed_trace_async
    async def method_with_custom_instrumentation(self):
        time.sleep(0.001)

    @distributed_trace_async
    async def method_with_kwargs(self, **kwargs):
        time.sleep(0.001)

    @distributed_trace_async
    async def nested_calls(self):
        time.sleep(0.001)
        await self.get_foo()
        await self.method_with_kwargs()


class TestAsyncDecorator(object):
    @pytest.mark.asyncio
    @pytest.mark.parametrize("http_request", HTTP_REQUESTS)
    async def test_decorator_tracing_attr(self, tracing_implementation, http_request):
        with FakeSpan(name="parent") as parent:
            client = MockClient(http_request)
            await client.tracing_attr()

        assert len(parent.children) == 1
        assert parent.children[0].name == "MockClient.tracing_attr"
        assert parent.children[0].kind == SpanKind.INTERNAL
        assert parent.children[0].attributes == {"foo": "bar"}

    @pytest.mark.asyncio
    @pytest.mark.parametrize("http_request", HTTP_REQUESTS)
    async def test_decorator_tracing_attr_custom(self, tracing_implementation, http_request):
        with FakeSpan(name="parent") as parent:
            client = MockClient(http_request)
            await client.tracing_attr(tracing_attributes={"biz": "baz"})

        assert len(parent.children) == 1
        assert parent.children[0].name == "MockClient.tracing_attr"
        assert parent.children[0].kind == SpanKind.INTERNAL
        assert parent.children[0].attributes == {"biz": "baz"}

    @pytest.mark.asyncio
    @pytest.mark.parametrize("http_request", HTTP_REQUESTS)
    async def test_decorator_has_different_name(self, tracing_implementation, http_request):
        with FakeSpan(name="parent") as parent:
            client = MockClient(http_request)
            await client.check_name_is_different()
        assert len(parent.children) == 1
        assert parent.children[0].name == "different name"
        assert parent.children[0].kind == SpanKind.INTERNAL

    @pytest.mark.asyncio
    @pytest.mark.parametrize("http_request", HTTP_REQUESTS)
    async def test_kind_override(self, tracing_implementation, http_request):
        with FakeSpan(name="parent") as parent:
            client = MockClient(http_request)
            await client.kind_override()

        assert len(parent.children) == 1
        assert parent.children[0].name == "MockClient.kind_override"
        assert parent.children[0].kind == SpanKind.PRODUCER

    @pytest.mark.asyncio
    @pytest.mark.parametrize("http_request", HTTP_REQUESTS)
    async def test_used(self, tracing_implementation, http_request):
        with FakeSpan(name="parent") as parent:
            client = MockClient(http_request, policies=[])
            await client.get_foo(parent_span=parent)
            await client.get_foo()

            assert len(parent.children) == 2

            assert parent.children[0].name == "MockClient.get_foo"
            assert not parent.children[0].children
            assert parent.children[1].name == "MockClient.get_foo"
            assert not parent.children[1].children

    @pytest.mark.asyncio
    @pytest.mark.parametrize("http_request", HTTP_REQUESTS)
    async def test_span_merge_span(self, tracing_implementation, http_request):
        with FakeSpan(name="parent") as parent:
            client = MockClient(http_request)
            await client.merge_span_method()
            await client.no_merge_span_method()

        assert len(parent.children) == 2
        assert parent.children[0].name == "MockClient.merge_span_method"
        assert not parent.children[0].children
        assert parent.children[1].name == "MockClient.no_merge_span_method"
        assert parent.children[1].children[0].name == "MockClient.get_foo"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("http_request", HTTP_REQUESTS)
    async def test_span_complicated(self, tracing_implementation, http_request):
        with FakeSpan(name="parent") as parent:
            client = MockClient(http_request)
            await client.make_request(2)
            with parent.span("child") as child:
                time.sleep(0.001)
                await client.make_request(2, parent_span=parent)
                assert FakeSpan.get_current_span() == child
                await client.make_request(2)

        assert len(parent.children) == 3
        assert parent.children[0].name == "MockClient.make_request"
        assert not parent.children[0].children
        assert parent.children[1].name == "child"
        assert parent.children[1].children[0].name == "MockClient.make_request"
        assert parent.children[2].name == "MockClient.make_request"
        assert not parent.children[2].children

    @pytest.mark.asyncio
    @pytest.mark.parametrize("http_request", HTTP_REQUESTS)
    async def test_span_with_exception(self, tracing_implementation, http_request):
        """Assert that if an exception is raised, the next sibling method is actually a sibling span."""
        with FakeSpan(name="parent") as parent:
            client = MockClient(http_request)
            try:
                await client.raising_exception()
            except:
                pass
            await client.get_foo()

        assert len(parent.children) == 2
        assert parent.children[0].name == "MockClient.raising_exception"
        # Exception should propagate status.
        assert parent.children[0].status == "Something went horribly wrong here"
        assert parent.children[1].name == "MockClient.get_foo"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("http_request", HTTP_REQUESTS)
    async def test_decorated_method_with_tracing_options(self, tracing_implementation, http_request):
        """Test that a decorated method can respect tracing options."""
        with FakeSpan(name="parent") as parent:
            client = MockClient(http_request)
            await client.method_with_kwargs(
                tracing_options={"enabled": True, "attributes": {"custom_key": "custom_value"}}
            )

        assert len(parent.children) == 1
        assert parent.children[0].name == "MockClient.method_with_kwargs"
        assert parent.children[0].attributes.get("custom_key") == "custom_value"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("http_request", HTTP_REQUESTS)
    async def test_decorated_method_with_tracing_disabled(self, tracing_implementation, http_request):
        """Test that a decorated method isn't traced if tracing is disabled on a per-operation basis."""
        with FakeSpan(name="parent") as parent:
            client = MockClient(http_request)
            await client.method_with_kwargs(tracing_options={"enabled": False})

        assert len(parent.children) == 0


class TestAsyncDecoratorNativeTracing:

    @pytest.mark.asyncio
    @pytest.mark.parametrize("http_request", HTTP_REQUESTS)
    async def test_decorator_raise_exception(self, tracing_helper, http_request):
        """Test that an exception is recorded as an error event."""
        client = MockClient(http_request)
        with tracing_helper.tracer.start_as_current_span("Root"):
            try:
                await client.raising_exception()
            except ValueError:
                pass
            await client.get_foo()

            finished_spans = tracing_helper.exporter.get_finished_spans()
            assert len(finished_spans) == 2
            assert finished_spans[0].name == "MockClient.raising_exception"
            assert finished_spans[0].status.status_code == OtelStatusCode.ERROR
            assert "Something went horribly wrong here" in finished_spans[0].status.description
            assert finished_spans[0].attributes.get("error.type") == "ValueError"

            assert finished_spans[1].name == "MockClient.get_foo"
            assert finished_spans[1].status.status_code == OtelStatusCode.UNSET

    @pytest.mark.asyncio
    @pytest.mark.parametrize("http_request", HTTP_REQUESTS)
    async def test_decorator_nested_calls(self, tracing_helper, http_request):
        """Test that only a span corresponding to the outermost method is created."""
        client = MockClient(http_request)
        with tracing_helper.tracer.start_as_current_span("Root"):
            await client.nested_calls()

            finished_spans = tracing_helper.exporter.get_finished_spans()
            assert len(finished_spans) == 1
            assert finished_spans[0].name == "MockClient.nested_calls"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("http_request", HTTP_REQUESTS)
    async def test_decorator_custom_instrumentation(self, tracing_helper, http_request):
        """Test that a custom tracer provider can be used."""
        client = MockClient(http_request)
        with tracing_helper.tracer.start_as_current_span("Root"):
            await client.method_with_custom_instrumentation()

            finished_spans = tracing_helper.exporter.get_finished_spans()
            assert len(finished_spans) == 1
            assert finished_spans[0].name == "MockClient.method_with_custom_instrumentation"
            assert finished_spans[0].instrumentation_scope.schema_url == "https://test.schema"
            assert finished_spans[0].instrumentation_scope.name == "my-library"
            assert finished_spans[0].instrumentation_scope.version == "1.0.0"
            assert finished_spans[0].instrumentation_scope.attributes.get("az.namespace") == "Sample.Namespace"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("http_request", HTTP_REQUESTS)
    async def test_decorated_method_with_tracing_options(self, tracing_helper, http_request):
        """Test that a decorated method can respect tracing options."""
        client = MockClient(http_request)
        settings.tracing_enabled = False
        with tracing_helper.tracer.start_as_current_span("Root"):
            await client.method_with_kwargs(
                tracing_options={"enabled": True, "attributes": {"custom_key": "custom_value"}}
            )

            finished_spans = tracing_helper.exporter.get_finished_spans()
            assert len(finished_spans) == 1
            assert finished_spans[0].name == "MockClient.method_with_kwargs"
            assert finished_spans[0].attributes.get("custom_key") == "custom_value"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("http_request", HTTP_REQUESTS)
    async def test_decorated_method_with_tracing_disabled(self, tracing_helper, http_request):
        """Test that a decorated method isn't traced if tracing is disabled on a per-operation basis."""
        client = MockClient(http_request)
        with tracing_helper.tracer.start_as_current_span("Root"):
            await client.method_with_kwargs(
                tracing_options={"enabled": False, "attributes": {"custom_key": "custom_value"}}
            )

            finished_spans = tracing_helper.exporter.get_finished_spans()
            assert len(finished_spans) == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize("http_request", HTTP_REQUESTS)
    async def test_decorated_method_with_tracing_disabled_globally(self, tracing_helper, http_request):
        """Test that a decorated method isn't traced if tracing is disabled globally."""
        client = MockClient(http_request)
        settings.tracing_enabled = False
        with tracing_helper.tracer.start_as_current_span("Root"):
            await client.method_with_kwargs()

            finished_spans = tracing_helper.exporter.get_finished_spans()
            assert len(finished_spans) == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize("http_request", HTTP_REQUESTS)
    async def test_tracing_impl_takes_precedence(self, tracing_implementation, http_request):
        """Test that a tracing implementation takes precedence over the native tracing."""
        client = MockClient(http_request)

        assert settings.tracing_implementation() is FakeSpan
        assert settings.tracing_enabled

        with FakeSpan(name="parent") as parent:
            await client.get_foo()
            assert len(parent.children) == 1
            assert parent.children[0].name == "MockClient.get_foo"
            assert parent.children[0].kind == SpanKind.INTERNAL
