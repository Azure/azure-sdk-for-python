import unittest
from azure.ai.evaluation._converters._ai_services import AIAgentConverter

class TestRunIdsFromConversation(unittest.TestCase):
    def test_run_ids_from_conversation(self):
        conversation = {
            "messages": [
                {"role": "user", "content": [{"text": {"value": "message1"}}], "run_id": "run1", "createdAt": "2023-01-01T00:00:00Z"},
                {"role": "agent", "content": [{"text": {"value": "message2"}}], "run_id": "run1", "createdAt": "2023-01-01T01:00:00Z"},
                {"role": "user", "content": [{"text": {"value": "message3"}}], "run_id": "run2", "createdAt": "2023-01-02T00:00:00Z"},
                {"role": "agent", "content": [{"text": {"value": "message4"}}], "run_id": "run2", "createdAt": "2023-01-02T01:00:00Z"},
                {"role": "user", "content": [{"text": {"value": "message5"}}], "run_id": "run3", "createdAt": "2023-01-03T00:00:00Z"},
                {"role": "agent", "content": [{"text": {"value": "message6"}}], "run_id": "run3", "createdAt": "2023-01-03T01:00:00Z"}
            ]
        }
        expected_run_ids = ["run1", "run2", "run3"]
        self.assertEqual(AIAgentConverter._run_ids_from_conversation(conversation), expected_run_ids)

    def test_run_ids_from_conversation_empty(self):
        conversation = {"messages": []}
        expected_run_ids = []
        self.assertEqual(AIAgentConverter._run_ids_from_conversation(conversation), expected_run_ids)

    def test_run_ids_from_conversation_no_run_id(self):
        conversation = {
            "messages": [
                {"role": "user", "content": [{"text": {"value": "message1"}}], "createdAt": "2023-01-01T00:00:00Z"},
                {"role": "agent", "content": [{"text": {"value": "message2"}}], "createdAt": "2023-01-01T01:00:00Z"}
            ]
        }
        expected_run_ids = []
        self.assertEqual(AIAgentConverter._run_ids_from_conversation(conversation), expected_run_ids)

if __name__ == '__main__':
    unittest.main()