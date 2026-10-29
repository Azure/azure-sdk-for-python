# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract type assertions for every public handler/consumer surface.

Every public API that returns protocol model objects returns dict-native
TypedDict payloads with discriminator fidelity.

Surfaces covered:
  1. context.request            → CreateResponse
  2. context.get_input_items()  → Sequence[Item] with subtype fidelity
  3. context.get_input_text()   → str
  4. context.get_history()      → Sequence[OutputItem] with subtype fidelity
  5. stream.response            → ResponseObject
  6. stream.response.output     → list of OutputItem subtypes
  7. Builder emit_* returns     → ResponseStreamEvent subtypes
  8. Generator convenience      → ResponseStreamEvent subtypes
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest

from azure.ai.agentserver.responses._response_context import ResponseContext
from azure.ai.agentserver.responses.models._generated import (
    CreateResponse,
    Item,
    ItemMessage,
    MessageContentInputTextContent,
    MessageRole,
    OutputItem,
    OutputItemFunctionToolCall,
    OutputItemMessage,
    OutputItemReasoningItem,
    ResponseCompletedEvent,
    ResponseContentPartAddedEvent,
    ResponseContentPartDoneEvent,
    ResponseCreatedEvent,
    ResponseFunctionCallArgumentsDeltaEvent,
    ResponseFunctionCallArgumentsDoneEvent,
    ResponseInProgressEvent,
    ResponseObject,
    ResponseOutputItemAddedEvent,
    ResponseOutputItemDoneEvent,
    ResponseStreamEvent,
    ResponseTextDeltaEvent,
    ResponseTextDoneEvent,
)
from azure.ai.agentserver.responses.models.runtime import ResponseModeFlags
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream

# ---- helpers ----


def _mode_flags() -> ResponseModeFlags:
    return ResponseModeFlags(stream=True, store=True, background=False)


def _make_request(inp: Any) -> CreateResponse:
    return cast(CreateResponse, {"model": "test-model", "input": inp})


def _mock_provider(**overrides: Any) -> Any:
    provider = AsyncMock()
    provider.get_items = AsyncMock(return_value=overrides.get("get_items_return", []))
    provider.get_history_item_ids = AsyncMock(return_value=overrides.get("get_history_item_ids_return", []))
    return provider


# =====================================================================
# 1. context.request → CreateResponse
# =====================================================================


class TestContextRequestType:
    """context.request must be a CreateResponse model instance."""

    @pytest.mark.asyncio
    async def test_request_is_create_response_model(self) -> None:
        request = _make_request("hello")
        ctx = ResponseContext(
            response_id="resp_type_1",
            mode_flags=_mode_flags(),
            request=request,
        )

        assert isinstance(ctx.request, dict)
        # Attribute access works (not a dict)
        assert ctx.request["model"] == "test-model"


# =====================================================================
# 2. context.get_input_items() → Sequence[Item] subtypes
# =====================================================================


class TestInputItemsContractTypes:
    """get_input_items() must return Item subtypes, never base Item or dicts."""

    @pytest.mark.asyncio
    async def test_inline_message_returns_item_message_subtype(self) -> None:
        msg = {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "hi"}]}
        request = cast(CreateResponse, {"model": "m", "input": [msg]})
        ctx = ResponseContext(response_id="resp_type_2a", mode_flags=_mode_flags(), request=request)

        items = await ctx.get_input_items()

        assert isinstance(items, Sequence)
        assert len(items) == 1
        assert isinstance(items[0], dict), f"Expected dict-native Item, got {type(items[0])}"
        assert items[0].get("type") == "message"

    @pytest.mark.asyncio
    async def test_resolved_reference_returns_typed_item(self) -> None:
        """Item references resolved via provider must also be Item subtypes."""
        stored_msg = cast(
            OutputItemMessage,
            {
                "id": "msg_ref_01",
                "type": "message",
                "role": "user",
                "status": "completed",
                "content": [{"type": "input_text", "text": "resolved"}],
            },
        )
        provider = _mock_provider(get_items_return=[stored_msg])
        request = cast(CreateResponse, {"model": "m", "input": [{"type": "item_reference", "id": "msg_ref_01"}]})
        ctx = ResponseContext(
            response_id="resp_type_2b",
            mode_flags=_mode_flags(),
            request=request,
            provider=provider,
        )

        items = await ctx.get_input_items()

        assert len(items) == 1
        assert isinstance(items[0], dict), f"Expected dict-native Item, got {type(items[0])}"
        assert items[0].get("type") == "message"


# =====================================================================
# 3. context.get_input_text() → str
# =====================================================================


class TestInputTextContractTypes:
    """get_input_text() must return a str, never bytes or other types."""

    @pytest.mark.asyncio
    async def test_returns_str_for_message_input(self) -> None:
        request = _make_request([{"role": "user", "content": [{"type": "input_text", "text": "hello world"}]}])
        ctx = ResponseContext(response_id="resp_type_3a", mode_flags=_mode_flags(), request=request)

        result = await ctx.get_input_text()

        assert isinstance(result, str)
        assert result == "hello world"

    @pytest.mark.asyncio
    async def test_returns_empty_str_for_no_text(self) -> None:
        request = _make_request([])
        ctx = ResponseContext(response_id="resp_type_3b", mode_flags=_mode_flags(), request=request)

        result = await ctx.get_input_text()

        assert isinstance(result, str)
        assert result == ""


# =====================================================================
# 4. context.get_history() → Sequence[OutputItem] subtypes
# =====================================================================


class TestGetHistoryContractTypes:
    """get_history() must return OutputItem subtypes with subtype fidelity."""

    @pytest.mark.asyncio
    async def test_returns_empty_sequence_without_provider(self) -> None:
        ctx = ResponseContext(response_id="resp_type_4a", mode_flags=_mode_flags())

        history = await ctx.get_history()

        assert isinstance(history, Sequence)
        assert len(history) == 0

    @pytest.mark.asyncio
    async def test_returns_typed_output_item_subtypes(self) -> None:
        """History items from provider.get_items must be proper OutputItem subtypes."""
        stored_message = cast(
            OutputItemMessage,
            {
                "id": "msg_hist_01",
                "type": "message",
                "role": "assistant",
                "status": "completed",
                "content": [{"type": "output_text", "text": "previous reply", "annotations": []}],
            },
        )
        stored_fn_call = cast(
            OutputItemFunctionToolCall,
            {
                "id": "fc_hist_01",
                "type": "function_call",
                "name": "get_weather",
                "call_id": "call_hist_01",
                "arguments": '{"city":"Seattle"}',
                "status": "completed",
            },
        )
        provider = _mock_provider(
            get_history_item_ids_return=["msg_hist_01", "fc_hist_01"],
            get_items_return=[stored_message, stored_fn_call],
        )
        ctx = ResponseContext(
            response_id="resp_type_4b",
            mode_flags=_mode_flags(),
            provider=provider,
            previous_response_id="resp_prev_x",
        )

        history = await ctx.get_history()

        assert isinstance(history, Sequence)
        assert len(history) == 2

        assert isinstance(history[0], dict), f"Expected dict-native OutputItem, got {type(history[0])}"
        assert history[0].get("type") == "message"
        assert history[0]["content"][0]["text"] == "previous reply"

        assert isinstance(history[1], dict), f"Expected dict-native OutputItem, got {type(history[1])}"
        assert history[1].get("type") == "function_call"
        assert history[1]["name"] == "get_weather"

    @pytest.mark.asyncio
    async def test_caches_result_on_second_call(self) -> None:
        """get_history() caches; second call returns same objects."""
        provider = _mock_provider(
            get_history_item_ids_return=["msg_h2"],
            get_items_return=[
                cast(
                    OutputItemMessage,
                    {
                        "id": "msg_h2",
                        "type": "message",
                        "role": "assistant",
                        "status": "completed",
                        "content": [{"type": "output_text", "text": "cached", "annotations": []}],
                    },
                )
            ],
        )
        ctx = ResponseContext(
            response_id="resp_type_4c",
            mode_flags=_mode_flags(),
            provider=provider,
            previous_response_id="resp_prev_y",
        )

        first = await ctx.get_history()
        second = await ctx.get_history()

        assert first is second  # cached tuple
        assert isinstance(first[0], dict)
        assert first[0].get("type") == "message"


# =====================================================================
# 5. stream.response → ResponseObject
# =====================================================================


class TestStreamResponseType:
    """stream.response must be a dict-native ResponseObject."""

    def test_response_is_response_object_model(self) -> None:
        stream = ResponseEventStream(response_id="resp_type_5a", model="gpt-4o")

        assert isinstance(stream.response, dict)
        assert stream.response["id"] == "resp_type_5a"
        assert stream.response["model"] == "gpt-4o"

    def test_seed_response_preserves_type(self) -> None:
        seed = cast(ResponseObject, {"id": "resp_type_5b", "object": "response", "output": [], "model": "gpt-4o"})
        stream = ResponseEventStream(response=seed)

        assert isinstance(stream.response, dict)
        assert stream.response["id"] == "resp_type_5b"


# =====================================================================
# 6. stream.response.output → list of OutputItem subtypes
# =====================================================================


class TestResponseOutputItemTypes:
    """After output_item.done, response.output items must be proper subtypes."""

    def test_message_output_item_is_output_item_message(self) -> None:
        stream = ResponseEventStream(response_id="resp_type_6a")
        stream.emit_created()
        message = stream.add_output_item_message()
        message.emit_added()
        text = message.add_text_content()
        text.emit_added()
        text.emit_delta("hello")
        text.emit_text_done()
        text.emit_done()
        message.emit_done()

        assert len(stream.response["output"]) == 1
        item = stream.response["output"][0]
        assert isinstance(item, dict), f"Expected dict-native OutputItem, got {type(item)}"
        assert item.get("type") == "message"
        assert item["content"][0]["text"] == "hello"

    def test_function_call_output_item_is_function_tool_call(self) -> None:
        stream = ResponseEventStream(response_id="resp_type_6b")
        stream.emit_created()
        fc = stream.add_output_item_function_call("get_weather", "call_1")
        fc.emit_added()
        fc.emit_arguments_delta('{"city":"Seattle"}')
        fc.emit_arguments_done('{"city":"Seattle"}')
        fc.emit_done()

        assert len(stream.response["output"]) == 1
        item = stream.response["output"][0]
        assert isinstance(item, dict), f"Expected dict-native OutputItem, got {type(item)}"
        assert item.get("type") == "function_call"
        assert item["name"] == "get_weather"
        assert item["arguments"] == '{"city":"Seattle"}'

    def test_reasoning_output_item_is_reasoning_item(self) -> None:
        stream = ResponseEventStream(response_id="resp_type_6c")
        stream.emit_created()
        reasoning = stream.add_output_item_reasoning_item()
        reasoning.emit_added()
        summary = reasoning.add_summary_part()
        summary.emit_added()
        summary.emit_text_done("thinking...")
        summary.emit_done()
        reasoning.emit_done()

        assert len(stream.response["output"]) == 1
        item = stream.response["output"][0]
        assert isinstance(item, dict), f"Expected dict-native OutputItem, got {type(item)}"
        assert item.get("type") == "reasoning"

    def test_multiple_output_items_all_typed(self) -> None:
        """Mixed output items must all be proper subtypes."""
        stream = ResponseEventStream(response_id="resp_type_6d")
        stream.emit_created()

        # Message
        msg = stream.add_output_item_message()
        msg.emit_added()
        t = msg.add_text_content()
        t.emit_added()
        t.emit_delta("hi")
        t.emit_text_done()
        t.emit_done()
        msg.emit_done()

        # Function call
        fc = stream.add_output_item_function_call("fn", "call_2")
        fc.emit_added()
        fc.emit_arguments_done("{}")
        fc.emit_done()

        assert len(stream.response["output"]) == 2
        assert stream.response["output"][0].get("type") == "message"
        assert stream.response["output"][1].get("type") == "function_call"


# =====================================================================
# 7. Builder emit_* returns → ResponseStreamEvent subtypes
# =====================================================================


class TestBuilderEventTypes:
    """Every builder emit_* method must return a dict-native ResponseStreamEvent payload."""

    def test_lifecycle_events_are_typed(self) -> None:
        stream = ResponseEventStream(response_id="resp_type_7a")

        created = stream.emit_created()
        assert isinstance(created, dict)
        assert created["type"] == "response.created"

        in_progress = stream.emit_in_progress()
        assert isinstance(in_progress, dict)
        assert in_progress["type"] == "response.in_progress"

        msg = stream.add_output_item_message()
        msg.emit_added()
        t = msg.add_text_content()
        t.emit_added()
        t.emit_delta("x")
        t.emit_text_done()
        t.emit_done()
        msg.emit_done()

        completed = stream.emit_completed()
        assert isinstance(completed, dict)
        assert completed["type"] == "response.completed"

    def test_message_builder_events_are_typed(self) -> None:
        stream = ResponseEventStream(response_id="resp_type_7b")
        stream.emit_created()

        message = stream.add_output_item_message()
        added = message.emit_added()
        assert isinstance(added, dict)
        assert added["type"] == "response.output_item.added"

        text = message.add_text_content()
        content_added = text.emit_added()
        assert isinstance(content_added, dict)
        assert content_added["type"] == "response.content_part.added"

        delta = text.emit_delta("hello")
        assert isinstance(delta, dict)
        assert delta["type"] == "response.output_text.delta"

        text_done = text.emit_text_done()
        assert isinstance(text_done, dict)
        assert text_done["type"] == "response.output_text.done"

        content_done = text.emit_done()
        assert isinstance(content_done, dict)
        assert content_done["type"] == "response.content_part.done"

        item_done = message.emit_done()
        assert isinstance(item_done, dict)
        assert item_done["type"] == "response.output_item.done"

    def test_function_call_builder_events_are_typed(self) -> None:
        stream = ResponseEventStream(response_id="resp_type_7c")
        stream.emit_created()

        fc = stream.add_output_item_function_call("fn", "call_1")
        added = fc.emit_added()
        assert added["type"] == "response.output_item.added"

        delta = fc.emit_arguments_delta('{"k":')
        assert delta["type"] == "response.function_call_arguments.delta"

        args_done = fc.emit_arguments_done('{"k":"v"}')
        assert args_done["type"] == "response.function_call_arguments.done"

        done = fc.emit_done()
        assert done["type"] == "response.output_item.done"


# =====================================================================
# 8. Generator convenience methods → ResponseStreamEvent subtypes
# =====================================================================


class TestGeneratorConvenienceTypes:
    """Generator convenience methods must yield dict-native ResponseStreamEvent payloads."""

    def test_output_item_message_events_are_typed(self) -> None:
        stream = ResponseEventStream(response_id="resp_type_8a")
        stream.emit_created()
        stream.emit_in_progress()

        events = list(stream.output_item_message("Hi there"))

        for event in events:
            assert isinstance(event, dict), f"Expected dict-native ResponseStreamEvent, got {type(event)}"

        # Verify specific subtypes for key events
        assert events[0]["type"] == "response.output_item.added"
        assert events[1]["type"] == "response.content_part.added"
        assert events[2]["type"] == "response.output_text.delta"
        assert events[3]["type"] == "response.output_text.done"
        assert events[4]["type"] == "response.content_part.done"
        assert events[5]["type"] == "response.output_item.done"

    def test_output_item_function_call_events_are_typed(self) -> None:
        stream = ResponseEventStream(response_id="resp_type_8b")
        stream.emit_created()
        stream.emit_in_progress()

        events = list(stream.output_item_function_call("fn", "call_1", "{}"))

        for event in events:
            assert isinstance(event, dict)

        assert events[0]["type"] == "response.output_item.added"
        assert events[-1]["type"] == "response.output_item.done"

    def test_output_item_reasoning_events_are_typed(self) -> None:
        stream = ResponseEventStream(response_id="resp_type_8c")
        stream.emit_created()
        stream.emit_in_progress()

        events = list(stream.output_item_reasoning_item("thinking"))

        for event in events:
            assert isinstance(event, dict)

        assert events[0]["type"] == "response.output_item.added"
        assert events[-1]["type"] == "response.output_item.done"


# =====================================================================
# 9. In-memory provider round-trip preserves OutputItem subtypes
# =====================================================================


class TestInMemoryProviderTypePreservation:
    """Items stored and retrieved through InMemoryResponseProvider must
    retain their discriminator identity."""

    @pytest.mark.asyncio
    async def test_stored_output_items_retrieved_as_subtypes(self) -> None:
        """output items stored via create_response → get_items must be proper subtypes."""
        from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider

        provider = InMemoryResponseProvider()

        # Build a response with typed output items on response.output
        response = cast(
            ResponseObject,
            {
                "id": "resp_mem_1",
                "object": "response",
                "status": "completed",
                "model": "gpt-4o",
                "output": [
                    {
                        "id": "msg_mem_1",
                        "type": "message",
                        "role": "assistant",
                        "status": "completed",
                        "content": [{"type": "output_text", "text": "stored text", "annotations": []}],
                    },
                    {
                        "id": "fc_mem_1",
                        "type": "function_call",
                        "name": "lookup",
                        "call_id": "call_mem_1",
                        "arguments": "{}",
                        "status": "completed",
                    },
                ],
            },
        )

        await provider.create_response(response, input_items=None, history_item_ids=None)

        # Retrieve items
        items = await provider.get_items(["msg_mem_1", "fc_mem_1"])

        assert len(items) == 2
        assert items[0] is not None
        assert items[1] is not None
        assert isinstance(items[0], dict)
        assert items[0].get("type") == "message"
        assert items[0]["content"][0]["text"] == "stored text"

        assert isinstance(items[1], dict)
        assert items[1].get("type") == "function_call"
        assert items[1]["name"] == "lookup"

    @pytest.mark.asyncio
    async def test_history_round_trip_preserves_subtypes(self) -> None:
        """Items stored as output → retrieved via get_history must be proper subtypes."""
        from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider

        provider = InMemoryResponseProvider()

        # Create a completed response with output items
        response = cast(
            ResponseObject,
            {
                "id": "resp_hist_rt_1",
                "object": "response",
                "status": "completed",
                "model": "gpt-4o",
                "conversation": {"id": "conv_rt_1"},
                "output": [
                    {
                        "id": "msg_rt_1",
                        "type": "message",
                        "role": "assistant",
                        "status": "completed",
                        "content": [{"type": "output_text", "text": "turn 1 reply", "annotations": []}],
                    }
                ],
            },
        )
        await provider.create_response(response, input_items=None, history_item_ids=None)

        # Now create a second response that references the first via previous_response_id
        ctx = ResponseContext(
            response_id="resp_hist_rt_2",
            mode_flags=_mode_flags(),
            provider=provider,
            previous_response_id="resp_hist_rt_1",
        )

        history = await ctx.get_history()

        assert len(history) >= 1
        # The message from turn 1 must be a proper OutputItemMessage
        msg_item = next((h for h in history if h.get("id") == "msg_rt_1"), None)
        assert msg_item is not None, "Expected msg_rt_1 in history"
        assert isinstance(msg_item, dict)
        assert msg_item.get("type") == "message"
        assert msg_item["content"][0]["text"] == "turn 1 reply"


# =====================================================================
# 10. Streaming response.output after full stream lifecycle
# =====================================================================


class TestStreamLifecycleOutputTypes:
    """After a full create→in_progress→items→completed stream, response.output
    must contain dict-native OutputItem payloads."""

    def test_full_stream_lifecycle_output_types(self) -> None:
        stream = ResponseEventStream(response_id="resp_type_10a", model="gpt-4o")
        stream.emit_created()
        stream.emit_in_progress()

        # Emit message item
        for _ in stream.output_item_message("Hello"):
            pass

        # Emit function call item
        for _ in stream.output_item_function_call("get_temp", "call_a", '{"unit":"C"}'):
            pass

        stream.emit_completed()

        output = stream.response["output"]
        assert len(output) == 2

        assert isinstance(output[0], dict)
        assert output[0].get("type") == "message"
        assert output[0]["content"][0]["text"] == "Hello"

        assert isinstance(output[1], dict)
        assert output[1].get("type") == "function_call"
        assert output[1]["name"] == "get_temp"
        assert output[1]["arguments"] == '{"unit":"C"}'
