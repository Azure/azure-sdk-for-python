# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the distributed tracing policy."""
import requests

import pytest

from azure.core.pipeline import (
    PipelineResponse,
    PipelineRequest,
    PipelineContext
)
from azure.core.pipeline.transport import (
    HttpRequest,
    HttpResponse,
)
from azure.core.pipeline.transport import RequestsTransportResponse
from azure.core.pipeline.policies.universal import UserAgentPolicy
from azure.core.pipeline.policies.distributed_tracing import DistributedTracingPolicy
from tracing_common import ContextHelper, MockExporter
from opencensus.trace import tracer as tracer_module
from opencensus.trace.samplers import AlwaysOnSampler


def test_distributed_tracing_policy_solo():
    with ContextHelper():
        exporter = MockExporter()
        trace = tracer_module.Tracer(sampler=AlwaysOnSampler(), exporter=exporter)
        policy = DistributedTracingPolicy()

        request = HttpRequest('GET', 'http://127.0.0.1/')
        policy.on_request(PipelineRequest(request, PipelineContext(None)))

        trace.finish()
        exporter.build_tree()
        parent = exporter.root
        network_span = parent.children[0]
        assert network_span.span_data.name == "span - http call"
        # assert request.headers["user-agent"].endswith("mytools")
