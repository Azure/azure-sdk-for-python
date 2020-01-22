# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""The tests for decorators.py and common.py"""

try:
    from unittest import mock
except ImportError:
    import mock

import sys
import time

import pytest
from azure.core.pipeline import Pipeline, PipelineResponse
from azure.core.pipeline.policies import HTTPPolicy
from azure.core.pipeline.transport import HttpTransport, HttpRequest
from azure.core.settings import settings
from azure.core.tracing import common
from azure.core.tracing.decorator import distributed_trace
from tracing_common import FakeSpan


@pytest.fixture(scope="module")
def fake_span():
    settings.tracing_implementation.set_value(FakeSpan)


class MockClient:
    @distributed_trace
    def __init__(self, policies=None, assert_current_span=False):
        time.sleep(0.001)
        self.request = HttpRequest("GET", "https://bing.com")
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

    @distributed_trace
    def make_request(self, numb_times, **kwargs):
        time.sleep(0.001)
        if numb_times < 1:
            return None
        response = self.pipeline.run(self.request, **kwargs)
        self.get_foo(merge_span=True)
        kwargs['merge_span'] = True
        self.make_request(numb_times - 1, **kwargs)
        return response

    @distributed_trace
    def merge_span_method(self):
        return self.get_foo(merge_span=True)

    @distributed_trace
    def no_merge_span_method(self):
        return self.get_foo()

    @distributed_trace
    def get_foo(self):
        time.sleep(0.001)
        return 5

    @distributed_trace(name_of_span="different name")
    def check_name_is_different(self):
        time.sleep(0.001)

    @distributed_trace(tracing_attributes={'foo': 'bar'})
    def tracing_attr(self):
        time.sleep(0.001)

    @distributed_trace
    def raising_exception(self):
        raise ValueError("Something went horribly wrong here")


def random_function():
    pass


def test_get_function_and_class_name():
    client = MockClient()
    assert common.get_function_and_class_name(client.get_foo, client) == "MockClient.get_foo"
    assert common.get_function_and_class_name(random_function) == "random_function"


@pytest.mark.usefixtures("fake_span")
class TestDecorator(object):

    def test_decorator_tracing_attr(self):
        with FakeSpan(name="parent") as parent:
            client = MockClient()
            client.tracing_attr()

        assert len(parent.children) == 2
        assert parent.children[0].name == "MockClient.__init__"
        assert parent.children[1].name == "MockClient.tracing_attr"
        assert parent.children[1].attributes == {'foo': 'bar'}

    def test_decorator_has_different_name(self):
        with FakeSpan(name="parent") as parent:
            client = MockClient()
            client.check_name_is_different()

        assert len(parent.children) == 2
        assert parent.children[0].name == "MockClient.__init__"
        assert parent.children[1].name == "different name"

    def test_used(self):
        with FakeSpan(name="parent") as parent:
            client = MockClient(policies=[])
            client.get_foo(parent_span=parent)
            client.get_foo()

        assert len(parent.children) == 3
        assert parent.children[0].name == "MockClient.__init__"
        assert not parent.children[0].children
        assert parent.children[1].name == "MockClient.get_foo"
        assert not parent.children[1].children
        assert parent.children[2].name == "MockClient.get_foo"
        assert not parent.children[2].children

    def test_span_merge_span(self):
        with FakeSpan(name="parent") as parent:
            client = MockClient()
            client.merge_span_method()
            client.no_merge_span_method()

        assert len(parent.children) == 3
        assert parent.children[0].name == "MockClient.__init__"
        assert not parent.children[0].children
        assert parent.children[1].name == "MockClient.merge_span_method"
        assert not parent.children[1].children
        assert parent.children[2].name == "MockClient.no_merge_span_method"
        assert parent.children[2].children[0].name == "MockClient.get_foo"

    def test_span_complicated(self):
        with FakeSpan(name="parent") as parent:
            client = MockClient()
            client.make_request(2)
            with parent.span("child") as child:
                time.sleep(0.001)
                client.make_request(2, parent_span=parent)
                assert FakeSpan.get_current_span() == child
                client.make_request(2)

        assert len(parent.children) == 4
        assert parent.children[0].name == "MockClient.__init__"
        assert not parent.children[0].children
        assert parent.children[1].name == "MockClient.make_request"
        assert not parent.children[1].children
        assert parent.children[2].name == "child"
        assert parent.children[2].children[0].name == "MockClient.make_request"
        assert parent.children[3].name == "MockClient.make_request"
        assert not parent.children[3].children

    def test_span_with_exception(self):
        """Assert that if an exception is raised, the next sibling method is actually a sibling span.
        """
        with FakeSpan(name="parent") as parent:
            client = MockClient()
            try:
                client.raising_exception()
            except:
                pass
            client.get_foo()

        assert len(parent.children) == 3
        assert parent.children[0].name == "MockClient.__init__"
        assert parent.children[1].name == "MockClient.raising_exception"
        # Exception should propagate status for Opencensus
        assert parent.children[1].status == 'Something went horribly wrong here'
        assert parent.children[2].name == "MockClient.get_foo"
