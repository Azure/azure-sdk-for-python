"""Resilient multi-turn session agent (invocations protocol).

Defines the resilient task that powers a sticky conversation session.
Each invocation runs this function from the top — ``ctx.entry_mode``
tells us whether this is a fresh start, a resume, or a crash recovery.

The sample explicitly stores both session history and per-invocation results
in Foundry State Store. Task metadata is not used as application storage.
"""

from __future__ import annotations

import logging
from typing import Any

from typing_extensions import TypedDict

from azure.ai.agentserver.core.storage import FoundryStateStore
from azure.ai.agentserver.core.tasks import TaskContext, multi_turn_task

logger = logging.getLogger(__name__)


def session_state_store_name(session_id: str) -> str:
    """Return the session-isolated conversation state store name."""
    return f"resilient-multiturn/sessions/{session_id}"


def invocation_state_store_name(session_id: str) -> str:
    """Return the session-isolated invocation status store name."""
    return f"resilient-multiturn/invocations/{session_id}"


class TaskInput(TypedDict):
    """Persisted input required to run or recover one conversation turn."""

    session_id: str
    message: str
    invocation_id: str


def _generate_reply(turn: int, last_msg: str) -> str:
    """Placeholder for an LLM call.  Replace with your model of choice."""

    if turn == 1:
        return (
            f"Thanks for reaching out! You said: '{last_msg}'. "
            "Could you share more details so I can help?"
        )
    if turn == 2:
        return (
            f"Great, noted: '{last_msg}'. Based on our conversation "
            "so far, here are some initial thoughts. What else?"
        )
    return (
        f"Turn {turn}: incorporating '{last_msg}' — "
        f"I now have context from {turn} turns of conversation."
    )


@multi_turn_task(name="session_workflow")
async def session_workflow(ctx: TaskContext[TaskInput]) -> dict[str, Any]:
    """Single resilient function for the entire session.

    Each invocation runs this function from the top.
    ``ctx.entry_mode`` tells us why we were entered.

    Session and invocation state are stored in separate State Stores.
    """

    session_id: str = ctx.input["session_id"]
    message: str = ctx.input["message"]
    invocation_id: str = ctx.input["invocation_id"]

    session_key = f"session/{session_id}"
    invocation_key = f"invocation/{invocation_id}"
    session_store = await FoundryStateStore.get_or_create(
        session_state_store_name(session_id),
        description="Multi-turn conversation state",
    )
    invocation_store = await FoundryStateStore.get_or_create(
        invocation_state_store_name(session_id),
        description="Multi-turn invocation status and results",
    )
    async with session_store, invocation_store:
        session_item = await session_store.get_item(session_key)
        session = (
            dict(session_item.value)
            if session_item is not None and isinstance(session_item.value, dict)
            else {}
        )
        history: list[dict[str, str]] = session.get("history", [])
        turn_count: int = session.get("turn_count", 0)

        if (
            ctx.entry_mode == "recovered"
            and session.get("last_applied_invocation_id") == invocation_id
        ):
            output = session.get("last_output")
            if isinstance(output, dict):
                await invocation_store.set_item(
                    invocation_key,
                    {"status": "completed", "output": output},
                )
                return output

        await invocation_store.set_item(
            invocation_key,
            {"status": "running"},
        )

        if ctx.entry_mode == "recovered":
            logger.warning("Recovered stale task for session %s", session_id)

        # Handle explicit session end
        if message.strip().lower() == "done":
            summary = (
                f"Session complete after {turn_count} turns. "
                f"Total messages exchanged: {len(history)}."
            )
            result = {"reply": summary, "turn": turn_count, "finished": True}
            # Clear the session history so a future session_id reuse starts clean.
            await session_store.set_item(
                session_key,
                {
                    "history": [],
                    "turn_count": 0,
                    "last_applied_invocation_id": invocation_id,
                    "last_output": result,
                },
                tags={"invocation_id": invocation_id},
            )

            await invocation_store.set_item(
                invocation_key,
                {"status": "completed", "output": result},
            )
            return result

        # Process this turn
        history.append({"role": "user", "content": message})
        turn_count += 1

        reply = _generate_reply(turn_count, message)
        history.append({"role": "assistant", "content": reply})
        output = {"reply": reply, "turn": turn_count}

        await session_store.set_item(
            session_key,
            {
                "history": history,
                "turn_count": turn_count,
                "last_applied_invocation_id": invocation_id,
                "last_output": output,
            },
            tags={"invocation_id": invocation_id},
        )

        await invocation_store.set_item(
            invocation_key,
            {"status": "completed", "output": output},
        )

        # Suspend — the client will resume with the next turn.
        # multi-turn `return X` is the implicit-suspend signal.
        # The chain stays alive across turns; ctx.suspend() is not part of
        # the public surface. The output value flows through
        # `return output` to the caller's `.result()`.
        return output
