# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Typed options for configuring the Responses server runtime."""

from __future__ import annotations

import os
from typing import Any, Mapping


class ResponsesServerOptions:
    """Configuration values for hosting and runtime behavior.

    This shape mirrors the .NET `ResponsesServerOptions` surface:
    - SSE keep-alive is disabled by default.
    - `default_model` is optional.
    - `default_fetch_history_count` defaults to 100.
    - `additional_server_identity` is optional.
    """

    def __init__(
        self,
        *,
        additional_server_identity: str | None = None,
        default_model: str | None = None,
        default_fetch_history_count: int = 100,
        sse_keep_alive_interval_seconds: int | None = None,
        shutdown_grace_period_seconds: int = 10,
        create_span_hook: Any | None = None,
    ) -> None:
        self.additional_server_identity = additional_server_identity
        self.default_model = default_model
        self.default_fetch_history_count = default_fetch_history_count
        self.sse_keep_alive_interval_seconds = sse_keep_alive_interval_seconds
        self.shutdown_grace_period_seconds = shutdown_grace_period_seconds
        self.create_span_hook = create_span_hook
        self._validate()

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "ResponsesServerOptions":
        """Create options from environment variables.

        Mirrors .NET environment-based configuration:
        - ``AZURE_AI_RESPONSES_SERVER_SSE_KEEPALIVE_INTERVAL`` (seconds)
        - ``AZURE_AI_RESPONSES_SERVER_DEFAULT_FETCH_HISTORY_ITEM_COUNT`` (integer)

        :param environ: Optional mapping to read environment variables from.
            Defaults to ``os.environ`` when None.
        :type environ: Mapping[str, str] | None
        :returns: A new options instance populated from the environment.
        :rtype: ResponsesServerOptions
        :raises ValueError: If an environment variable value is not a valid positive integer.
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
            "AZURE_AI_RESPONSES_SERVER_DEFAULT_FETCH_HISTORY_ITEM_COUNT",
        )
        sse_keep_alive_interval_seconds = _parse_positive_int(
            "AZURE_AI_RESPONSES_SERVER_SSE_KEEPALIVE_INTERVAL",
        )

        kwargs: dict[str, Any] = {}
        if default_fetch_history_count is not None:
            kwargs["default_fetch_history_count"] = default_fetch_history_count
        if sse_keep_alive_interval_seconds is not None:
            kwargs["sse_keep_alive_interval_seconds"] = sse_keep_alive_interval_seconds

        return cls(**kwargs)

    def _validate(self) -> None:
        """Validate and normalize option values.

        Strips whitespace from string fields and enforces positive-integer
        constraints on numeric fields.

        :raises ValueError: If any numeric option is not positive.
        """
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

    @property
    def sse_keep_alive_enabled(self) -> bool:
        """Return whether periodic SSE keep-alive comments are enabled.

        :returns: True if ``sse_keep_alive_interval_seconds`` is set, False otherwise.
        :rtype: bool
        """
        return self.sse_keep_alive_interval_seconds is not None
