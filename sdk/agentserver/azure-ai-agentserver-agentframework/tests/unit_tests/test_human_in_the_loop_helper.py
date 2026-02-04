import json
from types import SimpleNamespace

import pytest
from agent_framework import (
	ChatMessage,
	FunctionApprovalResponseContent,
	FunctionResultContent,
	RequestInfoEvent,
	Role as ChatRole,
)
from agent_framework._types import FunctionCallContent, UserInputRequestContents

from azure.ai.agentserver.agentframework.models.human_in_the_loop_helper import HumanInTheLoopHelper
from azure.ai.agentserver.core.server.common.constants import HUMAN_IN_THE_LOOP_FUNCTION_NAME


@pytest.fixture()
def helper() -> HumanInTheLoopHelper:
	return HumanInTheLoopHelper()


def _make_user_input_request(call_id: str = "call-1", arguments: str | dict = "{}") -> UserInputRequestContents:
	function_call = FunctionCallContent(call_id=call_id, name="needs_input", arguments=arguments)
	return UserInputRequestContents(id=f"req-{call_id}", function_call=function_call)


@pytest.mark.unit
def test_get_pending_hitl_request_uses_checkpoint_map(helper: HumanInTheLoopHelper) -> None:
	request_event = RequestInfoEvent(
		request_id="call-42",
		source_executor_id="workflow",
		request_data={"payload": True},
		response_type=dict,
	)
	checkpoint = SimpleNamespace(pending_request_info_events={"call-42": request_event.to_dict()})

	pending = helper.get_pending_hitl_request(checkpoint=checkpoint)

	assert list(pending.keys()) == ["call-42"]
	assert isinstance(pending["call-42"], RequestInfoEvent)
	assert pending["call-42"].data == {"payload": True}


@pytest.mark.unit
def test_get_pending_hitl_request_collects_thread_messages(helper: HumanInTheLoopHelper) -> None:
	request_content = _make_user_input_request(call_id="call-thread")
	message = ChatMessage(role="assistant", contents=[request_content])

	pending = helper.get_pending_hitl_request(thread_messages=[message])

	assert "call-thread" in pending
	event = pending["call-thread"]
	assert event.source_executor_id == "agent"
	assert event.data == request_content.function_call


@pytest.mark.unit
def test_get_pending_hitl_request_removes_after_function_result(helper: HumanInTheLoopHelper) -> None:
	request_content = _make_user_input_request(call_id="call-result")
	messages = [
		ChatMessage(role="assistant", contents=[request_content]),
		ChatMessage(role="tool", contents=[FunctionResultContent(call_id="call-result", result="done")]),
	]

	pending = helper.get_pending_hitl_request(thread_messages=messages)

	assert pending == {}


@pytest.mark.unit
def test_get_pending_hitl_request_removes_after_approval(helper: HumanInTheLoopHelper) -> None:
	request_content = _make_user_input_request(call_id="call-approval")
	function_call = request_content.function_call
	messages = [
		ChatMessage(role="assistant", contents=[request_content]),
		ChatMessage(
			role="assistant",
			contents=[
				FunctionApprovalResponseContent(
					approved=True,
					id="approval-1",
					function_call=FunctionCallContent(
						call_id=function_call.call_id,
						name=function_call.name,
						arguments=function_call.arguments,
					),
				)
			],
		),
	]

	pending = helper.get_pending_hitl_request(thread_messages=messages)

	assert pending == {}


@pytest.mark.unit
def test_convert_user_input_request_content_builds_payload(helper: HumanInTheLoopHelper) -> None:
	request_content = _make_user_input_request(call_id="call-007", arguments={"foo": "bar"})

	result = helper.convert_user_input_request_content(request_content)

	assert result["call_id"] == "call-007"
	assert result["name"] == HUMAN_IN_THE_LOOP_FUNCTION_NAME
	assert json.loads(result["arguments"]) == {"foo": "bar"}


@pytest.mark.unit
def test_convert_request_arguments_prefers_convert_to_payload(helper: HumanInTheLoopHelper) -> None:
	class PayloadCarrier:
		def convert_to_payload(self) -> str:
			return "encoded"

	arguments = {"data": PayloadCarrier()}

	assert helper.convert_request_arguments(arguments) == "encoded"


@pytest.mark.unit
def test_convert_request_arguments_uses_to_dict(helper: HumanInTheLoopHelper) -> None:
	class Serializable:
		def to_dict(self) -> dict:
			return {"value": 1}

	converted = helper.convert_request_arguments(Serializable())

	assert json.loads(converted) == {"value": 1}


@pytest.mark.unit
def test_validate_and_convert_hitl_response_rejects_non_list(helper: HumanInTheLoopHelper) -> None:
	assert helper.validate_and_convert_hitl_response(None, {}) is None
	assert helper.validate_and_convert_hitl_response("string", {}) is None


@pytest.mark.unit
def test_validate_and_convert_hitl_response_requires_function_call_output(helper: HumanInTheLoopHelper) -> None:
	payload = [{"type": "message"}]

	assert helper.validate_and_convert_hitl_response(payload, {}) is None


@pytest.mark.unit
def test_validate_and_convert_hitl_response_returns_messages(helper: HumanInTheLoopHelper) -> None:
	pending_requests = {
		"call-123": RequestInfoEvent(
			request_id="call-123",
			source_executor_id="agent",
			request_data={},
			response_type=None,
		)
	}
	payload = [
		{
			"type": "function_call_output",
			"call_id": "call-123",
			"output": {"status": "ok"},
		}
	]

	messages = helper.validate_and_convert_hitl_response(payload, pending_requests)

	assert messages is not None
	assert len(messages) == 1
	assert messages[0].role == ChatRole.TOOL
	content = messages[0].contents[0]
	assert isinstance(content, FunctionResultContent)
	assert content.call_id == "call-123"
	assert content.result == {"status": "ok"}


@pytest.mark.unit
def test_convert_response_uses_response_type_converter(helper: HumanInTheLoopHelper) -> None:
	class PayloadResponse:
		@staticmethod
		def convert_from_payload(payload):
			return {"decoded": payload}

	request = RequestInfoEvent(
		request_id="call-900",
		source_executor_id="agent",
		request_data={},
		response_type=PayloadResponse,
	)

	message = helper.convert_response(request, {"output": "raw"})

	assert message.role == ChatRole.TOOL
	content = message.contents[0]
	assert isinstance(content, FunctionResultContent)
	assert content.result == {"decoded": "raw"}
