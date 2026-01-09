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
                print(f"    Content {type(content)}: {content.to_dict()}")
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
            input: str | List[Dict] | None,
            pending_requests: Dict[str, RequestInfoEvent],
        ) -> List[ChatMessage] | None:

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