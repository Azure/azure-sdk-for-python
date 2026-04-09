# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 05 — Conversation History (multi-turn).

Demonstrates reading conversation history via ``context.get_history()``
using ``TextResponse`` with an async ``create_text`` callback.  The
response references previous turns so the user can observe continuity
across requests.

The server is configured with
``ResponsesServerOptions(default_fetch_history_count=20)`` to limit the
number of history items fetched per request.

Pattern: TextResponse with async create_text, multi-turn history.

Run:
    python samples/scenarios/sample_05_conversation_history.py
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

app = ResponsesAgentServerHost(
    options=ResponsesServerOptions(default_fetch_history_count=20),
)


def _build_reply(current_input: str, history: Sequence[OutputItem]) -> str:
    """Compose a reply that references the conversation history."""
    history_messages = [
        item for item in history if getattr(item, "type", None) == "message"
    ]
    turn_number = len(history_messages) + 1

    if not history_messages:
        return f"[Turn {turn_number}] No prior history. You said: \"{current_input}\""

    last = history_messages[-1]
    last_text = "(no text)"
    if last.get("content"):
        last_text = last["content"][0].get("text", "(no text)")

    return (
        f"[Turn {turn_number}] History has {len(history)} item(s). "
        f"Last assistant message: \"{last_text}\". "
        f"You said: \"{current_input}\""
    )


@app.create_handler
def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Multi-turn handler that reads and references conversation history."""

    async def _build():
        history = await context.get_history()
        current_input = get_input_text(request)
        return _build_reply(current_input, history)

    return TextResponse(context, request, create_text=_build)


def main() -> None:
    app.run(host="127.0.0.1", port=5204)


if __name__ == "__main__":
    main()
