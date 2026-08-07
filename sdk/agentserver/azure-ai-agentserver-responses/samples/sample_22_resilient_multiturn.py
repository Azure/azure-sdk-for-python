# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 22 — Resilient Multi-turn (serial conversation, no steering).

A self-contained multi-turn handler with no external LLM dependency.
Demonstrates the perpetual task lifecycle: each turn completes, the task
suspends, and the next turn resumes it.

Without steering, the framework serializes turns via a conversation lock.
If turn A is executing when turn B arrives, turn B waits (not cancels).

Key concepts:
- ``resilient_background=True``, ``steerable_conversations=False``
- Conversation history via ``context.get_history()`` (framework-managed)
- Conversation-isolated Foundry State Store for bounded execution state
- Crash recovery: handler re-invoked, same input + history → same output

Usage::

    python sample_22_resilient_multiturn.py

    # Turn 1
    curl -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "chat", "input": "My name is Alice", "store": true, "background": true}'

    # Turn 2 (reference previous for conversation context)
    curl -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "chat", "input": "What is my name?", "store": true, "background": true, "previous_response_id": "<id>"}'

    # End conversation
    curl -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "chat", "input": "done", "store": true, "background": true, "previous_response_id": "<id>"}'
"""

import asyncio

from azure.ai.agentserver.core.storage import FoundryStateStore
from azure.ai.agentserver.core.tasks import set_resilient_tasks_enabled
from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
    TextResponse,
)

options = ResponsesServerOptions(
    resilient_background=True,
    steerable_conversations=False,
)
app = ResponsesAgentServerHost(options=options)

# Explicitly opt into resilient-task startup recovery, for parity with the
# invocations resilient samples. The Responses framework already registers its
# internal durable tasks at host construction (so recovery runs regardless);
# this call just makes the opt-in intent explicit.
set_resilient_tasks_enabled(True)


@app.response_handler
async def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Multi-turn handler with perpetual task lifecycle."""
    input_text = await context.get_input_text()
    store = await FoundryStateStore.get_or_create(
        f"responses/resilient-multiturn/{context.conversation_chain_id}",
        description="State for the resilient multi-turn response sample",
    )
    async with store:
        item = await store.get_item("state")
        state = (
            dict(item.value)
            if item is not None and isinstance(item.value, dict)
            else {}
        )
        if (
            state.get("terminated")
            and state.get("last_response_id") != context.response_id
        ):
            state = {}
        if state.get("last_response_id") == context.response_id:
            turn_count = int(state.get("turn_count", 1))
        else:
            turn_count = int(state.get("turn_count", 0)) + 1

        # Explicit session termination
        if input_text.strip().lower() == "done":
            if state.get("last_response_id") == context.response_id and state.get(
                "terminated"
            ):
                completed_turns = int(state.get("completed_turns", 0))
            else:
                completed_turns = max(turn_count - 1, 0)
                await store.set_item(
                    "state",
                    {
                        "turn_count": completed_turns,
                        "last_response_id": context.response_id,
                        "terminated": True,
                        "completed_turns": completed_turns,
                    },
                )
            return TextResponse(
                context,
                request,
                text=f"Done! Session complete after {completed_turns} turns. Goodbye!",
            )

        # Get conversation history from framework store
        history_items = await context.get_history()

        # Generate reply (replace with your LLM of choice)
        reply = (
            f"Turn {turn_count}: You said '{input_text}'. "
            f"I have {len(history_items)} items of conversation context."
        )

        await store.set_item(
            "state",
            {"turn_count": turn_count, "last_response_id": context.response_id},
        )
        return TextResponse(context, request, text=reply)


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
