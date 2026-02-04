import json
from types import SimpleNamespace

import pytest
from langgraph.types import Command, Interrupt

from azure.ai.agentserver.core import AgentRunContext
from azure.ai.agentserver.core.models import projects as project_models
from azure.ai.agentserver.core.server.common.constants import HUMAN_IN_THE_LOOP_FUNCTION_NAME
from azure.ai.agentserver.langgraph._context import LanggraphRunContext
from azure.ai.agentserver.langgraph.models.human_in_the_loop_json_helper import (
    HumanInTheLoopJsonHelper,
)


class _DummyIdGenerator:
    def __init__(self):
        self._counter = 0

    def generate_function_call_id(self) -> str:
        self._counter += 1
        return f"hitl-call-{self._counter}"


@pytest.fixture
def helper() -> HumanInTheLoopJsonHelper:
    agent_run = AgentRunContext(payload={
        "conversation": {"id": "conv_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"},
    })
    context = LanggraphRunContext(agent_run=agent_run, tools=None)
    return HumanInTheLoopJsonHelper(context)


@pytest.mark.unit
def test_convert_interrupt_returns_function_call_item(helper: HumanInTheLoopJsonHelper):
    interrupt = Interrupt(value={"resume": "next"}, id="interrupt-1")

    result = helper.convert_interrupt(interrupt)

    assert isinstance(result, project_models.FunctionToolCallItemResource)
    assert result.call_id == "interrupt-1"
    assert result.name == HUMAN_IN_THE_LOOP_FUNCTION_NAME
    assert json.loads(result.arguments) == {"resume": "next"}
    assert result.status == "in_progress"


@pytest.mark.unit
def test_convert_interrupt_non_interrupt_returns_none(helper: HumanInTheLoopJsonHelper):
    assert helper.convert_interrupt(42) is None


@pytest.mark.unit
def test_convert_input_item_to_command_valid_payload(helper: HumanInTheLoopJsonHelper):
    payload = {
        "output": json.dumps({"resume": "workflow", "update": {"foo": "bar"}, "goto": "node-a"})
    }

    command = helper.convert_input_item_to_command(payload)

    assert isinstance(command, Command)
    assert command.resume == "workflow"
    assert command.update == {"foo": "bar"}
    assert command.goto == "node-a"


@pytest.mark.unit
def test_convert_input_item_to_command_invalid_json(helper: HumanInTheLoopJsonHelper):
    payload = {"output": "{\"resume\": \"workflow\""}

    assert helper.convert_input_item_to_command(payload) is None


@pytest.mark.unit
def test_convert_input_item_to_command_missing_fields(helper: HumanInTheLoopJsonHelper):
    payload = {"output": json.dumps({"irrelevant": True})}

    assert helper.convert_input_item_to_command(payload) is None


@pytest.mark.unit
def test_convert_input_item_to_command_non_string_output(helper: HumanInTheLoopJsonHelper):
    payload = {"output": ["not", "a", "string"]}

    assert helper.convert_input_item_to_command(payload) is None
