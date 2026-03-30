# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""ConversationHistory sample for azure-ai-agentserver-responses.

Run:
    python samples/ConversationHistory/app.py
"""

from collections.abc import Sequence
from typing import Any

from azure.ai.agentserver.core import AgentHost
from azure.ai.agentserver.responses import ResponseContext, ResponsesServerOptions, ResponseEventStream
from azure.ai.agentserver.responses.models import CreateResponse, OutputItem, get_input_text
from azure.ai.agentserver.responses.hosting import ResponseHandler


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

server = AgentHost()
responses = ResponseHandler(server, options=ResponsesServerOptions(default_fetch_history_count=20))

@responses.create_handler
async def create_async(request: CreateResponse, context: ResponseContext, cancellation_signal: Any):
    stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))

    yield stream.emit_created()
    yield stream.emit_in_progress()

    history = await context.get_history_async()
    current_input = get_input_text(request)
    reply = _build_reply(current_input, history)

    message_item = stream.add_output_item_message()
    yield message_item.emit_added()

    text_content = message_item.add_text_content()
    yield text_content.emit_added()
    yield text_content.emit_delta(reply)
    yield text_content.emit_done(reply)
    yield message_item.emit_content_done(text_content)
    yield message_item.emit_done()

    yield stream.emit_completed()



def main() -> None:
    server.run(host="127.0.0.1", port=5103)


if __name__ == "__main__":
    main()
