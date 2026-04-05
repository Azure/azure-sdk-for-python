# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Multi-protocol sample: Invocations + Responses on a single AgentHost.

Demonstrates how both protocol handlers can coexist on the same server,
sharing health probes, tracing, graceful shutdown, and the Hypercorn host.

Endpoints:
    POST   /invocations                            - Invoke the agent (invocation protocol)
    GET    /invocations/{id}                        - Get invocation status
    POST   /invocations/{id}/cancel                 - Cancel an invocation
    POST   /responses                               - Create a response (responses protocol)
    GET    /responses/{id}                          - Get a response
    DELETE /responses/{id}                          - Delete a response
    POST   /responses/{id}/cancel                   - Cancel a response
    GET    /responses/{id}/input_items               - List input items
    GET    /readiness                                 - Health probe (provided by hosting)

Usage::

    # Start the server
    python app.py

    # --- Invocation protocol ---
    curl -X POST http://localhost:8088/invocations \\
         -H "Content-Type: application/json" \\
         -d '{"message": "Hello from invocations!"}'

    # --- Responses protocol (non-streaming) ---
    curl -X POST http://localhost:8088/responses \\
         -H "Content-Type: application/json" \\
         -d '{"model": "echo", "input": "Hello from responses!", "stream": false, "store": true}'

    # --- Responses protocol (streaming) ---
    curl -X POST http://localhost:8088/responses \\
         -H "Content-Type: application/json" \\
         -d '{"model": "echo", "input": "Hello from responses!", "stream": true, "store": true}'

    # --- Health check (provided automatically by AgentHost) ---
    curl http://localhost:8088/readiness
"""

from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.invocations import InvocationAgentServerHost
from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponseEventStream, get_input_text


# =====================================================================
# 1. Create the server — multi-protocol via cooperative inheritance
# =====================================================================

class MyHost(InvocationAgentServerHost, ResponsesAgentServerHost):
    pass

server = MyHost()


# =====================================================================
# 2. Invocation protocol — simple echo agent
# =====================================================================


@server.invoke_handler
async def handle_invoke(request: Request) -> Response:
    """Process an invocation request by echoing the input.

    :param request: The incoming Starlette request.
    :type request: starlette.requests.Request
    :return: JSON response echoing the input.
    :rtype: starlette.responses.JSONResponse
    """
    data = await request.json()
    invocation_id = request.state.invocation_id
    message = data.get("message", "")

    return JSONResponse({
        "invocation_id": invocation_id,
        "status": "completed",
        "output": f"[Invocation] Echo: {message}",
    })


# =====================================================================
# 3. Responses protocol — streaming echo agent
# =====================================================================

responses = server


@responses.create_handler
def echo_response_handler(
    request: Any,
    context: Any,
    cancellation_signal: Any,
):
    """Handle a response request by echoing the input as a streamed message."""
    stream = ResponseEventStream(
        response_id=context.response_id,
        model=request.model,
    )
    yield from stream.start()
    echo_text = get_input_text(request) or "hello!"
    yield from stream.text_message(f"[Response] Echo: {echo_text}")
    yield from stream.complete()



# =====================================================================
# 4. Start the server
# =====================================================================

if __name__ == "__main__":
    server.run()
