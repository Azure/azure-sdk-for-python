# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from __future__ import annotations

import codecs
import json
from types import TracebackType
from typing import Any, AsyncGenerator, AsyncIterator, Generator, Iterator, Optional, Tuple, Type, Union
from typing_extensions import Self

from . import models
from ._utils.model_base import _deserialize


_TERMINAL_EVENTS = {"error", "response.completed"}

KnowledgeBaseRetrievalEventData = Union[
    models.KnowledgeBaseRetrievalStartedEvent,
    models.KnowledgeBaseActivityStartedEvent,
    models.KnowledgeBaseActivityRecord,
    models.KnowledgeBaseAnswerCompletedEvent,
    list[models.KnowledgeBaseReference],
    models.KnowledgeBaseStreamErrorEvent,
    models.KnowledgeBaseResponseCompletedEvent,
    dict[str, Any],
    list[Any],
    str,
    int,
    float,
    bool,
    None,
]


class KnowledgeBaseRetrievalEvent:
    """A typed event emitted by a knowledge base retrieval stream.

    :ivar event_type: The server-sent event name.
    :vartype event_type: str
    :ivar data: The deserialized event payload.
    :vartype data: object
    """

    event_type: str
    data: KnowledgeBaseRetrievalEventData

    def __init__(self, event_type: str, data: KnowledgeBaseRetrievalEventData) -> None:
        self.event_type = event_type
        self.data = data

    def __repr__(self) -> str:
        return f"KnowledgeBaseRetrievalEvent(event_type={self.event_type!r}, data={self.data!r})"


KnowledgeBaseRetrievalEvent.__module__ = "azure.search.documents.knowledgebases"


def _split_sse_lines(buffer: str) -> Tuple[list[str], str]:
    lines: list[str] = []
    start = 0
    index = 0
    while index < len(buffer):
        char = buffer[index]
        if char == "\n":
            lines.append(buffer[start:index])
            index += 1
            start = index
        elif char == "\r":
            if index + 1 == len(buffer):
                break
            lines.append(buffer[start:index])
            index += 2 if buffer[index + 1] == "\n" else 1
            start = index
        else:
            index += 1
    return lines, buffer[start:]


def _iter_sse_lines(raw_stream: Iterator[bytes]) -> Iterator[str]:
    decoder = codecs.getincrementaldecoder("utf-8-sig")(errors="replace")
    buffer = ""
    for chunk in raw_stream:
        buffer += decoder.decode(chunk)
        lines, buffer = _split_sse_lines(buffer)
        yield from lines
    buffer += decoder.decode(b"", final=True)
    lines, remainder = _split_sse_lines(buffer)
    yield from lines
    if remainder:
        yield remainder[:-1] if remainder.endswith("\r") else remainder


async def _aiter_sse_lines(raw_stream: AsyncIterator[bytes]) -> AsyncIterator[str]:
    decoder = codecs.getincrementaldecoder("utf-8-sig")(errors="replace")
    buffer = ""
    async for chunk in raw_stream:
        buffer += decoder.decode(chunk)
        lines, buffer = _split_sse_lines(buffer)
        for line in lines:
            yield line
    buffer += decoder.decode(b"", final=True)
    lines, remainder = _split_sse_lines(buffer)
    for line in lines:
        yield line
    if remainder:
        yield remainder[:-1] if remainder.endswith("\r") else remainder


class _SSEEventBuilder:
    def __init__(self) -> None:
        self._event_type = ""
        self._data: list[str] = []

    def add_line(self, line: str) -> Optional[Tuple[str, str]]:
        if line == "":
            return self._dispatch()
        if line.startswith(":"):
            return None

        field, _, value = line.partition(":")
        if value.startswith(" "):
            value = value[1:]
        if field == "event":
            self._event_type = value
        elif field == "data":
            self._data.append(value)
        return None

    def _dispatch(self) -> Optional[Tuple[str, str]]:
        if not self._data:
            self._event_type = ""
            return None
        event = (self._event_type or "message", "\n".join(self._data))
        self._event_type = ""
        self._data = []
        return event


def _iter_sse_events(raw_stream: Iterator[bytes]) -> Iterator[Tuple[str, str]]:
    builder = _SSEEventBuilder()
    for line in _iter_sse_lines(raw_stream):
        event = builder.add_line(line)
        if event is not None:
            yield event


async def _aiter_sse_events(raw_stream: AsyncIterator[bytes]) -> AsyncIterator[Tuple[str, str]]:
    builder = _SSEEventBuilder()
    async for line in _aiter_sse_lines(raw_stream):
        event = builder.add_line(line)
        if event is not None:
            yield event


def _deserialize_event(event_type: str, data: str) -> KnowledgeBaseRetrievalEvent:
    payload = json.loads(data)
    if event_type == "activity.completed":
        event_data = models.KnowledgeBaseActivityRecord._deserialize(payload, [])  # pylint: disable=protected-access
        return KnowledgeBaseRetrievalEvent(event_type, event_data)
    if event_type == "references.completed":
        references = [
            models.KnowledgeBaseReference._deserialize(item, []) for item in payload  # pylint: disable=protected-access
        ]
        return KnowledgeBaseRetrievalEvent(event_type, references)
    deserializer = {
        "retrieval.started": models.KnowledgeBaseRetrievalStartedEvent,
        "activity.started": models.KnowledgeBaseActivityStartedEvent,
        "answer.completed": models.KnowledgeBaseAnswerCompletedEvent,
        "error": models.KnowledgeBaseStreamErrorEvent,
        "response.completed": models.KnowledgeBaseResponseCompletedEvent,
    }.get(event_type)
    event_data = _deserialize(deserializer, payload) if deserializer is not None else payload
    return KnowledgeBaseRetrievalEvent(event_type, event_data)


class KnowledgeBaseRetrievalStream(Iterator[KnowledgeBaseRetrievalEvent]):
    """A synchronous stream of typed knowledge base retrieval events."""

    def __init__(self, *, response: Any, raw_stream: Iterator[bytes]) -> None:
        self._response = response
        self._raw_stream = raw_stream
        self._closed = False
        self._resources_closed = False
        self._iterator = self._iterate()

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> KnowledgeBaseRetrievalEvent:
        return next(self._iterator)

    def _iterate(self) -> Generator[KnowledgeBaseRetrievalEvent, None, None]:
        try:
            for event_type, data in _iter_sse_events(self._raw_stream):
                event = _deserialize_event(event_type, data)
                if event_type in _TERMINAL_EVENTS:
                    self._close_resources()
                yield event
                if event_type in _TERMINAL_EVENTS:
                    return
        finally:
            self._close_resources()
            self._closed = True

    def _close_resources(self) -> None:
        if self._resources_closed:
            return
        self._resources_closed = True
        close = getattr(self._raw_stream, "close", None)
        try:
            if close is not None:
                close()
        finally:
            self._response.close()

    def close(self) -> None:
        """Close the stream and its underlying HTTP response."""

        if self._closed:
            return
        self._closed = True
        try:
            self._iterator.close()
        finally:
            self._close_resources()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        self.close()


class AsyncKnowledgeBaseRetrievalStream(AsyncIterator[KnowledgeBaseRetrievalEvent]):
    """An asynchronous stream of typed knowledge base retrieval events."""

    def __init__(self, *, response: Any, raw_stream: AsyncIterator[bytes]) -> None:
        self._response = response
        self._raw_stream = raw_stream
        self._closed = False
        self._resources_closed = False
        self._iterator = self._iterate()

    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> KnowledgeBaseRetrievalEvent:
        return await self._iterator.__anext__()

    async def _iterate(self) -> AsyncGenerator[KnowledgeBaseRetrievalEvent, None]:
        try:
            async for event_type, data in _aiter_sse_events(self._raw_stream):
                event = _deserialize_event(event_type, data)
                if event_type in _TERMINAL_EVENTS:
                    await self._close_resources()
                yield event
                if event_type in _TERMINAL_EVENTS:
                    return
        finally:
            await self._close_resources()
            self._closed = True

    async def _close_resources(self) -> None:
        if self._resources_closed:
            return
        self._resources_closed = True
        aclose = getattr(self._raw_stream, "aclose", None)
        try:
            if aclose is not None:
                await aclose()
        finally:
            await self._response.close()

    async def close(self) -> None:
        """Close the stream and its underlying HTTP response."""

        if self._closed:
            return
        self._closed = True
        try:
            await self._iterator.aclose()
        finally:
            await self._close_resources()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        await self.close()


__all__ = [
    "AsyncKnowledgeBaseRetrievalStream",
    "KnowledgeBaseRetrievalEvent",
    "KnowledgeBaseRetrievalEventData",
    "KnowledgeBaseRetrievalStream",
]
