# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
from typing import Any, Dict, List, Optional, Union

from agent_framework import Content, Message, WorkflowCheckpoint, WorkflowEvent

from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.server.common.constants import HUMAN_IN_THE_LOOP_FUNCTION_NAME

logger = get_logger()


class HumanInTheLoopHelper:
    def get_pending_hitl_request(
        self,
        thread_messages: List[Message] = None,
        checkpoint: Optional[WorkflowCheckpoint] = None,
    ) -> dict[str, Union[WorkflowEvent, Any]]:
        res: dict[str, Union[WorkflowEvent, Any]] = {}

        if checkpoint:
            pending_events = getattr(checkpoint, "pending_request_info_events", None) or getattr(
                checkpoint, "pending_events", None
            )
            if pending_events:
                for call_id, request in pending_events.items():
                    request_obj = self._coerce_workflow_event(request)
                    if request_obj is not None:
                        res[call_id] = request_obj
                return res

        if not thread_messages:
            return res

        for message in thread_messages:
            for content in message.contents:
                if (
                    getattr(content, "type", None) == "function_approval_request"
                    or getattr(content, "user_input_request", False)
                ):
                    function_call = getattr(content, "function_call", None)
                    if function_call is None:
                        continue
                    call_id = getattr(function_call, "call_id", "")
                    if call_id:
                        res[call_id] = WorkflowEvent(
                            "request_info",
                            data={
                                "source_executor_id": "agent",
                                "request_id": call_id,
                                "response_type": None,
                                "request_data": function_call,
                            },
                        )
                elif content.type == "function_result":
                    call_id = getattr(content, "call_id", None)
                    if call_id and call_id in res:
                        res.pop(call_id)
                elif content.type == "function_approval_response":
                    function_call = getattr(content, "function_call", None)
                    call_id = getattr(function_call, "call_id", "") if function_call else ""
                    if call_id and call_id in res:
                        res.pop(call_id)
        return res

    def convert_user_input_request_content(self, content: Any) -> dict:
        function_call = content.function_call
        call_id = getattr(function_call, "call_id", "")
        arguments = self.convert_request_arguments(getattr(function_call, "arguments", ""))
        return {
            "call_id": call_id,
            "name": HUMAN_IN_THE_LOOP_FUNCTION_NAME,
            "arguments": arguments or "",
        }

    def convert_request_arguments(self, arguments: Any) -> str:
        if isinstance(arguments, dict):
            data = arguments.get("data")
            if data and hasattr(data, "convert_to_payload"):
                return data.convert_to_payload()

        if not isinstance(arguments, str):
            if hasattr(arguments, "to_dict"):
                arguments = arguments.to_dict()
            try:
                arguments = json.dumps(arguments)
            except Exception:  # pragma: no cover # pylint: disable=broad-exception-caught
                arguments = str(arguments)
        return arguments

    def validate_and_convert_hitl_response(
        self,
        input: Union[str, List[Dict], None],
        pending_requests: Dict[str, WorkflowEvent],
    ) -> Optional[List[Message]]:
        if input is None or isinstance(input, str):
            logger.warning("Expected list input for HitL response validation, got str.")
            return None

        res: list[Message] = []
        for item in input:
            if item.get("type") != "function_call_output":
                logger.warning("Expected function_call_output type for HitL response validation.")
                return None
            call_id = item.get("call_id", None)
            if call_id and call_id in pending_requests:
                res.append(self.convert_response(pending_requests[call_id], item))
        return res

    def convert_response(self, hitl_request: WorkflowEvent, input: Dict) -> Message:
        response_type = self._event_response_type(hitl_request)
        request_id = self._event_request_id(hitl_request)
        response_result = input.get("output", "")
        logger.info("response_type %s", response_type)
        if response_type and hasattr(response_type, "convert_from_payload"):
            response_result = response_type.convert_from_payload(input.get("output", ""))
        logger.info("response_result %s", response_result)

        response_content = self._content_from_function_result(
            call_id=request_id,
            result=response_result,
        )
        return Message(role="tool", contents=[response_content])

    def remove_hitl_content_from_thread(self, thread_messages: List[Message]) -> List[Message]:
        """Remove HITL function call contents and related results from a conversation thread."""
        filtered_messages: list[Message] = []

        prev_function_call = None
        prev_hitl_request = None
        prev_function_output = None
        pending_tool_message: Optional[Message] = None

        for message in thread_messages:
            filtered_contents: list[Any] = []
            for content in message.contents:
                if content.type == "function_result":
                    result_call_id = getattr(content, "call_id", "")
                    if not prev_function_call:
                        if prev_hitl_request and getattr(prev_hitl_request, "call_id", "") == result_call_id:
                            prev_hitl_request = None
                        else:
                            logger.warning(
                                "Got function result content with call_id %s but no previous function call found.",
                                result_call_id,
                            )
                    elif result_call_id == getattr(prev_function_call, "call_id", ""):
                        if prev_hitl_request:
                            prev_function_output = content
                        else:
                            filtered_contents.append(content)
                            prev_function_call = None
                    else:
                        logger.warning(
                            "Got unmatched function result content with call_id %s, expected call_id %s. Skipping it.",
                            result_call_id,
                            getattr(prev_function_call, "call_id", ""),
                        )
                        prev_function_call = None
                        prev_hitl_request = None
                else:
                    if pending_tool_message:
                        filtered_messages.append(pending_tool_message)
                        pending_tool_message = None
                        prev_function_call = None
                        prev_hitl_request = None
                        prev_function_output = None

                    if content.type == "function_call":
                        if getattr(content, "name", "") != HUMAN_IN_THE_LOOP_FUNCTION_NAME:
                            filtered_contents.append(content)
                            prev_function_call = content
                        else:
                            prev_hitl_request = content
                    else:
                        filtered_contents.append(content)
            if filtered_contents:
                filtered_messages.append(
                    Message(
                        role=message.role,
                        contents=filtered_contents,
                        message_id=message.message_id,
                        additional_properties=message.additional_properties,
                    )
                )

            if prev_function_output:
                pending_tool_message = Message(
                    role="tool",
                    contents=[prev_function_output],
                    message_id=message.message_id,
                    additional_properties=message.additional_properties,
                )
        return filtered_messages

    def _coerce_workflow_event(self, request: Any) -> Optional[WorkflowEvent]:
        if isinstance(request, WorkflowEvent):
            return request
        if isinstance(request, dict):
            event_type = request.get("type")
            event_data = request.get("data")
            if event_type:
                return WorkflowEvent(event_type, data=event_data)
        return None

    def _event_data(self, event: WorkflowEvent) -> Any:
        data = getattr(event, "data", None)
        if data is None and isinstance(event, dict):
            data = event.get("data")
        return data

    def _event_request_id(self, event: WorkflowEvent) -> str:
        data = self._event_data(event)
        if isinstance(data, dict):
            return data.get("request_id", "")
        return getattr(data, "request_id", "") if data is not None else ""

    def _event_response_type(self, event: WorkflowEvent) -> Any:
        data = self._event_data(event)
        if isinstance(data, dict):
            return data.get("response_type", None)
        return getattr(data, "response_type", None) if data is not None else None

    def _content_from_function_result(self, call_id: str, result: Any) -> Any:
        factory = getattr(Content, "from_function_result", None)
        if callable(factory):
            return factory(call_id=call_id, result=result)
        return Content(type="function_result", call_id=call_id, result=result)
