# Copyright (c) Microsoft. All rights reserved.

import asyncio
from typing import Annotated, Any, Collection
from dotenv import load_dotenv
import json

load_dotenv()

from agent_framework import ChatAgent, ChatMessage, ChatMessageStoreProtocol, FunctionResultContent, ai_function
from agent_framework._threads import ChatMessageStoreState
from agent_framework._types import UserInputRequestContents
from agent_framework.azure import AzureOpenAIChatClient

from azure.ai.agentserver.agentframework import from_agent_framework
from azure.ai.agentserver.agentframework.models.agent_thread_repository import JsonSerializedAgentThreadRepository, FileStorage

"""
Tool Approvals with Threads

This sample demonstrates using tool approvals with threads.
With threads, you don't need to manually pass previous messages -
the thread stores and retrieves them automatically.
"""


class CustomChatMessageStore(ChatMessageStoreProtocol):
    """Implementation of custom chat message store.
    In real applications, this can be an implementation of relational database or vector store."""

    def __init__(self, messages: Collection[ChatMessage] | None = None) -> None:
        self._messages: list[ChatMessage] = []
        if messages:
            self._messages.extend(messages)

    async def add_messages(self, messages: Collection[ChatMessage]) -> None:
        self._messages.extend(messages)

    async def list_messages(self) -> list[ChatMessage]:
        return self._messages

    @classmethod
    async def deserialize(cls, serialized_store_state: Any, **kwargs: Any) -> "CustomChatMessageStore":
        """Create a new instance from serialized state."""
        store = cls()
        await store.update_from_state(serialized_store_state, **kwargs)
        return store

    async def update_from_state(self, serialized_store_state: Any, **kwargs: Any) -> None:
        """Update this instance from serialized state."""
        if serialized_store_state:
            state = ChatMessageStoreState.from_dict(serialized_store_state, **kwargs)
            if state.messages:
                self._messages.extend(state.messages)

    async def serialize(self, **kwargs: Any) -> Any:
        """Serialize this store's state."""
        state = ChatMessageStoreState(messages=self._messages)
        return state.to_dict(**kwargs)


@ai_function(approval_mode="always_require")
def add_to_calendar(
    event_name: Annotated[str, "Name of the event"], date: Annotated[str, "Date of the event"]
) -> str:
    """Add an event to the calendar (requires approval)."""
    print(f">>> EXECUTING: add_to_calendar(event_name='{event_name}', date='{date}')")
    return f"Added '{event_name}' to calendar on {date}"


def build_agent():
    return ChatAgent(
        chat_client=AzureOpenAIChatClient(),
        name="CalendarAgent",
        instructions="You are a helpful calendar assistant.",
        tools=[add_to_calendar],
        chat_message_store_factory=CustomChatMessageStore,
    )

async def run_agent() -> None:
    """Example showing approval with threads."""
    print("=== Tool Approval with Thread ===\n")

    agent = build_agent()
    
    thread = agent.get_new_thread()
    thread_id = thread.service_thread_id
    # Step 1: Agent requests to call the tool
    query = "Add a dentist appointment on March 15th"
    print(f"User: {query}")
    result = await agent.run(query, thread=thread)
    serialized_thread = await thread.serialize()
    print(f"Agent: {result.to_dict()}")
    print(f"Thread: {serialized_thread}\n\n")

    resume_thread = await agent.deserialize_thread(serialized_thread)
    res = await resume_thread.message_store.list_messages()
    print(f"Resumed thread messages: {res}")
    for message in res:
        print(f"  Thread message {type(message)}: {message.to_dict()}")
        for content in message.contents:
            print(f"    Content {type(content)}: {content.to_dict()}")

    # Check for approval requests
    if result.user_input_requests:
        for request in result.user_input_requests:
            print("\nApproval needed:")
            print(f"  Function: {request.function_call.name}")
            print(f"  Arguments: {request.function_call.arguments}")
            print(f"  type: {type(request.function_call)}")
            print(f"  function arg type: {type(request.function_call.arguments)}")

            # User approves (in real app, this would be user input)
            approved = True  # Change to False to see rejection
            print(f"  Decision: {'Approved' if approved else 'Rejected'}")

            # Step 2: Send approval response
            # approval_response = request.create_response(approved=approved)
            #response_message = ChatMessage(role="user", contents=[approval_response])
            approval_response = FunctionResultContent(
                call_id = request.function_call.call_id,
                result="denied",
            )
            response_message = ChatMessage(role="tool", contents=[approval_response])
            result = await agent.run(response_message, thread=resume_thread)

    print(f"Agent: {result}\n")


async def main() -> None:
    agent = build_agent()
    thread_repository = JsonSerializedAgentThreadRepository(
        storage=FileStorage(storage_path="./thread_storage")
    )
    await from_agent_framework(agent, thread_repository=thread_repository).run_async()

if __name__ == "__main__":
    asyncio.run(main())
    # asyncio.run(run_agent())