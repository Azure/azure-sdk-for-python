# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""ConversationHistory sample for azure-ai-agentserver-responses.

Run:
    python samples/ConversationHistory/app.py
"""

from collections.abc import Sequence
from typing import Any

from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponseContext, ResponsesServerOptions, ResponseEventStream, get_input_text
from azure.ai.agentserver.responses.models import CreateResponse, OutputItem


def _build_reply(current_input: str, history: Sequence[OutputItem]) -> str:
    if len(history) == 0:
        return f"[Turn 1] No history. You said: \"{current_input}\""

    history_messages = [item for item in history if getattr(item, "type", None) == "message"]
    turn_number = len(history_messages) + 1
    last_message = history_messages[-1] if history_messages else None
    last_text = last_message["content"][0]["text"] if last_message and last_message.get("content") else "(no text)"

    return (
        f"[Turn {turn_number}] History has {len(history)} item(s). "
        f"Last assistant message: \"{last_text}\". "
        f"You said: \"{current_input}\""
    )

server = ResponsesAgentServerHost(options=ResponsesServerOptions(default_fetch_history_count=20))

@server.create_handler
async def create(request: CreateResponse, context: ResponseContext, cancellation_signal: Any):
    stream = ResponseEventStream(response_id=context.response_id, model=request.model)

    async for event in stream.astart():
        yield event

    history = await context.get_history()
    current_input = get_input_text(request)
    reply = _build_reply(current_input, history)

    async for event in stream.atext_message(reply):
        yield event
    async for event in stream.acomplete():
        yield event



def main() -> None:
    server.run(host="127.0.0.1", port=5103)


if __name__ == "__main__":
    main()
