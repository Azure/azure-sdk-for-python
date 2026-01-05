from typing import Any
import json

from agent_framework._types import UserInputRequestContents

from azure.ai.agentserver.core.server.common.constants import HUMAN_IN_THE_LOOP_FUNCTION_NAME


class HumanInTheLoopHelper:
    def convert_user_input_request_content(self, content: UserInputRequestContents) -> dict:
        call_id = getattr(content, "id")
        arguments = self.convert_request_arguments(getattr(content, "arguments", ""))
        return {
            "call_id": call_id,
            "name": HUMAN_IN_THE_LOOP_FUNCTION_NAME,
            "arguments": arguments or "",
        }
    
    def convert_request_arguments(self, arguments: Any) -> str:
        if not isinstance(arguments, str):
            try:
                arguments = json.dumps(arguments)
            except Exception:  # pragma: no cover - fallback # pylint: disable=broad-exception-caught
                arguments = str(arguments)
        return arguments
