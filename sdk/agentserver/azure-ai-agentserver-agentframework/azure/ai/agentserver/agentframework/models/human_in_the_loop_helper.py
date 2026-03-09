# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from agent_framework import Content, Message, WorkflowCheckpoint, WorkflowEvent

from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.server.common.constants import HUMAN_IN_THE_LOOP_FUNCTION_NAME

logger = get_logger()


@dataclass
class PendingHitlRequest:
    """Normalized representation of a pending human-in-the-loop request.

    Both the checkpoint path (real rc3 WorkflowEvents) and the session-messages
    path (synthetic reconstruction) normalize into this type so that downstream
    code never needs to inspect WorkflowEvent internals.

    :param request_id: Unique identifier for the pending request.
    :type request_id: str
    :param response_type: Expected Python type for deserializing the human response, or None.
    :type response_type: Any
    """

    request_id: str
    response_type: Any = None


class HumanInTheLoopHelper:
    def get_pending_hitl_request(
        self,
        session_messages: Optional[List[Message]] = None,
        checkpoint: Optional[WorkflowCheckpoint] = None,
    ) -> Dict[str, PendingHitlRequest]:
        res: Dict[str, PendingHitlRequest] = {}

        if checkpoint:
            pending_events = getattr(checkpoint, "pending_request_info_events", None) or getattr(
                checkpoint, "pending_events", None
            )
            logger.info("Checking checkpoint for pending HITL requests, found %d pending events", len(pending_events) if pending_events else 0)
            if pending_events:
                for call_id, request in pending_events.items():
                    logger.info("Processing pending event with call_id %s from checkpoint %s", call_id, type(request))
                    pending = self._to_pending_hitl_request(call_id, request)
                    if pending is not None:
                        res[call_id] = pending
                return res

        if not session_messages:
            return res

        for message in session_messages:
            for content in message.contents:
                if content.type == "function_approval_request" or content.user_input_request:
                    function_call = content.function_call
                    if function_call is None:
                        continue
                    call_id = function_call.call_id
                    if call_id:
                        res[call_id] = PendingHitlRequest(request_id=call_id, response_type=None)
                elif content.type == "function_result":
                    call_id = content.call_id
                    if call_id and call_id in res:
                        res.pop(call_id)
                elif content.type == "function_approval_response":
                    function_call = content.function_call
                    call_id = function_call.call_id if function_call else ""
                    if call_id and call_id in res:
                        res.pop(call_id)
        return res

    def convert_user_input_request_content(self, content: Any) -> dict:
        function_call = content.function_call
        call_id = function_call.call_id if function_call else ""
        arguments = self.convert_request_arguments(function_call.arguments if function_call else "")
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
        pending_requests: Dict[str, PendingHitlRequest],
    ) -> Optional[List[Message]]:
        if input is None or isinstance(input, str):
            logger.warning("Expected list input for HitL response validation, got str.")
            return None

        res: List[Message] = []
        for item in input:
            if item.get("type") != "function_call_output":
                logger.warning("Expected function_call_output type for HitL response validation.")
                return None
            call_id = item.get("call_id", None)
            if call_id and call_id in pending_requests:
                logger.info("convert_hitl_response: converting response for call_id %s", call_id)
                res.append(self.convert_response(pending_requests[call_id], item))
        for item in res:
            logger.info("HitL response item: %s", item.to_dict() if hasattr(item, "to_dict") else str(item))
        return res

    def convert_response(self, hitl_request: PendingHitlRequest, input: Dict) -> Message:
        response_type = hitl_request.response_type
        request_id = hitl_request.request_id
        response_result = input.get("output", "")
        logger.info("response_type %s", response_type)
        if response_type and hasattr(response_type, "convert_from_payload"):
            response_result = response_type.convert_from_payload(input.get("output", ""))
        logger.info("response_result %s", response_result)

        response_content = Content.from_function_result(
            call_id=request_id,
            result=response_result,
        )
        return Message(role="tool", contents=[response_content])

    def remove_hitl_content_from_session(self, session_messages: List[Message]) -> List[Message]:
        """Remove HITL function call contents and related results from a conversation session."""
        filtered_messages: List[Message] = []

        prev_function_call = None
        prev_hitl_request = None
        prev_function_output = None
        pending_tool_message: Optional[Message] = None

        for message in session_messages:
            filtered_contents: List[Any] = []
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

    def _to_pending_hitl_request(self, call_id: str, request: Any) -> Optional[PendingHitlRequest]:
        """Normalize a checkpoint pending-event entry into a PendingHitlRequest.

        :param call_id: The call/request identifier from the checkpoint dict key.
        :type call_id: str
        :param request: A WorkflowEvent (rc3) or a dict (legacy/serialized).
        :type request: Any
        :return: A normalized PendingHitlRequest, or None if the entry is unrecognised.
        :rtype: Optional[PendingHitlRequest]
        """
        if isinstance(request, WorkflowEvent):
            request_id = getattr(request, "request_id", None) or call_id
            response_type = getattr(request, "response_type", None)
            return PendingHitlRequest(request_id=request_id, response_type=response_type)
        if isinstance(request, dict):
            request_id = request.get("request_id", call_id)
            response_type = request.get("response_type", None)
            return PendingHitlRequest(request_id=request_id, response_type=response_type)
        return None
