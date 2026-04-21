# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 05 — Conversation History — Study Tutor.

Demonstrates reading conversation history via ``context.get_history()``
using ``TextResponse``.  The study
tutor references previous turns to give contextual follow-up answers,
demonstrating multi-turn conversational flows using
``previous_response_id``.

The server is configured with
``ResponsesServerOptions(default_fetch_history_count=20)`` to limit the
number of history items fetched per request.

Usage::

    # Start the server
    python sample_05_conversation_history.py

    # Turn 1 — initial message (no history)
    curl -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "tutor", "input": "Explain photosynthesis."}'
    # -> {"id": "resp_...", "output": [{"type": "message", "content":
    #     [{"type": "output_text", "text": "Welcome! I'm your study tutor. You asked: ..."}]}]}

    # Turn 2 — chain via previous_response_id (use the id from Turn 1)
    curl -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "tutor", "input": "What role does chlorophyll play?", "previous_response_id": "<id-from-turn-1>"}'
    # -> {"output": [{"type": "message", "content": [{"type": "output_text",
    #     "text": "[Turn 2] Building on our previous discussion ..."}]}]}
"""

import asyncio
from collections.abc import Sequence

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
    TextResponse,
)
from azure.ai.agentserver.responses.models import OutputItem

app = ResponsesAgentServerHost(
    options=ResponsesServerOptions(default_fetch_history_count=20),
)


def _build_reply(current_input: str, history: Sequence[OutputItem]) -> str:
    """Compose a study-tutor reply that references the conversation history."""
    history_messages = [item for item in history if getattr(item, "type", None) == "message"]
    turn_number = len(history_messages) + 1

    if not history_messages:
        return f'Welcome! I\'m your study tutor. You asked: "{current_input}". Let me help you understand that topic.'

    last = history_messages[-1]
    last_text = "(none)"
    if last.get("content"):
        raw = last["content"][0].get("text", "(none)")
        last_text = raw[:50] + "..." if len(raw) > 50 else raw

    return (
        f"[Turn {turn_number}] Building on our previous discussion "
        f'(last answer: "{last_text}"), '
        f'you asked: "{current_input}".'
    )


@app.response_handler
async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Study tutor that reads and references conversation history."""
    history = await context.get_history()
    current_input = await context.get_input_text()
    return TextResponse(context, request, text=_build_reply(current_input, history))


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
