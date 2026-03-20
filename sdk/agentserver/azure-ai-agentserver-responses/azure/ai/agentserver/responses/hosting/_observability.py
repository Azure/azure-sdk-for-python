# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Observability and identity header helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol, runtime_checkable


def build_platform_server_header(sdk_name: str, version: str, runtime: str, extra: str | None = None) -> str:
    """Build the platform server identity header value.

    :param sdk_name: SDK package name.
    :param version: SDK package version.
    :param runtime: Runtime marker, such as python/3.10.
    :param extra: Optional additional identity suffix.
    :returns: Formatted identity header value.
    """
    base_value = f"{sdk_name}/{version} ({runtime})"
    return f"{base_value} {extra}".strip() if extra else base_value


@runtime_checkable
class CreateSpanHook(Protocol):
    """Hook contract for one-root-span-per-create observability."""

    def on_span_start(self, name: str, tags: dict[str, Any]) -> None:
        """Called when a create span starts."""

    def on_span_end(self, name: str, tags: dict[str, Any], error: Exception | None) -> None:
        """Called when a create span ends."""


@dataclass(slots=True)
class CreateSpan:
    """Mutable create-span helper used by hosting orchestration."""

    name: str
    tags: dict[str, Any]
    _hook: CreateSpanHook | None = None
    _ended: bool = False

    def set_tag(self, key: str, value: Any) -> None:
        """Set or overwrite one span tag."""
        self.tags[key] = value

    def set_tags(self, values: dict[str, Any]) -> None:
        """Merge a set of tags into this span."""
        self.tags.update(values)

    def end(self, error: Exception | None = None) -> None:
        """Complete the span exactly once."""
        if self._ended:
            return

        self._ended = True
        if self._hook is None:
            return
        self._hook.on_span_end(self.name, dict(self.tags), error)


def start_create_span(name: str, tags: dict[str, Any], hook: CreateSpanHook | None = None) -> CreateSpan:
    """Start a create span and notify hook subscribers."""
    span = CreateSpan(name=name, tags=dict(tags), _hook=hook)
    if hook is not None:
        hook.on_span_start(name, dict(span.tags))
    return span


def build_create_span_tags(
    *,
    response_id: str | None,
    model: str | None,
    agent_reference: dict[str, Any] | None,
    service_name: str,
) -> dict[str, Any]:
    """Build a baseline GenAI tag set for create spans."""
    agent_name = None
    agent_id = None
    if agent_reference is not None:
        agent_name = agent_reference.get("name")
        agent_version = agent_reference.get("version")
        if agent_name and agent_version:
            agent_id = f"{agent_name}:{agent_version}"

    return {
        "service.name": service_name,
        "gen_ai.system": "responses",
        "gen_ai.operation.name": "create_response",
        "gen_ai.response.id": response_id,
        "gen_ai.request.model": model,
        "gen_ai.agent.name": agent_name,
        "gen_ai.agent.id": agent_id,
    }


@dataclass(slots=True)
class RecordedSpan:
    """Recorded span event for tests and diagnostics."""

    name: str
    tags: dict[str, Any]
    started_at: datetime
    ended_at: datetime | None = None
    error: Exception | None = None


@dataclass(slots=True)
class InMemoryCreateSpanHook:
    """Simple in-memory hook for asserting span lifecycle in tests."""

    spans: list[RecordedSpan] = field(default_factory=list)

    def on_span_start(self, name: str, tags: dict[str, Any]) -> None:
        self.spans.append(
            RecordedSpan(
                name=name,
                tags=dict(tags),
                started_at=datetime.now(timezone.utc),
            )
        )

    def on_span_end(self, name: str, tags: dict[str, Any], error: Exception | None) -> None:
        if not self.spans:
            self.on_span_start(name, tags)

        span = self.spans[-1]
        span.tags = dict(tags)
        span.error = error
        span.ended_at = datetime.now(timezone.utc)
