"""Basic full-duplex Voice Live Bridge agent using the Invocations submodule.

The Voice SDK only decodes events, dispatches callbacks, and serializes
``Session.send`` calls. This sample deliberately owns its generation tasks and
terminal-event correlation in application code.
"""

import asyncio
import contextvars
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
    SessionTermination,
    TargetTurn,
    TargetTurnOrigin,
    TargetTurnOutcome,
    UserMessage,
    VoiceAgentServerHost,
    new_item_id,
    new_response_id,
)

logger = logging.getLogger("azure.ai.agentserver")
app = VoiceAgentServerHost()
SUPPORTED_PROTOCOL_VERSION = "1.0"
MAX_ACTIVE_GENERATIONS_PER_SESSION = 8
MAX_OUTPUT_CHUNKS = 4096
MAX_OUTPUT_UTF8_BYTES = 512 * 1024


@dataclass
class Generation:
    """Application-owned generation task, trace, and terminal facts."""

    session: Session
    input_ids: tuple[str, ...]
    response_id: str
    turn: TargetTurn
    preparation_ready: asyncio.Event
    task: asyncio.Task[None] | None = None
    response_started: bool = False
    output_item_count: int = 0
    outcome_hint: TargetTurnOutcome | None = None


GenerationKey = tuple[int, str]

generations: dict[GenerationKey, Generation] = {}
input_generations: dict[tuple[int, str], GenerationKey] = {}


async def generate_answer(text: str) -> AsyncIterator[str]:
    """Simulate a streaming model response."""
    for chunk in ("You said: ", text):
        await asyncio.sleep(0.1)
        yield chunk


async def stream_response(
    generation: Generation,
    *,
    item_id: str,
    text: str,
) -> None:
    """Translate one model stream into explicit Bridge output events."""
    await generation.session.send(ResponseCreated(response_id=generation.response_id, in_reply_to=generation.input_ids))
    generation.response_started = True
    chunks: list[str] = []
    output_utf8_bytes = 0
    async for delta in generate_answer(text):
        delta_utf8_bytes = len(delta.encode("utf-8"))
        if len(chunks) >= MAX_OUTPUT_CHUNKS or output_utf8_bytes + delta_utf8_bytes > MAX_OUTPUT_UTF8_BYTES:
            raise RuntimeError("Voice model output exceeded sample limits")
        output_utf8_bytes += delta_utf8_bytes
        chunks.append(delta)
        await generation.session.send(
            ResponseOutputTextDelta(
                response_id=generation.response_id,
                item_id=item_id,
                delta=delta,
            )
        )
    await generation.session.send(
        ResponseOutputTextDone(
            response_id=generation.response_id,
            item_id=item_id,
            text="".join(chunks),
        )
    )
    generation.output_item_count = 1
    await generation.session.send(ResponseDone(response_id=generation.response_id))


def completion_facts(generation: Generation) -> tuple[str | None, int]:
    """Project only application-committed response facts into tracing."""
    response_id = generation.response_id if generation.response_started else None
    return response_id, generation.output_item_count


def complete_generation(generation: Generation, outcome: TargetTurnOutcome) -> None:
    """Complete one application turn after its activation scope has exited."""
    response_id, output_item_count = completion_facts(generation)
    generation.turn.complete(
        outcome=outcome,
        response_id=response_id,
        output_item_count=output_item_count,
    )


def termination_outcome(termination: SessionTermination | None) -> TargetTurnOutcome:
    """Map a physical connection fact to an unfinished application decision."""
    if termination is None or termination is SessionTermination.CANCELLED:
        return TargetTurnOutcome.CANCELLED
    if termination is SessionTermination.COMPLETED:
        return TargetTurnOutcome.ABANDONED
    if termination in {SessionTermination.PROTOCOL_ERROR, SessionTermination.TRANSPORT_ERROR}:
        return TargetTurnOutcome.TRANSPORT_ERROR
    if termination in {
        SessionTermination.ACCEPT_ERROR,
        SessionTermination.CALLBACK_ERROR,
        SessionTermination.INTERNAL_ERROR,
    }:
        return TargetTurnOutcome.ERROR
    raise AssertionError(f"Unhandled Voice session termination: {termination!r}")


def generation_error_outcome(generation: Generation) -> TargetTurnOutcome:
    """Prefer already-committed application or connection facts over a generic error."""
    if generation.outcome_hint is not None:
        return generation.outcome_hint
    if generation.session.termination is not None:
        return termination_outcome(generation.session.termination)
    return TargetTurnOutcome.ERROR


async def send_no_response(session: Session, input_ids: tuple[str, ...], reason: str) -> None:
    """Send one bounded no-response decision under an explicit target turn."""
    turn = session.start_target_turn(origin=TargetTurnOrigin.USER, input_count=len(input_ids))
    try:
        with turn.activate():
            await session.send(ResponseNone(in_reply_to=input_ids, reason=reason))
        turn.complete(outcome=TargetTurnOutcome.NONE, output_item_count=0)
    except asyncio.CancelledError:
        if not turn.is_completed:
            turn.complete(outcome=termination_outcome(session.termination), output_item_count=0)
        raise
    except BaseException:
        if not turn.is_completed:
            outcome = (
                termination_outcome(session.termination) if session.termination is not None else TargetTurnOutcome.ERROR
            )
            turn.complete(outcome=outcome, output_item_count=0)
        raise


async def run_generation(generation: Generation, *, item_id: str, text: str) -> None:
    """Run all descendant-producing work under the declared target turn."""
    await generation.preparation_ready.wait()
    try:
        with generation.turn.activate():
            await stream_response(generation, item_id=item_id, text=text)
        complete_generation(generation, TargetTurnOutcome.RESPONSE)
    except asyncio.CancelledError:
        complete_generation(
            generation,
            generation.outcome_hint or termination_outcome(generation.session.termination),
        )
        raise
    except BaseException:
        complete_generation(generation, generation_error_outcome(generation))
        raise


def generation_finished(key: GenerationKey, completed: asyncio.Task[None]) -> None:
    """Release application correlation and observe task failures."""
    generation = generations.get(key)
    if generation is None or generation.task is not completed:
        return
    try:
        if not generation.turn.is_completed:
            if completed.cancelled():
                outcome = generation.outcome_hint or termination_outcome(generation.session.termination)
            elif completed.exception() is not None:
                outcome = generation_error_outcome(generation)
            else:
                outcome = TargetTurnOutcome.ABANDONED
            complete_generation(generation, outcome)
        if not completed.cancelled() and completed.exception() is not None:
            logger.error("Voice response generation failed")
    finally:
        if generations.get(key) is generation:
            del generations[key]
        for input_id in generation.input_ids:
            input_key = (id(generation.session), input_id)
            if input_generations.get(input_key) == key:
                del input_generations[input_key]


def set_outcome_hint(generation: Generation, outcome: TargetTurnOutcome) -> None:
    """Commit the first application-known terminal hint."""
    if generation.outcome_hint is None:
        generation.outcome_hint = outcome


def cancel_generation(session: Session, response_id: str, outcome: TargetTurnOutcome) -> None:
    """Cancel one application-owned generation task when present."""
    generation = generations.get((id(session), response_id))
    if generation is not None and generation.task is not None:
        set_outcome_hint(generation, outcome)
        generation.task.cancel()


def cancel_session_generation_tasks(
    session: Session,
    outcome: TargetTurnOutcome | None = None,
) -> tuple[asyncio.Task[None], ...]:
    """Synchronously signal every application-owned task for one connection."""
    selected = tuple(generation for generation in tuple(generations.values()) if generation.session is session)
    tasks = []
    for generation in selected:
        if outcome is not None:
            set_outcome_hint(generation, outcome)
        if generation.task is not None:
            tasks.append(generation.task)
            generation.task.cancel()
    return tuple(tasks)


async def cancel_session_generations(session: Session, outcome: TargetTurnOutcome) -> None:
    """Cancel and join all application-owned tasks for one connection."""
    tasks = cancel_session_generation_tasks(session, outcome)
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


@app.on_session_start
async def on_session_start(session: Session, event: SessionStart) -> None:
    """Restore application state when needed, then acknowledge readiness."""
    if event.protocol_version != SUPPORTED_PROTOCOL_VERSION:
        await session.send(SessionRejected(code="protocol_mismatch", retriable=False))
        return
    if event.reconnect:
        logger.info("Voice transport reattached")
    await session.send(SessionReady())


@app.on_user_message
async def on_user_message(session: Session, event: UserMessage) -> None:
    """Start generation without blocking later full-duplex control events."""
    text = " ".join(part.text for part in event.content if isinstance(part, InputTextPart))
    input_ids = (event.item_id,)
    if not text:
        await send_no_response(session, input_ids, "no_reply_needed")
        return
    active_generations = sum(generation.session is session for generation in generations.values())
    if active_generations >= MAX_ACTIVE_GENERATIONS_PER_SESSION:
        await send_no_response(session, input_ids, "capacity_exceeded")
        return

    response_id = new_response_id()
    item_id = new_item_id()
    key = (id(session), response_id)
    turn = session.start_target_turn(origin=TargetTurnOrigin.USER, input_count=len(input_ids))
    generation = Generation(
        session=session,
        input_ids=input_ids,
        response_id=response_id,
        turn=turn,
        preparation_ready=asyncio.Event(),
    )
    coroutine = run_generation(generation, item_id=item_id, text=text)
    task = None
    try:
        task = asyncio.create_task(coroutine, name=f"voice-response-{response_id}")
        generation.task = task

        def on_generation_finished(completed: asyncio.Task[None]) -> None:
            generation_finished(key, completed)

        task.add_done_callback(on_generation_finished, context=contextvars.Context())
        generations[key] = generation
        input_generations[(id(session), event.item_id)] = key
        generation.preparation_ready.set()
    except BaseException:
        turn.complete(outcome=TargetTurnOutcome.ABANDONED, output_item_count=0)
        generations.pop(key, None)
        input_generations.pop((id(session), event.item_id), None)
        if task is None:
            coroutine.close()
        else:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        raise


@app.on_barge_in
async def on_barge_in(session: Session, event: BargeIn) -> None:
    """Stop generation and reconcile history from the playback snapshot."""
    cancel_generation(session, event.response_id, TargetTurnOutcome.CANCELLED)
    logger.info("Voice response interrupted")


@app.on_response_cancelled
async def on_response_cancelled(session: Session, event: ResponseCancelled) -> None:
    """Handle the terminal outcome of an explicit self-cancel request."""
    cancel_generation(session, event.response_id, TargetTurnOutcome.CANCELLED)


@app.on_response_timeout
async def on_response_timeout(session: Session, event: ResponseTimeout) -> None:
    """Stop the application task targeted by the Bridge timeout."""
    if event.response_id is not None:
        cancel_generation(session, event.response_id, TargetTurnOutcome.TIMEOUT)
        return
    for input_id in event.item_ids or ():
        key = input_generations.get((id(session), input_id))
        if key is not None and (generation := generations.get(key)) is not None:
            set_outcome_hint(generation, TargetTurnOutcome.TIMEOUT)
            assert generation.task is not None
            generation.task.cancel()


@app.on_session_end
async def on_session_end(session: Session, event: SessionEnd) -> None:
    """Cancel and join all application tasks for this connection."""
    del event
    logger.info("Voice session ended")
    await cancel_session_generations(session, TargetTurnOutcome.END_CALL)


@app.on_disconnect
async def on_disconnect(session: Session, event: SessionDisconnected) -> None:
    """Observe a peer transport disconnect."""
    del session, event
    logger.info("Voice transport disconnected")


@app.on_connection_terminating
def on_connection_terminating(session: Session) -> None:
    """Synchronously cancel application tasks whenever the handler exits."""
    cancel_session_generation_tasks(session, termination_outcome(session.termination))


if __name__ == "__main__":
    app.run()
