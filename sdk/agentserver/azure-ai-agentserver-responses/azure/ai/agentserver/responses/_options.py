"""Typed options for configuring the Responses server runtime."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ResponsesServerOptions:
    """Configuration values for hosting and runtime behavior.

    This shape mirrors the .NET `ResponsesServerOptions` surface:
    - SSE keep-alive is disabled by default.
    - `default_model` is optional.
    - `default_fetch_history_count` defaults to 100.
    - `additional_server_identity` is optional.
    """

    default_fetch_history_count_value: int = 100
    additional_server_identity: str | None = None
    default_model: str | None = None
    default_fetch_history_count: int = default_fetch_history_count_value
    sse_keep_alive_interval_seconds: int | None = None

    def __post_init__(self) -> None:
        """Validate and normalize option values."""
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

    @property
    def sse_keep_alive_enabled(self) -> bool:
        """Return whether periodic SSE keep-alive comments are enabled."""
        return self.sse_keep_alive_interval_seconds is not None
