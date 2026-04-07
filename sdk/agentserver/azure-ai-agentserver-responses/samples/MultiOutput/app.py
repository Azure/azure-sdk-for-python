# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""MultiOutput sample for azure-ai-agentserver-responses.

Run:
    python samples/MultiOutput/app.py
"""

import asyncio

from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponseContext, CreateResponse, ResponseEventStream


server = ResponsesAgentServerHost()


@server.create_handler
def multi_output_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Produces reasoning plus final message output in one response."""
    stream = ResponseEventStream(response_id=context.response_id, model=request.model)
    yield stream.emit_created()
    yield stream.emit_in_progress()
    yield from stream.output_item_reasoning_item("Let me think about this...")
    yield from stream.output_item_message("Here is my answer.")
    yield stream.emit_completed()


def main() -> None:
    server.run(host="127.0.0.1", port=5102)


if __name__ == "__main__":
    main()