# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, List, Dict, Optional, Union
import json

from agent_framework import (
    ChatMessage,
    FunctionResultContent,
    FunctionApprovalResponseContent,
    RequestInfoEvent,
    WorkflowCheckpoint,
)
from agent_framework._types import UserInputRequestContents

from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.server.common.constants import HUMAN_IN_THE_LOOP_FUNCTION_NAME

logger = get_logger()

class HumanInTheLoopHelper:

    def get_pending_hitl_request(self,
            thread_messages: List[ChatMessage] = None,
            checkpoint: Optional[WorkflowCheckpoint] = None,
        ) -> dict[str, Union[RequestInfoEvent, Any]]:
        res = {}
        # if has checkpoint (WorkflowAgent), find pending request info from checkpoint
        if checkpoint and checkpoint.pending_request_info_events:
            for call_id, request in checkpoint.pending_request_info_events.items():
                # find if the request is already responded in the thread messages
                if isinstance(request, dict):
                    request_obj = RequestInfoEvent.from_dict(request)
                res[call_id] = request_obj
            return res

        if not thread_messages:
            return res

        # if no checkpoint (Agent), find user input request and pair the feedbacks
        for message in thread_messages:
            for content in message.contents:
                if isinstance(content, UserInputRequestContents):
                    # is a human input request
                    function_call = content.function_call
                    call_id = getattr(function_call, "call_id", "")
                    if call_id:
                        res[call_id] = RequestInfoEvent(
                            source_executor_id="agent",
                            request_id=call_id,
                            response_type=None,
                            request_data=function_call,
                        )
                elif isinstance(content, FunctionResultContent):
                    if content.call_id and content.call_id in res:
                        # remove requests that already got feedback
                        res.pop(content.call_id)
                elif isinstance(content, FunctionApprovalResponseContent):
                    function_call = content.function_call
                    call_id = getattr(function_call, "call_id", "")
                    if call_id and call_id in res:
                        res.pop(call_id)
        return res

    def convert_user_input_request_content(self, content: UserInputRequestContents) -> dict:
        function_call = content.function_call
        call_id = getattr(function_call, "call_id", "")
        arguments = self.convert_request_arguments(getattr(function_call, "arguments", ""))
        return {
            "call_id": call_id,
            "name": HUMAN_IN_THE_LOOP_FUNCTION_NAME,
            "arguments": arguments or "",
        }

    def convert_request_arguments(self, arguments: Any) -> str:
        # convert data to payload if possible
        if isinstance(arguments, dict):
            data = arguments.get("data")
            if data and hasattr(data, "convert_to_payload"):
                return data.convert_to_payload()

        if not isinstance(arguments, str):
            if hasattr(arguments, "to_dict"):   # agentframework models have to_dict method
                arguments = arguments.to_dict()
            try:
                arguments = json.dumps(arguments)
            except Exception:  # pragma: no cover - fallback # pylint: disable=broad-exception-caught
                arguments = str(arguments)
        return arguments

    def validate_and_convert_hitl_response(self,
            input: Union[str, List[Dict], None],
            pending_requests: Dict[str, RequestInfoEvent],
        ) -> Optional[List[ChatMessage]]:

        if input is None or isinstance(input, str):
            logger.warning("Expected list input for HitL response validation, got str.")
            return None

        res = []
        for item in input:
            if item.get("type") != "function_call_output":
                logger.warning("Expected function_call_output type for HitL response validation.")
                return None
            call_id = item.get("call_id", None)
            if call_id and call_id in pending_requests:
                res.append(self.convert_response(pending_requests[call_id], item))
        return res

    def convert_response(self, hitl_request: RequestInfoEvent, input: Dict) -> ChatMessage:
        response_type  = hitl_request.response_type
        response_result = input.get("output", "")
        logger.info(f"response_type {type(response_type)}: %s", response_type)
        if response_type and hasattr(response_type, "convert_from_payload"):
            response_result = response_type.convert_from_payload(input.get("output", ""))
        logger.info(f"response_result {type(response_result)}: %s", response_result)
        response_content = FunctionResultContent(
            call_id=hitl_request.request_id,
            result=response_result,
        )
        return ChatMessage(role="tool", contents=[response_content])

    def remove_hitl_content_from_thread(self, thread_messages: List[ChatMessage]) -> List[ChatMessage]:
        """Remove HITL function call contents and related results from a conversation thread.

        HITL requests become ``function_call`` entries named ``HUMAN_IN_THE_LOOP_FUNCTION_NAME`` when converted
        by the adapter. To avoid feeding those synthetic requests back into the agent, this method strips the
        HITL function_calls and their placeholder outputs while preserving real tool invocations.

        :param thread_messages: The messages converted from the conversation API.
        :type thread_messages: List[ChatMessage]
        :return: Messages without HITL-specific artifacts.
        :rtype: List[ChatMessage]
        """
        filtered_messages = []

        prev_function_call = None
        prev_hitl_request = None
        prev_function_output = None
        pending_tool_message = None

        for message in thread_messages:
            filtered_contents = []
            for content in message.contents:
                if content.type == "function_result":
                    result_call_id = getattr(content, "call_id", "")
                    if not prev_function_call:
                        if prev_hitl_request and prev_hitl_request.call_id == result_call_id:
                            # this is a hitl function result without the function call content, we can
                            # just skip it and wait for the next function call or result.
                            prev_hitl_request = None
                        else:
                            logger.warning(
                                "Got function result content with call_id %s but no previous function call found.",
                                result_call_id,
                            )
                    elif result_call_id == getattr(prev_function_call, "call_id", ""):
                        # prev_function_call is not None and call_id matches
                        if prev_hitl_request:
                            # A HITL request may followed by one or two function result contents.
                            # if there are two, the last one is the real function result, the first
                            # one is just for recording the human feedback, we should remove it.
                            prev_function_output = content
                        else:
                            # function call without hitl result of the function call content
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
                        # for the case mentioned above, we should append the real function result content
                        # when we see the next content, which means the function call and output cycle is ended.
                        # attach the real function result to the thread
                        filtered_messages.append(pending_tool_message)
                        pending_tool_message = None
                        prev_function_call = None
                        prev_hitl_request = None
                        prev_function_output = None

                    if content.type == "function_call":
                        if content.name != HUMAN_IN_THE_LOOP_FUNCTION_NAME:
                            filtered_contents.append(content)
                            prev_function_call = content
                        else:
                            # hitl request converted by adapter, skip this message.
                            prev_hitl_request = content
                    else:
                        filtered_contents.append(content)
            if filtered_contents:
                filtered_message = ChatMessage(
                    role=message.role,
                    contents=filtered_contents,
                    message_id=message.message_id,
                    additional_properties=message.additional_properties,
                )
                filtered_messages.append(filtered_message)

            if prev_function_output:
                pending_tool_message = ChatMessage(
                    role="tool",
                    contents=[prev_function_output],
                    message_id=message.message_id,
                    additional_properties=message.additional_properties,
                )
        return filtered_messages
