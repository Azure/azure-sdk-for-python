# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""ConversationHistory sample for azure-ai-agentserver-responses.

Run:
    python samples/ConversationHistory/app.py
"""

import asyncio
from collections.abc import Sequence

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
    TextResponse,
    get_input_text,
)
from azure.ai.agentserver.responses.models import OutputItem


def _build_reply(current_input: str, history: Sequence[OutputItem]) -> str:
    if len(history) == 0:
        return f'[Turn 1] No history. You said: "{current_input}"'

    history_messages = [
        item for item in history if getattr(item, "type", None) == "message"
    ]
    turn_number = len(history_messages) + 1
    last_message = history_messages[-1] if history_messages else None
    last_text = (
        last_message["content"][0]["text"]
        if last_message and last_message.get("content")
        else "(no text)"
    )

    return (
        f"[Turn {turn_number}] History has {len(history)} item(s). "
        f'Last assistant message: "{last_text}". '
        f'You said: "{current_input}"'
    )


server = ResponsesAgentServerHost(
    options=ResponsesServerOptions(default_fetch_history_count=20),
)


@server.create_handler
def create(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    async def _build():
        history = await context.get_history()
        current_input = get_input_text(request)
        return _build_reply(current_input, history)

    return TextResponse(context, request, create_text=_build)


def main() -> None:
    server.run(host="127.0.0.1", port=5103)


if __name__ == "__main__":
    main()
