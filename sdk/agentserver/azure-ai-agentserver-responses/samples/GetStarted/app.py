# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""GettingStarted sample for azure-ai-agentserver-responses.

Run:
    python samples/GetStarted/app.py
"""

import asyncio
from collections.abc import AsyncIterable
from typing import Any

from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponseContext, ResponseEventStream, CreateResponse
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream


app = ResponsesAgentServerHost()


@app.create_handler
def my_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    stream = ResponseEventStream(response_id=context.response_id, model=request.model)

    yield stream.emit_created()
    yield stream.emit_in_progress()

    message_item = stream.add_output_item_message()
    yield message_item.emit_added()

    text_content = message_item.add_text_content()
    yield text_content.emit_added()
    yield text_content.emit_delta("Hello from the Python GettingStarted sample!")
    yield text_content.emit_done("Hello from the Python GettingStarted sample!")
    yield message_item.emit_content_done(text_content)

    yield message_item.emit_done()

    yield stream.emit_completed()


def main() -> None:
    app.run(host="127.0.0.1", port=5100)


if __name__ == "__main__":
    main()
