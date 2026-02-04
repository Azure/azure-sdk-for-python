from types import SimpleNamespace

import pytest
from langgraph.types import Command, Interrupt, StateSnapshot

from azure.ai.agentserver.core import AgentRunContext
from azure.ai.agentserver.core.models import projects as project_models
from azure.ai.agentserver.langgraph._context import LanggraphRunContext
from azure.ai.agentserver.langgraph.models.human_in_the_loop_helper import HumanInTheLoopHelper


class _TestHumanInTheLoopHelper(HumanInTheLoopHelper):
    def __init__(self, context: LanggraphRunContext):
        super().__init__(context)
        self.command_to_return = Command()
        self.convert_calls: list = []

    def convert_interrupt(self, interrupt_info):
        return None

    def convert_input_item_to_command(self, input_item):
        self.convert_calls.append(input_item)
        return self.command_to_return


def _state_with_interrupts(interrupts: tuple) -> StateSnapshot:
    return StateSnapshot(
        values={},
        next=(),
        config={"configurable": {}},
        metadata=None,
        created_at=None,
        parent_config=None,
        tasks=(),
        interrupts=interrupts,
    )


@pytest.fixture
def helper() -> _TestHumanInTheLoopHelper:
    agent_run = AgentRunContext(payload={
        "conversation": {"id": "conv_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"},
    })
    context = LanggraphRunContext(agent_run=agent_run, tools=None)
    return _TestHumanInTheLoopHelper(context)


@pytest.mark.unit
def test_validate_and_convert_human_feedback_without_interrupt(helper: _TestHumanInTheLoopHelper):
    state = _state_with_interrupts(())

    result = helper.validate_and_convert_human_feedback(state, [])

    assert result is None
    assert helper.convert_calls == []


@pytest.mark.unit
def test_validate_and_convert_human_feedback_invalid_interrupt(helper: _TestHumanInTheLoopHelper):
    state = _state_with_interrupts(("not-an-interrupt",))

    result = helper.validate_and_convert_human_feedback(state, [])

    assert result is None
    assert helper.convert_calls == []


@pytest.mark.unit
def test_validate_and_convert_human_feedback_invalid_input_type(helper: _TestHumanInTheLoopHelper):
    interrupt = Interrupt(value={}, id="interrupt-123")
    state = _state_with_interrupts((interrupt,))

    result = helper.validate_and_convert_human_feedback(state, "raw string")

    assert result is None
    assert helper.convert_calls == []


@pytest.mark.unit
def test_validate_and_convert_human_feedback_call_id_mismatch(helper: _TestHumanInTheLoopHelper):
    interrupt = Interrupt(value={}, id="interrupt-123")
    state = _state_with_interrupts((interrupt,))
    input_item = {
        "type": project_models.ItemType.FUNCTION_CALL_OUTPUT,
        "call_id": "another-id",
        "output": "{}",
    }

    result = helper.validate_and_convert_human_feedback(state, [input_item])

    assert result is None
    assert helper.convert_calls == []


@pytest.mark.unit
def test_validate_and_convert_human_feedback_successfully_converts(helper: _TestHumanInTheLoopHelper):
    interrupt = Interrupt(value={"needs": "review"}, id="interrupt-123")
    state = _state_with_interrupts((interrupt,))
    input_item = {
        "type": project_models.ItemType.FUNCTION_CALL_OUTPUT,
        "call_id": "interrupt-123",
        "output": "{}",
    }
    expected_command = Command(resume={"next": True})
    helper.command_to_return = expected_command

    result = helper.validate_and_convert_human_feedback(state, [input_item])

    assert result is expected_command
    assert helper.convert_calls == [input_item]
