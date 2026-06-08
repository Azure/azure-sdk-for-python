import json
import unittest
from datetime import datetime

from azure.ai.evaluation import AIAgentConverter
from azure.ai.evaluation._converters._models import (
    Message,
    AssistantMessage,
    ToolMessage,
    ToolCall,
    break_tool_call_into_messages,
)

# Breaking changes introduced in newer version of the agents SDK
# Models have been moved, so try a few different locations
try:
    from azure.ai.projects.models import (
        RunStepCodeInterpreterToolCall,
        RunStepCodeInterpreterToolCallDetails,
        RunStepFileSearchToolCall,
        RunStepFileSearchToolCallResults,
        RunStepFileSearchToolCallResult,
    )
except ImportError:
    pass
try:
    from azure.ai.agents.models import (
        RunStepCodeInterpreterToolCall,
        RunStepCodeInterpreterToolCallDetails,
        RunStepFileSearchToolCall,
        RunStepFileSearchToolCallResults,
        RunStepFileSearchToolCallResult,
    )
except ImportError:
    pass

from serialization_helper import ToolDecoder, ThreadRunDecoder


class _HybridDict(dict):
    """Dict subclass that also exposes its keys as attributes.

    The converter (`break_tool_call_into_messages`) mixes subscript access on the request side
    (`tool_call.details["type"]`, `tool_call.details["bing_grounding"]["requesturl"]`) with attribute
    access on the result side (`tool_call.details.type`, `tool_call.details.azure_ai_search["output"]`).
    The production code path uses typed runtime models (`RunStep*ToolCall`) that satisfy both shapes;
    `_HybridDict` mimics that surface in unit tests without depending on the agents SDK models, which
    have moved between packages and are not guaranteed to be importable in every test environment.
    """

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(name) from e


def _build_builtin_tool_call(call_id: str, tool_type: str, payload: dict) -> ToolCall:
    """Construct a `ToolCall` for a built-in tool without going through `ToolDecoder`.

    `payload` is the per-tool sub-object (e.g. `{"requesturl": "..."}` for Bing or
    `{"input": "...", "output": {...}}` for SharePoint). The returned `ToolCall.details` is a
    nested `_HybridDict` so both subscript and attribute access work.
    """
    details = _HybridDict(
        {
            "id": call_id,
            "type": tool_type,
            tool_type: _HybridDict(payload),
        }
    )
    now = datetime.now()
    return ToolCall(created=now, completed=now, details=details)


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
                    "content": [{"type": "text", "text" : "Sample content"}]
                },
                {
                    "file_name": "dragons.txt",
                    "file_id": "assistant-BsRfTatRwQzF96Uz4EhhqT",
                    "score": 0.02539682574570179,
                    "content": [{"type": "text", "text" : "Sample content"}]
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
                    "content": [{"type": "text", "text": "Sample content"}],
                },
                {
                    "file_name": "dragons.txt",
                    "file_id": "assistant-BsRfTatRwQzF96Uz4EhhqT",
                    "score": 0.02539682574570179,
                    "content": [{"type": "text", "text": "Sample content"}],
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

    def test_bing_custom_search_tool_calls(self):
        # bing_custom_search mirrors bing_grounding: arguments-only tool_call, no tool_result
        # (results are redacted upstream for Bing-family tools).
        # Built directly rather than via ToolDecoder so the test does not depend on the
        # RunStepBingCustomSearchToolCall model being present in the installed agents SDK.
        tool_call = _build_builtin_tool_call(
            call_id="call_BCS123",
            tool_type="bing_custom_search",
            payload={"requesturl": "https://api.bing.microsoft.com/v7.0/custom/search?customconfig=abc&q=foo"},
        )
        messages = break_tool_call_into_messages(tool_call, "abc123")
        self.assertTrue(len(messages) == 1)  # Bing variants emit no tool_result
        self.assertTrue(isinstance(messages[0], AssistantMessage))
        tool_call_content = messages[0].content[0]
        self.assertTrue(tool_call_content["type"] == "tool_call")
        self.assertTrue(tool_call_content["tool_call_id"] == "call_BCS123")
        self.assertTrue(tool_call_content["name"] == "bing_custom_search")
        self.assertTrue(
            tool_call_content["arguments"]
            == {"requesturl": "https://api.bing.microsoft.com/v7.0/custom/search?customconfig=abc&q=foo"}
        )

    def test_sharepoint_grounding_tool_calls(self):
        # sharepoint_grounding mirrors azure_ai_search: arguments + dumped output.
        # Exercises the `input` argument key on the request side.
        tool_call = _build_builtin_tool_call(
            call_id="call_SP123",
            tool_type="sharepoint_grounding",
            payload={
                "input": "quarterly sales report",
                "output": {
                    "documents": [
                        {
                            "title": "Q3 Sales",
                            "url": "https://contoso.sharepoint.com/Q3.docx",
                            "content": "Q3 was up 12%",
                        }
                    ]
                },
            },
        )
        messages = break_tool_call_into_messages(tool_call, "abc123")
        self.assertTrue(len(messages) == 2)
        self.assertTrue(isinstance(messages[0], AssistantMessage))
        tool_call_content = messages[0].content[0]
        self.assertTrue(tool_call_content["type"] == "tool_call")
        self.assertTrue(tool_call_content["tool_call_id"] == "call_SP123")
        self.assertTrue(tool_call_content["name"] == "sharepoint_grounding")
        self.assertTrue(tool_call_content["arguments"] == {"input": "quarterly sales report"})
        self.assertTrue(isinstance(messages[1], ToolMessage))
        self.assertTrue(messages[1].content[0]["type"] == "tool_result")
        self.assertTrue(
            messages[1].content[0]["tool_result"]
            == {
                "documents": [
                    {
                        "title": "Q3 Sales",
                        "url": "https://contoso.sharepoint.com/Q3.docx",
                        "content": "Q3 was up 12%",
                    }
                ]
            }
        )

    def test_sharepoint_grounding_tool_calls_query_key_fallback(self):
        # Live agent traces emit the search term under `query` instead of `input` for SharePoint.
        # The converter must fall back to `query` so downstream evaluators see a non-empty argument.
        tool_call = _build_builtin_tool_call(
            call_id="call_SP456",
            tool_type="sharepoint_grounding",
            payload={"query": "vacation policy", "output": {"documents": []}},
        )
        messages = break_tool_call_into_messages(tool_call, "abc123")
        self.assertTrue(len(messages) == 2)
        tool_call_content = messages[0].content[0]
        self.assertTrue(tool_call_content["arguments"] == {"input": "vacation policy"})

    def test_azure_ai_search_tool_calls_query_key_fallback(self):
        # Live agent traces emit the search term under `query` instead of `input` for Azure AI Search.
        # The converter must fall back to `query` so downstream evaluators see a non-empty argument.
        tool_call = _build_builtin_tool_call(
            call_id="call_AIS789",
            tool_type="azure_ai_search",
            payload={"query": "refund policy", "output": []},
        )
        messages = break_tool_call_into_messages(tool_call, "abc123")
        self.assertTrue(len(messages) == 2)
        tool_call_content = messages[0].content[0]
        self.assertTrue(tool_call_content["name"] == "azure_ai_search")
        self.assertTrue(tool_call_content["arguments"] == {"input": "refund policy"})

    def test_fabric_dataagent_tool_calls_query_key_fallback(self):
        # Same `query` vs `input` drift for fabric_dataagent.
        tool_call = _build_builtin_tool_call(
            call_id="call_FAB012",
            tool_type="fabric_dataagent",
            payload={"query": "top customers by revenue", "output": {}},
        )
        messages = break_tool_call_into_messages(tool_call, "abc123")
        self.assertTrue(len(messages) == 2)
        tool_call_content = messages[0].content[0]
        self.assertTrue(tool_call_content["name"] == "fabric_dataagent")
        self.assertTrue(tool_call_content["arguments"] == {"input": "top customers by revenue"})

    def test_extract_tool_definitions(self):
        thread_run_data = """{
  "id": "run_zs3USbTw61ZpRk8bwBPP8Ue7",
  "created_at": 1746115656,
  "assistant_id": "asst_mI8CZVyxDF0jHBFxt7xkIpgx",
  "thread_id": "thread_gMETMuBx3bMDTIB6bREOHF6Y",
  "status": "completed",
  "started_at": 1746115656,
  "expires_at": null,
  "cancelled_at": null,
  "failed_at": null,
  "completed_at": 1746115660,
  "required_action": null,
  "last_error": null,
  "model": "gpt-4o-2024-08-06",
  "instructions": "You are a helpful assistant.",
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "fetch_weather",
        "description": "Fetches the weather information for the specified location.",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The location to fetch weather for."
            }
          },
          "required": ["location"]
        },
        "strict": false
      }
    },
    {
      "type": "code_interpreter"
    }
  ],
  "tool_resources": {},
  "metadata": {},
  "temperature": 1.0,
  "top_p": 1.0,
  "max_completion_tokens": null,
  "max_prompt_tokens": null,
  "truncation_strategy": {
    "type": "auto",
    "last_messages": null
  },
  "incomplete_details": null,
  "usage": {
    "prompt_tokens": 845,
    "completion_tokens": 57,
    "total_tokens": 902,
    "prompt_token_details": {
      "cached_tokens": 0
    }
  },
  "response_format": "auto",
  "tool_choice": "auto",
  "parallel_tool_calls": true
}"""
        thread_run = json.loads(thread_run_data, cls=ThreadRunDecoder)
        tool_definitions = AIAgentConverter._extract_function_tool_definitions(thread_run)
        self.assertTrue(len(tool_definitions) == 2)
        self.assertTrue(tool_definitions[0].name == "fetch_weather")
        self.assertTrue(
            tool_definitions[0].description == "Fetches the weather information for the specified location."
        )
        self.assertTrue(tool_definitions[0].parameters["properties"]["location"]["type"] == "string")
        self.assertTrue(
            tool_definitions[0].parameters["properties"]["location"]["description"]
            == "The location to fetch weather for."
        )
        self.assertTrue(tool_definitions[1].type == "code_interpreter")
        self.assertTrue(tool_definitions[1].name == "code_interpreter")
        self.assertTrue(
            tool_definitions[1].description
            == "Use code interpreter to read and interpret information from datasets, "
            + "generate code, and create graphs and charts using your data. Supports "
            + "up to 20 files."
        )
        self.assertTrue(tool_definitions[1].parameters["properties"]["input"]["type"] == "string")
        self.assertTrue(
            tool_definitions[1].parameters["properties"]["input"]["description"] == "Generated code to be executed."
        )


if __name__ == "__main__":
    unittest.main()
