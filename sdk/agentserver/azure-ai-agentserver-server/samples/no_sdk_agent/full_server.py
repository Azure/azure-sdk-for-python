"""Full-featured agent — no SDK required.

Implements optional Invocation API features:
- Invocation ID tracking (x-agent-invocation-id header)
- Health probes (/liveness, /readiness)
- OpenTelemetry tracing with App Insights export

See SPEC.md for the full Invocation API contract.

Usage::

    pip install fastapi uvicorn opentelemetry-api opentelemetry-sdk \\
        azure-monitor-opentelemetry-exporter

    # Optional: set App Insights connection string for trace export
    export APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=..."
    export AGENT_ENABLE_TRACING=true
    export AGENT_NAME=my-agent
    export AGENT_VERSION=1.0

    python full_server.py

    curl -X POST http://localhost:8088/invocations -H "Content-Type: application/json" -d '{"name": "Alice"}'
    # -> {"greeting": "Hello, Alice!"}

    curl http://localhost:8088/liveness
    # -> {"status": "alive"}
"""
import logging
import os
import uuid
from contextlib import contextmanager
from typing import Any, Iterator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# ---------------------------------------------------------------------------
# Configuration from environment variables
# ---------------------------------------------------------------------------

LOG_LEVEL = os.environ.get("AGENT_LOG_LEVEL", "INFO").upper()
ENABLE_TRACING = os.environ.get("AGENT_ENABLE_TRACING", "").lower() in ("true", "1", "yes")
APPINSIGHTS_CONN_STR = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING", "")
AGENT_NAME = os.environ.get("AGENT_NAME", "")
AGENT_VERSION = os.environ.get("AGENT_VERSION", "")
AGENT_PROJECT_NAME = os.environ.get("AGENT_PROJECT_NAME", "")

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

INVOCATION_ID_HEADER = "x-agent-invocation-id"

app = FastAPI()


# ---------------------------------------------------------------------------
# OpenTelemetry tracing (optional)
# ---------------------------------------------------------------------------

_tracer: Any = None
_propagator: Any = None

if ENABLE_TRACING:
    try:
        from opentelemetry import trace
        from opentelemetry.trace.propagation.tracecontext import (
            TraceContextTextMapPropagator,
        )

        # Set up App Insights export if connection string is available
        if APPINSIGHTS_CONN_STR:
            try:
                from opentelemetry.sdk.resources import Resource
                from opentelemetry.sdk.trace import TracerProvider
                from opentelemetry.sdk.trace.export import BatchSpanProcessor
                from azure.monitor.opentelemetry.exporter import (
                    AzureMonitorTraceExporter,
                )

                resource = Resource.create({"service.name": "agent"})
                provider = TracerProvider(resource=resource)
                exporter = AzureMonitorTraceExporter(
                    connection_string=APPINSIGHTS_CONN_STR
                )
                provider.add_span_processor(BatchSpanProcessor(exporter))
                trace.set_tracer_provider(provider)
                logger.info("App Insights trace exporter configured")
            except ImportError:
                logger.warning(
                    "App Insights export requires opentelemetry-sdk and "
                    "azure-monitor-opentelemetry-exporter"
                )

        _tracer = trace.get_tracer("agent")
        _propagator = TraceContextTextMapPropagator()
        logger.info("OpenTelemetry tracing enabled")

    except ImportError:
        logger.warning(
            "AGENT_ENABLE_TRACING=true but opentelemetry-api is not installed"
        )


def _build_span_attrs(
    invocation_id: str,
    session_id: str = "",
    operation_name: str = "invoke_agent",
) -> dict[str, str]:
    """Build GenAI semantic convention span attributes."""
    agent_label = (
        f"{AGENT_NAME}:{AGENT_VERSION}" if AGENT_NAME and AGENT_VERSION else AGENT_NAME
    )
    attrs: dict[str, str] = {
        "invocation.id": invocation_id,
        "gen_ai.response.id": invocation_id,
        "gen_ai.provider.name": "microsoft.foundry",
        "gen_ai.operation.name": operation_name,
    }
    if agent_label:
        attrs["gen_ai.agent.id"] = agent_label
    if AGENT_PROJECT_NAME:
        attrs["microsoft.foundry.project.id"] = AGENT_PROJECT_NAME
    if session_id:
        attrs["gen_ai.conversation.id"] = session_id
    return attrs


def _parse_baggage_key(baggage_header: str, key: str) -> str:
    """Parse a single key from a W3C Baggage header.

    The baggage header is a comma-separated list of key=value pairs.
    See https://www.w3.org/TR/baggage/

    :param baggage_header: Raw baggage header value.
    :param key: Key to extract.
    :return: The value if found, or empty string.
    """
    for member in baggage_header.split(","):
        member = member.strip()
        if "=" not in member:
            continue
        k, _, v = member.partition("=")
        if k.strip() == key:
            # Value may have properties after ';' — take only the value part
            return v.split(";")[0].strip()
    return ""


def _override_parent_span_id(
    ctx: Any,
    leaf_span_id_hex: str,
) -> Any:
    """Re-parent the trace context using leaf_customer_span_id from baggage.

    Creates a new parent context with the same trace_id but the span_id
    replaced by *leaf_span_id_hex*.  This connects the agent's root span
    to the caller's leaf span so the trace tree renders correctly in
    App Insights.

    :param ctx: OpenTelemetry context with extracted traceparent.
    :param leaf_span_id_hex: 16-character lower-hex span ID from baggage.
    :return: New context with overridden parent span ID.
    """
    from opentelemetry.trace import (
        NonRecordingSpan,
        SpanContext,
        set_span_in_context,
    )

    # Get the current span from the context to extract trace_id and trace_flags
    current_span = trace.get_current_span(ctx) if ctx else None
    if current_span is None:
        return ctx

    current_ctx = current_span.get_span_context()
    if current_ctx is None or not current_ctx.is_valid:
        return ctx

    try:
        new_span_id = int(leaf_span_id_hex, 16)
    except ValueError:
        logger.warning("Invalid leaf_customer_span_id: %s", leaf_span_id_hex)
        return ctx

    # Build a new SpanContext with the overridden span_id
    new_span_context = SpanContext(
        trace_id=current_ctx.trace_id,
        span_id=new_span_id,
        is_remote=True,
        trace_flags=current_ctx.trace_flags,
        trace_state=current_ctx.trace_state,
    )
    return set_span_in_context(NonRecordingSpan(new_span_context), ctx)


_LEAF_CUSTOMER_SPAN_ID = "leaf_customer_span_id"


@contextmanager
def _request_span(
    request: Request,
    invocation_id: str,
    operation_name: str = "invoke_agent",
) -> Iterator[Any]:
    """Create a traced span for a request, propagating W3C context.

    Handles full W3C Trace Context propagation including the
    ``leaf_customer_span_id`` baggage key, which re-parents the agent's
    root span under the caller's leaf span for correct trace tree
    rendering in App Insights.

    Yields the OTel span or None if tracing is disabled.
    """
    if _tracer is None or _propagator is None:
        yield None
        return

    # Extract W3C trace context from incoming headers
    carrier = {
        k: v
        for k in ("traceparent", "tracestate")
        if (v := request.headers.get(k)) is not None
    }
    ctx = _propagator.extract(carrier=carrier) if carrier else None

    # Override parent span ID with leaf_customer_span_id from baggage
    # (see SPEC.md § leaf_customer_span_id)
    baggage = request.headers.get("baggage", "")
    if ctx is not None and baggage:
        leaf_span_id = _parse_baggage_key(baggage, _LEAF_CUSTOMER_SPAN_ID)
        if leaf_span_id:
            ctx = _override_parent_span_id(ctx, leaf_span_id)

    session_id = request.query_params.get("agent_session_id", "")
    attrs = _build_span_attrs(invocation_id, session_id, operation_name)

    agent_label = (
        f"{AGENT_NAME}:{AGENT_VERSION}" if AGENT_NAME and AGENT_VERSION else AGENT_NAME
    )
    span_name = f"execute_agent {agent_label}" if agent_label else "execute_agent"

    with _tracer.start_as_current_span(
        name=span_name,
        attributes=attrs,
        kind=trace.SpanKind.SERVER,
        context=ctx,
    ) as otel_span:
        yield otel_span


def _record_error(span: Any, exc: Exception) -> None:
    """Record an exception on a span if tracing is active."""
    if span is not None and ENABLE_TRACING:
        try:
            span.set_status(trace.StatusCode.ERROR, str(exc))
            span.record_exception(exc)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Health probes
# ---------------------------------------------------------------------------


@app.get("/liveness")
async def liveness():
    """liveness probe."""
    return {"status": "alive"}


@app.get("/readiness")
async def readiness():
    """readiness probe."""
    return {"status": "ready"}


# ---------------------------------------------------------------------------
# Agent logic — replace this with your own
# ---------------------------------------------------------------------------


async def run_agent(data: dict) -> dict:
    """Your agent logic goes here.

    :param data: Parsed JSON request body.
    :return: Response dict to serialize as JSON.
    """
    greeting = f"Hello, {data.get('name', 'World')}!"
    return {"greeting": greeting}


# ---------------------------------------------------------------------------
# POST /invocations — required
# ---------------------------------------------------------------------------


@app.post("/invocations")
async def invoke(request: Request):
    """Execute the agent."""
    invocation_id = (
        request.headers.get(INVOCATION_ID_HEADER) or str(uuid.uuid4())
    )

    data = await request.json()

    with _request_span(request, invocation_id) as span:
        try:
            result = await run_agent(data)
        except Exception as exc:
            _record_error(span, exc)
            raise

    return JSONResponse(
        result,
        headers={INVOCATION_ID_HEADER: invocation_id},
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("AGENT_SERVER_PORT", "8088"))
    uvicorn.run(app, host="0.0.0.0", port=port)
