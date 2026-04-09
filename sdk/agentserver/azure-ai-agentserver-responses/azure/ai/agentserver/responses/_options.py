# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Typed options for configuring the Responses server runtime."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:
    from .hosting._observability import CreateSpanHook


@dataclass
class ResponsesServerOptions:
    """Configuration values for hosting and runtime behavior."""

    additional_server_identity: str | None = None
    default_model: str | None = None
    default_fetch_history_count: int = 100
    sse_keep_alive_interval_seconds: int | None = None
    shutdown_grace_period_seconds: int = 10
    create_span_hook: CreateSpanHook | None = None

    def __post_init__(self) -> None:
        if self.additional_server_identity is not None:
            normalized = self.additional_server_identity.strip()
            self.additional_server_identity = normalized or None
        if self.default_model is not None:
            normalized_model = self.default_model.strip()
            self.default_model = normalized_model or None
        if self.sse_keep_alive_interval_seconds is not None and self.sse_keep_alive_interval_seconds <= 0:
            raise ValueError("sse_keep_alive_interval_seconds must be > 0 when set")
        if self.default_fetch_history_count <= 0:
            raise ValueError("default_fetch_history_count must be > 0")
        if self.shutdown_grace_period_seconds <= 0:
            raise ValueError("shutdown_grace_period_seconds must be > 0")

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "ResponsesServerOptions":
        """Create options from environment variables."""
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
        """Return whether periodic SSE keep-alive comments are enabled."""
        return self.sse_keep_alive_interval_seconds is not None
