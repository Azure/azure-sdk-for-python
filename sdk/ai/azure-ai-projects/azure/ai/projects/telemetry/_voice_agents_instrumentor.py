# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Opt-in Voice Agents tracing using the existing Foundry tracer and settings."""

from asyncio import CancelledError  # pylint: disable=do-not-import-asyncio
import functools
import importlib
import inspect
import json
import logging
import threading
import time
import weakref
from collections import deque
from collections.abc import Mapping
from contextlib import contextmanager, nullcontext
from typing import Any, Callable, Optional
from urllib.parse import urlsplit

from azure.core.settings import settings
from azure.core.tracing import AbstractSpan

from ._utils import (
    ERROR_TYPE,
    GEN_AI_AGENT_ID,
    GEN_AI_AGENT_NAME,
    GEN_AI_AGENT_TYPE,
    GEN_AI_AGENT_VERSION,
    GEN_AI_CONVERSATION_ID,
    GEN_AI_INPUT_MESSAGES,
    GEN_AI_OPERATION_NAME,
    GEN_AI_OUTPUT_MESSAGES,
    GEN_AI_REQUEST_MODEL,
    GEN_AI_RESPONSE_ID,
    GEN_AI_SYSTEM_MESSAGE,
    GEN_AI_TOOL_CALL_ID,
    GEN_AI_TOOL_NAME,
    GEN_AI_USAGE_INPUT_TOKENS,
    GEN_AI_USAGE_OUTPUT_TOKENS,
    OperationName,
    start_span,
)
from . import _responses_instrumentor

_LOGGER = logging.getLogger("azure.ai.projects.realtime")
_PREFIX = "az.ai.voice_agents."
_MAX_RESPONSES = 64
_MAX_PARTS = 32
_MAX_CONTENT = 4096
_ERROR_TYPES = {
    "TypeError",
    "ValueError",
    "RuntimeError",
    "ConnectionError",
    "ConnectionResetError",
    "TimeoutError",
    "ClientAuthenticationError",
    "HttpResponseError",
    "ResourceNotFoundError",
    "ServiceRequestError",
    "ServiceResponseError",
    "invalid_request_error",
    "server_error",
    "authentication_error",
    "rate_limit_error",
}
_ERROR_CODES = {
    "agent_disabled",
    "invalid_request",
    "invalid_request_error",
    "invalid_event",
    "invalid_state",
    "rate_limit_exceeded",
    "insufficient_quota",
    "session_expired",
    "authentication_error",
    "permission_denied",
    "server_error",
}
_ORIGINALS: dict[tuple[type, str], Callable] = {}
_SESSIONS: weakref.WeakSet = weakref.WeakSet()


def _record(action: Callable[[], Any]) -> Any:
    # Exporter/provider failures must not change service results or expose their messages.
    try:
        return action()
    except Exception:  # pylint: disable=broad-exception-caught
        _LOGGER.warning("Unable to record Voice Agents telemetry.")
        return None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _limited(value: Any) -> Optional[str]:
    return value[:_MAX_CONTENT] if isinstance(value, str) else None


def _identifier(value: Any) -> Optional[str]:
    return value if isinstance(value, str) and 0 < len(value) <= _MAX_CONTENT else None


def _recording(span: Optional[AbstractSpan]) -> bool:
    return span is not None and span.span_instance.is_recording()


def _attributes(span: Optional[AbstractSpan], values: Mapping[str, Any]) -> None:
    if span is not None and _recording(span):
        for key, value in values.items():
            if value is not None:
                _record(functools.partial(span.add_attribute, key, value))


def _event(span: Optional[AbstractSpan], name: str, values: Optional[dict[str, Any]] = None) -> None:
    if span is not None and _recording(span):
        span.span_instance.add_event(
            name, attributes={key: val for key, val in (values or {}).items() if val is not None}
        )


def _context(span: Optional[AbstractSpan]) -> Any:
    if span is None:
        return nullcontext()
    from opentelemetry.trace import use_span  # pylint: disable=import-outside-toplevel

    return use_span(span.span_instance, end_on_exit=False, record_exception=False, set_status_on_exception=False)


def _start(name: str, endpoint: str, parent: Optional[AbstractSpan] = None) -> Optional[AbstractSpan]:
    parsed = urlsplit(endpoint)
    with _context(parent):
        span = start_span(
            OperationName.CREATE_AGENT if name == "create_agent" else OperationName.RESPONSES,
            server_address=parsed.hostname,
            port=parsed.port,
            span_name=name,
        )
    if name in ("create_agent", "invoke_agent"):
        _attributes(span, {GEN_AI_OPERATION_NAME: name, GEN_AI_AGENT_TYPE: "voice"})
    return span


def _error_attributes(error: Any) -> dict[str, Any]:
    if isinstance(error, Mapping):
        kind = error.get("type")
        code = error.get("code")
        result: dict[str, Any] = {ERROR_TYPE: kind if isinstance(kind, str) and kind in _ERROR_TYPES else "Error"}
        if isinstance(code, str) and code in _ERROR_CODES:
            result[_PREFIX + "error.code"] = code
        return result
    kind = type(error).__name__
    result = {ERROR_TYPE: kind if kind in _ERROR_TYPES else "Error"}
    status = getattr(error, "status_code", None)
    if isinstance(status, int):
        result["http.response.status_code"] = status
    return result


def _fail(span: Optional[AbstractSpan], error: BaseException) -> None:
    if isinstance(error, (CancelledError, KeyboardInterrupt)):
        _attributes(span, {_PREFIX + "cancelled": True})
    else:
        _set_error(span, _error_attributes(error))


def _set_error(span: Optional[AbstractSpan], attributes: Mapping[str, Any]) -> None:
    if span is not None and _recording(span):
        from opentelemetry.trace import StatusCode  # pylint: disable=import-outside-toplevel

        _attributes(span, attributes)
        span.span_instance.set_status(StatusCode.ERROR)


def _end(span: Optional[AbstractSpan]) -> None:
    if span is not None:
        span.span_instance.end()


@contextmanager
def _rest_context(span: AbstractSpan) -> Any:
    # Reuse Core's nested-method suppression, but never pass raw exceptions to its exporter.
    _record(span.__enter__)
    try:
        yield
    except BaseException as error:
        _record(lambda: _fail(span, error))
        raise
    finally:
        # Core's legacy annotation omits None for a normal context-manager exit.
        _record(lambda: span.__exit__(None, None, None))  # type: ignore[arg-type]


def _audio_size(value: Any) -> int:
    if isinstance(value, (bytes, bytearray)):
        return len(value)
    if isinstance(value, str):
        # The protocol carries padded base64. Count bytes without allocating or retaining media.
        return max(0, len(value) * 3 // 4 - (2 if value.endswith("==") else 1 if value.endswith("=") else 0))
    return 0


def _part(value: Any, content: bool) -> Optional[dict[str, Any]]:
    value = _mapping(value)
    kind = value.get("type")
    if kind not in ("input_text", "output_text", "text", "input_audio", "output_audio", "audio"):
        return None
    audio = "audio" in kind
    result: dict[str, Any] = {"type": "audio" if audio else "text"}
    if content:
        text = _limited(value.get("transcript") if audio else value.get("text"))
        if text is not None:
            result["content"] = text
    return result


def _message(value: Any, content: bool) -> Optional[dict[str, Any]]:
    item = _mapping(value)
    kind = item.get("type")
    if kind in ("function_call", "function_call_output", "mcp_call", "system_tool"):
        part: dict[str, Any] = {"type": "tool_call_response" if kind == "function_call_output" else "tool_call"}
        if isinstance(item.get("call_id"), str):
            part["id"] = _limited(item["call_id"])
        if content:
            for source, target in (("name", "name"), ("arguments", "arguments"), ("output", "result")):
                text = _limited(item.get(source))
                if text is not None:
                    part[target] = text
        return {"role": "tool" if kind == "function_call_output" else "assistant", "parts": [part]}
    if kind == "message":
        parts = [_part(part, content) for part in (item.get("content") or [])[:_MAX_PARTS]]
        parts = [part for part in parts if part is not None]
        if parts:
            role = item.get("role")
            return {"role": role if role in ("system", "user") else "assistant", "parts": parts}
    return None


def _without_content(message: dict[str, Any]) -> None:
    for part in message["parts"]:
        for name in ("content", "name", "arguments", "result"):
            part.pop(name, None)


class _Response:
    def __init__(self, span: Optional[AbstractSpan], model: Optional[str]) -> None:
        self.span = span
        self.model = model
        self.started = time.perf_counter()
        self.audio_bytes = 0
        self.first_audio: Optional[float] = None
        self.first_text: Optional[float] = None
        self.messages: dict[str, dict[str, Any]] = {}
        self.parts: dict[tuple[str, int, str], dict[str, Any]] = {}


class _Session:  # pylint: disable=too-many-instance-attributes
    def __init__(self, instrumentor: "_VoiceAgentsInstrumentor", manager: Any) -> None:
        self.instrumentor = instrumentor
        self.endpoint = manager._endpoint  # pylint: disable=protected-access
        self.span = _start("voice_agents.realtime.session", self.endpoint)
        self.connect_span = _record(lambda: _start("voice_agents.realtime.connect", self.endpoint, self.span))
        transport = manager._transport or "websocket"  # pylint: disable=protected-access
        safe_transport = transport if transport in ("websocket", "webrtc") else "other"
        for span in (self.span, self.connect_span):
            _attributes(span, {_PREFIX + "connection.transport": safe_transport})
        self.lock = threading.RLock()
        self.responses: dict[str, _Response] = {}
        self.model: Optional[str] = None
        self.conversation_id: Optional[str] = None
        self.input_bytes = 0
        self.output_bytes = 0
        self.finished = 0
        self.untracked = 0
        self.connected = False
        self.ended = False
        self.audio_summary_recorded = False
        self.input_kind: Optional[str] = None
        self.input_item_id: Optional[str] = None
        self.input_item_pending = False
        self.input_generation = 0
        self.pending_audio_commits: deque[int] = deque(maxlen=_MAX_PARTS)
        self.untracked_audio_commits = 0
        self.committed_audio_ids: deque[str] = deque(maxlen=_MAX_PARTS)
        self.audio_item_ids: deque[str] = deque(maxlen=_MAX_PARTS)
        self.failure: Optional[dict[str, Any]] = None
        self.cancelled = False
        self.receive_cancelled = False
        _SESSIONS.add(self)

    def opened(self) -> None:
        self.connected = True
        _end(self.connect_span)
        self.connect_span = None

    def snapshot_sent(self, value: Any) -> dict[str, Any]:
        event = _mapping(json.loads(value)) if isinstance(value, str) else _mapping(value)
        kind = event.get("type")
        summary: dict[str, Any] = {"type": kind if isinstance(kind, str) else None}
        if kind == "input_audio_buffer.append":
            summary["audio_bytes"] = _audio_size(event.get("audio"))
        elif kind == "conversation.item.create":
            item = _mapping(event.get("item"))
            summary["item_id"] = _identifier(item.get("id"))
            summary["input_audio"] = (
                item.get("type") == "message"
                and item.get("role") == "user"
                and any(
                    _mapping(part).get("type") in ("input_audio", "audio")
                    for part in (item.get("content") or [])[:_MAX_PARTS]
                )
            )
            if _recording(self.span):
                summary["message"] = _message(item, self.instrumentor.content())
            if item.get("type") == "function_call_output":
                summary["call_id"] = _limited(item.get("call_id"))
                summary["tool_output"] = True
        return summary

    def sent(self, event: Mapping[str, Any]) -> None:
        with self.lock:
            if self.ended:
                return
            kind = event.get("type")
            content = self.instrumentor.content()
            if kind == "input_audio_buffer.append":
                self.input_bytes += event["audio_bytes"]
                if not self.audio_summary_recorded:
                    self.input_generation += 1
                    self.input_kind = "audio"
                    self.input_item_pending = True
                    self._input_audio_summary()
                    self.audio_summary_recorded = True
            elif kind in ("input_audio_buffer.commit", "input_audio_buffer.clear"):
                self.audio_summary_recorded = False
                if kind == "input_audio_buffer.commit" and self.input_kind == "audio":
                    if len(self.pending_audio_commits) == _MAX_PARTS:
                        self.untracked_audio_commits += 1
                    self.pending_audio_commits.append(self.input_generation)
                elif kind == "input_audio_buffer.clear":
                    self.input_item_pending = True
            elif kind == "conversation.item.create":
                self.audio_summary_recorded = False
                self.input_generation += 1
                self.input_kind = "audio" if event.get("input_audio") else "message"
                self.input_item_pending = True
                identifier = _identifier(event.get("item_id"))
                if self.input_kind == "audio" and identifier is not None:
                    self.input_item_id = identifier
                    self.input_item_pending = False
                    self.audio_item_ids.append(identifier)
                summary = event.get("message")
                if summary:
                    if not content:
                        _without_content(summary)
                    _attributes(self.span, {GEN_AI_INPUT_MESSAGES: json.dumps([summary])})
                if event.get("tool_output"):
                    _event(self.span, "voice_agents.tool.output_sent", {GEN_AI_TOOL_CALL_ID: event.get("call_id")})
            elif kind == "response.cancel":
                _event(self.span, "voice_agents.response.cancel_requested")
            elif kind == "session.update":
                _event(self.span, "voice_agents.session.update_sent")

    def _input_audio_summary(self, transcript: Any = None) -> None:
        part: dict[str, Any] = {"type": "audio"}
        text = _limited(transcript) if self.instrumentor.content() else None
        if text is not None:
            part["content"] = text
        _attributes(self.span, {GEN_AI_INPUT_MESSAGES: json.dumps([{"role": "user", "parts": [part]}])})

    def _audio_boundary(self, event: Mapping[str, Any]) -> None:
        identifier = _identifier(event.get("item_id"))
        if identifier is None:
            return
        if event.get("type") == "input_audio_buffer.committed":
            if identifier in self.committed_audio_ids:
                return
            self.committed_audio_ids.append(identifier)
            if self.untracked_audio_commits:
                self.untracked_audio_commits -= 1
                self.audio_item_ids.append(identifier)
                return
            if self.pending_audio_commits and self.pending_audio_commits.popleft() != self.input_generation:
                self.audio_item_ids.append(identifier)
                return
        if self.input_kind == "message":
            return
        if identifier in self.audio_item_ids and (identifier != self.input_item_id or self.input_item_pending):
            return
        if identifier != self.input_item_id or self.input_item_pending:
            self.input_kind = "audio"
            self.input_item_id = identifier
            self.input_item_pending = False
            self.audio_item_ids.append(identifier)
            self._input_audio_summary()
        self.audio_summary_recorded = event.get("type") == "input_audio_buffer.speech_started"

    def received(self, value: Any) -> None:  # pylint: disable=too-many-branches,too-many-statements
        with self.lock:
            if self.ended:
                return
            event = _mapping(value)
            kind = event.get("type")
            content = self.instrumentor.content()
            response_id = event.get("response_id")
            tracked = self.responses.get(response_id) if isinstance(response_id, str) else None
            if kind in ("session.created", "session.updated"):
                session = _mapping(event.get("session"))
                self.model = _limited(session.get("model")) or self.model
                self.conversation_id = _limited(event.get("conversation_id")) or self.conversation_id
                _attributes(
                    self.span,
                    {
                        _PREFIX + "session.id": _limited(session.get("id")),
                        GEN_AI_CONVERSATION_ID: self.conversation_id,
                        GEN_AI_REQUEST_MODEL: self.model,
                    },
                )
                _event(self.span, "voice_agents." + kind)
                audio = _mapping(session.get("audio"))
                for direction in ("input", "output"):
                    config = _mapping(_mapping(audio.get(direction)).get("format"))
                    if config.get("type") in ("audio/pcm", "audio/pcmu", "audio/pcma"):
                        _attributes(self.span, {_PREFIX + direction + ".audio.format": config["type"]})
                    if isinstance(config.get("rate"), int):
                        _attributes(self.span, {_PREFIX + direction + ".audio.sample_rate": config["rate"]})
            elif kind in ("input_audio_buffer.speech_started", "input_audio_buffer.committed"):
                self._audio_boundary(event)
            elif kind == "input_audio_buffer.cleared":
                self.audio_summary_recorded = False
                self.input_item_pending = True
            elif kind == "response.created":
                response = _mapping(event.get("response"))
                identifier = _identifier(response.get("id"))
                if identifier is not None and identifier not in self.responses:
                    if len(self.responses) >= _MAX_RESPONSES:
                        self.untracked += 1
                        return
                    span = _start("invoke_agent", self.endpoint, self.span)
                    _attributes(
                        span,
                        {
                            GEN_AI_RESPONSE_ID: _limited(identifier),
                            GEN_AI_REQUEST_MODEL: self.model,
                            GEN_AI_CONVERSATION_ID: _limited(response.get("conversation_id")) or self.conversation_id,
                        },
                    )
                    self.responses[identifier] = _Response(span, self.model)
            elif kind in ("response.output_audio.delta", "response.audio.delta"):
                size = _audio_size(event.get("delta"))
                self.output_bytes += size
                if tracked:
                    tracked.audio_bytes += size
                    if size and tracked.first_audio is None:
                        tracked.first_audio = time.perf_counter() - tracked.started
            elif kind in ("response.output_text.delta", "response.text.delta"):
                if tracked and tracked.first_text is None and event.get("delta"):
                    tracked.first_text = time.perf_counter() - tracked.started
            elif kind == "response.done":
                self.complete(_mapping(event.get("response")))
            elif kind in (
                "response.output_text.done",
                "response.text.done",
                "response.output_audio_transcript.done",
                "response.audio_transcript.done",
                "response.output_audio.done",
                "response.audio.done",
            ):
                if tracked and _recording(tracked.span):
                    is_audio = "audio" in kind
                    part: dict[str, Any] = {"type": "audio" if is_audio else "text"}
                    text = _limited(event.get("transcript") if is_audio else event.get("text"))
                    if content and text is not None:
                        part["content"] = text
                    item_id = _identifier(event.get("item_id"))
                    index = event.get("content_index", 0)
                    if item_id is not None and isinstance(index, int):
                        key = (item_id, index, part["type"])
                        if key in tracked.parts:
                            tracked.parts[key].update(part)
                        elif len(tracked.parts) < _MAX_PARTS:
                            tracked.parts[key] = part
            elif kind in ("response.function_call_arguments.done", "response.system_tool_arguments.done"):
                span = tracked.span if tracked else self.span
                attributes = {
                    GEN_AI_TOOL_CALL_ID: _limited(event.get("call_id")),
                    _PREFIX + "tool.kind": "function" if kind == "response.function_call_arguments.done" else "system",
                }
                if content:
                    attributes[GEN_AI_TOOL_NAME] = _limited(event.get("name"))
                    attributes[_PREFIX + "tool.arguments"] = _limited(event.get("arguments"))
                _event(
                    span,
                    "voice_agents.tool.requested",
                    {key: val for key, val in attributes.items() if val is not None},
                )
                summary = _message({**event, "type": "function_call"}, content) if _recording(span) else None
                call_id = _identifier(event.get("call_id"))
                if tracked and summary and call_id is not None and len(tracked.messages) < _MAX_PARTS:
                    tracked.messages["tool:" + call_id] = summary
            elif kind in (
                "response.mcp_call.completed",
                "response.mcp_call.failed",
                "session.end_conversation.completed",
            ):
                _event(self.span, kind, {_PREFIX + "item.id": _limited(event.get("item_id"))})
            elif kind in ("error", "rtc.call.error"):
                _event(
                    self.span,
                    "voice_agents.server_error" if kind == "error" else kind,
                    _error_attributes(_mapping(event.get("error"))),
                )
            elif kind == "warning":
                _event(self.span, "voice_agents.warning")
            elif kind in (
                "conversation.item.input_audio_transcription.completed",
                "conversation.item.input_audio_transcription.failed",
            ):
                # Late transcription must not replace a newer message or an unconfirmed audio turn.
                if (
                    self.input_kind == "audio"
                    and not self.input_item_pending
                    and self.input_item_id == _identifier(event.get("item_id"))
                ):
                    self._input_audio_summary(event.get("transcript") if kind.endswith("completed") else None)
                _event(self.span, "voice_agents.transcription." + kind.rsplit(".", 1)[-1])
            elif kind in ("session.subagent.started", "session.subagent.completed", "session.subagent.aborted"):
                attributes = {_PREFIX + "subagent.consultation.id": _limited(event.get("consultation_id"))}
                if event.get("reason") in (
                    "unknown_target",
                    "timeout",
                    "cancelled",
                    "stopped_by_user",
                    "superseded",
                    "failed",
                ):
                    attributes[_PREFIX + "subagent.abort_reason"] = event["reason"]
                _event(self.span, kind, {key: val for key, val in attributes.items() if val is not None})

    def _output_parts(self, tracked: _Response, item_id: str, content: list[Any]) -> list[dict[str, Any]]:
        parts = []
        for index, value in enumerate(content[:_MAX_PARTS]):
            part = _part(value, self.instrumentor.content())
            if part is None:
                continue
            observed = tracked.parts.get((item_id, index, part["type"]))
            if self.instrumentor.content() and observed and "content" in observed:
                part.setdefault("content", observed["content"])
            parts.append(part)
        return parts

    def flush(self, tracked: _Response, response: Optional[Mapping[str, Any]] = None) -> None:
        _attributes(
            tracked.span,
            {
                _PREFIX + "output.audio.bytes": tracked.audio_bytes,
                _PREFIX + "response.time_to_first_audio_seconds": tracked.first_audio,
                _PREFIX + "response.time_to_first_text_seconds": tracked.first_text,
            },
        )
        if not _recording(tracked.span):
            return
        fallback = dict(tracked.messages)
        for (item_id, _, _), part in sorted(tracked.parts.items()):
            message = fallback.setdefault(item_id, {"role": "assistant", "parts": []})
            message["parts"].append(part)
        messages = []
        unkeyed = False
        for item in (_mapping(response).get("output") or [])[:_MAX_PARTS]:
            summary = _message(item, self.instrumentor.content())
            if summary is None:
                continue
            item = _mapping(item)
            call_id = _identifier(item.get("call_id"))
            key = (
                "tool:" + call_id
                if item.get("type") in ("function_call", "system_tool", "mcp_call") and call_id is not None
                else _identifier(item.get("id"))
            )
            if key:
                fallback.pop(key, None)
                if item.get("type") == "message":
                    summary["parts"] = self._output_parts(tracked, key, item.get("content") or [])
            else:
                unkeyed = True
            messages.append(summary)
        if not unkeyed:
            messages.extend(fallback.values())
        if not self.instrumentor.content():
            for message in messages:
                _without_content(message)
        if messages:
            _attributes(tracked.span, {GEN_AI_OUTPUT_MESSAGES: json.dumps(messages[:_MAX_PARTS])})

    def complete(self, response: Mapping[str, Any]) -> None:
        identifier = response.get("id")
        tracked = self.responses.pop(identifier, None) if isinstance(identifier, str) else None
        if tracked is None:
            return
        usage = _mapping(response.get("usage"))
        status = response.get("status")
        status = status if status in ("completed", "cancelled", "failed", "incomplete", "in_progress") else "unknown"
        try:
            _attributes(tracked.span, {_PREFIX + "response.status": status})
            for key, attribute in (
                ("input_tokens", GEN_AI_USAGE_INPUT_TOKENS),
                ("output_tokens", GEN_AI_USAGE_OUTPUT_TOKENS),
            ):
                if isinstance(usage.get(key), int):
                    _attributes(tracked.span, {attribute: usage[key]})
            modalities = response.get("output_modalities")
            if isinstance(modalities, list) and all(value in ("text", "audio") for value in modalities):
                _attributes(tracked.span, {_PREFIX + "response.output_modalities": modalities})
            self.flush(tracked, response)
            if status == "failed":
                _fail(tracked.span, RuntimeError())
                _attributes(tracked.span, {ERROR_TYPE: "response_failed"})
            elif status == "completed" and tracked.span is not None and _recording(tracked.span):
                from opentelemetry.trace import StatusCode  # pylint: disable=import-outside-toplevel

                tracked.span.span_instance.set_status(StatusCode.OK)
            elif status == "cancelled":
                _attributes(tracked.span, {_PREFIX + "cancelled": True})
        finally:
            _record(lambda: _end(tracked.span))
            self.finished += 1
            _record(lambda: self.metrics(tracked, usage, "response_failed" if status == "failed" else None))

    def metrics(self, tracked: _Response, usage: Mapping[str, Any], error: Optional[str] = None) -> None:
        parsed = urlsplit(self.endpoint)
        metrics = self.instrumentor.metrics
        with _context(tracked.span):
            metrics._record_operation_duration(  # pylint: disable=protected-access
                time.perf_counter() - tracked.started,
                "invoke_agent",
                parsed.hostname,
                parsed.port,
                tracked.model,
                error,
            )
            for key, token_type in (("input_tokens", "input"), ("output_tokens", "completion")):
                count = usage.get(key)
                if isinstance(count, int) and count >= 0:
                    metrics._record_token_usage(  # pylint: disable=protected-access
                        count, token_type, "invoke_agent", parsed.hostname, tracked.model
                    )

    def fail(self, error: BaseException) -> None:
        with self.lock:
            if isinstance(error, (CancelledError, KeyboardInterrupt)):
                self.cancelled = True
            else:
                self.failure = _error_attributes(error)
            _record(functools.partial(_fail, self.span, error))

    def _mark_error(self, span: Optional[AbstractSpan]) -> None:
        if self.failure is not None:
            _set_error(span, self.failure)
        elif self.cancelled:
            _attributes(span, {_PREFIX + "cancelled": True})

    def close(self, code: Optional[int] = None, clean: bool = True, error: Optional[BaseException] = None) -> None:
        with self.lock:
            if self.ended:
                return
            self.ended = True
            _SESSIONS.discard(self)
            if error:
                self.fail(error)
            _record(functools.partial(self._mark_error, self.connect_span))
            _record(lambda: _end(self.connect_span))
            self.connect_span = None
            for tracked in self.responses.values():
                _record(functools.partial(self.flush, tracked))
                _attributes(tracked.span, {_PREFIX + "response.status": "interrupted"})
                _record(functools.partial(self._mark_error, tracked.span))
                _record(functools.partial(_end, tracked.span))
                _record(functools.partial(self.metrics, tracked, {}, "response_interrupted" if self.failure else None))
            self.responses.clear()
            _attributes(
                self.span,
                {
                    _PREFIX + "connected": self.connected,
                    _PREFIX + "close.code": code if isinstance(code, int) and 1000 <= code <= 4999 else None,
                    _PREFIX + "close.was_clean": clean,
                    _PREFIX + "input.audio.bytes": self.input_bytes,
                    _PREFIX + "output.audio.bytes": self.output_bytes,
                    _PREFIX + "responses.finished": self.finished,
                    _PREFIX + "responses.untracked": self.untracked or None,
                },
            )
            _record(lambda: _end(self.span))


class _VoiceAgentsInstrumentor:
    def __init__(self, owner: Any, metrics: Any) -> None:
        self.owner = owner
        self.metrics = metrics

    def enabled(self, kwargs: Optional[dict[str, Any]] = None) -> bool:
        requested = _mapping((kwargs or {}).get("tracing_options")).get("enabled")
        return (
            self.owner.is_instrumented()
            and (requested is True or settings.tracing_enabled())
            and settings.tracing_implementation() is not None
            and requested is not False
        )

    def content(self) -> bool:
        return self.owner.is_content_recording_enabled()

    def _rest(self, function: Callable, operation: str, voice_only: bool = False) -> Callable:
        signature = inspect.signature(function)

        def begin(args: tuple, kwargs: dict[str, Any]) -> Optional[AbstractSpan]:
            if not self.enabled(kwargs):
                return None
            bound = signature.bind_partial(*args, **kwargs).arguments
            definition = _mapping(bound.get("definition")) or _mapping(_mapping(bound.get("body")).get("definition"))
            if voice_only and definition.get("kind") != "voice":
                return None
            endpoint = args[0]._config.endpoint  # pylint: disable=protected-access
            span = _start(operation, endpoint)
            _attributes(
                span,
                {
                    GEN_AI_REQUEST_MODEL: _limited(definition.get("model")),
                    GEN_AI_AGENT_NAME: _limited(bound.get("agent_name")),
                    _PREFIX + "operation": operation.rsplit(".", 1)[-1] if operation != "create_agent" else None,
                },
            )
            instructions = _limited(definition.get("instructions")) if self.content() else None
            if instructions is not None:
                _attributes(span, {GEN_AI_SYSTEM_MESSAGE: json.dumps([{"type": "text", "content": instructions}])})
            return span

        def finish(span: Optional[AbstractSpan], result: Any) -> None:
            if operation == "create_agent":
                _attributes(
                    span,
                    {
                        GEN_AI_AGENT_ID: _limited(getattr(result, "id", None)),
                        GEN_AI_AGENT_VERSION: _limited(getattr(result, "version", None)),
                        GEN_AI_AGENT_NAME: _limited(getattr(result, "name", None)),
                    },
                )
                latest = _mapping(_mapping(getattr(result, "versions", None)).get("latest"))
                definition = _mapping(latest.get("definition"))
                _attributes(span, {GEN_AI_REQUEST_MODEL: _limited(definition.get("model"))})

        # create_version already has a Foundry wrapper. Bypass only that wrapper for voice
        # definitions; non-voice creation continues through its original instrumentation.
        original = getattr(function, "_original", function) if voice_only else function

        def untraced(args: tuple, kwargs: dict[str, Any]) -> Callable:
            if voice_only:
                definition = _mapping(kwargs.get("definition"))
                body = kwargs.get("body", args[2] if len(args) > 2 else None)
                definition = definition or _mapping(_mapping(body).get("definition"))
                if definition.get("kind") == "voice":
                    return original
            return function

        if inspect.iscoroutinefunction(function):

            @functools.wraps(function)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                span = _record(lambda: begin(args, kwargs))
                if span is None:
                    return await untraced(args, kwargs)(*args, **kwargs)
                with _rest_context(span):
                    result = await original(*args, **{**kwargs, "merge_span": True})
                    _record(lambda: finish(span, result))
                    return result

            return async_wrapper

        @functools.wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            span = _record(lambda: begin(args, kwargs))
            if span is None:
                return untraced(args, kwargs)(*args, **kwargs)
            with _rest_context(span):
                result = original(*args, **{**kwargs, "merge_span": True})
                _record(lambda: finish(span, result))
                return result

        return wrapper

    def _enter(self, function: Callable) -> Callable:
        def prepare(manager: Any) -> Optional[_Session]:
            return _Session(self, manager) if self.enabled() else None

        def headers(manager: Any, session: Optional[_Session]) -> dict[str, str]:
            from ._ai_project_instrumentor import (  # pylint: disable=import-outside-toplevel
                _trace_context_propagation_enabled,
                _trace_context_baggage_propagation_enabled,
            )

            original = manager._extra_headers  # pylint: disable=protected-access
            if session and _trace_context_propagation_enabled:
                from opentelemetry import propagate  # pylint: disable=import-outside-toplevel

                carrier: dict[str, str] = {}
                propagate.inject(carrier)
                allowed = {"traceparent", "tracestate"}
                if _trace_context_baggage_propagation_enabled:
                    allowed.add("baggage")
                copied = dict(original)
                present = {key.lower() for key in copied}
                copied.update(
                    {
                        key: value
                        for key, value in carrier.items()
                        if key.lower() in allowed and key.lower() not in present
                    }
                )
                manager._extra_headers = copied  # pylint: disable=protected-access
            return original

        if inspect.iscoroutinefunction(function):

            @functools.wraps(function)
            async def async_wrapper(manager: Any) -> Any:
                session = _record(lambda: prepare(manager))
                original_headers = manager._extra_headers  # pylint: disable=protected-access
                try:
                    with _context(session.connect_span if session else None):
                        _record(lambda: headers(manager, session))
                        connection = await function(manager)
                    if session:
                        connection._voice_trace = session  # pylint: disable=protected-access
                        _record(session.opened)
                    return connection
                except BaseException as error:
                    if session:
                        _record(lambda: session.close(clean=False, error=error))
                    raise
                finally:
                    manager._extra_headers = original_headers  # pylint: disable=protected-access

            return async_wrapper

        @functools.wraps(function)
        def wrapper(manager: Any) -> Any:
            session = _record(lambda: prepare(manager))
            original_headers = manager._extra_headers  # pylint: disable=protected-access
            try:
                with _context(session.connect_span if session else None):
                    _record(lambda: headers(manager, session))
                    connection = function(manager)
                if session:
                    connection._voice_trace = session  # pylint: disable=protected-access
                    _record(session.opened)
                return connection
            except BaseException as error:
                if session:
                    _record(lambda: session.close(clean=False, error=error))
                raise
            finally:
                manager._extra_headers = original_headers  # pylint: disable=protected-access

        return wrapper

    def _connection(self, function: Callable, method: str) -> Callable:
        def snapshot(connection: Any, args: tuple, kwargs: dict) -> Optional[dict[str, Any]]:
            session = getattr(connection, "_voice_trace", None)
            if method == "send" and session and not session.ended and self.enabled():
                return session.snapshot_sent(args[0] if args else kwargs.get("event"))
            return None

        def observe(connection: Any, kwargs: dict, result: Any, error: Optional[BaseException]) -> None:
            session = getattr(connection, "_voice_trace", None)
            if session is None or session.ended:
                return
            if method == "close":
                received_code = getattr(connection._connection, "close_code", None)  # pylint: disable=protected-access
                code = received_code if isinstance(received_code, int) else kwargs.get("code", 1000)
                clean = error is None and code in (1000, 1001)
                termination = error
                if termination is None and not clean:
                    # aiohttp assigns 1006 locally when a receive wait is cancelled.
                    if session.receive_cancelled and code == 1006 and kwargs.get("code", 1000) in (1000, 1001):
                        termination = CancelledError()
                    else:
                        termination = ConnectionResetError()
                session.close(code, clean, termination)
            elif error:
                if method == "recv" and isinstance(error, CancelledError):
                    session.receive_cancelled = True
                    _event(session.span, "voice_agents.receive.cancelled")
                elif method == "recv" and isinstance(error, ConnectionResetError):
                    code = getattr(connection._connection, "close_code", None)  # pylint: disable=protected-access
                    clean = error.__cause__ is None and code in (1000, 1001)
                    session.close(code, clean, None if clean else error)
                else:
                    _event(
                        session.span,
                        "voice_agents." + ("send" if method == "send" else "receive") + ".failed",
                        _error_attributes(error),
                    )
            elif self.enabled():
                if method == "send":
                    if result is not None:
                        session.sent(result)
                else:
                    session.receive_cancelled = False
                    session.received(result)

        if inspect.iscoroutinefunction(function):

            @functools.wraps(function)
            async def async_wrapper(connection: Any, *args: Any, **kwargs: Any) -> Any:
                sent = _record(lambda: snapshot(connection, args, kwargs)) if method == "send" else None
                try:
                    result = await function(connection, *args, **kwargs)
                except BaseException as error:
                    _record(lambda: observe(connection, kwargs, None, error))
                    raise
                _record(lambda: observe(connection, kwargs, sent if method == "send" else result, None))
                return result

            return async_wrapper

        @functools.wraps(function)
        def wrapper(connection: Any, *args: Any, **kwargs: Any) -> Any:
            sent = _record(lambda: snapshot(connection, args, kwargs)) if method == "send" else None
            try:
                result = function(connection, *args, **kwargs)
            except BaseException as error:
                _record(lambda: observe(connection, kwargs, None, error))
                raise
            _record(lambda: observe(connection, kwargs, sent if method == "send" else result, None))
            return result

        return wrapper

    def _exit(self, function: Callable) -> Callable:
        def mark(instance: Any, details: tuple) -> None:
            connection = getattr(instance, "_connection", None)
            session = getattr(instance, "_voice_trace", None) or getattr(connection, "_voice_trace", None)
            if session and len(details) > 1 and isinstance(details[1], BaseException):
                session.fail(details[1])

        if inspect.iscoroutinefunction(function):

            @functools.wraps(function)
            async def async_wrapper(instance: Any, *details: Any) -> Any:
                _record(lambda: mark(instance, details))
                return await function(instance, *details)

            return async_wrapper

        @functools.wraps(function)
        def wrapper(instance: Any, *details: Any) -> Any:
            _record(lambda: mark(instance, details))
            return function(instance, *details)

        return wrapper

    def instrument(self) -> None:
        if _ORIGINALS:
            return
        if _responses_instrumentor._operation_duration_histogram is None:  # pylint: disable=protected-access
            self.metrics._initialize_metrics()  # pylint: disable=protected-access
        mutations = (
            "create_call_job",
            "cancel_call_job",
            "transfer_call",
            "end_call",
            "create_binding",
            "update_binding",
            "delete_binding",
            "replace_transfer_targets",
        )
        for module in ("azure.ai.projects.operations", "azure.ai.projects.aio.operations"):
            operations = importlib.import_module(module)
            targets = [
                ("AgentsOperations", "create_version", "create_agent", True),
                ("BetaAgentsOperations", "create_from_prompt", "create_agent", False),
                ("BetaVoiceAgentsConversationsOperations", "delete", "voice_agents.conversations.delete", False),
            ] + [
                ("BetaVoiceAgentsTelephonyOperations", method, "voice_agents.telephony." + method, False)
                for method in mutations
            ]
            for class_name, method, operation, voice_only in targets:
                cls = getattr(operations, class_name)
                original = getattr(cls, method)
                _ORIGINALS[(cls, method)] = original
                setattr(cls, method, self._rest(original, operation, voice_only))
        for module, prefix in (("azure.ai.projects._realtime", ""), ("azure.ai.projects.aio._realtime", "Async")):
            realtime = importlib.import_module(module)
            manager = getattr(realtime, prefix + "BetaRealtimeConnectionManager")
            original = manager.enter
            _ORIGINALS[(manager, "enter")] = original
            manager.enter = self._enter(original)
            connection = getattr(realtime, prefix + "BetaRealtimeConnection")
            exit_method = "__aexit__" if prefix else "__exit__"
            for cls in (manager, connection):
                original = getattr(cls, exit_method)
                _ORIGINALS[(cls, exit_method)] = original
                setattr(cls, exit_method, self._exit(original))
            for method in ("send", "recv", "close"):
                original = getattr(connection, method)
                _ORIGINALS[(connection, method)] = original
                setattr(connection, method, self._connection(original, method))

    def uninstrument(self) -> None:
        for session in tuple(_SESSIONS):
            _record(session.close)
        for (cls, method), original in _ORIGINALS.items():
            setattr(cls, method, original)
        _ORIGINALS.clear()
