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

from collections.abc import AsyncIterable
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.core import AgentHost
from azure.ai.agentserver.invocations import InvocationHandler
from azure.ai.agentserver.responses.hosting import ResponseHandler
from azure.ai.agentserver.responses import ResponseEventStream, get_input_text


# =====================================================================
# 1. Create the server — single host for both protocols
# =====================================================================

server = AgentHost()


# =====================================================================
# 2. Invocation protocol — simple echo agent
# =====================================================================

invocations = InvocationHandler(server)


@invocations.invoke_handler
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

responses = ResponseHandler(server)


@responses.create_handler
def echo_response_handler(
    request: Any,
    context: Any,
    cancellation_signal: Any,
) -> AsyncIterable[dict[str, Any]]:
    """Handle a response request by echoing the input as a streamed message.

    Emits the full Responses API event lifecycle:
    created -> in_progress -> output items -> completed

    :param request: The parsed create-response request.
    :param context: Runtime context with response_id and mode flags.
    :param cancellation_signal: Event that signals cancellation.
    :return: Async iterable of response events.
    """
    # Build the event stream helper
    stream = ResponseEventStream(
        response_id=context.response_id,
        model=request.model,
    )

    # Lifecycle: created -> in_progress
    yield stream.emit_created()
    yield stream.emit_in_progress()

    # Extract input text
    echo_text = get_input_text(request) or "hello!"

    # Emit an output message with text content
    message_item = stream.add_output_item_message()
    yield message_item.emit_added()

    text_content = message_item.add_text_content()
    yield text_content.emit_added()

    # Stream the echo text word-by-word for demonstration
    words = f"[Response] Echo: {echo_text}".split()
    for i, word in enumerate(words):
        # Check for cancellation between chunks
        if cancellation_signal.is_set():
            yield stream.emit_incomplete(reason="cancelled")
            return

        delta = word if i == 0 else f" {word}"
        yield text_content.emit_delta(delta)

    yield text_content.emit_done()
    yield message_item.emit_content_done(text_content)
    yield message_item.emit_done()

    # Lifecycle: completed
    yield stream.emit_completed()



# =====================================================================
# 4. Start the server
# =====================================================================

if __name__ == "__main__":
    server.run()
