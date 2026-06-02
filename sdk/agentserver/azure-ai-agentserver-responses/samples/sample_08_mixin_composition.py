# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 08 — Mixin Composition (multi-protocol).

Demonstrates running both the **Invocations** and **Responses** protocols
on a single server using Python's cooperative (mixin) inheritance.

Endpoints exposed:
    POST  /invocations               — Invocation protocol
    POST  /responses                  — Responses protocol
    GET   /readiness                  — Health probe (from core)

Usage::

    # Start the dual-protocol server
    python sample_08_mixin_composition.py

    # Hit the Invocation endpoint
    curl -X POST http://localhost:8088/invocations \
        -H "Content-Type: application/json" \
        -d '{"message": "Hello!"}'
    # -> {"invocation_id": "...", "status": "completed",
    #     "output": "[Invocation] Echo: Hello!"}

    # Hit the Responses endpoint
    curl -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "test", "input": "Hello!"}'
    # -> {"output": [{"type": "message", "content":
    #     [{"type": "output_text", "text": "[Response] Echo: Hello!"}]}]}
"""

import asyncio

from azure.ai.agentserver.invocations import InvocationAgentServerHost
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    TextResponse,
)


class MyHost(InvocationAgentServerHost, ResponsesAgentServerHost):
    pass


app = MyHost()


@app.invoke_handler
async def handle_invoke(request: Request) -> Response:
    """Echo invocation: returns the message from the JSON body."""
    data = await request.json()
    invocation_id = request.state.invocation_id
    message = data.get("message", "")
    return JSONResponse(
        {
            "invocation_id": invocation_id,
            "status": "completed",
            "output": f"[Invocation] Echo: {message}",
        }
    )


@app.response_handler
async def handle_response(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Echo response: returns the user's input text."""
    input_text = await context.get_input_text()
    return TextResponse(context, request, text=f"[Response] Echo: {input_text}")


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
