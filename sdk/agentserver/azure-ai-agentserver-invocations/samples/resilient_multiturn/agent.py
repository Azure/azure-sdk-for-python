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
STATE_STORE_NAME = "resilient-multiturn"


class TaskInput(TypedDict):
    """Persisted input required to run or recover one conversation turn."""

    session_id: str
    message: str
    invocation_id: str
    call_id: str


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

    Session and invocation state are stored as separate State Store items.
    """

    session_id: str = ctx.input["session_id"]
    message: str = ctx.input["message"]
    invocation_id: str = ctx.input["invocation_id"]
    call_id: str | None = ctx.input.get("call_id")

    session_key = f"session/{session_id}"
    invocation_key = f"invocation/{invocation_id}"
    store = await FoundryStateStore.get_or_create(
        STATE_STORE_NAME,
        user_isolation=True,
        description="Multi-turn conversation state and invocation results",
    )
    async with store:
        session_item = await store.get_item(session_key, call_id=call_id)
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
                await store.set_item(
                    invocation_key,
                    {"status": "completed", "output": output},
                    tags={"session_id": session_id},
                    call_id=call_id,
                )
                return output

        await store.set_item(
            invocation_key,
            {"status": "running"},
            tags={"session_id": session_id},
            call_id=call_id,
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
            await store.set_item(
                session_key,
                {
                    "history": [],
                    "turn_count": 0,
                    "last_applied_invocation_id": invocation_id,
                    "last_output": result,
                },
                tags={"session_id": session_id},
                call_id=call_id,
            )

            await store.set_item(
                invocation_key,
                {"status": "completed", "output": result},
                tags={"session_id": session_id},
                call_id=call_id,
            )
            return result

        # Process this turn
        history.append({"role": "user", "content": message})
        turn_count += 1

        reply = _generate_reply(turn_count, message)
        history.append({"role": "assistant", "content": reply})
        output = {"reply": reply, "turn": turn_count}

        await store.set_item(
            session_key,
            {
                "history": history,
                "turn_count": turn_count,
                "last_applied_invocation_id": invocation_id,
                "last_output": output,
            },
            tags={"session_id": session_id},
            call_id=call_id,
        )

        await store.set_item(
            invocation_key,
            {"status": "completed", "output": output},
            tags={"session_id": session_id},
            call_id=call_id,
        )

        # Suspend — the client will resume with the next turn.
        # multi-turn `return X` is the implicit-suspend signal.
        # The chain stays alive across turns; ctx.suspend() is not part of
        # the public surface. The output value flows through
        # `return output` to the caller's `.result()`.
        return output
