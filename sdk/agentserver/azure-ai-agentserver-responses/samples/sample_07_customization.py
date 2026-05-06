# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 07 — Customization Options.

Shows how to configure the server with custom runtime options:

  - ``ResponsesServerOptions`` for default model, SSE keep-alive, and
    shutdown grace period.
  - ``log_level`` on the host for verbose logging.
  - A handler that relies on ``request.model``, which is automatically
    filled from ``default_model`` when the client omits it.

Usage::

    # Start the server (with DEBUG logging)
    python sample_07_customization.py

    # Send a request (model defaults to gpt-4o via default_model)
    curl -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"input": "Hello!"}'
    # -> {"output": [{"type": "message", "content":
    #     [{"type": "output_text", "text": "[model=gpt-4o] Echo: Hello!"}]}]}

    # Override the model explicitly
    curl -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "custom", "input": "Hello!"}'
    # -> {"output": [{"type": "message", "content":
    #     [{"type": "output_text", "text": "[model=custom] Echo: Hello!"}]}]}
"""

import asyncio

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
    TextResponse,
)

options = ResponsesServerOptions(
    default_model="gpt-4o",
    sse_keep_alive_interval_seconds=5,
    shutdown_grace_period_seconds=15,
)

app = ResponsesAgentServerHost(options=options, log_level="DEBUG")


@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Echo handler that reports which model is being used."""
    input_text = await context.get_input_text()
    return TextResponse(context, request, text=f"[model={request.model}] Echo: {input_text}")


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
