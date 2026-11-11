# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Async response event stream."""
# pylint: disable=invalid-overridden-method

from __future__ import annotations

from collections.abc import AsyncIterable
from typing import Any, AsyncIterator, Sequence

from ..._id_generator import IdGenerator
from ... import models as response_models
from ...streaming._event_stream import ResponseEventStream as SyncResponseEventStream
from ._builders import (
    OutputItemCodeInterpreterCallBuilder,
    OutputItemCustomToolCallBuilder,
    OutputItemFunctionCallBuilder,
    OutputItemMessageBuilder,
    OutputItemMcpCallBuilder,
    OutputItemReasoningItemBuilder,
)


class ResponseEventStream(SyncResponseEventStream):  # pylint: disable=too-many-public-methods
    """Async response event stream with deterministic sequence numbers."""

    def add_output_item_message(self) -> OutputItemMessageBuilder:
        """Add a message output item and return its async scoped builder.

        :returns: A builder for emitting message content, text deltas, and lifecycle events.
        :rtype: OutputItemMessageBuilder
        """
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_message_item_id(self._response_id)
        return OutputItemMessageBuilder(self, output_index=output_index, item_id=item_id)

    def add_output_item_function_call(self, name: str, call_id: str) -> OutputItemFunctionCallBuilder:
        """Add a function-call output item and return its async scoped builder.

        :param name: The function name being called.
        :type name: str
        :param call_id: Unique identifier for this function call.
        :type call_id: str
        :returns: A builder for emitting function-call argument deltas and lifecycle events.
        :rtype: OutputItemFunctionCallBuilder
        """
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_function_call_item_id(self._response_id)
        return OutputItemFunctionCallBuilder(
            self,
            output_index=output_index,
            item_id=item_id,
            name=name,
            call_id=call_id,
        )

    def add_output_item_reasoning_item(self) -> OutputItemReasoningItemBuilder:
        """Add a reasoning output item and return its async scoped builder.

        :returns: A builder for emitting reasoning summary parts and lifecycle events.
        :rtype: OutputItemReasoningItemBuilder
        """
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_reasoning_item_id(self._response_id)
        return OutputItemReasoningItemBuilder(self, output_index=output_index, item_id=item_id)

    def add_output_item_code_interpreter_call(
        self,
    ) -> OutputItemCodeInterpreterCallBuilder:
        """Add a code-interpreter tool call output item.

        :returns: A builder for emitting code-interpreter call lifecycle events.
        :rtype: OutputItemCodeInterpreterCallBuilder
        """
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_code_interpreter_call_item_id(self._response_id)
        return OutputItemCodeInterpreterCallBuilder(self, output_index=output_index, item_id=item_id)

    def add_output_item_mcp_call(
        self,
        server_label: str,
        name: str,
        *,
        item_id: str | None = None,
    ) -> OutputItemMcpCallBuilder:
        """Add an MCP tool call output item and return its async scoped builder.

        :param server_label: Label identifying the MCP server.
        :type server_label: str
        :param name: Name of the MCP tool being called.
        :type name: str
        :keyword item_id: Optional caller-supplied output item identifier.
        :keyword type item_id: str | None
        :returns: A builder for emitting MCP call argument deltas and lifecycle events.
        :rtype: OutputItemMcpCallBuilder
        """
        output_index = self._output_index
        self._output_index += 1
        if item_id is None:
            resolved_item_id = IdGenerator.new_mcp_call_item_id(self._response_id)
        else:
            if not isinstance(item_id, str):
                raise TypeError("item_id must be a string")
            resolved_item_id = item_id.strip()
            if not resolved_item_id:
                raise ValueError("item_id must be a non-empty string")
        return OutputItemMcpCallBuilder(
            self,
            output_index=output_index,
            item_id=resolved_item_id,
            server_label=server_label,
            name=name,
        )

    def add_output_item_custom_tool_call(self, call_id: str, name: str) -> OutputItemCustomToolCallBuilder:
        """Add a custom tool call output item and return its async scoped builder.

        :param call_id: Unique identifier for this tool call.
        :type call_id: str
        :param name: Name of the custom tool being called.
        :type name: str
        :returns: A builder for emitting custom tool call input deltas and lifecycle events.
        :rtype: OutputItemCustomToolCallBuilder
        """
        output_index = self._output_index
        self._output_index += 1
        item_id = IdGenerator.new_custom_tool_call_item_id(self._response_id)
        return OutputItemCustomToolCallBuilder(
            self,
            output_index=output_index,
            item_id=item_id,
            call_id=call_id,
            name=name,
        )

    async def output_item_message(  # type: ignore[override]
        self,
        text: str | AsyncIterable[str],
        *,
        annotations: Sequence[response_models.Annotation] | None = None,
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield the full lifecycle for a text message output item.

        :param text: Complete text or async iterable of text chunks.
        :type text: str | AsyncIterable[str]
        :keyword annotations: Optional annotations to attach to the text content.
        :keyword type annotations: Sequence[Annotation] | None
        :returns: An async iterator of events.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        if isinstance(text, str):
            for event in super().output_item_message(text, annotations=annotations):
                yield event
            return
        message = self.add_output_item_message()
        yield message.emit_added()
        tc = message.add_text_content()
        yield tc.emit_added()
        accumulated = ""
        async for chunk in text:
            yield tc.emit_delta(chunk)
            accumulated += chunk
        yield tc.emit_text_done(accumulated)
        if annotations:
            for ann in annotations:
                yield tc.emit_annotation_added(ann)
        yield tc.emit_done()
        yield message.emit_done()

    async def output_item_function_call(  # type: ignore[override]
        self, name: str, call_id: str, arguments: str | AsyncIterable[str]
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield the full lifecycle for a function call output item.

        :param name: The function name being called.
        :type name: str
        :param call_id: Unique identifier for this function call.
        :type call_id: str
        :param arguments: Complete arguments string or async iterable of chunks.
        :type arguments: str | AsyncIterable[str]
        :returns: An async iterator of events.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        fc = self.add_output_item_function_call(name=name, call_id=call_id)
        yield fc.emit_added()
        async for event in fc.arguments(arguments):
            yield event
        yield fc.emit_done()

    async def output_item_function_call_output(  # type: ignore[override]
        self, call_id: str, output: str
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield the full lifecycle for a function call output item.

        :param call_id: The call ID of the function call this output belongs to.
        :type call_id: str
        :param output: The output value for the function call.
        :type output: str
        :returns: An async iterator of events.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        for event in super().output_item_function_call_output(call_id, output):
            yield event

    async def output_item_reasoning_item(  # type: ignore[override]
        self, summary_text: str | AsyncIterable[str]
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield the full lifecycle for a reasoning output item.

        :param summary_text: Complete summary text or async iterable of chunks.
        :type summary_text: str | AsyncIterable[str]
        :returns: An async iterator of events.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        item = self.add_output_item_reasoning_item()
        yield item.emit_added()
        async for event in item.summary_part(summary_text):
            yield event
        yield item.emit_done()

    async def output_item_image_gen_call(  # type: ignore[override]
        self,
        result_base64: str,
        *,
        partials: AsyncIterable[str] | None = None,
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield the full lifecycle for an image generation call.

        :param result_base64: The final base64-encoded image result.
        :type result_base64: str
        :keyword partials: Optional async iterable of partial base64 image strings.
        :keyword type partials: AsyncIterable[str] | None
        :returns: An async iterator of events.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        ig = self.add_output_item_image_gen_call()
        yield ig.emit_added()
        yield ig.emit_in_progress()
        yield ig.emit_generating()
        if partials is not None:
            async for partial in partials:
                yield ig.emit_partial_image(partial)
        yield ig.emit_completed()
        yield ig.emit_done(result_base64)

    async def output_item_structured_outputs(  # type: ignore[override]
        self, output: Any
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield the full lifecycle for a structured outputs item.

        :param output: The structured output data.
        :type output: Any
        :returns: An async iterator of events.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        for event in super().output_item_structured_outputs(output):
            yield event

    async def output_item_computer_call(  # type: ignore[override]
        self,
        call_id: str,
        action: response_models.ComputerAction,
        *,
        pending_safety_checks: list[response_models.ComputerCallSafetyCheckParam] | None = None,
        status: str = "completed",
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield the full lifecycle for a computer call output item.

        :param call_id: Unique identifier for this tool call.
        :type call_id: str
        :param action: The computer action.
        :type action: ComputerAction
        :keyword pending_safety_checks: Optional safety checks.
        :keyword type pending_safety_checks: list[ComputerCallSafetyCheckParam] | None
        :keyword status: Status; defaults to ``"completed"``.
        :keyword type status: str
        :returns: An async iterator of events.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        for event in super().output_item_computer_call(
            call_id, action, pending_safety_checks=pending_safety_checks, status=status
        ):
            yield event

    async def output_item_computer_call_output(  # type: ignore[override]
        self,
        call_id: str,
        output: response_models.ComputerScreenshotImage,
        *,
        acknowledged_safety_checks: list[response_models.ComputerCallSafetyCheckParam] | None = None,
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield the full lifecycle for a computer call output item.

        :param call_id: The call ID this output belongs to.
        :type call_id: str
        :param output: The screenshot image output.
        :type output: ComputerScreenshotImage
        :keyword acknowledged_safety_checks: Optional acknowledged safety checks.
        :keyword type acknowledged_safety_checks: list[ComputerCallSafetyCheckParam] | None
        :returns: An async iterator of events.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        for event in super().output_item_computer_call_output(
            call_id, output, acknowledged_safety_checks=acknowledged_safety_checks
        ):
            yield event

    async def output_item_local_shell_call(  # type: ignore[override]
        self,
        call_id: str,
        action: response_models.LocalShellExecAction,
        *,
        status: str = "completed",
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield the full lifecycle for a local shell call output item.

        :param call_id: Unique identifier for this tool call.
        :type call_id: str
        :param action: The shell exec action.
        :type action: LocalShellExecAction
        :keyword status: Status; defaults to ``"completed"``.
        :keyword type status: str
        :returns: An async iterator of events.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        for event in super().output_item_local_shell_call(call_id, action, status=status):
            yield event

    async def output_item_local_shell_call_output(  # type: ignore[override]
        self, output: str
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield the full lifecycle for a local shell call output item.

        :param output: The shell output string.
        :type output: str
        :returns: An async iterator of events.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        for event in super().output_item_local_shell_call_output(output):
            yield event

    async def output_item_function_shell_call(  # type: ignore[override]
        self,
        call_id: str,
        action: response_models.FunctionShellAction,
        environment: response_models.FunctionShellCallEnvironment,
        *,
        status: str = "completed",
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield the full lifecycle for a function shell call output item.

        :param call_id: Unique identifier for this tool call.
        :type call_id: str
        :param action: The function shell action.
        :type action: FunctionShellAction
        :param environment: The execution environment.
        :type environment: FunctionShellCallEnvironment
        :keyword status: Status; defaults to ``"completed"``.
        :keyword type status: str
        :returns: An async iterator of events.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        for event in super().output_item_function_shell_call(call_id, action, environment, status=status):
            yield event

    async def output_item_function_shell_call_output(  # type: ignore[override]
        self,
        call_id: str,
        output: list[response_models.FunctionShellCallOutputContent],
        *,
        status: str = "completed",
        max_output_length: int | None = None,
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield the full lifecycle for a function shell call output item.

        :param call_id: The call ID this output belongs to.
        :type call_id: str
        :param output: The output content list.
        :type output: list[FunctionShellCallOutputContent]
        :keyword status: Status; defaults to ``"completed"``.
        :keyword type status: str
        :keyword max_output_length: Maximum output length.
        :keyword type max_output_length: int | None
        :returns: An async iterator of events.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        for event in super().output_item_function_shell_call_output(
            call_id, output, status=status, max_output_length=max_output_length
        ):
            yield event

    async def output_item_apply_patch_call(  # type: ignore[override]
        self,
        call_id: str,
        operation: response_models.ApplyPatchFileOperation,
        *,
        status: str = "completed",
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield the full lifecycle for an apply-patch call output item.

        :param call_id: Unique identifier for this tool call.
        :type call_id: str
        :param operation: The patch file operation.
        :type operation: ApplyPatchFileOperation
        :keyword status: Status; defaults to ``"completed"``.
        :keyword type status: str
        :returns: An async iterator of events.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        for event in super().output_item_apply_patch_call(call_id, operation, status=status):
            yield event

    async def output_item_apply_patch_call_output(  # type: ignore[override]
        self,
        call_id: str,
        *,
        status: str = "completed",
        output: str | None = None,
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield the full lifecycle for an apply-patch call output item.

        :param call_id: The call ID this output belongs to.
        :type call_id: str
        :keyword status: Status; defaults to ``"completed"``.
        :keyword type status: str
        :keyword output: Optional output string.
        :keyword type output: str | None
        :returns: An async iterator of events.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        for event in super().output_item_apply_patch_call_output(call_id, status=status, output=output):
            yield event

    async def output_item_custom_tool_call_output(  # type: ignore[override]
        self,
        call_id: str,
        output: str | list[response_models.FunctionAndCustomToolCallOutput],
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield the full lifecycle for a custom tool call output item.

        :param call_id: The call ID this output belongs to.
        :type call_id: str
        :param output: The output value (string or structured list).
        :type output: str | list[FunctionAndCustomToolCallOutput]
        :returns: An async iterator of events.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        for event in super().output_item_custom_tool_call_output(call_id, output):
            yield event

    async def output_item_mcp_approval_request(  # type: ignore[override]
        self, server_label: str, name: str, arguments: str
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield the full lifecycle for an MCP approval request item.

        :param server_label: Label identifying the MCP server.
        :type server_label: str
        :param name: Tool name requiring approval.
        :type name: str
        :param arguments: JSON string of the tool arguments.
        :type arguments: str
        :returns: An async iterator of events.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        for event in super().output_item_mcp_approval_request(server_label, name, arguments):
            yield event

    async def output_item_mcp_approval_response(  # type: ignore[override]
        self,
        approval_request_id: str,
        approve: bool,
        *,
        reason: str | None = None,
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield the full lifecycle for an MCP approval response item.

        :param approval_request_id: The request ID being responded to.
        :type approval_request_id: str
        :param approve: Whether to approve.
        :type approve: bool
        :keyword reason: Optional reason for the decision.
        :keyword type reason: str | None
        :returns: An async iterator of events.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        for event in super().output_item_mcp_approval_response(approval_request_id, approve, reason=reason):
            yield event

    async def output_item_compaction(  # type: ignore[override]
        self, encrypted_content: str
    ) -> AsyncIterator[response_models.ResponseStreamEvent]:
        """Yield the full lifecycle for a compaction output item.

        :param encrypted_content: The encrypted compaction content.
        :type encrypted_content: str
        :returns: An async iterator of events.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        for event in super().output_item_compaction(encrypted_content):
            yield event


__all__ = [
    "ResponseEventStream",
]
