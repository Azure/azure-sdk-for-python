import pytest
from opentelemetry import context as otel_context
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


@pytest.mark.asyncio
async def test_streaming_context_restore_uses_previous_context() -> None:
    prev_ctx = otel_context.get_current()
    ctx = TraceContextTextMapPropagator().extract(carrier={})

    otel_context.attach(ctx)
    otel_context.attach(prev_ctx)

    assert otel_context.get_current() is prev_ctx
