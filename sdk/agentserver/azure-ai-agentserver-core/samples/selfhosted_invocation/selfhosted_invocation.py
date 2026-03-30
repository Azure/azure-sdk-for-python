"""Self-hosted invocation agent with tracing using only the hosting package (Tier 3).

Demonstrates implementing the invocations protocol directly with
``AgentHost``, ``register_routes``, and ``TracingHelper`` — without
the invocations protocol package.  You handle invocation ID tracking,
session resolution, tracing spans, and response headers yourself.

This pattern is useful when:

- You need a custom protocol not provided by the SDK
- You want full control over endpoint routing, tracing, and request handling
- You're learning how the protocol packages work internally

Usage::

    pip install azure-ai-agentserver-core[tracing]

    # Enable tracing via App Insights connection string
    export APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=..."

    python selfhosted_invocation.py

    # Invoke the agent
    curl -X POST http://localhost:8088/invocations -H "Content-Type: application/json" -d '{"name": "Alice"}'
    # -> {"greeting": "Hello, Alice!"}

    # Health check (provided by AgentHost)
    curl http://localhost:8088/readiness
    # -> {"status": "healthy"}
"""
import contextlib
import os
import uuid
from typing import Optional

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from azure.ai.agentserver.core import AgentLogger, AgentHost, TracingHelper

logger = AgentLogger.get()

server = AgentHost()

# Access the tracing helper from the server (None if tracing is disabled)
tracing: Optional[TracingHelper] = server.tracing


async def invoke(request: Request) -> Response:
    """POST /invocations — handle an invocation request with tracing.

    Demonstrates using TracingHelper to create spans, set attributes,
    record errors, and propagate W3C trace context.
    """
    invocation_id = request.headers.get("x-agent-invocation-id") or str(uuid.uuid4())
    session_id = (
        request.query_params.get("agent_session_id")
        or os.environ.get("FOUNDRY_AGENT_SESSION_ID")
        or str(uuid.uuid4())
    )

    # Create a traced span that covers the entire request.
    # When tracing is disabled, request_span yields None and is a no-op.
    if tracing is not None:
        span_cm = tracing.request_span(
            headers=request.headers,
            invocation_id=invocation_id,
            span_operation="invoke_agent",
            operation_name="invoke_agent",
            session_id=session_id,
        )
    else:
        span_cm = contextlib.nullcontext(None)

    with span_cm as otel_span:
        logger.info("Processing invocation %s in session %s", invocation_id, session_id)

        try:
            data = await request.json()
            name = data.get("name", "World")
            result = {"greeting": f"Hello, {name}!"}
        except Exception as exc:
            # Record the error on the span if tracing is active
            if tracing is not None and otel_span is not None:
                tracing.record_error(otel_span, exc)
            logger.error("Invocation %s failed: %s", invocation_id, exc)
            raise

        return JSONResponse(
            result,
            headers={
                "x-agent-invocation-id": invocation_id,
                "x-agent-session-id": session_id,
            },
        )


server.register_routes([
    Route("/invocations", invoke, methods=["POST"]),
])

if __name__ == "__main__":
    server.run()
