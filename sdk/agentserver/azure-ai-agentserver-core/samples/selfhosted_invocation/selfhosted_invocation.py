"""Self-hosted invocation agent with tracing using only the core package (Tier 3).

Demonstrates implementing the invocations protocol directly by subclassing
``AgentServerHost`` — without the invocations protocol package.  You handle
invocation ID tracking, session resolution, tracing spans, and response
headers yourself.

This pattern is useful when:

- You need a custom protocol not provided by the SDK
- You want full control over endpoint routing, tracing, and request handling
- You're learning how the protocol packages work internally

Usage::

    pip install azure-ai-agentserver-core

    # Enable tracing via App Insights connection string
    export APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=..."

    python selfhosted_invocation.py

    # Invoke the agent
    curl -X POST http://localhost:8088/invocations -H "Content-Type: application/json" -d '{"name": "Alice"}'
    # -> {"greeting": "Hello, Alice!"}

    # Health check (provided by AgentServerHost)
    curl http://localhost:8088/readiness
    # -> {"status": "healthy"}
"""
import logging
import os
import uuid
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from azure.ai.agentserver.core import AgentServerHost, record_error

logger = logging.getLogger("azure.ai.agentserver")


class SelfHostedInvocationHost(AgentServerHost):
    """Custom invocation host that implements the protocol directly."""

    def __init__(self, **kwargs: Any) -> None:
        custom_routes = [
            Route("/invocations", self._invoke, methods=["POST"]),
        ]
        existing = list(kwargs.pop("routes", None) or [])
        super().__init__(routes=existing + custom_routes, **kwargs)

    async def _invoke(self, request: Request) -> Response:
        """POST /invocations — handle an invocation request with tracing."""
        invocation_id = request.headers.get("x-agent-invocation-id") or str(uuid.uuid4())
        session_id = (
            request.query_params.get("agent_session_id")
            or os.environ.get("FOUNDRY_AGENT_SESSION_ID")
            or str(uuid.uuid4())
        )

        with self.request_span(
            request.headers, invocation_id, "invoke_agent",
            operation_name="invoke_agent", session_id=session_id,
        ) as otel_span:
            logger.info("Processing invocation %s in session %s", invocation_id, session_id)

            try:
                data = await request.json()
                name = data.get("name", "World")
                result = {"greeting": f"Hello, {name}!"}
            except Exception as exc:
                record_error(otel_span, exc)
                logger.error("Invocation %s failed: %s", invocation_id, exc)
                raise

            return JSONResponse(
                result,
                headers={
                    "x-agent-invocation-id": invocation_id,
                    "x-agent-session-id": session_id,
                },
            )


if __name__ == "__main__":
    app = SelfHostedInvocationHost()
    app.run()
