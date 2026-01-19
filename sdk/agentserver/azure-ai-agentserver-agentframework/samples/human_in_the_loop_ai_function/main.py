# Copyright (c) Microsoft. All rights reserved.

import asyncio
from typing import Annotated, Any, Collection
from dotenv import load_dotenv

load_dotenv()

from agent_framework import ChatAgent, ChatMessage, ChatMessageStoreProtocol, ai_function
from agent_framework._threads import ChatMessageStoreState
from agent_framework.azure import AzureOpenAIChatClient

from azure.ai.agentserver.agentframework import from_agent_framework
from azure.ai.agentserver.agentframework.persistence.agent_thread_repository import JsonLocalFileAgentThreadRepository

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


async def main() -> None:
    agent = build_agent()
    thread_repository = JsonLocalFileAgentThreadRepository(agent=agent, storage_path="./thread_storage")
    await from_agent_framework(agent, thread_repository=thread_repository).run_async()

if __name__ == "__main__":
    asyncio.run(main())
