# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""GettingStarted sample for azure-ai-agentserver-responses.

Run:
    python samples/GetStarted/app.py
"""

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    TextResponse,
    get_input_text,
)

app = ResponsesAgentServerHost()


@app.create_handler
def my_handler(request: CreateResponse, context: ResponseContext, cancellation_signal):
    return TextResponse(
        context,
        request,
        create_text=lambda: f"Echo: {get_input_text(request)}",
    )


def main() -> None:
    app.run(host="127.0.0.1", port=5100)


if __name__ == "__main__":
    main()
