import json
import unittest
from datetime import datetime

from azure.ai.evaluation._converters._ai_services import AIAgentConverter
from azure.ai.evaluation._converters._models import (
    Message,
    AssistantMessage,
    ToolMessage,
    ToolCall,
    break_tool_call_into_messages,
)
from azure.ai.projects.models import (
    RunStepCodeInterpreterToolCall,
    RunStepCodeInterpreterToolCallDetails,
    RunStepFileSearchToolCall,
    RunStepFileSearchToolCallResults,
    RunStepFileSearchToolCallResult,
)

from serialization_helper import ToolDecoder


class TestAIAgentConverter(unittest.TestCase):
    def test_is_agent_tool_call(self):
        # Test case where message is an agent tool call
        message = Message(
            role="assistant",
            content=[{"type": "tool_call", "details": "some details"}],
            createdAt="2023-01-01T00:00:00Z",
        )
        self.assertTrue(AIAgentConverter._is_agent_tool_call(message))

        # Test case where message is not an agent tool call (role is not agent)
        message = Message(
            role="not_assistant",
            content=[{"type": "tool_call", "details": "some details"}],
            createdAt="2023-01-01T00:00:00Z",
        )
        self.assertFalse(AIAgentConverter._is_agent_tool_call(message))

        # Test case where message is not an agent tool call (content type is not tool_call)
        message = Message(
            role="assistant", content=[{"type": "text", "details": "some details"}], createdAt="2023-01-01T00:00:00Z"
        )
        self.assertFalse(AIAgentConverter._is_agent_tool_call(message))

        # Test case where message is not an agent tool call (content is empty)
        message = Message(role="assistant", content=[], createdAt="2023-01-01T00:00:00Z")
        self.assertFalse(AIAgentConverter._is_agent_tool_call(message))

    class CustomEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, ToolCall):
                return {"completed": obj.completed, "created": obj.created, "details": obj.details}
            if isinstance(obj, RunStepCodeInterpreterToolCall):
                return {"id": obj.id, "type": obj.type, "code_interpreter": obj.code_interpreter}
            if isinstance(obj, RunStepCodeInterpreterToolCallDetails):
                return {"input": obj.input, "outputs": obj.outputs}
            if isinstance(obj, RunStepFileSearchToolCall):
                return {"id": obj.id, "type": obj.type, "file_search": obj.file_search}
            if isinstance(obj, RunStepFileSearchToolCallResults):
                return {"results": obj.results}
            if isinstance(obj, RunStepFileSearchToolCallResult):
                return {"file_name": obj.file_name, "file_path": obj.file_path, "file_size": obj.file_size}
            return super().default(obj)

    def test_code_interpreter_tool_calls(self):
        tool_call_data = """{
    "completed": "2025-03-24T18:45:57+00:00",
    "created": "2025-03-24T18:45:54+00:00",
    "details": {
        "id": "call_CNw8VOVOBxKF3ggZM2Fif1V0",
        "type": "code_interpreter",
        "code_interpreter": {
            "input": "import math\\n\\n# Calculate the square root of 139485\\nsquare_root = math.sqrt(139485)\\nsquare_root",
            "outputs": []
        }
    }
}
"""
        tool_call = json.loads(tool_call_data, cls=ToolDecoder)
        messages = break_tool_call_into_messages(tool_call, "abc123")
        self.assertTrue(len(messages) == 2)
        self.assertTrue(isinstance(messages[0], AssistantMessage))
        tool_call_content = messages[0].content[0]
        self.assertTrue(tool_call_content["type"] == "tool_call")
        self.assertTrue(tool_call_content["tool_call_id"] == "call_CNw8VOVOBxKF3ggZM2Fif1V0")
        self.assertTrue(tool_call_content["name"] == "code_interpreter")
        self.assertTrue(
            tool_call_content["arguments"]
            == {
                "input": "import math\n\n# Calculate the square root of 139485"
                "\nsquare_root = math.sqrt(139485)\nsquare_root"
            }
        )
        self.assertTrue(isinstance(messages[1], ToolMessage))
        # TODO: example with outputs populated

    def test_file_search_tool_calls(self):
        tool_call_data = """{
    "completed": "2025-03-24T20:55:29+00:00",
    "created": "2025-03-24T20:55:27+00:00",
    "details": {
        "id": "call_sot1fUR9Pazh3enT2E6EjX5g",
        "type": "file_search",
        "file_search": {
            "ranking_options": {
                "ranker": "default_2024_08_21",
                "score_threshold": 0.0
            },
            "results": [
                {
                    "file_name": "dragons.txt",
                    "file_id": "assistant-BsRfTatRwQzF96Uz4EhhqT",
                    "score": 0.03201844170689583,
                    "content": null
                },
                {
                    "file_name": "dragons.txt",
                    "file_id": "assistant-BsRfTatRwQzF96Uz4EhhqT",
                    "score": 0.02539682574570179,
                    "content": null
                }
            ]
        }
    }
}"""
        tool_call = json.loads(tool_call_data, cls=ToolDecoder)
        messages = break_tool_call_into_messages(tool_call, "abc123")
        self.assertTrue(len(messages) == 2)
        self.assertTrue(isinstance(messages[0], AssistantMessage))
        tool_call_content = messages[0].content[0]
        self.assertTrue(tool_call_content["type"] == "tool_call")
        self.assertTrue(tool_call_content["tool_call_id"] == "call_sot1fUR9Pazh3enT2E6EjX5g")
        self.assertTrue(tool_call_content["name"] == "file_search")
        self.assertTrue(
            tool_call_content["arguments"]
            == {"ranking_options": {"ranker": "default_2024_08_21", "score_threshold": 0.0}}
        )
        self.assertTrue(isinstance(messages[1], ToolMessage))
        self.assertTrue(messages[1].content[0]["type"] == "tool_result")
        self.assertTrue(
            messages[1].content[0]["tool_result"]
            == [
                {
                    "file_name": "dragons.txt",
                    "file_id": "assistant-BsRfTatRwQzF96Uz4EhhqT",
                    "score": 0.03201844170689583,
                    "content": None,
                },
                {
                    "file_name": "dragons.txt",
                    "file_id": "assistant-BsRfTatRwQzF96Uz4EhhqT",
                    "score": 0.02539682574570179,
                    "content": None,
                },
            ]
        )

    def test_bing_grounding_tool_calls(self):
        tool_call_data = """{
    "completed": "2025-03-24T19:15:17+00:00",
    "created": "2025-03-24T19:15:16+00:00",
    "details": {
        "id": "call_PG9cYqLGAVO30BWBwgHMcvJQ",
        "type": "bing_grounding",
        "bing_grounding": {
            "requesturl": "https://api.bing.microsoft.com/v7.0/search?q="
        }
    }
}"""
        tool_call = json.loads(tool_call_data, cls=ToolDecoder)
        messages = break_tool_call_into_messages(tool_call, "abc123")
        self.assertTrue(len(messages) == 1)  # we don't have results from bing
        self.assertTrue(isinstance(messages[0], AssistantMessage))
        tool_call_content = messages[0].content[0]
        self.assertTrue(tool_call_content["type"] == "tool_call")
        self.assertTrue(tool_call_content["tool_call_id"] == "call_PG9cYqLGAVO30BWBwgHMcvJQ")
        self.assertTrue(tool_call_content["name"] == "bing_grounding")
        self.assertTrue(
            tool_call_content["arguments"] == {"requesturl": "https://api.bing.microsoft.com/v7.0/search?q="}
        )


if __name__ == "__main__":
    unittest.main()
