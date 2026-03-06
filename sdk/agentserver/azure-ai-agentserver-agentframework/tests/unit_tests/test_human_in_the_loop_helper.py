import pytest

from agent_framework import (
    ChatMessage,
    FunctionCallContent,
    FunctionResultContent,
    Role as ChatRole,
    TextContent,
)

from azure.ai.agentserver.agentframework.models.human_in_the_loop_helper import (
    HumanInTheLoopHelper,
)
from azure.ai.agentserver.core.server.common.constants import (
    HUMAN_IN_THE_LOOP_FUNCTION_NAME,
)


@pytest.fixture()
def helper() -> HumanInTheLoopHelper:
    return HumanInTheLoopHelper()


@pytest.mark.unit
def test_remove_hitl_messages_keeps_latest_function_result(helper: HumanInTheLoopHelper) -> None:
    hitl_call = FunctionCallContent(
        call_id="hitl-1",
        name=HUMAN_IN_THE_LOOP_FUNCTION_NAME,
        arguments="{}",
    )
    real_call = FunctionCallContent(call_id="tool-1", name="calculator", arguments="{}")
    feedback_result = FunctionResultContent(call_id="tool-1", result="intermediate")
    final_result = FunctionResultContent(call_id="tool-1", result={"total": 42})
    follow_up_content = TextContent("work resumed")

    thread_messages = [
        ChatMessage(role="assistant", contents=[real_call, hitl_call]),
        ChatMessage(role="tool", contents=[feedback_result]),
        ChatMessage(role="tool", contents=[final_result]),
        ChatMessage(role="assistant", contents=[follow_up_content]),
    ]

    filtered = helper.remove_hitl_content_from_thread(thread_messages)

    assert len(filtered) == 3
    assert filtered[0].role == ChatRole.ASSISTANT
    assert len(filtered[0].contents) == 1
    assert filtered[0].contents[0] is real_call
    assert filtered[1].role == ChatRole.TOOL
    assert len(filtered[1].contents) == 1
    assert filtered[1].contents[0] is final_result
    assert len(filtered[2].contents) == 1
    assert filtered[2].contents[0] is follow_up_content


@pytest.mark.unit
def test_remove_hitl_messages_keeps_the_function_result(helper: HumanInTheLoopHelper) -> None:
    hitl_call = FunctionCallContent(
        call_id="hitl-1",
        name=HUMAN_IN_THE_LOOP_FUNCTION_NAME,
        arguments="{}",
    )
    real_call = FunctionCallContent(call_id="tool-1", name="calculator", arguments="{}")
    final_result = FunctionResultContent(call_id="tool-1", result={"total": 42})
    follow_up_content = TextContent("work resumed")

    thread_messages = [
        ChatMessage(role="assistant", contents=[real_call, hitl_call]),
        ChatMessage(role="tool", contents=[final_result]),
        ChatMessage(role="assistant", contents=[follow_up_content]),
    ]

    filtered = helper.remove_hitl_content_from_thread(thread_messages)

    assert len(filtered) == 3
    assert filtered[0].role == ChatRole.ASSISTANT
    assert len(filtered[0].contents) == 1
    assert filtered[0].contents[0] is real_call
    assert filtered[1].role == ChatRole.TOOL
    assert len(filtered[1].contents) == 1
    assert filtered[1].contents[0] is final_result
    assert len(filtered[2].contents) == 1
    assert filtered[2].contents[0] is follow_up_content

@pytest.mark.unit
def test_remove_hitl_messages_skips_orphaned_hitl_results(helper: HumanInTheLoopHelper) -> None:
    hitl_call = FunctionCallContent(
        call_id="hitl-2",
        name=HUMAN_IN_THE_LOOP_FUNCTION_NAME,
        arguments="{}",
    )
    orphan_result = FunctionResultContent(call_id="hitl-2", result="ignored")
    user_update = TextContent("ready")

    thread_messages = [
        ChatMessage(role="assistant", contents=[hitl_call]),
        ChatMessage(role="tool", contents=[orphan_result]),
        ChatMessage(role="user", contents=[user_update]),
    ]

    filtered = helper.remove_hitl_content_from_thread(thread_messages)

    assert len(filtered) == 1
    assert len(filtered[0].contents) == 1
    assert filtered[0].contents[0] is user_update


@pytest.mark.unit
def test_remove_hitl_messages_preserves_regular_tool_cycle(helper: HumanInTheLoopHelper) -> None:
    real_call = FunctionCallContent(call_id="tool-3", name="lookup", arguments="{}")
    result_content = FunctionResultContent(call_id="tool-3", result="done")

    thread_messages = [
        ChatMessage(role="assistant", contents=[real_call]),
        ChatMessage(role="tool", contents=[result_content]),
    ]

    filtered = helper.remove_hitl_content_from_thread(thread_messages)

    assert len(filtered) == 2
    assert len(filtered[0].contents) == 1
    assert filtered[0].role == ChatRole.ASSISTANT
    assert filtered[0].contents[0] is real_call
    assert filtered[1].role == ChatRole.TOOL
    assert len(filtered[1].contents) == 1
    assert filtered[1].contents[0] is result_content