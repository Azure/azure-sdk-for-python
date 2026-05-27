# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Durable orchestrator — wraps existing response execution in the task primitive.

This module bridges the Responses API and the durable tasks system. It creates
a ``@task``-decorated function whose body calls ``_run_background_non_stream``
(the existing pipeline). The developer's handler is unchanged — the task wrapping
is a transparent infrastructure concern.

Architecture:
  POST /responses → _ResponseOrchestrator.run_background()
    → (durable=True)  → DurableResponseOrchestrator.start_durable(...)
        → task_fn.start(task_id=derived_id, input=execution_params)
          → task body → _run_background_non_stream(...)  [existing pipeline]
    → (durable=False) → asyncio.create_task(_shielded_runner())  [unchanged]
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import logging
from typing import TYPE_CHECKING, Any, Callable

from azure.ai.agentserver.core.durable import (
    Task,
    TaskContext,
    TaskConflictError,
    task,
)

from .._durability_context import (
    DurabilityContext,
    DurabilityEntryMode,
    _FilteredMetadata,
)
from .._options import ResponsesServerOptions
from ..models.runtime import CancellationReason
from ._task_id import derive_task_id

if TYPE_CHECKING:
    from .._response_context import ResponseContext
    from ..models._generated import CreateResponse
    from ..models.runtime import ResponseExecution
    from ..store._base import ResponseProviderProtocol
    from ._runtime_state import _RuntimeState

logger = logging.getLogger("azure.ai.agentserver.responses.durable")

# Framework-internal metadata key prefix
_FW_PREFIX = "_framework."
_FW_RESPONSE_ID = f"{_FW_PREFIX}response_id"
_FW_LAST_SEQ = f"{_FW_PREFIX}last_sequence_number"
_FW_BACKGROUND = f"{_FW_PREFIX}background"


def _map_entry_mode(task_entry_mode: str) -> DurabilityEntryMode:
    """Map task primitive entry_mode to DurabilityContext entry_mode.

    Task 'resumed' (new turn arriving) maps to 'fresh' for the handler —
    from the handler developer's perspective, a resume is just a new turn.
    """
    if task_entry_mode == "recovered":
        return "recovered"
    return "fresh"  # "fresh" and "resumed" both → "fresh"


class DurableResponseOrchestrator:
    """Wraps the existing response execution pipeline in the durable task primitive.

    When ``durable_background=True``, the normal ``asyncio.create_task()`` path
    is replaced by ``task_fn.start()``. The task body reconstructs the execution
    context and calls ``_run_background_non_stream`` — the same function the
    non-durable path uses. This ensures:
    - Zero handler code changes (same create_fn, same ResponseContext)
    - Crash recovery via task primitive lease + re-entry
    - DurabilityContext populated before handler invocation

    :param create_fn: The handler factory (bound ``create_fn`` method).
    :param options: Server options (steerable, max_pending, etc.).
    :param provider: Response persistence provider.
    """

    def __init__(
        self,
        *,
        create_fn: Callable[..., Any],
        options: ResponsesServerOptions,
        provider: "ResponseProviderProtocol",
    ) -> None:
        self._create_fn = create_fn
        self._options = options
        self._provider = provider

        # Create the internal task function
        self._task_fn: Task[dict[str, Any], None] = self._create_task_fn()

    @property
    def task_fn(self) -> Task[dict[str, Any], None]:
        """The underlying durable task descriptor."""
        return self._task_fn

    def _create_task_fn(self) -> Task[dict[str, Any], None]:
        """Create the @task-decorated function that wraps _run_background_non_stream."""
        orchestrator = self

        @task(
            name="responses_durable_background",
            steerable=self._options.steerable_conversations,
            max_pending=self._options.max_pending,
            ephemeral=False,  # Task lives for conversation lifetime
            store_input=True,
        )
        async def _durable_response_task(ctx: TaskContext[dict[str, Any]]) -> None:
            """Task body: executes the response pipeline with durability context.

            On fresh entry: runs the full pipeline via _run_background_non_stream.
            On recovery: re-runs the pipeline (handler is re-invoked from scratch).
            After completion: suspends awaiting the next turn.
            """
            await orchestrator._execute_in_task(ctx)

        return _durable_response_task

    async def _execute_in_task(self, ctx: TaskContext[dict[str, Any]]) -> None:
        """Execute the response pipeline inside the task body.

        This is the re-entrant function. On each entry:
        1. Builds DurabilityContext from TaskContext
        2. Attaches it to the ResponseContext
        3. Delegates to _run_background_non_stream (existing pipeline)
        4. Persists last_sequence_number to metadata
        5. Suspends (task stays alive for next turn)
        """
        # Import here to avoid circular imports
        from ._orchestrator import (
            _run_background_non_stream,
        )  # pylint: disable=import-outside-toplevel

        params = ctx.input
        entry_mode = _map_entry_mode(ctx.entry_mode)
        is_recovery = entry_mode == "recovered"

        # Track response_id in framework metadata
        response_id = params["response_id"]
        if ctx.metadata.get(_FW_RESPONSE_ID) is None:
            ctx.metadata[_FW_RESPONSE_ID] = response_id

        # Store background flag on first entry for recovery decisions
        if _FW_BACKGROUND not in ctx.metadata:
            ctx.metadata[_FW_BACKGROUND] = params.get("background", True)

        # Non-background recovery: persist as failed without re-invoking handler.
        # Non-background responses are tied to the HTTP connection lifetime —
        # if the server crashes, the client is already disconnected, so
        # re-invocation is pointless. Mark failed and suspend.
        if is_recovery and not ctx.metadata.get(_FW_BACKGROUND, True):
            logger.info(
                "Non-background task recovered (response_id=%s) — marking failed",
                response_id,
            )
            await self._persist_non_bg_crash_failed(response_id, params)
            if self._options.steerable_conversations:
                return await ctx.suspend(reason="non_bg_crash_failed")
            return

        # Build DurabilityContext for the handler.
        # Note: `last_snapshot` was intentionally removed — the response object is
        # only persisted at `response.created` and at terminal events, so
        # a between-states snapshot is never useful. Handlers build their
        # resumption response from upstream framework state.
        durability_ctx = DurabilityContext(
            entry_mode=entry_mode,
            run_attempt=ctx.run_attempt,
            was_steered=ctx.was_steered,
            pending_inputs=len(ctx.pending_inputs),
            metadata=ctx.metadata,
        )

        # The execution params contain everything _run_background_non_stream needs.
        # The record and context are reconstructed from serialized state.
        # For Phase 1, we pass the durability_ctx through the response_context
        # which is already attached to the record.
        context: ResponseContext | None = params.get("_context_ref")
        if context is not None:
            context._durability = durability_ctx  # pylint: disable=protected-access

        record: ResponseExecution | None = params.get("_record_ref")
        if record is None:
            # This shouldn't happen in normal flow — but on recovery we need
            # to reconstruct. For Phase 1 (no recovery yet), log and return.
            logger.error(
                "No record reference in task input (response_id=%s, entry_mode=%s)",
                response_id,
                entry_mode,
            )
            return

        # Bridge task cancellation → response cancellation signal
        cancellation_signal: asyncio.Event = params.get("_cancel_ref", asyncio.Event())
        cancel_bridge: asyncio.Task[None] | None = None
        if not ctx.cancel.is_set():

            async def _bridge() -> None:
                await ctx.cancel.wait()
                if context is not None and context.cancellation_reason is None:
                    context.cancellation_reason = CancellationReason.STEERED
                cancellation_signal.set()

            cancel_bridge = asyncio.create_task(_bridge())
        else:
            if context is not None and context.cancellation_reason is None:
                context.cancellation_reason = CancellationReason.STEERED
            cancellation_signal.set()

        try:
            await _run_background_non_stream(
                create_fn=self._create_fn,
                parsed=params["_parsed_ref"],
                context=context,
                cancellation_signal=cancellation_signal,
                record=record,
                response_id=response_id,
                agent_reference=params.get("agent_reference"),
                model=params.get("model"),
                provider=self._provider,
                store=params.get("store", True),
                agent_session_id=params.get("agent_session_id"),
                conversation_id=params.get("conversation_id"),
                history_limit=params.get("history_limit", 100),
                runtime_state=params.get("_runtime_state_ref"),
            )
        finally:
            if cancel_bridge is not None and not cancel_bridge.done():
                cancel_bridge.cancel()

        # Suspend — task stays alive for next turn in steerable mode
        if self._options.steerable_conversations:
            return await ctx.suspend(reason="awaiting_next_turn")

    async def start_durable(
        self,
        *,
        record: "ResponseExecution",
        ctx_params: dict[str, Any],
    ) -> bool:
        """Start the durable task for a background response.

        Called by _ResponseOrchestrator.run_background() when durable_background=True.
        The task takes over responsibility for execution and crash recovery.

        :param record: The mutable execution record (same as non-durable path).
        :param ctx_params: Execution parameters dict containing all values needed
            by _run_background_non_stream plus object references.
        :returns: True if task was freshly started, False if input was queued
            on an already-active steerable task.
        """
        task_id = derive_task_id(
            agent_name=ctx_params.get("agent_name", "default"),
            session_id=ctx_params.get("session_id", ""),
            conversation_id=ctx_params.get("conversation_id"),
            previous_response_id=ctx_params.get("previous_response_id"),
            response_id=ctx_params["response_id"],
            steerable=self._options.steerable_conversations,
        )

        try:
            task_run = await self._task_fn.start(
                task_id=task_id,
                input=ctx_params,
            )
            # Store the task run reference on the record for observability
            record.durable_task_run = task_run  # type: ignore[attr-defined]
            return True  # Freshly started
        except TaskConflictError:
            # Task already running (e.g. steerable conversation in progress)
            # This is expected for steerable mode — the input is queued
            logger.debug(
                "Task %s already active — input queued for steering",
                task_id,
            )
            return False  # Input queued on existing task

    async def _persist_non_bg_crash_failed(
        self,
        response_id: str,
        params: dict[str, Any],
    ) -> None:
        """Persist a non-background response as failed after crash recovery.

        Non-background responses cannot be re-invoked (client disconnected),
        so we mark them as failed with a server_crashed error code.
        """
        from ..models._generated import (
            ResponseObject,
        )  # pylint: disable=import-outside-toplevel

        failed_response = {
            "id": response_id,
            "object": "response",
            "status": "failed",
            "output": [],
            "error": {
                "type": "server_error",
                "code": "server_crashed",
                "message": "Server crashed during non-background response execution",
            },
        }

        try:
            isolation = None
            context = params.get("_context_ref")
            if context is not None:
                isolation = getattr(context, "isolation", None)
            await self._provider.update_response(
                ResponseObject(failed_response), isolation=isolation
            )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error(
                "Failed to persist non-bg crash failure for %s: %s",
                response_id,
                exc,
            )
