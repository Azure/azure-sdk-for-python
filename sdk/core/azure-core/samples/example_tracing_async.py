"""
FILE: example_async_tracing.py
DESCRIPTION:
    This sample demonstrates how to trace an async client method.

    NOTE: The following example is for library developers to demonstrate how to customize tracing for their library.
    End users should be using OpenTelemetry directly for their tracing needs.

    This sample requires the opentelemetry-sdk library to be installed.
USAGE:
    python example_tracing_async.py
"""

import asyncio
from typing import Iterable, Union, Any

from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core import AsyncPipelineClient
from azure.core.rest import HttpRequest, AsyncHttpResponse
from azure.core.pipeline.policies import (
    AsyncHTTPPolicy,
    SansIOHTTPPolicy,
    HeadersPolicy,
    UserAgentPolicy,
    AsyncRetryPolicy,
    DistributedTracingPolicy,
)


class SampleAsyncClient:
    """Sample async client to demonstrate how an SDK developer would add tracing to their client."""

    _instrumentation_config = {
        "library_name": "my-library",
        "library_version": "1.0.0",
        "attributes": {"az.namespace": "Sample.Namespace"},
    }

    def __init__(self, endpoint: str) -> None:
        policies: Iterable[Union[AsyncHTTPPolicy, SansIOHTTPPolicy]] = [
            HeadersPolicy(),
            UserAgentPolicy("myuseragent"),
            AsyncRetryPolicy(),
            DistributedTracingPolicy(instrumentation_config=self._instrumentation_config),
        ]

        self._client: AsyncPipelineClient[HttpRequest, AsyncHttpResponse] = AsyncPipelineClient(
            endpoint, policies=policies
        )

    @distributed_trace_async
    async def sample_method(self, **kwargs: Any) -> AsyncHttpResponse:
        request = HttpRequest("GET", "https://paulvaneck.com")
        response = await self._client.send_request(request, **kwargs)
        return response

    async def close(self) -> None:
        await self._client.close()

    async def __aenter__(self) -> "SampleAsyncClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *exc_details: Any) -> None:
        await self._client.__aexit__(*exc_details)


async def sample_user():
    """Sample showing how an end user would enable tracing and configure OpenTelemetry."""
    from azure.core.settings import settings

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
    async with SampleAsyncClient(endpoint) as client:
        with tracer.start_as_current_span(name="MyApplication"):  # type: ignore
            response = await client.sample_method(tracing_options={"attributes": {"custom_key": "custom_value"}})
            print(f"Response: {response}")


if __name__ == "__main__":
    asyncio.run(sample_user())
