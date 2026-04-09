# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 07 — Customization Options.

Shows how to configure the server with custom runtime options:

  - ``ResponsesServerOptions`` for default model, SSE keep-alive, and
    shutdown grace period.
  - ``log_level`` on the host for verbose logging.
  - A handler that relies on ``request.model``, which is automatically
    filled from ``default_model`` when the client omits it.

Pattern: TextResponse with custom options, default model, debug logging.

Run:
    python samples/scenarios/sample_07_customization.py
"""

import asyncio

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
    TextResponse,
    get_input_text,
)

options = ResponsesServerOptions(
    default_model="gpt-4o",
    sse_keep_alive_interval_seconds=5,
    shutdown_grace_period_seconds=15,
)

app = ResponsesAgentServerHost(options=options, log_level="DEBUG")


@app.create_handler
def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Echo handler that reports which model is being used."""
    return TextResponse(
        context,
        request,
        create_text=lambda: f"[model={request.model}] Echo: {get_input_text(request)}",
    )


def main() -> None:
    app.run(host="127.0.0.1", port=5206)


if __name__ == "__main__":
    main()
