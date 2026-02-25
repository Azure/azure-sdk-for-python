import pytest
from agent_framework import Content, Message
from azure.ai.agentserver.core.server.common.constants import (
    HUMAN_IN_THE_LOOP_FUNCTION_NAME,
)

from azure.ai.agentserver.agentframework.models.human_in_the_loop_helper import (
    HumanInTheLoopHelper,
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
