# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Observability and server version header helpers."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from .._platform_headers import REQUEST_ID

if TYPE_CHECKING:
    from ._execution_context import _ExecutionContext


def build_platform_server_header(sdk_name: str, version: str, runtime: str, extra: str | None = None) -> str:
    """Build the platform server user-agent header value.

    :param sdk_name: SDK package name.
    :type sdk_name: str
    :param version: SDK package version.
    :type version: str
    :param runtime: Runtime marker, such as python/3.10.
    :type runtime: str
    :param extra: Optional additional user-agent suffix.
    :type extra: str | None
    :returns: Formatted user-agent header value.
    :rtype: str
    """
    base_value = f"{sdk_name}/{version} ({runtime})"
    return f"{base_value} {extra}".strip() if extra else base_value


@runtime_checkable
class CreateSpanHook(Protocol):
    """Hook contract for one-root-span-per-create observability."""

    def on_span_start(self, name: str, tags: dict[str, Any]) -> None:
        """Called when a create span starts.

        :param name: Span name.
        :type name: str
        :param tags: Initial span tags.
        :type tags: dict[str, Any]
        :return: None
        :rtype: None
        """

    def on_span_end(self, name: str, tags: dict[str, Any], error: BaseException | None) -> None:
        """Called when a create span ends.

        :param name: Span name.
        :type name: str
        :param tags: Final span tags.
        :type tags: dict[str, Any]
        :param error: The exception if the span ended with an error, or ``None``.
        :type error: BaseException | None
        :return: None
        :rtype: None
        """


class CreateSpan:
    """Mutable create-span helper used by hosting orchestration."""

    def __init__(
        self,
        *,
        name: str,
        tags: dict[str, Any],
        _hook: CreateSpanHook | None = None,
        _ended: bool = False,
    ) -> None:
        self.name = name
        self.tags = tags
        self._hook = _hook
        self._ended = _ended

    def set_tag(self, key: str, value: Any) -> None:
        """Set or overwrite one span tag.

        :param key: Tag key.
        :type key: str
        :param value: Tag value.
        :type value: Any
        :return: None
        :rtype: None
        """
        self.tags[key] = value

    def set_tags(self, values: dict[str, Any]) -> None:
        """Merge a set of tags into this span.

        :param values: Dictionary of tags to merge.
        :type values: dict[str, Any]
        :return: None
        :rtype: None
        """
        self.tags.update(values)

    def end(self, error: BaseException | None = None) -> None:
        """Complete the span exactly once.

        Subsequent calls are no-ops.

        :param error: The exception if the span ended with an error, or ``None``.
        :type error: BaseException | None
        :return: None
        :rtype: None
        """
        if self._ended:
            return

        self._ended = True
        if self._hook is None:
            return
        self._hook.on_span_end(self.name, dict(self.tags), error)


def start_create_span(name: str, tags: dict[str, Any], hook: CreateSpanHook | None = None) -> CreateSpan:
    """Start a create span and notify hook subscribers.

    :param name: Span name.
    :type name: str
    :param tags: Initial span tags.
    :type tags: dict[str, Any]
    :param hook: Optional hook to receive span lifecycle events.
    :type hook: CreateSpanHook | None
    :return: The started ``CreateSpan`` instance.
    :rtype: CreateSpan
    """
    span = CreateSpan(name=name, tags=dict(tags), _hook=hook)
    if hook is not None:
        hook.on_span_start(name, dict(span.tags))
    return span


def build_create_span_tags(
    ctx: "_ExecutionContext",
    *,
    request_id: str | None = None,
    project_id: str = "",
) -> dict[str, Any]:
    """Build a GenAI tag set for create spans from an execution context.

    :param ctx: Current execution context.
    :type ctx: _ExecutionContext
    :keyword request_id: Truncated ``X-Request-Id`` value, or ``None``.
    :keyword type request_id: str | None
    :keyword project_id: Foundry project ARM resource ID.
    :keyword type project_id: str
    :return: Dictionary of OpenTelemetry-style GenAI span tags.
    :rtype: dict[str, Any]
    """
    agent_name, agent_version, agent_id = _resolve_agent_fields(ctx.agent_reference)
    tags: dict[str, Any] = {
        "service.name": _SERVICE_NAME,
        "gen_ai.provider.name": _PROVIDER_NAME,
        "gen_ai.system": "responses",
        "gen_ai.operation.name": "invoke_agent",
        "gen_ai.response.id": ctx.response_id,
        "gen_ai.request.model": ctx.model,
        "gen_ai.agent.name": agent_name,
        "gen_ai.agent.id": agent_id if agent_id is not None else "",
        # Namespaced tags per spec §7.2
        "azure.ai.agentserver.responses.response_id": ctx.response_id,
        "azure.ai.agentserver.responses.conversation_id": ctx.conversation_id or "",
        "azure.ai.agentserver.responses.streaming": ctx.stream,
    }
    if project_id:
        tags["microsoft.foundry.project.id"] = project_id
    if agent_version is not None:
        tags["gen_ai.agent.version"] = agent_version
    if ctx.conversation_id is not None:
        tags["gen_ai.conversation.id"] = ctx.conversation_id
    if request_id is not None:
        tags["request.id"] = request_id
    return tags


_SERVICE_NAME = "azure.ai.agentserver"
_PROVIDER_NAME = "AzureAI Hosted Agents"
_MAX_REQUEST_ID_LEN = 256


def _initial_create_span_tags() -> dict[str, Any]:
    """Placeholder tags for the initial create span (before request context is known).

    Used to initialise :class:`CreateSpan` before :class:`_ExecutionContext` is
    available.  The real tags are written via :func:`build_create_span_tags`
    once the execution context has been constructed.

    :return: Minimal tag dict with fixed provider identifiers.
    :rtype: dict[str, Any]
    """
    return {
        "service.name": _SERVICE_NAME,
        "gen_ai.provider.name": _PROVIDER_NAME,
        "gen_ai.system": "responses",
        "gen_ai.operation.name": "invoke_agent",
    }


def extract_request_id(headers: Mapping[str, str]) -> str | None:
    """Extract and truncate the ``X-Request-Id`` header value.

    Returns the value truncated to 256 characters, or ``None`` when the
    header is absent.

    :param headers: HTTP request headers mapping.
    :type headers: Mapping[str, str]
    :return: Truncated request ID string, or ``None``.
    :rtype: str | None
    """
    raw = headers.get(REQUEST_ID) or headers.get("X-Request-Id")
    return raw[:_MAX_REQUEST_ID_LEN] if raw else None


def _resolve_agent_fields(
    agent_reference: MutableMapping[str, Any] | dict[str, Any] | None,
) -> tuple[str | None, str | None, str | None]:
    """Return ``(agent_name, agent_version, agent_id)`` from *agent_reference*.

    :param agent_reference: Agent reference mapping containing name and version fields.
    :type agent_reference: MutableMapping[str, Any] | dict[str, Any] | None
    :return: A tuple of (agent_name, agent_version, agent_id).
    :rtype: tuple[str | None, str | None, str | None]
    """
    if agent_reference is None or not isinstance(agent_reference, (dict, MutableMapping)):
        return None, None, None
    name = agent_reference.get("name") or None
    version = agent_reference.get("version") or None
    agent_id = f"{name}:{version}" if name and version else None
    return name, version, agent_id


def build_create_otel_attrs(
    ctx: "_ExecutionContext",
    *,
    request_id: str | None,
    project_id: str = "",
) -> dict[str, Any]:
    """Build the OTel span attribute dict for ``POST /responses``.

    :param ctx: Current execution context.
    :type ctx: _ExecutionContext
    :keyword request_id: Truncated ``X-Request-Id`` value, or ``None``.
    :keyword type request_id: str | None
    :keyword project_id: Foundry project ARM resource ID.
    :keyword type project_id: str
    :return: Attribute dict ready to be set on an OTel span.
    :rtype: dict[str, Any]
    """
    agent_name, agent_version, agent_id = _resolve_agent_fields(ctx.agent_reference)
    attrs: dict[str, Any] = {
        "gen_ai.response.id": ctx.response_id,
        "gen_ai.provider.name": _PROVIDER_NAME,
        "service.name": _SERVICE_NAME,
        "gen_ai.operation.name": "invoke_agent",
        "gen_ai.request.model": ctx.model or "",
        "gen_ai.agent.id": agent_id if agent_id is not None else "",
        # Namespaced tags per spec §7.2
        "azure.ai.agentserver.responses.response_id": ctx.response_id,
        "azure.ai.agentserver.responses.conversation_id": ctx.conversation_id or "",
        "azure.ai.agentserver.responses.streaming": ctx.stream,
    }
    if project_id:
        attrs["microsoft.foundry.project.id"] = project_id
    if ctx.conversation_id:
        attrs["gen_ai.conversation.id"] = ctx.conversation_id
    if agent_name:
        attrs["gen_ai.agent.name"] = agent_name
    if agent_version:
        attrs["gen_ai.agent.version"] = agent_version
    if request_id:
        attrs["request.id"] = request_id
    return attrs


class RecordedSpan:
    """Recorded span event for tests and diagnostics."""

    def __init__(
        self,
        *,
        name: str,
        tags: dict[str, Any],
        started_at: datetime,
        ended_at: datetime | None = None,
        error: BaseException | None = None,
    ) -> None:
        self.name = name
        self.tags = tags
        self.started_at = started_at
        self.ended_at = ended_at
        self.error = error


class InMemoryCreateSpanHook:
    """Simple in-memory hook for asserting span lifecycle in tests."""

    def __init__(self, spans: list[RecordedSpan] | None = None) -> None:
        self.spans: list[RecordedSpan] = spans if spans is not None else []

    def on_span_start(self, name: str, tags: dict[str, Any]) -> None:
        """Record a span start event.

        :param name: Span name.
        :type name: str
        :param tags: Span tags at start time.
        :type tags: dict[str, Any]
        :return: None
        :rtype: None
        """
        self.spans.append(
            RecordedSpan(
                name=name,
                tags=dict(tags),
                started_at=datetime.now(timezone.utc),
            )
        )

    def on_span_end(self, name: str, tags: dict[str, Any], error: BaseException | None) -> None:
        """Record a span end event.

        :param name: Span name.
        :type name: str
        :param tags: Final span tags.
        :type tags: dict[str, Any]
        :param error: The exception if the span ended with an error, or ``None``.
        :type error: BaseException | None
        :return: None
        :rtype: None
        """
        if not self.spans:
            self.on_span_start(name, tags)

        span = self.spans[-1]
        span.tags = dict(tags)
        span.error = error
        span.ended_at = datetime.now(timezone.utc)
