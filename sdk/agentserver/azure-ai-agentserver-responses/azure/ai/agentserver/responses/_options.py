# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Typed options for configuring the Responses server runtime."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:
    from .hosting._observability import CreateSpanHook


class ResponsesServerOptions:
    """Configuration values for hosting and runtime behavior."""

    def __init__(
        self,
        *,
        additional_server_version: str | None = None,
        default_model: str | None = None,
        default_fetch_history_count: int = 100,
        sse_keep_alive_interval_seconds: int | None = None,
        shutdown_grace_period_seconds: int = 10,
        create_span_hook: "CreateSpanHook | None" = None,
        resilient_background: bool = False,
        steerable_conversations: bool = False,
    ) -> None:
        if additional_server_version is not None:
            normalized = additional_server_version.strip()
            additional_server_version = normalized or None
        self.additional_server_version = additional_server_version

        if default_model is not None:
            normalized_model = default_model.strip()
            default_model = normalized_model or None
        self.default_model = default_model

        if sse_keep_alive_interval_seconds is not None and sse_keep_alive_interval_seconds <= 0:
            raise ValueError("sse_keep_alive_interval_seconds must be > 0 when set")
        self.sse_keep_alive_interval_seconds = sse_keep_alive_interval_seconds

        if default_fetch_history_count <= 0:
            raise ValueError("default_fetch_history_count must be > 0")
        self.default_fetch_history_count = default_fetch_history_count

        if shutdown_grace_period_seconds <= 0:
            raise ValueError("shutdown_grace_period_seconds must be > 0")
        self.shutdown_grace_period_seconds = shutdown_grace_period_seconds

        self.create_span_hook = create_span_hook

        # (Spec 024 Phase 5 — Proposal #5) ``store_disabled`` and
        # ``max_pending`` options DELETED. The file-backed response
        # provider is always available; per-conversation pending counts
        # are controlled by the underlying task primitive (which does
        # not expose a cap). ``replay_event_ttl_seconds`` is similarly
        # framework-internal — the stream registry hardcodes a sensible
        # default (10 minutes).
        # (Spec 024 Phase 4 — Proposal #9) Composition guard relaxed:
        # steerable_conversations and resilient_background are independent
        # options. Pre-Phase-4 the framework rejected
        # `steerable=True + resilient_bg=False`, assuming steering required
        # resilience for background responses. That assumption was wrong:
        # the chain extends across turns regardless of resilience, and
        # the lock/queue semantics are independent of the recovery
        # disposition. The guard is deleted.
        self.resilient_background = resilient_background
        self.steerable_conversations = steerable_conversations

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "ResponsesServerOptions":
        """Create options from environment variables.

        :param environ: Optional mapping of environment variables. Defaults to ``os.environ``.
        :type environ: Mapping[str, str] | None
        :returns: A new options instance populated from environment variables.
        :rtype: ResponsesServerOptions
        """
        source: Mapping[str, str] = os.environ if environ is None else environ

        def _first_non_empty(*keys: str) -> str | None:
            for key in keys:
                raw = source.get(key)
                if raw is None:
                    continue
                normalized = raw.strip()
                if normalized:
                    return normalized
            return None

        def _parse_positive_int(*keys: str) -> int | None:
            raw = _first_non_empty(*keys)
            if raw is None:
                return None
            try:
                value = int(raw)
            except ValueError as exc:
                raise ValueError(f"{keys[0]} must be a positive integer") from exc
            if value <= 0:
                raise ValueError(f"{keys[0]} must be > 0")
            return value

        default_fetch_history_count = _parse_positive_int(
            "DEFAULT_FETCH_HISTORY_ITEM_COUNT",
        )

        kwargs: dict[str, Any] = {}
        if default_fetch_history_count is not None:
            kwargs["default_fetch_history_count"] = default_fetch_history_count

        return cls(**kwargs)

    @property
    def sse_keep_alive_enabled(self) -> bool:
        """Return whether periodic SSE keep-alive comments are enabled.

        :rtype: bool
        """
        return self.sse_keep_alive_interval_seconds is not None
