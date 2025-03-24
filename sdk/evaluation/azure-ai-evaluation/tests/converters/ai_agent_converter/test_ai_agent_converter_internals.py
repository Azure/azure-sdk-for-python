import unittest

from azure.ai.evaluation._converters._ai_services import AIAgentConverter
from azure.ai.evaluation._converters._models import Message, ToolCall
from azure.ai.projects.models import RunStepFunctionToolCall


class TestAIAgentConverter(unittest.TestCase):
    def test_is_agent_tool_call(self):
        # Test case where message is an agent tool call
        message = Message(
            role='assistant',
            content=[{"type": "tool_call", "details": "some details"}],
            createdAt="2023-01-01T00:00:00Z"
        )
        self.assertTrue(AIAgentConverter._is_agent_tool_call(message))

        # Test case where message is not an agent tool call (role is not agent)
        message = Message(
            role='assistant',
            content=[{"type": "tool_call", "details": "some details"}],
            createdAt="2023-01-01T00:00:00Z"
        )
        self.assertTrue(AIAgentConverter._is_agent_tool_call(message))

        # Test case where message is not an agent tool call (content type is not tool_call)
        message = Message(
            role='assistant',
            content=[{"type": "text", "details": "some details"}],
            createdAt="2023-01-01T00:00:00Z"
        )
        self.assertFalse(AIAgentConverter._is_agent_tool_call(message))

        # Test case where message is not an agent tool call (content is empty)
        message = Message(
            role='assistant',
            content=[],
            createdAt="2023-01-01T00:00:00Z"
        )
        self.assertFalse(AIAgentConverter._is_agent_tool_call(message))

    # def test_tool_call_format(self):
    #     tool_call = ToolCall(created=, completed=, details=RunStepFunctionToolCall())
    #     break_tool_call_into_messages(tool_call: ToolCall, run_id: str)
    #     # Test case where message is an agent tool call
    #     message = Message(
    #         role='assistant',
    #         content=[{"type": "tool_call", "details": "some details"}],
    #         createdAt="2023-01-01T00:00:00Z"
    #     )
    #     self.assertTrue(AIAgentConverter._is_agent_tool_call(message))

if __name__ == '__main__':
    unittest.main()