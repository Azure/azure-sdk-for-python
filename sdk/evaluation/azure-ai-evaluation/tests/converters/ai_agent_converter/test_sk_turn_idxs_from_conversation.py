import pytest

try:
    from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
    from semantic_kernel.contents import (
        ChatHistory,
        ChatMessageContent,
        FunctionCallContent,
        FunctionResultContent,
    )
    from semantic_kernel.contents.utils.author_role import AuthorRole
    from converters._sk_services import SKAgentConverter  # Update if needed

    has_sk = True
except ImportError:
    has_sk = False


# @pytest.mark.unittest
@pytest.mark.asyncio
@pytest.mark.skipif(not has_sk, reason="semantic-kernel is not installed")
async def test_skagent_extract_turns():
    from semantic_kernel.agents import ChatHistoryAgentThread
    from semantic_kernel.contents import ChatHistory, ChatMessageContent
    from semantic_kernel.contents.utils.author_role import AuthorRole
    from semantic_kernel.contents import FunctionCallContent, FunctionResultContent
    from converters._sk_services import SKAgentConverter

    # Create chat history
    chat_history = ChatHistory()
    chat_history.add_system_message("You are a helpful assistant.")
    chat_history.add_user_message("What is the capital of Egypt?")
    chat_history.add_assistant_message("The capital of Egypt is Cairo.")
    chat_history.add_user_message("What is the capital of France?")
    chat_history.add_assistant_message("The capital of France is Paris.")

    # Add new user query with function calls
    chat_history.add_user_message(
        "What are the allergies of laimonisdumins and emavargova?"
    )
    chat_history.add_message(
        ChatMessageContent(
            role=AuthorRole.ASSISTANT,
            items=[
                FunctionCallContent(
                    name="User-get_user_allergies",
                    id="0001",
                    arguments=str({"username": "laimonisdumins"}),
                ),
                FunctionCallContent(
                    name="User-get_user_allergies",
                    id="0002",
                    arguments=str({"username": "emavargova"}),
                ),
            ],
        )
    )

    # Add function results (tool responses)
    chat_history.add_message(
        ChatMessageContent(
            role=AuthorRole.TOOL,
            items=[
                FunctionResultContent(
                    name="User-get_user_allergies",
                    id="0001",
                    result='{ "allergies": ["peanuts", "gluten"] }',
                )
            ],
        )
    )
    chat_history.add_message(
        ChatMessageContent(
            role=AuthorRole.TOOL,
            items=[
                FunctionResultContent(
                    name="User-get_user_allergies",
                    id="0002",
                    result='{ "allergies": ["dairy", "gluten"] }',
                )
            ],
        )
    )

    chat_history.add_assistant_message(
        "Laimonisdumins has allergies to peanuts and gluten. Emavargova has allergies to dairy and gluten."
    )

    thread = ChatHistoryAgentThread(chat_history)

    # Act
    await SKAgentConverter._get_thread_turn_indices(thread)
    messages = await SKAgentConverter._get_messages_from_thread(thread)
    turns = SKAgentConverter._extract_turns_from_messages(
        messages, turn_index_to_stop=2
    )

    # Assert number of turns
    assert len(turns) == 3

    # Unpack and validate turns
    turn0_query, turn0_response = turns[0]
    assert len(turn0_query) == 2
    assert len(turn0_response) == 1

    turn1_query, turn1_response = turns[1]
    assert len(turn1_query) == 4
    assert len(turn1_response) == 1

    turn2_query, turn2_response = turns[2]
    assert (
        len(turn2_query) == 6
    )  # Includes system, 3 user queries, 2 assistant responses
    assert (
        len(turn2_response) == 5
    )  # 2 tool calls, 2 tool results, 1 assistant follow-up

    # Print for debug
    print("Turn 2 Query Messages:", [msg.role for msg in turn2_query])
    print("Turn 2 Response Messages:", [msg.role for msg in turn2_response])
