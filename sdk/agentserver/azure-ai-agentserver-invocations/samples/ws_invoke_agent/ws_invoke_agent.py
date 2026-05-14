"""Echo agent over the ``invocations_ws`` (WebSocket) protocol.

Exposes the same host on:

* ``POST /invocations``       — HTTP, JSON request/response;
* ``/invocations_ws``         — WebSocket, full-duplex streaming;
* ``GET  /readiness``         — readiness probe inherited from
  ``azure-ai-agentserver-core``.

Usage::

    # Start the agent
    python ws_invoke_agent.py

    # HTTP turn
    curl -X POST http://localhost:8088/invocations \\
        -H "Content-Type: application/json" \\
        -d '{"name": "Alice"}'
    # -> {"echo": {"name": "Alice"}}

    # WebSocket turn (with the `websockets` client library)
    pip install websockets
    python -m websockets ws://localhost:8088/invocations_ws
    # > hello
    # < hello
"""
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.websockets import WebSocket

from azure.ai.agentserver.invocations import InvocationAgentServerHost


app = InvocationAgentServerHost()


@app.invoke_handler  # POST /invocations
async def handle_invoke(request: Request) -> Response:
    """Echo the JSON payload back over HTTP."""
    payload = await request.json()
    return JSONResponse({"echo": payload})


@app.ws_handler  # /invocations_ws
async def handle_ws(websocket: WebSocket) -> None:
    """Echo every text frame back over the WebSocket connection.

    The SDK has already accepted the connection by the time this function
    runs and will close it cleanly on return.  An uncaught exception is
    mapped to RFC 6455 close code 1011.  WebSocket protocol-level Ping/Pong
    keep-alive is disabled by default; enable it by setting the
    ``WS_KEEPALIVE_INTERVAL`` environment variable or by passing
    ``InvocationAgentServerHost(ws_ping_interval=<seconds>)``.
    """
    async for message in websocket.iter_text():
        await websocket.send_text(message)


if __name__ == "__main__":
    app.run()
