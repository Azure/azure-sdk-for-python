# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""ResponseContext for user-defined response execution.

(Spec 024 Phase 5) Flat handler-facing surface — the pre-Phase-5
``ResilienceContext`` indirection is collapsed; recovery + steering
fields live directly on :class:`ResponseContext`. The cancellation
surface mirrors the task primitive's composing-cause shape (separate
``cancel`` + ``shutdown`` events, independent cause booleans).
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, NoReturn, Sequence, cast
from .models._generated import (
    CreateResponse,
    Item,
    OutputItem,
    ResponseObject,
)
from .models._generated._unions import InputParam
from .models._helpers import get_input_expanded, to_item, to_output_item
from .models.runtime import ResponseModeFlags

if TYPE_CHECKING:
    from azure.ai.agentserver.core.tasks import TaskContext as _CoreTaskContext

    from .store._base import ResponseProviderProtocol


# (Spec 024 Phase 5 — Proposal #11) ``_ExitForRecoverySentinel`` is the
# framework's internal sentinel that leaves a response ``in_progress`` for
# next-lifetime recovery. The public handler idiom is
# ``await context.exit_for_recovery()`` which raises
# :class:`ResponseExitForRecovery`; the orchestrator translates that to this
# core sentinel at the resilient task boundary.
# Falls back to ``Any`` when the core module is unavailable at import
# time (e.g. for type-stub generation).
try:
    from azure.ai.agentserver.core.tasks._context import _ExitForRecovery as _ExitForRecoverySentinel
except ImportError:  # pragma: no cover - defensive
    _ExitForRecoverySentinel = Any  # type: ignore[assignment,misc]

ExitForRecoverySignal = _ExitForRecoverySentinel
"""Sentinel type the framework uses internally to leave a response
``in_progress`` for next-lifetime recovery. Handlers do not use this directly —
they call ``await context.exit_for_recovery()`` (see
:class:`ResponseExitForRecovery`)."""


class ResponseExitForRecovery(BaseException):
    """Control-flow signal raised by :meth:`ResponseContext.exit_for_recovery`.

    Subclasses :class:`BaseException` (NOT :class:`Exception`) — like
    :class:`asyncio.CancelledError` / :class:`GeneratorExit` — so a handler's
    broad ``except Exception`` cannot accidentally swallow the recovery signal.
    ``try/finally`` cleanup still runs. The framework catches it at the resilient
    task boundary and leaves the response ``in_progress`` for the next-lifetime
    recovery scanner.

    Handlers never construct or catch this directly; they simply
    ``await context.exit_for_recovery()`` (which raises it), in any handler
    shape — coroutine, async generator, or sync.
    """


class PlatformContext:
    """Platform-injected identity context for multi-tenant state partitioning.

    The Foundry hosting platform injects ``x-agent-user-id`` and (on container
    protocol version ``2.0.0``) ``x-agent-foundry-call-id`` headers on every
    protocol request (not on health probes):

    - ``user_id_key`` — global, cross-agent per-user partition key; the same user
      yields the same value regardless of which agent they interact with.  Use it
      as the primary partition key for per-user state.
    - ``call_id`` — opaque per-request call identifier (protocol ``2.0.0`` only).
      Providers **MUST** forward it on outbound Foundry API calls so 1P services
      can resolve the server-side-stored caller context.  Never parse it.

    When a header is absent (e.g. local development, or ``call_id`` under protocol
    version ``1.0.0``), the corresponding field is ``None``.  When the platform
    sends the header with an empty value, the field is an empty string.  Use
    ``is None`` to detect whether the header was present at all.
    """

    def __init__(self, *, user_id_key: str | None = None, call_id: str | None = None) -> None:
        self.user_id_key = user_id_key
        """Partition key for per-user state (from ``x-agent-user-id``).
        ``None`` when the header was not sent."""

        self.call_id = call_id
        """Opaque per-request call identifier (from ``x-agent-foundry-call-id``).
        ``None`` when the header was not sent (protocol ``1.0.0`` or local dev)."""


class ResponseContext:  # pylint: disable=too-many-instance-attributes
    """Runtime context exposed to response handlers and used by hosting orchestration.

    Public surface (post-spec-024 Phase 5):

    Identity / request shape:
        - :attr:`response_id` — stable id for this response.
        - :attr:`mode_flags` — bg/stream/store flags.
        - :attr:`request` — parsed CreateResponse.
        - :attr:`created_at` — UTC timestamp.
        - :attr:`client_headers` / :attr:`query_parameters` — request metadata.
        - :attr:`platform_context` — tenant partition identity (user id / call id).
        - :attr:`conversation_id` / :attr:`previous_response_id`.
        - :attr:`conversation_chain_id` — derived chain identifier.

    Recovery + steering classifiers (Proposal #6/#10/#13):
        - :attr:`is_recovery` — True on a crash-recovered re-entry.
        - :attr:`is_steered_turn` — True on a steering-drain re-entry.
        - :attr:`pending_input_count` — queued steering inputs (live count).

    Cancellation surface (Proposal #11):
        - :attr:`cancel` — asyncio.Event set when any cancel cause fires.
        - :attr:`shutdown` — asyncio.Event set when the server is shutting down.
        - :attr:`client_cancelled` — bool, True for explicit /cancel
          endpoint OR non-background POST disconnect.
        - :meth:`exit_for_recovery` — opt-in graceful-shutdown primitive
          (call as a bare ``await context.exit_for_recovery()`` — it raises
          internally; works in any handler shape).

    Async helpers:
        - :meth:`get_input_items` / :meth:`get_input_text` / :meth:`get_history`.
    """

    # Class-level type annotations for the public surface (Spec 024
    # Phase 5 — Proposal #10/#11/#13). Listed here so `get_type_hints`
    # and IDEs surface the precise types without scanning ``__init__``.
    response_id: str
    mode_flags: ResponseModeFlags
    request: "CreateResponse | None"
    created_at: datetime
    client_headers: dict[str, str]
    query_parameters: dict[str, str]
    platform_context: PlatformContext
    conversation_id: "str | None"
    is_recovery: bool
    is_steered_turn: bool
    pending_input_count: int
    shutdown: asyncio.Event
    client_cancelled: bool
    persisted_response: ResponseObject | None

    def __init__(  # pylint: disable=too-many-arguments
        self,
        *,
        response_id: str,
        mode_flags: ResponseModeFlags,
        request: CreateResponse | None = None,
        created_at: datetime | None = None,
        provider: "ResponseProviderProtocol | None" = None,
        input_items: list[InputParam] | list[OutputItem] | None = None,
        previous_response_id: str | None = None,
        conversation_id: str | None = None,
        history_limit: int = 100,
        client_headers: dict[str, str] | None = None,
        query_parameters: dict[str, str] | None = None,
        platform_context: PlatformContext | None = None,
        prefetched_history_ids: list[str] | None = None,
        steerable: bool = False,
        agent_name: str = "",
        session_id: str = "",
    ) -> None:
        self.response_id = response_id
        self.mode_flags = mode_flags
        self.request = request
        self.created_at = created_at if created_at is not None else datetime.now(timezone.utc)
        self.client_headers: dict[str, str] = client_headers or {}
        self.query_parameters: dict[str, str] = query_parameters or {}
        self.platform_context: PlatformContext = platform_context if platform_context is not None else PlatformContext()
        self._provider: "ResponseProviderProtocol | None" = provider
        _items: list[Any]
        if input_items is not None:
            _items = list(input_items)
        else:
            _items = []
        self._input_items: list[Any] = _items
        self._previous_response_id: str | None = previous_response_id
        self.conversation_id: str | None = conversation_id
        self._history_limit: int = history_limit
        self._input_items_resolved_cache: Sequence[Item] | None = None
        self._input_items_unresolved_cache: Sequence[Item] | None = None
        self._history_cache: Sequence[OutputItem] | None = None
        self._prefetched_history_ids: list[str] | None = prefetched_history_ids
        # Stash the deployment's ``steerable_conversations`` option so
        # ``conversation_chain_id`` resolves the correct chain partition: for
        # non-steerable chains each fork is its own identity (full response_id),
        # while steerable chains share the partition key of the sequential chain.
        self._steerable: bool = steerable
        # Agent + session identity used to scope ``conversation_chain_id`` (and
        # the resilient task id, which is the same hash with a fixed prefix).
        self._agent_name: str = agent_name
        self._session_id: str = session_id

        # (Spec 024 Phase 5 — Proposal #6/#10/#13) Flattened recovery +
        # steering classifiers. Defaults represent a fresh non-recovered
        # handler invocation; the orchestrator overrides them when
        # constructing the context for a recovery / steering-drain entry.
        self.is_recovery: bool = False
        self.is_steered_turn: bool = False
        self.pending_input_count: int = 0
        # (Spec 025 §A.3) Entry-only cached snapshot of the persisted response,
        # populated by the orchestrator on the recovery path so a recovered
        # handler can seed its stream from already-persisted items. ``None`` on
        # fresh entries; never refreshed mid-execution.
        self.persisted_response: ResponseObject | None = None
        # Composing cancellation surface. ``_cancellation_signal`` is
        # the per-request cancel Event delivered to the handler as the
        # 3rd positional argument; it fires on /cancel API calls, client
        # disconnect on non-bg create, or steering pressure. It is
        # framework-internal — handlers should observe their 3rd
        # positional ``cancellation_signal`` parameter, not the private
        # attribute. ``shutdown`` is a DISTINCT Event — server shutdown
        # does NOT fire the cancel signal; handlers that care about
        # both must observe each independently.
        # ``client_cancelled`` is a cause flag stamped by the /cancel
        # endpoint and the disconnect monitor.
        self._cancellation_signal: asyncio.Event = asyncio.Event()
        self.shutdown: asyncio.Event = asyncio.Event()
        self.client_cancelled: bool = False

        # Private link to the underlying TaskContext (set by the
        # orchestrator on resilient paths) — enables exit_for_recovery to
        # delegate to the framework's recovery sentinel.
        self._task_context: "_CoreTaskContext[Any] | None" = None

    @property
    def conversation_chain_id(self) -> str:
        """Stable identifier for the multi-turn conversation chain.

        Returns an opaque, agent/session-scoped hex id that is the **same for
        every turn** of a conversation chain. It is derived from the partition
        key embedded in the chain's response IDs (chained response IDs all carry
        the same embedded key), so it stays stable across turns and across crash
        recovery without any history walk. The resilient task backing the
        conversation uses this same hash (with a fixed prefix), so the two never
        drift apart.

        Priority for the underlying chain partition:

        1. ``conversation_id`` if supplied on the request.
        2. ``previous_response_id`` (steerable chains) — the shared partition key
           of the sequential chain.
        3. ``response_id`` — for the first turn, or as the per-fork identity when
           ``steerable_conversations`` is disabled.

        Handlers use this id as a key into application-side conversation state
        (e.g., an upstream SDK session id, per-conversation rate limits, or a
        conversation index): store it in a resilient side store and look it up on
        recovery to re-attach to the prior session.

        Known limitation: the identity is derived from framework-generated IDs. A
        client that supplies its own ``response_id`` (via ``x-agent-response-id``
        or an explicit request field) carrying a mismatched embedded partition can
        shift the chain identity for later turns.

        :rtype: str
        """
        # Local import to avoid a top-level cycle with hosting.
        from .hosting._chain_id import derive_conversation_chain_id  # pylint: disable=import-outside-toplevel

        return derive_conversation_chain_id(
            conversation_id=self.conversation_id,
            previous_response_id=self._previous_response_id,
            response_id=self.response_id,
            agent_name=self._agent_name,
            session_id=self._session_id,
            steerable=self._steerable,
        )

    async def exit_for_recovery(self) -> "NoReturn":
        """Defer this response to next-lifetime recovery — one idiom, any shape.

        Call it as a bare statement, in coroutine, async-generator, or sync
        handlers alike::

            if context.shutdown.is_set():
                await context.exit_for_recovery()

        It **raises** :class:`ResponseExitForRecovery` internally — it NEVER
        returns. The framework catches the signal at the resilient task boundary
        and leaves the response ``in_progress`` so the handler is re-invoked on
        the next process start (for ``resilient_background=True`` responses).

        (Streaming handlers that simply ``return`` without emitting a terminal
        while ``context.shutdown`` is set also recover via the implicit
        fallback; ``await context.exit_for_recovery()`` is the explicit,
        recommended form.)

        :raises RuntimeError: When called outside a resilient task body (e.g. on a
            ``store=false`` request where there is no task to defer).
        :raises ResponseExitForRecovery: Always, on success — the control-flow
            signal the framework catches.
        :rtype: NoReturn
        """
        if self._task_context is None:
            raise RuntimeError(
                "context.exit_for_recovery() can only be called inside a resilient "
                "response handler (store=true). For store=false responses there is "
                "no task to defer for recovery."
            )
        raise ResponseExitForRecovery()

    async def get_input_items(self, *, resolve_references: bool = True) -> Sequence[Item]:
        """Return the caller's input items as :class:`Item` subtypes.

        Inline items are returned as-is — the same :class:`Item` subtypes from
        the original request (e.g. :class:`ItemMessage`,
        :class:`FunctionCallOutputItemParam`).
        :class:`ItemReferenceParam` entries are batch-resolved via the
        provider and converted back to :class:`Item` subtypes.
        Unresolvable references (provider returns ``None``) are silently dropped.

        :keyword resolve_references: When ``True`` (default),
            :class:`ItemReferenceParam` items are resolved via the provider and
            returned as their concrete :class:`Item` subtype.  When ``False``,
            item references are left as :class:`ItemReferenceParam` in the
            returned sequence.
        :type resolve_references: bool
        :returns: A tuple of input items.
        :rtype: Sequence[Item]
        """
        if resolve_references:
            return await self._get_input_items_resolved()
        return await self._get_input_items_unresolved()

    async def get_input_text(self, *, resolve_references: bool = True) -> str:
        """Resolve input items and extract all text content as a single string.

        Convenience method that calls :meth:`get_input_items`, filters for
        :class:`ItemMessage` items, expands their content, and joins all
        :class:`MessageContentInputTextContent` text values with newline
        separators.

        :keyword resolve_references: When ``True`` (default), item references
            are resolved before extracting text.
        :type resolve_references: bool
        :returns: The combined text content, or ``""`` if no text found.
        :rtype: str
        """
        items = await self.get_input_items(resolve_references=resolve_references)
        texts: list[str] = []
        for item in items:
            if isinstance(item, dict) and item.get("type") == "message":
                for part in cast("list[Any]", item.get("content") or []):
                    if isinstance(part, dict) and part.get("type") == "input_text":
                        text = part.get("text")
                        if text is not None:
                            texts.append(text)
        return "\n".join(texts)

    async def _get_input_items_for_persistence(self) -> Sequence[OutputItem]:
        """Return input items as :class:`OutputItem` for storage persistence.

        The orchestrator needs :class:`OutputItem` instances when creating the
        stored response.  This method resolves references (so stored items are
        always concrete), converts each :class:`Item` to :class:`OutputItem`,
        and caches the result.

        :returns: A tuple of output items suitable for persistence.
        :rtype: Sequence[OutputItem]
        """
        items = await self.get_input_items(resolve_references=True)
        return tuple(out for item in items if (out := to_output_item(item, self.response_id)) is not None)

    # ------------------------------------------------------------------
    # Private resolution helpers (cached independently per mode)
    # ------------------------------------------------------------------

    async def _get_input_items_resolved(self) -> Sequence[Item]:
        """Resolve and cache input items with references resolved.

        :returns: A tuple of resolved input items.
        :rtype: Sequence[Item]
        """
        if self._input_items_resolved_cache is not None:
            return self._input_items_resolved_cache

        expanded = self._expand_input()
        if not expanded:
            self._input_items_resolved_cache = ()
            return self._input_items_resolved_cache

        # Collect ItemReferenceParam positions and IDs for batch resolution.
        reference_ids: list[str] = []
        reference_positions: list[int] = []
        results: list[Item | None] = []

        for item in expanded:
            if isinstance(item, dict) and item.get("type") == "item_reference":
                item_id = item.get("id")
                if not isinstance(item_id, str):
                    continue
                reference_ids.append(item_id)
                reference_positions.append(len(results))
                results.append(None)  # placeholder
            else:
                results.append(item)

        # Batch-resolve references if we have a provider and pending refs.
        if reference_ids and self._provider is not None:
            resolved = await self._provider.get_items(reference_ids, context=self.platform_context)
            for idx, pos in enumerate(reference_positions):
                if idx < len(resolved) and resolved[idx] is not None:
                    converted = to_item(resolved[idx])  # type: ignore[arg-type]
                    if converted is not None:
                        results[pos] = converted

        # Remove unresolved (None) placeholders.
        self._input_items_resolved_cache = tuple(item for item in results if item is not None)
        return self._input_items_resolved_cache

    async def _get_input_items_unresolved(self) -> Sequence[Item]:
        """Return input items without resolving references.

        :returns: A tuple of unresolved input items.
        :rtype: Sequence[Item]
        """
        if self._input_items_unresolved_cache is not None:
            return self._input_items_unresolved_cache

        expanded = self._expand_input()
        self._input_items_unresolved_cache = tuple(expanded)
        return self._input_items_unresolved_cache

    def _expand_input(self) -> list[Item]:
        """Normalize raw input into typed Item instances.

        :returns: A list of typed Item instances.
        :rtype: list[Item]
        """
        if self.request is not None:
            return get_input_expanded(self.request)
        return list(self._input_items)  # type: ignore[arg-type]

    async def get_history(self) -> Sequence[OutputItem]:
        """Resolve and cache conversation history items via the provider.

        When prefetched history IDs are available (from eager validation),
        the provider's ``get_history_item_ids`` call is skipped and only
        ``get_items`` is invoked to materialise the items.

        :returns: A tuple of conversation history items.
        :rtype: Sequence[OutputItem]
        """
        if self._history_cache is not None:
            return self._history_cache

        if self._provider is None:
            self._history_cache = ()
            return self._history_cache

        # No conversation context — nothing to look up.
        if not self._previous_response_id and not self.conversation_id:
            self._history_cache = ()
            return self._history_cache

        # Use eagerly-prefetched IDs when available; otherwise call provider.
        if self._prefetched_history_ids is not None:
            item_ids = self._prefetched_history_ids
        else:
            item_ids = await self._provider.get_history_item_ids(
                self._previous_response_id,
                self.conversation_id,
                self._history_limit,
                context=self.platform_context,
            )
        if not item_ids:
            self._history_cache = ()
            return self._history_cache

        items = await self._provider.get_items(item_ids, context=self.platform_context)
        self._history_cache = tuple(item for item in items if item is not None)
        return self._history_cache
