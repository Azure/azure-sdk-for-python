import pytest
import os
import pathlib
import base64
import json

from azure.ai.evaluation._common.utils import nltk_tokenize
from azure.ai.evaluation._common.utils import validate_conversation
from azure.ai.evaluation._common.utils import (
    _extract_text_from_content,
    _get_conversation_history,
    _pretty_format_conversation_history,
    reformat_conversation_history,
    _get_agent_response,
    reformat_agent_response,
)
from azure.ai.evaluation._exceptions import EvaluationException, ErrorMessage


@pytest.mark.unittest
class TestUtils:
    def test_nltk_tokenize(self):

        # Test with English text
        text = "The capital of China is Beijing."
        tokens = nltk_tokenize(text)

        assert tokens == ["The", "capital", "of", "China", "is", "Beijing", "."]

        # Test with Multi-language text
        text = "The capital of China is 北京."
        tokens = nltk_tokenize(text)

        assert tokens == ["The", "capital", "of", "China", "is", "北京", "."]

    def convert_json_list_to_jsonl(self, project_scope, azure_cred):

        parent = pathlib.Path(__file__).parent.resolve()
        path = os.path.join(parent, "data")
        image_path = os.path.join(path, "image1.jpg")

        with pathlib.Path(image_path).open("rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

        conversation = [
            {
                "role": "system",
                "content": [
                    {"type": "text", "text": "This is a nature boardwalk at the University of Wisconsin-Madison."}
                ],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Can you describe this image?"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}},
                ],
            },
        ]

        messages = [{"messages": conversation}]
        datafile_jsonl_path = os.path.join(path, "datafile.jsonl")
        with open(datafile_jsonl_path, "w") as outfile:
            for json_obj in messages:
                json_line = json.dumps(json_obj)
                outfile.write(json_line + "\n")

    def test_messages_with_one_assistant_message(self):
        conversation = {
            "messages": [
                {
                    "role": "system",
                    "content": [
                        {"type": "text", "text": "This is a nature boardwalk at the University of Wisconsin-Madison."}
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Can you describe this image?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
                            },
                        },
                    ],
                },
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": "The image shows a man with short brown hair smiling, wearing a dark-colored shirt.",
                        }
                    ],
                },
            ]
        }
        validate_conversation(conversation=conversation)

    def test_messages_with_missing_assistant_message(self):
        conversation = {
            "messages": [
                {
                    "role": "system",
                    "content": [
                        {"type": "text", "text": "This is a nature boardwalk at the University of Wisconsin-Madison."}
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Can you describe this image?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
                            },
                        },
                    ],
                },
            ]
        }
        try:
            validate_conversation(conversation=conversation)
        except EvaluationException as ex:
            assert ex.message in "Assistant role required in one of the messages."

    def test_messages_with_missing_user_message(self):
        conversation = {
            "messages": [
                {
                    "role": "system",
                    "content": [
                        {"type": "text", "text": "This is a nature boardwalk at the University of Wisconsin-Madison."}
                    ],
                },
                {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": "Here is the picture you requested"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
                            },
                        },
                    ],
                },
            ]
        }
        try:
            validate_conversation(conversation=conversation)
        except EvaluationException as ex:
            assert ex.message in "User role required in one of the messages."

    def test_messages_with_more_than_one_assistant_message(self):
        conversation = {
            "messages": [
                {
                    "role": "system",
                    "content": [
                        {"type": "text", "text": "This is a nature boardwalk at the University of Wisconsin-Madison."}
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Can you describe this image?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
                            },
                        },
                    ],
                },
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": "The image shows a man with short brown hair smiling, wearing a dark-colored shirt.",
                        }
                    ],
                },
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": "The image shows a man with short brown hair smiling, wearing a dark-colored shirt.",
                        }
                    ],
                },
            ]
        }
        try:
            validate_conversation(conversation=conversation)
        except EvaluationException as ex:
            assert (
                ex.message
                in "Evaluators for multimodal conversations only support single turn. User and assistant role expected as the only role in each message."
            )

    def test_messages_multi_turn(self):
        conversation = {
            "messages": [
                {
                    "role": "system",
                    "content": [
                        {"type": "text", "text": "This is a nature boardwalk at the University of Wisconsin-Madison."}
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Can you describe this image?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
                            },
                        },
                    ],
                },
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": "The image shows a man with short brown hair smiling, wearing a dark-colored shirt.",
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Okay, try again with this image"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
                            },
                        },
                    ],
                },
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": "The image shows a same man with short brown hair smiling, wearing a dark-colored shirt.",
                        }
                    ],
                },
            ]
        }
        try:
            validate_conversation(conversation=conversation)
        except EvaluationException as ex:
            assert (
                ex.message
                in "Evaluators for multimodal conversations only support single turn. User and assistant role expected as the only role in each message."
            )

    def test__extract_text_from_content(self):
        """Test _extract_text_from_content function"""
        # Test with content containing text
        content = [
            {"type": "text", "text": "Hello world"},
            {"type": "text", "text": "How are you?"},
            {"type": "image_url", "image_url": {"url": "http://example.com/image.jpg"}},
        ]
        result = _extract_text_from_content(content)
        assert result == ["Hello world", "How are you?"]

        # Test with empty content
        result = _extract_text_from_content([])
        assert result == []

        # Test with content without text
        content = [
            {"type": "image_url", "image_url": {"url": "http://example.com/image.jpg"}},
            {"type": "other", "data": "some data"},
        ]
        result = _extract_text_from_content(content)
        assert result == []

        # Test with mixed content
        content = [
            {"type": "text", "text": "First message"},
            {"type": "image_url", "image_url": {"url": "http://example.com/image.jpg"}},
            {"type": "text", "text": "Second message"},
        ]
        result = _extract_text_from_content(content)
        assert result == ["First message", "Second message"]

    def test__get_conversation_history(self):
        """Test _get_conversation_history function"""
        # Test basic conversation
        query = [
            {"role": "user", "content": [{"type": "text", "text": "What is the weather?"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "It's sunny today."}]},
            {"role": "user", "content": [{"type": "text", "text": "Will it rain tomorrow?"}]},
        ]

        result = _get_conversation_history(query)
        expected = {
            "user_queries": [[["What is the weather?"]], [["Will it rain tomorrow?"]]],
            "agent_responses": [[["It's sunny today."]]],
        }
        assert result == expected

        # Test conversation with multiple messages per turn
        query = [
            {"role": "user", "content": [{"type": "text", "text": "Hello"}, {"type": "text", "text": "How are you?"}]},
            {
                "role": "assistant",
                "content": [{"type": "text", "text": "Hi there!"}, {"type": "text", "text": "I'm doing well, thanks."}],
            },
        ]

        # there is an assertion because there is one user query ["Hello", "How are you?"] and one agent response ["Hi there!", "I'm doing well, thanks."]
        # the user query length needs to be one more than the agent response length
        with pytest.raises(EvaluationException, match=str(ErrorMessage.MALFORMED_CONVERSATION_HISTORY)):
            _get_conversation_history(query)

        # Test conversation ending with user message
        query = [
            {"role": "user", "content": [{"type": "text", "text": "First question"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "First answer"}]},
            {"role": "user", "content": [{"type": "text", "text": "Second question"}]},
        ]

        result = _get_conversation_history(query)
        expected = {
            "user_queries": [[["First question"]], [["Second question"]]],
            "agent_responses": [[["First answer"]]],
        }
        assert result == expected

    def test__get_conversation_history_with_invalid_data(self):
        """Test _get_conversation_history with edge cases"""
        # Test with messages missing role
        query = [
            {"content": [{"type": "text", "text": "No role"}]},
            {"role": "user", "content": [{"type": "text", "text": "Has role"}]},
        ]

        result = _get_conversation_history(query)
        expected = {"user_queries": [[["Has role"]]], "agent_responses": []}
        assert result == expected

        # Test with messages missing content
        query = [{"role": "user"}, {"role": "user", "content": [{"type": "text", "text": "Has content"}]}]

        result = _get_conversation_history(query)
        expected = {"user_queries": [[["Has content"]]], "agent_responses": []}
        assert result == expected

    def test__pretty_format_conversation_history(self):
        """Test _pretty_format_conversation_history function"""
        conversation_history = {
            "user_queries": [[["What is the weather?"]], [["Will it rain tomorrow?"]]],
            "agent_responses": [[["It's sunny today."]]],
        }

        result = _pretty_format_conversation_history(conversation_history)
        expected = (
            "User turn 1:\n"
            "  What is the weather?\n\n"
            "Agent turn 1:\n"
            "  It's sunny today.\n\n"
            "User turn 2:\n"
            "  Will it rain tomorrow?\n\n"
        )
        assert result == expected

        # Test with multiple messages per turn
        conversation_history = {
            "user_queries": [[["Hello", "How are you?"]]],
            "agent_responses": [[["Hi there!", "I'm doing well, thanks."]]],
        }

        result = _pretty_format_conversation_history(conversation_history)
        expected = (
            "User turn 1:\n"
            "  Hello\n  How are you?\n\n"
            "Agent turn 1:\n"
            "  Hi there!\n  I'm doing well, thanks.\n\n"
        )
        assert result == expected

    def test_reformat_conversation_history(self):
        """Test reformat_conversation_history function"""
        # Test valid conversation
        query = [
            {"role": "user", "content": [{"type": "text", "text": "What is AI?"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "AI stands for Artificial Intelligence."}]},
            {"role": "user", "content": [{"type": "text", "text": "Tell me more."}]},
        ]

        result = reformat_conversation_history(query)
        expected = (
            "User turn 1:\n"
            "  What is AI?\n\n"
            "Agent turn 1:\n"
            "  AI stands for Artificial Intelligence.\n\n"
            "User turn 2:\n"
            "  Tell me more.\n\n"
        )
        assert result == expected

        # Test fallback behavior with invalid input
        invalid_query = "This is not a valid conversation format"
        result = reformat_conversation_history(invalid_query)
        assert result == invalid_query

    def test__get_agent_response(self):
        """Test _get_agent_response function"""
        # Test with valid agent response
        agent_response_msgs = [
            {
                "role": "assistant",
                "content": [{"type": "text", "text": "Hello!"}, {"type": "text", "text": "How can I help you?"}],
            }
        ]

        result = _get_agent_response(agent_response_msgs)
        assert result == ["Hello!", "How can I help you?"]

        # Test with multiple assistant messages
        agent_response_msgs = [
            {"role": "assistant", "content": [{"type": "text", "text": "First response"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "Second response"}]},
        ]

        result = _get_agent_response(agent_response_msgs)
        assert result == ["First response", "Second response"]

        # Test with non-assistant messages
        agent_response_msgs = [
            {"role": "user", "content": [{"type": "text", "text": "User message"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "Assistant message"}]},
        ]

        result = _get_agent_response(agent_response_msgs)
        assert result == ["Assistant message"]

        # Test with empty input
        result = _get_agent_response([])
        assert result == []

        # Test with messages missing role or content
        agent_response_msgs = [
            {"content": [{"type": "text", "text": "No role"}]},
            {"role": "assistant"},
            {"role": "assistant", "content": [{"type": "text", "text": "Valid message"}]},
        ]

        result = _get_agent_response(agent_response_msgs)
        assert result == ["Valid message"]

    def test_reformat_agent_response(self):
        """Test reformat_agent_response function"""
        # Test with valid agent response
        response = [
            {
                "role": "assistant",
                "content": [{"type": "text", "text": "Hello!"}, {"type": "text", "text": "How can I help you?"}],
            }
        ]

        result = reformat_agent_response(response)
        assert result == "Hello!\nHow can I help you?"

        # Test with empty response
        response = []
        result = reformat_agent_response(response)
        assert result == ""

        # Test with no valid assistant messages
        response = [{"role": "user", "content": [{"type": "text", "text": "User message"}]}]
        result = reformat_agent_response(response)
        assert result == response

        # Test fallback behavior with invalid input
        invalid_response = "This is not a valid response format"
        result = reformat_agent_response(invalid_response)
        assert result == invalid_response

    def test_edge_cases_and_error_handling(self):
        """Test edge cases and error handling"""
        # Test _extract_text_from_content with malformed content
        malformed_content = [
            {"text": "Missing type field"},
            {"type": "text"},  # Missing text field
            {"type": "text", "text": ""},  # Empty text
            {"type": "text", "text": "Valid text"},
        ]
        result = _extract_text_from_content(malformed_content)
        assert result == ["Missing type field", "", "Valid text"]

        # Test _get_conversation_history assertion error
        query_with_unbalanced_turns = [
            {"role": "assistant", "content": [{"type": "text", "text": "Response without user query"}]}
        ]

        with pytest.raises(EvaluationException, match=str(ErrorMessage.MALFORMED_CONVERSATION_HISTORY)):
            _get_conversation_history(query_with_unbalanced_turns)

    def test_extract_text_from_content_with_list(self):
        """Test _extract_text_from_content function with list input."""
        # Test with list of dict content
        content = [{"text": "Hello"}, {"text": " world"}]
        assert _extract_text_from_content(content) == ["Hello", " world"]

        # Test with mixed content (text and non-text)
        content = [{"text": "Hello"}, {"type": "image", "url": "image.jpg"}, {"text": " world"}]
        assert _extract_text_from_content(content) == ["Hello", " world"]

        # Test with empty list
        assert _extract_text_from_content([]) == []

        # Test with non-text items only
        content = [{"type": "image", "url": "image.jpg"}, {"type": "video", "url": "video.mp4"}]
        assert _extract_text_from_content(content) == []

    def test_get_conversation_history_with_queries_and_responses(self):
        """Test _get_conversation_history function that returns user_queries and agent_responses."""
        # Test with simple conversation
        conversation = [
            {"role": "user", "content": [{"text": "Hello"}]},
            {"role": "assistant", "content": [{"text": "Hi there!"}]},
            {"role": "user", "content": [{"text": "How are you?"}]},
        ]

        result = _get_conversation_history(conversation)
        expected = {"user_queries": [[["Hello"]], [["How are you?"]]], "agent_responses": [[["Hi there!"]]]}
        assert result == expected

        conversation = []
        with pytest.raises(EvaluationException, match=str(ErrorMessage.MALFORMED_CONVERSATION_HISTORY)):
            _get_conversation_history(conversation)

    def test_pretty_format_conversation_history_with_dict(self):
        """Test _pretty_format_conversation_history function with dict input."""
        # Test with conversation history dict
        conversation_history = {"user_queries": [[["Hello"]], [["How are you?"]]], "agent_responses": [[["Hi there!"]]]}

        formatted = _pretty_format_conversation_history(conversation_history)
        assert "User turn 1:" in formatted
        assert "Hello" in formatted
        assert "Agent turn 1:" in formatted
        assert "Hi there!" in formatted
        assert "User turn 2:" in formatted
        assert "How are you?" in formatted

    def test_conversation_history_integration(self):
        """Test integration of conversation history functions."""
        # Test with simple conversation
        conversation = [
            {"role": "user", "content": [{"text": "What's the weather?"}]},
            {"role": "assistant", "content": [{"text": "It's sunny today."}]},
            {"role": "user", "content": [{"text": "Will it rain tomorrow?"}]},
        ]

        # Test reformatting
        formatted = reformat_conversation_history(conversation)
        assert isinstance(formatted, str)
        assert "User turn" in formatted

        # Test fallback behavior with malformed conversation
        malformed_conversation = {"invalid": "data"}
        formatted = reformat_conversation_history(malformed_conversation)
        assert str(formatted) == str(malformed_conversation)

    def test_get_agent_response_with_list(self):
        """Test _get_agent_response function with list input."""
        # Test with list of messages
        messages = [
            {"role": "assistant", "content": [{"text": "Hello!"}]},
            {"role": "user", "content": [{"text": "Hi"}]},
            {"role": "assistant", "content": [{"text": "How can I help?"}]},
        ]

        result = _get_agent_response(messages)
        assert result == ["Hello!", "How can I help?"]

        # Test with empty list
        assert _get_agent_response([]) == []

        # Test with no assistant messages
        messages = [{"role": "user", "content": [{"text": "Hello"}]}]
        assert _get_agent_response(messages) == []

    def test_agent_response_integration(self):
        """Test integration of agent response functions."""
        # Test with list of messages
        response = [
            {"role": "assistant", "content": [{"text": "Hello!"}]},
            {"role": "assistant", "content": [{"text": "How can I help?"}]},
        ]

        formatted = reformat_agent_response(response)
        assert formatted == "Hello!\nHow can I help?"

        # Test with empty response
        assert reformat_agent_response([]) == ""

        # Test fallback behavior
        malformed_response = {"invalid": "structure"}
        formatted = reformat_agent_response(malformed_response)
        assert str(formatted) == str(malformed_response)

    def test_utility_functions_edge_cases(self):
        """Test edge cases and error handling for utility functions."""

        # Test _extract_text_from_content with malformed data
        malformed_content = [{"missing_text": "Hello"}, {"text": "world"}]
        # Should handle gracefully and extract what it can
        result = _extract_text_from_content(malformed_content)
        assert result == ["world"]

        # Test functions with very large inputs
        large_content = [{"text": "x" * 1000}] * 10
        result = _extract_text_from_content(large_content)
        assert len(result) == 10
        assert all(len(text) == 1000 for text in result)

        # Test with unicode content
        unicode_content = [{"text": "Hello 世界 🌍"}]
        result = _extract_text_from_content(unicode_content)
        assert result == ["Hello 世界 🌍"]
