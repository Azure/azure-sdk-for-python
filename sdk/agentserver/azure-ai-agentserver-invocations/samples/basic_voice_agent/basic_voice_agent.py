"""Basic full-duplex Voice Live Bridge agent using the Invocations submodule.

The Voice SDK only decodes events, dispatches callbacks, and serializes
``Session.send`` calls. This sample deliberately owns its generation tasks and
terminal-event correlation in application code.
"""

import asyncio
import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass

from azure.ai.agentserver.invocations.voice import (
    BargeIn,
    InputTextPart,
    ResponseCancelled,
    ResponseCreated,
    ResponseDone,
    ResponseNone,
    ResponseOutputTextDelta,
    ResponseOutputTextDone,
    ResponseTimeout,
    Session,
    SessionDisconnected,
    SessionEnd,
    SessionReady,
    SessionRejected,
    SessionStart,
    UserMessage,
    VoiceAgentServerHost,
    new_item_id,
    new_response_id,
)

logger = logging.getLogger("azure.ai.agentserver")
app = VoiceAgentServerHost()
SUPPORTED_PROTOCOL_VERSION = "1.0"


@dataclass(frozen=True)
class Generation:
    """Application-owned generation task and its input correlation."""

    session: Session
    input_ids: tuple[str, ...]
    task: asyncio.Task[None]


GenerationKey = tuple[int, str]

generations: dict[GenerationKey, Generation] = {}
input_generations: dict[tuple[int, str], GenerationKey] = {}


async def generate_answer(text: str) -> AsyncIterator[str]:
    """Simulate a streaming model response."""
    for chunk in ("You said: ", text):
        await asyncio.sleep(0.1)
        yield chunk


async def stream_response(
    session: Session,
    *,
    response_id: str,
    item_id: str,
    in_reply_to: tuple[str, ...],
    text: str,
) -> None:
    """Translate one model stream into explicit Bridge output events."""
    await session.send(ResponseCreated(response_id=response_id, in_reply_to=in_reply_to))
    chunks: list[str] = []
    async for delta in generate_answer(text):
        chunks.append(delta)
        await session.send(
            ResponseOutputTextDelta(
                response_id=response_id,
                item_id=item_id,
                delta=delta,
            )
        )
    await session.send(
        ResponseOutputTextDone(
            response_id=response_id,
            item_id=item_id,
            text="".join(chunks),
        )
    )
    await session.send(ResponseDone(response_id=response_id))


def generation_finished(key: GenerationKey, completed: asyncio.Task[None]) -> None:
    """Release application correlation and observe task failures."""
    generation = generations.get(key)
    if generation is None or generation.task is not completed:
        return
    del generations[key]
    for input_id in generation.input_ids:
        input_key = (id(generation.session), input_id)
        if input_generations.get(input_key) == key:
            del input_generations[input_key]
    if not completed.cancelled() and (exception := completed.exception()) is not None:
        logger.error(
            "Voice response generation failed",
            exc_info=(type(exception), exception, exception.__traceback__),
        )


def cancel_generation(session: Session, response_id: str) -> None:
    """Cancel one application-owned generation task when present."""
    generation = generations.get((id(session), response_id))
    if generation is not None:
        generation.task.cancel()


def cancel_session_generation_tasks(session: Session) -> tuple[asyncio.Task[None], ...]:
    """Synchronously signal every application-owned task for one connection."""
    tasks = tuple(generation.task for generation in tuple(generations.values()) if generation.session is session)
    for task in tasks:
        task.cancel()
    return tasks


async def cancel_session_generations(session: Session) -> None:
    """Cancel and join all application-owned tasks for one connection."""
    tasks = cancel_session_generation_tasks(session)
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


@app.on_session_start
async def on_session_start(session: Session, event: SessionStart) -> None:
    """Restore application state when needed, then acknowledge readiness."""
    if event.protocol_version != SUPPORTED_PROTOCOL_VERSION:
        await session.send(SessionRejected(code="protocol_mismatch", retriable=False))
        return
    if event.reconnect:
        logger.info("Voice transport reattached; restore durable application state here")
    await session.send(SessionReady())


@app.on_user_message
async def on_user_message(session: Session, event: UserMessage) -> None:
    """Start generation without blocking later full-duplex control events."""
    text = " ".join(part.text for part in event.content if isinstance(part, InputTextPart))
    if not text:
        await session.send(ResponseNone(in_reply_to=(event.item_id,), reason="no_reply_needed"))
        return

    response_id = new_response_id()
    item_id = new_item_id()
    input_ids = (event.item_id,)
    key = (id(session), response_id)
    task = asyncio.create_task(
        stream_response(
            session,
            response_id=response_id,
            item_id=item_id,
            in_reply_to=input_ids,
            text=text,
        ),
        name=f"voice-response-{response_id}",
    )
    generations[key] = Generation(session=session, input_ids=input_ids, task=task)
    input_generations[(id(session), event.item_id)] = key

    def on_generation_finished(completed: asyncio.Task[None]) -> None:
        generation_finished(key, completed)

    task.add_done_callback(on_generation_finished)


@app.on_barge_in
async def on_barge_in(session: Session, event: BargeIn) -> None:
    """Stop generation and reconcile history from the playback snapshot."""
    cancel_generation(session, event.response_id)
    logger.info("Caller heard %d characters before barge-in", len(event.heard_text))


@app.on_response_cancelled
async def on_response_cancelled(session: Session, event: ResponseCancelled) -> None:
    """Handle the terminal outcome of an explicit self-cancel request."""
    cancel_generation(session, event.response_id)


@app.on_response_timeout
async def on_response_timeout(session: Session, event: ResponseTimeout) -> None:
    """Stop the application task targeted by the Bridge timeout."""
    if event.response_id is not None:
        cancel_generation(session, event.response_id)
        return
    for input_id in event.item_ids or ():
        key = input_generations.get((id(session), input_id))
        if key is not None and (generation := generations.get(key)) is not None:
            generation.task.cancel()


@app.on_session_end
async def on_session_end(session: Session, event: SessionEnd) -> None:
    """Cancel and join all application tasks for this connection."""
    logger.info("Voice session ended: %s", event.reason)
    await cancel_session_generations(session)


@app.on_disconnect
async def on_disconnect(session: Session, event: SessionDisconnected) -> None:
    """Observe a peer transport disconnect."""
    del session
    logger.info("Voice transport disconnected with close code %d", event.code)


@app.on_connection_terminating
def on_connection_terminating(session: Session) -> None:
    """Synchronously cancel application tasks whenever the handler exits."""
    cancel_session_generation_tasks(session)


if __name__ == "__main__":
    app.run()
