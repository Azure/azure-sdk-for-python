# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Async streaming output-item builders."""
# pylint: disable=invalid-overridden-method

from __future__ import annotations

from collections.abc import AsyncIterable
from typing import AsyncIterator

from ... import models as response_models
from ...streaming._builders import (
    OutputItemBuilder,
    OutputItemCodeInterpreterCallBuilder as SyncOutputItemCodeInterpreterCallBuilder,
    OutputItemCustomToolCallBuilder as SyncOutputItemCustomToolCallBuilder,
    OutputItemFileSearchCallBuilder,
    OutputItemFunctionCallBuilder as SyncOutputItemFunctionCallBuilder,
    OutputItemFunctionCallOutputBuilder,
    OutputItemImageGenCallBuilder,
    OutputItemMcpCallBuilder as SyncOutputItemMcpCallBuilder,
    OutputItemMcpListToolsBuilder,
    OutputItemMessageBuilder as SyncOutputItemMessageBuilder,
    OutputItemReasoningItemBuilder as SyncOutputItemReasoningItemBuilder,
    OutputItemWebSearchCallBuilder,
    ReasoningSummaryPartBuilder,
    RefusalContentBuilder,
    TextContentBuilder,
)


class OutputItemMessageBuilder(SyncOutputItemMessageBuilder):
    """Async scoped builder for a message output item."""

    async def text_content(  # type: ignore[override]
        self, text: str | AsyncIterable[str]
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield the full lifecycle for a text content part.

        :param text: Complete text or async iterable of text chunks.
        :type text: str | AsyncIterable[str]
        :returns: An async iterator of event dicts.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        if isinstance(text, str):
            for event in super().text_content(text):
                yield event
            return
        tc = self.add_text_content()
        yield tc.emit_added()
        async for chunk in text:
            yield tc.emit_delta(chunk)
        yield tc.emit_text_done()
        yield tc.emit_done()

    async def refusal_content(  # type: ignore[override]
        self, text: str | AsyncIterable[str]
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield the full lifecycle for a refusal content part.

        :param text: Complete refusal text or async iterable of text chunks.
        :type text: str | AsyncIterable[str]
        :returns: An async iterator of event dicts.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        if isinstance(text, str):
            for event in super().refusal_content(text):
                yield event
            return
        rc = self.add_refusal_content()
        yield rc.emit_added()
        accumulated: list[str] = []
        async for chunk in text:
            accumulated.append(chunk)
            yield rc.emit_delta(chunk)
        yield rc.emit_refusal_done("".join(accumulated))
        yield rc.emit_done()


class OutputItemFunctionCallBuilder(SyncOutputItemFunctionCallBuilder):
    """Async scoped builder for a function-call output item."""

    async def arguments(  # type: ignore[override]
        self, args: str | AsyncIterable[str]
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield argument delta and done events.

        :param args: Complete arguments string or async iterable of chunks.
        :type args: str | AsyncIterable[str]
        :returns: An async iterator of events.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        if isinstance(args, str):
            for event in super().arguments(args):
                yield event
            return
        accumulated: list[str] = []
        async for chunk in args:
            accumulated.append(chunk)
            yield self.emit_arguments_delta(chunk)
        yield self.emit_arguments_done("".join(accumulated))


class OutputItemReasoningItemBuilder(SyncOutputItemReasoningItemBuilder):
    """Async scoped builder for a reasoning output item."""

    async def summary_part(  # type: ignore[override]
        self,
        text: str | AsyncIterable[str],
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield the full lifecycle for a reasoning summary part.

        :param text: Complete summary text or async iterable of text chunks.
        :type text: str | AsyncIterable[str]
        :returns: An async iterator of events.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        if isinstance(text, str):
            for event in super().summary_part(text):
                yield event
            return
        part = self.add_summary_part()
        yield part.emit_added()
        accumulated: list[str] = []
        async for chunk in text:
            accumulated.append(chunk)
            yield part.emit_text_delta(chunk)
        final = "".join(accumulated)
        yield part.emit_text_done(final)
        yield part.emit_done()


class OutputItemCodeInterpreterCallBuilder(SyncOutputItemCodeInterpreterCallBuilder):
    """Async scoped builder for code-interpreter tool call events."""

    async def code(  # type: ignore[override]
        self, code_text: str | AsyncIterable[str]
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield code delta and done events.

        :param code_text: Complete code string or async iterable of chunks.
        :type code_text: str | AsyncIterable[str]
        :returns: An async iterator of event dicts.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        if isinstance(code_text, str):
            for event in super().code(code_text):
                yield event
            return
        accumulated: list[str] = []
        async for chunk in code_text:
            accumulated.append(chunk)
            yield self.emit_code_delta(chunk)
        yield self.emit_code_done("".join(accumulated))


class OutputItemMcpCallBuilder(SyncOutputItemMcpCallBuilder):
    """Async scoped builder for MCP call argument deltas and lifecycle events."""

    async def arguments(  # type: ignore[override]
        self, args: str | AsyncIterable[str]
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield MCP call argument delta and done events.

        :param args: Complete arguments string or async iterable of chunks.
        :type args: str | AsyncIterable[str]
        :returns: An async iterator of event dicts.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        if isinstance(args, str):
            for event in super().arguments(args):
                yield event
            return
        accumulated: list[str] = []
        async for chunk in args:
            accumulated.append(chunk)
            yield self.emit_arguments_delta(chunk)
        yield self.emit_arguments_done("".join(accumulated))


class OutputItemCustomToolCallBuilder(SyncOutputItemCustomToolCallBuilder):
    """Async scoped builder for custom tool call input deltas and lifecycle events."""

    async def input(  # type: ignore[override]
        self, input_text: str | AsyncIterable[str]
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield custom tool input delta and done events.

        :param input_text: Complete input text or async iterable of chunks.
        :type input_text: str | AsyncIterable[str]
        :returns: An async iterator of event dicts.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        if isinstance(input_text, str):
            for event in super().input(input_text):
                yield event
            return
        accumulated: list[str] = []
        async for chunk in input_text:
            accumulated.append(chunk)
            yield self.emit_input_delta(chunk)
        yield self.emit_input_done("".join(accumulated))


__all__ = [
    "TextContentBuilder",
    "OutputItemMessageBuilder",
    "OutputItemBuilder",
    "OutputItemFunctionCallBuilder",
    "OutputItemFunctionCallOutputBuilder",
    "RefusalContentBuilder",
    "OutputItemReasoningItemBuilder",
    "ReasoningSummaryPartBuilder",
    "OutputItemFileSearchCallBuilder",
    "OutputItemWebSearchCallBuilder",
    "OutputItemCodeInterpreterCallBuilder",
    "OutputItemImageGenCallBuilder",
    "OutputItemMcpCallBuilder",
    "OutputItemMcpListToolsBuilder",
    "OutputItemCustomToolCallBuilder",
]
