# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Strongly-typed return type assertions for every public emit_* method.

Every builder ``emit_*`` method must return the specific ``ResponseStreamEvent``
subtype per spec (e.g. ``emit_added()`` on a message
builder returns ``ResponseOutputItemAddedEvent``, not the base
``ResponseStreamEvent``).  These tests assert the ``isinstance`` contract for
every public emit method on every builder class.

Builder classes covered:
  - ResponseEventStream (lifecycle: queued, created, in_progress, completed, failed, incomplete)
  - OutputItemBuilder (generic: emit_added, emit_done)
  - OutputItemMessageBuilder (emit_added, emit_done)
  - TextContentBuilder (emit_added, emit_delta, emit_text_done, emit_done, emit_annotation_added)
  - RefusalContentBuilder (emit_added, emit_delta, emit_refusal_done, emit_done)
  - OutputItemFunctionCallBuilder (emit_added, emit_arguments_delta, emit_arguments_done, emit_done)
  - OutputItemFunctionCallOutputBuilder (emit_added, emit_done)
  - OutputItemReasoningItemBuilder (emit_added, emit_done)
  - ReasoningSummaryPartBuilder (emit_added, emit_text_delta, emit_text_done, emit_done)
  - OutputItemFileSearchCallBuilder (emit_added, emit_in_progress, emit_searching, emit_completed, emit_done)
  - OutputItemWebSearchCallBuilder (emit_added, emit_in_progress, emit_searching, emit_completed, emit_done)
  - OutputItemCodeInterpreterCallBuilder (emit_added, emit_in_progress, emit_interpreting,
      emit_code_delta, emit_code_done, emit_completed, emit_done)
  - OutputItemImageGenCallBuilder (emit_added, emit_in_progress, emit_generating,
      emit_partial_image, emit_completed, emit_done)
  - OutputItemMcpCallBuilder (emit_added, emit_in_progress, emit_arguments_delta,
      emit_arguments_done, emit_completed, emit_failed, emit_done)
  - OutputItemMcpListToolsBuilder (emit_added, emit_in_progress, emit_completed,
      emit_failed, emit_done)
  - OutputItemCustomToolCallBuilder (emit_added, emit_input_delta, emit_input_done, emit_done)
"""

from __future__ import annotations

from azure.ai.agentserver.responses.models._generated import (
    ResponseCodeInterpreterCallCodeDeltaEvent,
    ResponseCodeInterpreterCallCodeDoneEvent,
    ResponseCodeInterpreterCallCompletedEvent,
    ResponseCodeInterpreterCallInProgressEvent,
    ResponseCodeInterpreterCallInterpretingEvent,
    ResponseCompletedEvent,
    ResponseContentPartAddedEvent,
    ResponseContentPartDoneEvent,
    ResponseCreatedEvent,
    ResponseCustomToolCallInputDeltaEvent,
    ResponseCustomToolCallInputDoneEvent,
    ResponseFailedEvent,
    ResponseFileSearchCallCompletedEvent,
    ResponseFileSearchCallInProgressEvent,
    ResponseFileSearchCallSearchingEvent,
    ResponseFunctionCallArgumentsDeltaEvent,
    ResponseFunctionCallArgumentsDoneEvent,
    ResponseImageGenCallCompletedEvent,
    ResponseImageGenCallGeneratingEvent,
    ResponseImageGenCallInProgressEvent,
    ResponseImageGenCallPartialImageEvent,
    ResponseIncompleteEvent,
    ResponseInProgressEvent,
    ResponseMCPCallArgumentsDeltaEvent,
    ResponseMCPCallArgumentsDoneEvent,
    ResponseMCPCallCompletedEvent,
    ResponseMCPCallFailedEvent,
    ResponseMCPCallInProgressEvent,
    ResponseMCPListToolsCompletedEvent,
    ResponseMCPListToolsFailedEvent,
    ResponseMCPListToolsInProgressEvent,
    ResponseOutputItemAddedEvent,
    ResponseOutputItemDoneEvent,
    ResponseOutputTextAnnotationAddedEvent,
    ResponseQueuedEvent,
    ResponseReasoningSummaryPartAddedEvent,
    ResponseReasoningSummaryPartDoneEvent,
    ResponseReasoningSummaryTextDeltaEvent,
    ResponseReasoningSummaryTextDoneEvent,
    ResponseRefusalDeltaEvent,
    ResponseRefusalDoneEvent,
    ResponseTextDeltaEvent,
    ResponseTextDoneEvent,
    ResponseWebSearchCallCompletedEvent,
    ResponseWebSearchCallInProgressEvent,
    ResponseWebSearchCallSearchingEvent,
    StructuredOutputsOutputItem,
    UrlCitationBody,
)
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream

# ---- helper ----


def _stream() -> ResponseEventStream:
    return ResponseEventStream(response_id="resp_emit_types")


# =====================================================================
# ResponseEventStream lifecycle methods
# =====================================================================


class TestLifecycleReturnTypes:
    """Lifecycle emit methods on ResponseEventStream must return specific subtypes."""

    def test_emit_queued(self) -> None:
        # The state-machine validator requires ``response.created`` as the first
        # event so we cannot call ``emit_queued`` in isolation.  Instead, verify
        # the underlying cast by constructing the model directly – the same
        # ``construct_event_model`` helper that ``_emit_event`` delegates to.
        from azure.ai.agentserver.responses.streaming._internals import construct_event_model

        raw = {
            "type": "response.queued",
            "sequence_number": 0,
            "response": {"id": "r1", "object": "response", "output": []},
        }
        model = construct_event_model(raw)
        assert isinstance(model, ResponseQueuedEvent)

    def test_emit_created(self) -> None:
        s = _stream()
        event = s.emit_created()
        assert isinstance(event, ResponseCreatedEvent), f"Expected ResponseCreatedEvent, got {type(event)}"

    def test_emit_in_progress(self) -> None:
        s = _stream()
        s.emit_created()
        event = s.emit_in_progress()
        assert isinstance(event, ResponseInProgressEvent), f"Expected ResponseInProgressEvent, got {type(event)}"

    def test_emit_completed(self) -> None:
        s = _stream()
        s.emit_created()
        s.emit_in_progress()
        # Need at least one output item before completed
        msg = s.add_output_item_message()
        msg.emit_added()
        tc = msg.add_text_content()
        tc.emit_added()
        tc.emit_delta("x")
        tc.emit_text_done()
        tc.emit_done()
        msg.emit_done()
        event = s.emit_completed()
        assert isinstance(event, ResponseCompletedEvent), f"Expected ResponseCompletedEvent, got {type(event)}"

    def test_emit_failed(self) -> None:
        s = _stream()
        s.emit_created()
        s.emit_in_progress()
        event = s.emit_failed()
        assert isinstance(event, ResponseFailedEvent), f"Expected ResponseFailedEvent, got {type(event)}"

    def test_emit_incomplete(self) -> None:
        s = _stream()
        s.emit_created()
        s.emit_in_progress()
        event = s.emit_incomplete(reason="max_output_tokens")
        assert isinstance(event, ResponseIncompleteEvent), f"Expected ResponseIncompleteEvent, got {type(event)}"


# =====================================================================
# OutputItemBuilder (generic)
# =====================================================================


class TestGenericOutputItemBuilderReturnTypes:
    """Generic OutputItemBuilder.emit_added/emit_done must return typed events."""

    def test_emit_added_returns_output_item_added_event(self) -> None:
        s = _stream()
        s.emit_created()
        builder = s.add_output_item_structured_outputs()
        item = StructuredOutputsOutputItem(id=builder.item_id, output="data")
        event = builder.emit_added(item)
        assert isinstance(event, ResponseOutputItemAddedEvent), (
            f"Expected ResponseOutputItemAddedEvent, got {type(event)}"
        )

    def test_emit_done_returns_output_item_done_event(self) -> None:
        s = _stream()
        s.emit_created()
        builder = s.add_output_item_structured_outputs()
        item = StructuredOutputsOutputItem(id=builder.item_id, output="data")
        builder.emit_added(item)
        event = builder.emit_done(item)
        assert isinstance(event, ResponseOutputItemDoneEvent), (
            f"Expected ResponseOutputItemDoneEvent, got {type(event)}"
        )


# =====================================================================
# OutputItemMessageBuilder
# =====================================================================


class TestMessageBuilderReturnTypes:
    """OutputItemMessageBuilder emit methods must return typed events."""

    def test_emit_added(self) -> None:
        s = _stream()
        s.emit_created()
        msg = s.add_output_item_message()
        event = msg.emit_added()
        assert isinstance(event, ResponseOutputItemAddedEvent)

    def test_emit_done(self) -> None:
        s = _stream()
        s.emit_created()
        msg = s.add_output_item_message()
        msg.emit_added()
        tc = msg.add_text_content()
        tc.emit_added()
        tc.emit_delta("x")
        tc.emit_text_done()
        tc.emit_done()
        event = msg.emit_done()
        assert isinstance(event, ResponseOutputItemDoneEvent)


# =====================================================================
# TextContentBuilder
# =====================================================================


class TestTextContentBuilderReturnTypes:
    """TextContentBuilder emit methods must return typed events."""

    def _setup(self):
        s = _stream()
        s.emit_created()
        msg = s.add_output_item_message()
        msg.emit_added()
        tc = msg.add_text_content()
        return s, msg, tc

    def test_emit_added(self) -> None:
        _, _, tc = self._setup()
        event = tc.emit_added()
        assert isinstance(event, ResponseContentPartAddedEvent), (
            f"Expected ResponseContentPartAddedEvent, got {type(event)}"
        )

    def test_emit_delta(self) -> None:
        _, _, tc = self._setup()
        tc.emit_added()
        event = tc.emit_delta("hello")
        assert isinstance(event, ResponseTextDeltaEvent), (
            f"Expected ResponseTextDeltaEvent, got {type(event)}"
        )

    def test_emit_text_done(self) -> None:
        _, _, tc = self._setup()
        tc.emit_added()
        tc.emit_delta("hello")
        event = tc.emit_text_done()
        assert isinstance(event, ResponseTextDoneEvent), (
            f"Expected ResponseTextDoneEvent, got {type(event)}"
        )

    def test_emit_done(self) -> None:
        _, _, tc = self._setup()
        tc.emit_added()
        tc.emit_delta("hello")
        tc.emit_text_done()
        event = tc.emit_done()
        assert isinstance(event, ResponseContentPartDoneEvent), (
            f"Expected ResponseContentPartDoneEvent, got {type(event)}"
        )

    def test_emit_annotation_added(self) -> None:
        _, _, tc = self._setup()
        tc.emit_added()
        tc.emit_delta("hello")
        tc.emit_text_done()
        annotation = UrlCitationBody(
            url="https://example.com",
            start_index=0,
            end_index=5,
            title="Example",
        )
        event = tc.emit_annotation_added(annotation)
        assert isinstance(event, ResponseOutputTextAnnotationAddedEvent), (
            f"Expected ResponseOutputTextAnnotationAddedEvent, got {type(event)}"
        )


# =====================================================================
# RefusalContentBuilder
# =====================================================================


class TestRefusalContentBuilderReturnTypes:
    """RefusalContentBuilder emit methods must return typed events."""

    def _setup(self):
        s = _stream()
        s.emit_created()
        msg = s.add_output_item_message()
        msg.emit_added()
        rc = msg.add_refusal_content()
        return s, msg, rc

    def test_emit_added(self) -> None:
        _, _, rc = self._setup()
        event = rc.emit_added()
        assert isinstance(event, ResponseContentPartAddedEvent)

    def test_emit_delta(self) -> None:
        _, _, rc = self._setup()
        rc.emit_added()
        event = rc.emit_delta("I cannot do that")
        assert isinstance(event, ResponseRefusalDeltaEvent), (
            f"Expected ResponseRefusalDeltaEvent, got {type(event)}"
        )

    def test_emit_refusal_done(self) -> None:
        _, _, rc = self._setup()
        rc.emit_added()
        rc.emit_delta("I cannot do that")
        event = rc.emit_refusal_done("I cannot do that")
        assert isinstance(event, ResponseRefusalDoneEvent), (
            f"Expected ResponseRefusalDoneEvent, got {type(event)}"
        )

    def test_emit_done(self) -> None:
        _, _, rc = self._setup()
        rc.emit_added()
        rc.emit_delta("I cannot do that")
        rc.emit_refusal_done("I cannot do that")
        event = rc.emit_done()
        assert isinstance(event, ResponseContentPartDoneEvent)


# =====================================================================
# OutputItemFunctionCallBuilder
# =====================================================================


class TestFunctionCallBuilderReturnTypes:
    """OutputItemFunctionCallBuilder emit methods must return typed events."""

    def test_emit_added(self) -> None:
        s = _stream()
        s.emit_created()
        fc = s.add_output_item_function_call("fn", "call_1")
        event = fc.emit_added()
        assert isinstance(event, ResponseOutputItemAddedEvent)

    def test_emit_arguments_delta(self) -> None:
        s = _stream()
        s.emit_created()
        fc = s.add_output_item_function_call("fn", "call_1")
        fc.emit_added()
        event = fc.emit_arguments_delta('{"k":')
        assert isinstance(event, ResponseFunctionCallArgumentsDeltaEvent), (
            f"Expected ResponseFunctionCallArgumentsDeltaEvent, got {type(event)}"
        )

    def test_emit_arguments_done(self) -> None:
        s = _stream()
        s.emit_created()
        fc = s.add_output_item_function_call("fn", "call_1")
        fc.emit_added()
        event = fc.emit_arguments_done('{"k":"v"}')
        assert isinstance(event, ResponseFunctionCallArgumentsDoneEvent), (
            f"Expected ResponseFunctionCallArgumentsDoneEvent, got {type(event)}"
        )

    def test_emit_done(self) -> None:
        s = _stream()
        s.emit_created()
        fc = s.add_output_item_function_call("fn", "call_1")
        fc.emit_added()
        fc.emit_arguments_done("{}")
        event = fc.emit_done()
        assert isinstance(event, ResponseOutputItemDoneEvent)


# =====================================================================
# OutputItemFunctionCallOutputBuilder
# =====================================================================


class TestFunctionCallOutputBuilderReturnTypes:
    """OutputItemFunctionCallOutputBuilder emit methods must return typed events."""

    def test_emit_added(self) -> None:
        s = _stream()
        s.emit_created()
        fco = s.add_output_item_function_call_output("call_1")
        event = fco.emit_added("result")
        assert isinstance(event, ResponseOutputItemAddedEvent)

    def test_emit_done(self) -> None:
        s = _stream()
        s.emit_created()
        fco = s.add_output_item_function_call_output("call_1")
        fco.emit_added("result")
        event = fco.emit_done("result")
        assert isinstance(event, ResponseOutputItemDoneEvent)


# =====================================================================
# OutputItemReasoningItemBuilder
# =====================================================================


class TestReasoningItemBuilderReturnTypes:
    """OutputItemReasoningItemBuilder emit methods must return typed events."""

    def test_emit_added(self) -> None:
        s = _stream()
        s.emit_created()
        r = s.add_output_item_reasoning_item()
        event = r.emit_added()
        assert isinstance(event, ResponseOutputItemAddedEvent)

    def test_emit_done(self) -> None:
        s = _stream()
        s.emit_created()
        r = s.add_output_item_reasoning_item()
        r.emit_added()
        sp = r.add_summary_part()
        sp.emit_added()
        sp.emit_text_done("thinking")
        sp.emit_done()
        event = r.emit_done()
        assert isinstance(event, ResponseOutputItemDoneEvent)


# =====================================================================
# ReasoningSummaryPartBuilder
# =====================================================================


class TestReasoningSummaryPartBuilderReturnTypes:
    """ReasoningSummaryPartBuilder emit methods must return typed events."""

    def _setup(self):
        s = _stream()
        s.emit_created()
        r = s.add_output_item_reasoning_item()
        r.emit_added()
        sp = r.add_summary_part()
        return s, r, sp

    def test_emit_added(self) -> None:
        _, _, sp = self._setup()
        event = sp.emit_added()
        assert isinstance(event, ResponseReasoningSummaryPartAddedEvent), (
            f"Expected ResponseReasoningSummaryPartAddedEvent, got {type(event)}"
        )

    def test_emit_text_delta(self) -> None:
        _, _, sp = self._setup()
        sp.emit_added()
        event = sp.emit_text_delta("thinking")
        assert isinstance(event, ResponseReasoningSummaryTextDeltaEvent), (
            f"Expected ResponseReasoningSummaryTextDeltaEvent, got {type(event)}"
        )

    def test_emit_text_done(self) -> None:
        _, _, sp = self._setup()
        sp.emit_added()
        event = sp.emit_text_done("thinking")
        assert isinstance(event, ResponseReasoningSummaryTextDoneEvent), (
            f"Expected ResponseReasoningSummaryTextDoneEvent, got {type(event)}"
        )

    def test_emit_done(self) -> None:
        _, _, sp = self._setup()
        sp.emit_added()
        sp.emit_text_done("thinking")
        event = sp.emit_done()
        assert isinstance(event, ResponseReasoningSummaryPartDoneEvent), (
            f"Expected ResponseReasoningSummaryPartDoneEvent, got {type(event)}"
        )


# =====================================================================
# OutputItemFileSearchCallBuilder
# =====================================================================


class TestFileSearchCallBuilderReturnTypes:
    """OutputItemFileSearchCallBuilder emit methods must return typed events."""

    def test_emit_added(self) -> None:
        s = _stream()
        s.emit_created()
        fs = s.add_output_item_file_search_call()
        event = fs.emit_added()
        assert isinstance(event, ResponseOutputItemAddedEvent)

    def test_emit_in_progress(self) -> None:
        s = _stream()
        s.emit_created()
        fs = s.add_output_item_file_search_call()
        fs.emit_added()
        event = fs.emit_in_progress()
        assert isinstance(event, ResponseFileSearchCallInProgressEvent), (
            f"Expected ResponseFileSearchCallInProgressEvent, got {type(event)}"
        )

    def test_emit_searching(self) -> None:
        s = _stream()
        s.emit_created()
        fs = s.add_output_item_file_search_call()
        fs.emit_added()
        fs.emit_in_progress()
        event = fs.emit_searching()
        assert isinstance(event, ResponseFileSearchCallSearchingEvent), (
            f"Expected ResponseFileSearchCallSearchingEvent, got {type(event)}"
        )

    def test_emit_completed(self) -> None:
        s = _stream()
        s.emit_created()
        fs = s.add_output_item_file_search_call()
        fs.emit_added()
        event = fs.emit_completed()
        assert isinstance(event, ResponseFileSearchCallCompletedEvent), (
            f"Expected ResponseFileSearchCallCompletedEvent, got {type(event)}"
        )

    def test_emit_done(self) -> None:
        s = _stream()
        s.emit_created()
        fs = s.add_output_item_file_search_call()
        fs.emit_added()
        event = fs.emit_done()
        assert isinstance(event, ResponseOutputItemDoneEvent)


# =====================================================================
# OutputItemWebSearchCallBuilder
# =====================================================================


class TestWebSearchCallBuilderReturnTypes:
    """OutputItemWebSearchCallBuilder emit methods must return typed events."""

    def test_emit_added(self) -> None:
        s = _stream()
        s.emit_created()
        ws = s.add_output_item_web_search_call()
        event = ws.emit_added()
        assert isinstance(event, ResponseOutputItemAddedEvent)

    def test_emit_in_progress(self) -> None:
        s = _stream()
        s.emit_created()
        ws = s.add_output_item_web_search_call()
        ws.emit_added()
        event = ws.emit_in_progress()
        assert isinstance(event, ResponseWebSearchCallInProgressEvent), (
            f"Expected ResponseWebSearchCallInProgressEvent, got {type(event)}"
        )

    def test_emit_searching(self) -> None:
        s = _stream()
        s.emit_created()
        ws = s.add_output_item_web_search_call()
        ws.emit_added()
        event = ws.emit_searching()
        assert isinstance(event, ResponseWebSearchCallSearchingEvent), (
            f"Expected ResponseWebSearchCallSearchingEvent, got {type(event)}"
        )

    def test_emit_completed(self) -> None:
        s = _stream()
        s.emit_created()
        ws = s.add_output_item_web_search_call()
        ws.emit_added()
        event = ws.emit_completed()
        assert isinstance(event, ResponseWebSearchCallCompletedEvent), (
            f"Expected ResponseWebSearchCallCompletedEvent, got {type(event)}"
        )

    def test_emit_done(self) -> None:
        s = _stream()
        s.emit_created()
        ws = s.add_output_item_web_search_call()
        ws.emit_added()
        event = ws.emit_done()
        assert isinstance(event, ResponseOutputItemDoneEvent)


# =====================================================================
# OutputItemCodeInterpreterCallBuilder
# =====================================================================


class TestCodeInterpreterCallBuilderReturnTypes:
    """OutputItemCodeInterpreterCallBuilder emit methods must return typed events."""

    def test_emit_added(self) -> None:
        s = _stream()
        s.emit_created()
        ci = s.add_output_item_code_interpreter_call()
        event = ci.emit_added()
        assert isinstance(event, ResponseOutputItemAddedEvent)

    def test_emit_in_progress(self) -> None:
        s = _stream()
        s.emit_created()
        ci = s.add_output_item_code_interpreter_call()
        ci.emit_added()
        event = ci.emit_in_progress()
        assert isinstance(event, ResponseCodeInterpreterCallInProgressEvent), (
            f"Expected ResponseCodeInterpreterCallInProgressEvent, got {type(event)}"
        )

    def test_emit_interpreting(self) -> None:
        s = _stream()
        s.emit_created()
        ci = s.add_output_item_code_interpreter_call()
        ci.emit_added()
        event = ci.emit_interpreting()
        assert isinstance(event, ResponseCodeInterpreterCallInterpretingEvent), (
            f"Expected ResponseCodeInterpreterCallInterpretingEvent, got {type(event)}"
        )

    def test_emit_code_delta(self) -> None:
        s = _stream()
        s.emit_created()
        ci = s.add_output_item_code_interpreter_call()
        ci.emit_added()
        event = ci.emit_code_delta("print('hello')")
        assert isinstance(event, ResponseCodeInterpreterCallCodeDeltaEvent), (
            f"Expected ResponseCodeInterpreterCallCodeDeltaEvent, got {type(event)}"
        )

    def test_emit_code_done(self) -> None:
        s = _stream()
        s.emit_created()
        ci = s.add_output_item_code_interpreter_call()
        ci.emit_added()
        event = ci.emit_code_done("print('hello')")
        assert isinstance(event, ResponseCodeInterpreterCallCodeDoneEvent), (
            f"Expected ResponseCodeInterpreterCallCodeDoneEvent, got {type(event)}"
        )

    def test_emit_completed(self) -> None:
        s = _stream()
        s.emit_created()
        ci = s.add_output_item_code_interpreter_call()
        ci.emit_added()
        event = ci.emit_completed()
        assert isinstance(event, ResponseCodeInterpreterCallCompletedEvent), (
            f"Expected ResponseCodeInterpreterCallCompletedEvent, got {type(event)}"
        )

    def test_emit_done(self) -> None:
        s = _stream()
        s.emit_created()
        ci = s.add_output_item_code_interpreter_call()
        ci.emit_added()
        event = ci.emit_done()
        assert isinstance(event, ResponseOutputItemDoneEvent)


# =====================================================================
# OutputItemImageGenCallBuilder
# =====================================================================


class TestImageGenCallBuilderReturnTypes:
    """OutputItemImageGenCallBuilder emit methods must return typed events."""

    def test_emit_added(self) -> None:
        s = _stream()
        s.emit_created()
        ig = s.add_output_item_image_gen_call()
        event = ig.emit_added()
        assert isinstance(event, ResponseOutputItemAddedEvent)

    def test_emit_in_progress(self) -> None:
        s = _stream()
        s.emit_created()
        ig = s.add_output_item_image_gen_call()
        ig.emit_added()
        event = ig.emit_in_progress()
        assert isinstance(event, ResponseImageGenCallInProgressEvent), (
            f"Expected ResponseImageGenCallInProgressEvent, got {type(event)}"
        )

    def test_emit_generating(self) -> None:
        s = _stream()
        s.emit_created()
        ig = s.add_output_item_image_gen_call()
        ig.emit_added()
        event = ig.emit_generating()
        assert isinstance(event, ResponseImageGenCallGeneratingEvent), (
            f"Expected ResponseImageGenCallGeneratingEvent, got {type(event)}"
        )

    def test_emit_partial_image(self) -> None:
        s = _stream()
        s.emit_created()
        ig = s.add_output_item_image_gen_call()
        ig.emit_added()
        event = ig.emit_partial_image("base64data")
        assert isinstance(event, ResponseImageGenCallPartialImageEvent), (
            f"Expected ResponseImageGenCallPartialImageEvent, got {type(event)}"
        )

    def test_emit_completed(self) -> None:
        s = _stream()
        s.emit_created()
        ig = s.add_output_item_image_gen_call()
        ig.emit_added()
        event = ig.emit_completed()
        assert isinstance(event, ResponseImageGenCallCompletedEvent), (
            f"Expected ResponseImageGenCallCompletedEvent, got {type(event)}"
        )

    def test_emit_done(self) -> None:
        s = _stream()
        s.emit_created()
        ig = s.add_output_item_image_gen_call()
        ig.emit_added()
        event = ig.emit_done("final_b64_image")
        assert isinstance(event, ResponseOutputItemDoneEvent)


# =====================================================================
# OutputItemMcpCallBuilder
# =====================================================================


class TestMcpCallBuilderReturnTypes:
    """OutputItemMcpCallBuilder emit methods must return typed events."""

    def test_emit_added(self) -> None:
        s = _stream()
        s.emit_created()
        mcp = s.add_output_item_mcp_call("server", "tool")
        event = mcp.emit_added()
        assert isinstance(event, ResponseOutputItemAddedEvent)

    def test_emit_in_progress(self) -> None:
        s = _stream()
        s.emit_created()
        mcp = s.add_output_item_mcp_call("server", "tool")
        mcp.emit_added()
        event = mcp.emit_in_progress()
        assert isinstance(event, ResponseMCPCallInProgressEvent), (
            f"Expected ResponseMCPCallInProgressEvent, got {type(event)}"
        )

    def test_emit_arguments_delta(self) -> None:
        s = _stream()
        s.emit_created()
        mcp = s.add_output_item_mcp_call("server", "tool")
        mcp.emit_added()
        event = mcp.emit_arguments_delta('{"key":')
        assert isinstance(event, ResponseMCPCallArgumentsDeltaEvent), (
            f"Expected ResponseMCPCallArgumentsDeltaEvent, got {type(event)}"
        )

    def test_emit_arguments_done(self) -> None:
        s = _stream()
        s.emit_created()
        mcp = s.add_output_item_mcp_call("server", "tool")
        mcp.emit_added()
        event = mcp.emit_arguments_done('{"key":"val"}')
        assert isinstance(event, ResponseMCPCallArgumentsDoneEvent), (
            f"Expected ResponseMCPCallArgumentsDoneEvent, got {type(event)}"
        )

    def test_emit_completed(self) -> None:
        s = _stream()
        s.emit_created()
        mcp = s.add_output_item_mcp_call("server", "tool")
        mcp.emit_added()
        event = mcp.emit_completed()
        assert isinstance(event, ResponseMCPCallCompletedEvent), (
            f"Expected ResponseMCPCallCompletedEvent, got {type(event)}"
        )

    def test_emit_failed(self) -> None:
        s = _stream()
        s.emit_created()
        mcp = s.add_output_item_mcp_call("server", "tool")
        mcp.emit_added()
        event = mcp.emit_failed()
        assert isinstance(event, ResponseMCPCallFailedEvent), (
            f"Expected ResponseMCPCallFailedEvent, got {type(event)}"
        )

    def test_emit_done(self) -> None:
        s = _stream()
        s.emit_created()
        mcp = s.add_output_item_mcp_call("server", "tool")
        mcp.emit_added()
        mcp.emit_completed()
        event = mcp.emit_done()
        assert isinstance(event, ResponseOutputItemDoneEvent)


# =====================================================================
# OutputItemMcpListToolsBuilder
# =====================================================================


class TestMcpListToolsBuilderReturnTypes:
    """OutputItemMcpListToolsBuilder emit methods must return typed events."""

    def test_emit_added(self) -> None:
        s = _stream()
        s.emit_created()
        mlt = s.add_output_item_mcp_list_tools("server")
        event = mlt.emit_added()
        assert isinstance(event, ResponseOutputItemAddedEvent)

    def test_emit_in_progress(self) -> None:
        s = _stream()
        s.emit_created()
        mlt = s.add_output_item_mcp_list_tools("server")
        mlt.emit_added()
        event = mlt.emit_in_progress()
        assert isinstance(event, ResponseMCPListToolsInProgressEvent), (
            f"Expected ResponseMCPListToolsInProgressEvent, got {type(event)}"
        )

    def test_emit_completed(self) -> None:
        s = _stream()
        s.emit_created()
        mlt = s.add_output_item_mcp_list_tools("server")
        mlt.emit_added()
        event = mlt.emit_completed()
        assert isinstance(event, ResponseMCPListToolsCompletedEvent), (
            f"Expected ResponseMCPListToolsCompletedEvent, got {type(event)}"
        )

    def test_emit_failed(self) -> None:
        s = _stream()
        s.emit_created()
        mlt = s.add_output_item_mcp_list_tools("server")
        mlt.emit_added()
        event = mlt.emit_failed()
        assert isinstance(event, ResponseMCPListToolsFailedEvent), (
            f"Expected ResponseMCPListToolsFailedEvent, got {type(event)}"
        )

    def test_emit_done(self) -> None:
        s = _stream()
        s.emit_created()
        mlt = s.add_output_item_mcp_list_tools("server")
        mlt.emit_added()
        event = mlt.emit_done()
        assert isinstance(event, ResponseOutputItemDoneEvent)


# =====================================================================
# OutputItemCustomToolCallBuilder
# =====================================================================


class TestCustomToolCallBuilderReturnTypes:
    """OutputItemCustomToolCallBuilder emit methods must return typed events."""

    def test_emit_added(self) -> None:
        s = _stream()
        s.emit_created()
        ct = s.add_output_item_custom_tool_call("call_1", "my_tool")
        event = ct.emit_added()
        assert isinstance(event, ResponseOutputItemAddedEvent)

    def test_emit_input_delta(self) -> None:
        s = _stream()
        s.emit_created()
        ct = s.add_output_item_custom_tool_call("call_1", "my_tool")
        ct.emit_added()
        event = ct.emit_input_delta('{"key":')
        assert isinstance(event, ResponseCustomToolCallInputDeltaEvent), (
            f"Expected ResponseCustomToolCallInputDeltaEvent, got {type(event)}"
        )

    def test_emit_input_done(self) -> None:
        s = _stream()
        s.emit_created()
        ct = s.add_output_item_custom_tool_call("call_1", "my_tool")
        ct.emit_added()
        event = ct.emit_input_done('{"key":"val"}')
        assert isinstance(event, ResponseCustomToolCallInputDoneEvent), (
            f"Expected ResponseCustomToolCallInputDoneEvent, got {type(event)}"
        )

    def test_emit_done(self) -> None:
        s = _stream()
        s.emit_created()
        ct = s.add_output_item_custom_tool_call("call_1", "my_tool")
        ct.emit_added()
        ct.emit_input_done("{}")
        event = ct.emit_done()
        assert isinstance(event, ResponseOutputItemDoneEvent)
