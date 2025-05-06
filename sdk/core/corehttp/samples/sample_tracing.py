# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_tracing.py

DESCRIPTION:
    This sample demonstrates how to trace a client method.

    Note: This sample requires the opentelemetry-sdk library to be installed.

USAGE:
    python sample_tracing.py
"""
from typing import Iterable, Union, Any
from functools import partial

from corehttp.instrumentation import get_tracer
from corehttp.instrumentation.tracing import distributed_trace
from corehttp.runtime import PipelineClient
from corehttp.rest import HttpRequest, HttpResponse
from corehttp.runtime.policies import (
    HTTPPolicy,
    SansIOHTTPPolicy,
    HeadersPolicy,
    UserAgentPolicy,
    RetryPolicy,
    DistributedHttpTracingPolicy,
)


class SampleClient:
    """Sample client to demonstrate how an SDK developer would add tracing to their client."""

    _instrumentation_config = {
        "library_name": "my-library",
        "library_version": "1.0.0",
        "attributes": {"namespace": "Sample.Namespace"},
    }

    def __init__(self, endpoint: str) -> None:
        policies: Iterable[Union[HTTPPolicy, SansIOHTTPPolicy]] = [
            HeadersPolicy(),
            UserAgentPolicy("myuseragent"),
            RetryPolicy(),
            DistributedHttpTracingPolicy(instrumentation_config=self._instrumentation_config),
        ]

        self._client: PipelineClient[HttpRequest, HttpResponse] = PipelineClient(endpoint, policies=policies)

    @distributed_trace()
    def sample_method(self, **kwargs: Any) -> HttpResponse:
        request = HttpRequest("GET", "https://bing.com")
        response = self._client.send_request(request, **kwargs)
        return response

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "SampleClient":
        self._client.__enter__()
        return self

    def __exit__(self, *exc_details: Any) -> None:
        self._client.__exit__(*exc_details)


def sample_user():
    """Sample showing how an end user would enable tracing and configure OpenTelemetry."""
    from corehttp.settings import settings

    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import ConsoleSpanExporter
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor

    tracer_provider = TracerProvider()
    exporter = ConsoleSpanExporter()
    span_processor = SimpleSpanProcessor(exporter)

    tracer_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(tracer_provider)
    tracer = tracer_provider.get_tracer("my-application")

    settings.tracing_enabled = True

    endpoint = "https://bing.com"
    with SampleClient(endpoint) as client:
        with tracer.start_as_current_span(name="MyApplication"):  # type: ignore
            response = client.sample_method(tracing_options={"attributes": {"custom_key": "custom_value"}})
            print(f"Response: {response}")


if __name__ == "__main__":
    sample_user()
