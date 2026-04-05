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
    yield from stream.start()
    yield from stream.text_message("Hello from the Python GettingStarted sample!")
    yield from stream.complete()


def main() -> None:
    app.run(host="127.0.0.1", port=5100)


if __name__ == "__main__":
    main()
