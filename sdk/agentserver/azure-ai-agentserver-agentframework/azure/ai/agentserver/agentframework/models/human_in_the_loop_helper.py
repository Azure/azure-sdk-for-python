from typing import Any, List, Dict
import json

from agent_framework import ChatMessage, FunctionResultContent, RequestInfoEvent
from agent_framework._types import UserInputRequestContents

from azure.ai.agentserver.core.server.common.constants import HUMAN_IN_THE_LOOP_FUNCTION_NAME


class HumanInTheLoopHelper:

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
    
    def convert_response(self, hitl_request: RequestInfoEvent, input: Dict) -> List[ChatMessage]:
        response_type  = hitl_request.response_type
        response_result = input.get("output", "")
        if response_type and hasattr(response_type, "convert_from_payload"):
            response_result = response_type.convert_from_payload(input.get("output", ""))
        response_content = FunctionResultContent(
            call_id=hitl_request.request_id,
            result=response_result,
        )
        return [ChatMessage(role="tool", contents=[response_content])]