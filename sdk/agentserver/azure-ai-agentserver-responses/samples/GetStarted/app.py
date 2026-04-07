# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""GettingStarted sample for azure-ai-agentserver-responses.

Run:
    python samples/GetStarted/app.py
"""

import asyncio

from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponseContext, ResponseEventStream, CreateResponse


app = ResponsesAgentServerHost()


@app.create_handler
def my_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    stream = ResponseEventStream(response_id=context.response_id, model=request.model)
    yield stream.emit_created()
    yield stream.emit_in_progress()
    yield from stream.output_item_message("Hello from the Python GettingStarted sample!")
    yield stream.emit_completed()


def main() -> None:
    app.run(host="127.0.0.1", port=5100)


if __name__ == "__main__":
    main()
