# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""MultiOutput sample for azure-ai-agentserver-responses.

Run:
    python samples/MultiOutput/app.py
"""

import asyncio
from collections.abc import AsyncIterable
from typing import Any

from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponseContext, CreateResponse, ResponseEventStream


server = ResponsesAgentServerHost()


@server.create_handler
def multi_output_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event) -> AsyncIterable[dict[str, Any]]:
    """Produces reasoning plus final message output in one response."""
    stream = ResponseEventStream(response_id=context.response_id, model=request.model)

    yield stream.emit_created()
    yield stream.emit_in_progress()

    reasoning_item = stream.add_output_item_reasoning_item()
    yield reasoning_item.emit_added()

    summary_part = reasoning_item.add_summary_part()
    yield summary_part.emit_added()
    yield summary_part.emit_text_delta("Let me think about this...")
    yield summary_part.emit_text_done("Let me think about this...")
    yield summary_part.emit_done()
    reasoning_item.emit_summary_part_done(summary_part)
    yield reasoning_item.emit_done()

    message_item = stream.add_output_item_message()
    yield message_item.emit_added()

    text_content = message_item.add_text_content()
    yield text_content.emit_added()
    yield text_content.emit_delta("Here is my answer.")
    yield text_content.emit_done("Here is my answer.")
    yield message_item.emit_content_done(text_content)
    yield message_item.emit_done()

    yield stream.emit_completed()


def main() -> None:
    server.run(host="127.0.0.1", port=5102)


if __name__ == "__main__":
    main()