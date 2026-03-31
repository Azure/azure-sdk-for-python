from unittest.mock import MagicMock

import pytest
from agent_framework import Content, Message, WorkflowEvent
from azure.ai.agentserver.core.server.common.constants import (
    HUMAN_IN_THE_LOOP_FUNCTION_NAME,
)

from azure.ai.agentserver.agentframework.models.human_in_the_loop_helper import (
    HumanInTheLoopHelper,
    PendingHitlRequest,
)


@pytest.fixture()
def helper() -> HumanInTheLoopHelper:
    return HumanInTheLoopHelper()


def _function_call(call_id: str, name: str, arguments: str):
    return Content.from_function_call(call_id=call_id, name=name, arguments=arguments)


def _function_result(call_id: str, result):
    return Content.from_function_result(call_id=call_id, result=result)


@pytest.mark.unit
def test_remove_hitl_messages_keeps_latest_function_result(helper: HumanInTheLoopHelper) -> None:
    hitl_call = _function_call("hitl-1", HUMAN_IN_THE_LOOP_FUNCTION_NAME, "{}")
    real_call = _function_call("tool-1", "calculator", "{}")
    feedback_result = _function_result("tool-1", "intermediate")
    final_result = _function_result("tool-1", {"total": 42})
    follow_up_content = Content.from_text("work resumed")

    session_messages = [
        Message(role="assistant", contents=[real_call, hitl_call]),
        Message(role="tool", contents=[feedback_result]),
        Message(role="tool", contents=[final_result]),
        Message(role="assistant", contents=[follow_up_content]),
    ]

    filtered = helper.remove_hitl_content_from_session(session_messages)

    assert len(filtered) == 3
    assert filtered[0].role == "assistant"
    assert len(filtered[0].contents) == 1
    assert filtered[0].contents[0] is real_call
    assert filtered[1].role == "tool"
    assert len(filtered[1].contents) == 1
    assert filtered[1].contents[0] is final_result
    assert len(filtered[2].contents) == 1
    assert filtered[2].contents[0] is follow_up_content


@pytest.mark.unit
def test_remove_hitl_messages_keeps_the_function_result(helper: HumanInTheLoopHelper) -> None:
    hitl_call = _function_call("hitl-1", HUMAN_IN_THE_LOOP_FUNCTION_NAME, "{}")
    real_call = _function_call("tool-1", "calculator", "{}")
    final_result = _function_result("tool-1", {"total": 42})
    follow_up_content = Content.from_text("work resumed")

    session_messages = [
        Message(role="assistant", contents=[real_call, hitl_call]),
        Message(role="tool", contents=[final_result]),
        Message(role="assistant", contents=[follow_up_content]),
    ]

    filtered = helper.remove_hitl_content_from_session(session_messages)

    assert len(filtered) == 3
    assert filtered[0].role == "assistant"
    assert len(filtered[0].contents) == 1
    assert filtered[0].contents[0] is real_call
    assert filtered[1].role == "tool"
    assert len(filtered[1].contents) == 1
    assert filtered[1].contents[0] is final_result
    assert len(filtered[2].contents) == 1
    assert filtered[2].contents[0] is follow_up_content


@pytest.mark.unit
def test_remove_hitl_messages_skips_orphaned_hitl_results(helper: HumanInTheLoopHelper) -> None:
    hitl_call = _function_call("hitl-2", HUMAN_IN_THE_LOOP_FUNCTION_NAME, "{}")
    orphan_result = _function_result("hitl-2", "ignored")
    user_update = Content.from_text("ready")

    session_messages = [
        Message(role="assistant", contents=[hitl_call]),
        Message(role="tool", contents=[orphan_result]),
        Message(role="user", contents=[user_update]),
    ]

    filtered = helper.remove_hitl_content_from_session(session_messages)

    assert len(filtered) == 1
    assert len(filtered[0].contents) == 1
    assert filtered[0].contents[0] is user_update


@pytest.mark.unit
def test_remove_hitl_messages_preserves_regular_tool_cycle(helper: HumanInTheLoopHelper) -> None:
    real_call = _function_call("tool-3", "lookup", "{}")
    result_content = _function_result("tool-3", "done")

    session_messages = [
        Message(role="assistant", contents=[real_call]),
        Message(role="tool", contents=[result_content]),
    ]

    filtered = helper.remove_hitl_content_from_session(session_messages)

    assert len(filtered) == 2
    assert len(filtered[0].contents) == 1
    assert filtered[0].role == "assistant"
    assert filtered[0].contents[0] is real_call
    assert filtered[1].role == "tool"
    assert len(filtered[1].contents) == 1
    assert filtered[1].contents[0] is result_content


# ---------------------------------------------------------------------------
# _to_pending_hitl_request — checkpoint path
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_checkpoint_rc3_workflow_event(helper: HumanInTheLoopHelper) -> None:
    """Real rc3 WorkflowEvent with top-level request_id/response_type."""
    event = WorkflowEvent("request_info", data="payload", request_id="req-1", response_type=str)

    checkpoint = MagicMock()
    checkpoint.pending_request_info_events = {"req-1": event}

    result = helper.get_pending_hitl_request(checkpoint=checkpoint)

    assert "req-1" in result
    pending = result["req-1"]
    assert isinstance(pending, PendingHitlRequest)
    assert pending.request_id == "req-1"
    assert pending.response_type is str


@pytest.mark.unit
def test_checkpoint_dict_fallback(helper: HumanInTheLoopHelper) -> None:
    """Dict entry in pending_events (legacy/serialized checkpoint)."""
    entry = {"request_id": "req-2", "response_type": None, "type": "request_info"}
    checkpoint = MagicMock()
    checkpoint.pending_request_info_events = {"req-2": entry}

    result = helper.get_pending_hitl_request(checkpoint=checkpoint)

    assert "req-2" in result
    pending = result["req-2"]
    assert isinstance(pending, PendingHitlRequest)
    assert pending.request_id == "req-2"
    assert pending.response_type is None


@pytest.mark.unit
def test_checkpoint_dict_uses_call_id_when_request_id_missing(helper: HumanInTheLoopHelper) -> None:
    """Dict without request_id falls back to the dict key (call_id)."""
    entry = {"type": "request_info"}
    checkpoint = MagicMock()
    checkpoint.pending_request_info_events = {"key-99": entry}

    result = helper.get_pending_hitl_request(checkpoint=checkpoint)

    assert result["key-99"].request_id == "key-99"


@pytest.mark.unit
def test_checkpoint_unrecognised_entry_skipped(helper: HumanInTheLoopHelper) -> None:
    """Non-dict, non-WorkflowEvent entries are silently skipped."""
    checkpoint = MagicMock()
    checkpoint.pending_request_info_events = {"bad": 12345}

    result = helper.get_pending_hitl_request(checkpoint=checkpoint)

    assert result == {}


# ---------------------------------------------------------------------------
# get_pending_hitl_request — session-messages path
# ---------------------------------------------------------------------------


def _user_input_request_content(call_id: str):
    """Create a Content-like mock that triggers the session-messages HITL path."""
    fc = MagicMock()
    fc.call_id = call_id
    content = MagicMock()
    content.type = "function_approval_request"
    content.user_input_request = True
    content.function_call = fc
    return content


def _message_with_contents(role: str, contents):
    """Create a Message-like mock with the given contents list."""
    msg = MagicMock()
    msg.role = role
    msg.contents = contents
    return msg


@pytest.mark.unit
def test_session_messages_approval_request(helper: HumanInTheLoopHelper) -> None:
    """Session messages with function_approval_request produce PendingHitlRequest."""
    content = _user_input_request_content("call-1")
    messages = [_message_with_contents("assistant", [content])]
    result = helper.get_pending_hitl_request(session_messages=messages)

    assert "call-1" in result
    pending = result["call-1"]
    assert isinstance(pending, PendingHitlRequest)
    assert pending.request_id == "call-1"
    assert pending.response_type is None


@pytest.mark.unit
def test_session_messages_fulfilled_request_removed(helper: HumanInTheLoopHelper) -> None:
    """A function_result for a pending request removes it from the result."""
    req_content = _user_input_request_content("call-2")
    res_content = MagicMock()
    res_content.type = "function_result"
    res_content.call_id = "call-2"
    res_content.user_input_request = None

    messages = [
        _message_with_contents("assistant", [req_content]),
        _message_with_contents("tool", [res_content]),
    ]
    result = helper.get_pending_hitl_request(session_messages=messages)

    assert result == {}


# ---------------------------------------------------------------------------
# convert_response
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_convert_response_without_response_type(helper: HumanInTheLoopHelper) -> None:
    """PendingHitlRequest with response_type=None passes raw string through."""
    pending = PendingHitlRequest(request_id="req-10", response_type=None)
    input_item = {"type": "function_call_output", "call_id": "req-10", "output": "looks good"}

    msg = helper.convert_response(pending, input_item)

    assert msg.role == "tool"
    assert len(msg.contents) == 1
    assert msg.contents[0].call_id == "req-10"
    assert msg.contents[0].result == "looks good"


@pytest.mark.unit
def test_convert_response_with_response_type(helper: HumanInTheLoopHelper) -> None:
    """PendingHitlRequest with a response_type that has convert_from_payload() deserializes."""

    class FeedbackResponse:
        @staticmethod
        def convert_from_payload(payload: str) -> "FeedbackResponse":
            resp = FeedbackResponse()
            resp.feedback = payload.upper()
            return resp

    pending = PendingHitlRequest(request_id="req-11", response_type=FeedbackResponse)
    input_item = {"type": "function_call_output", "call_id": "req-11", "output": "make it shorter"}

    msg = helper.convert_response(pending, input_item)

    assert msg.contents[0].call_id == "req-11"
    result = msg.contents[0].result
    assert isinstance(result, FeedbackResponse)
    assert result.feedback == "MAKE IT SHORTER"


# ---------------------------------------------------------------------------
# End-to-end: validate_and_convert_hitl_response
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_end_to_end_hitl_round_trip(helper: HumanInTheLoopHelper) -> None:
    """Pending request + function_call_output → Message with correct call_id."""
    pending = {"req-20": PendingHitlRequest(request_id="req-20", response_type=None)}
    input_items = [{"type": "function_call_output", "call_id": "req-20", "output": "approved"}]

    result = helper.validate_and_convert_hitl_response(input_items, pending_requests=pending)

    assert result is not None
    assert len(result) == 1
    msg = result[0]
    assert msg.role == "tool"
    assert msg.contents[0].call_id == "req-20"
    assert msg.contents[0].result == "approved"


@pytest.mark.unit
def test_validate_hitl_response_rejects_string_input(helper: HumanInTheLoopHelper) -> None:
    pending = {"req-30": PendingHitlRequest(request_id="req-30")}
    result = helper.validate_and_convert_hitl_response("plain text", pending_requests=pending)
    assert result is None


@pytest.mark.unit
def test_validate_hitl_response_rejects_wrong_type(helper: HumanInTheLoopHelper) -> None:
    pending = {"req-31": PendingHitlRequest(request_id="req-31")}
    result = helper.validate_and_convert_hitl_response(
        [{"type": "text", "call_id": "req-31"}], pending_requests=pending
    )
    assert result is None


@pytest.mark.unit
def test_validate_hitl_response_skips_unmatched_call_id(helper: HumanInTheLoopHelper) -> None:
    pending = {"req-40": PendingHitlRequest(request_id="req-40")}
    result = helper.validate_and_convert_hitl_response(
        [{"type": "function_call_output", "call_id": "unknown", "output": "x"}],
        pending_requests=pending,
    )
    assert result is not None
    assert len(result) == 0
