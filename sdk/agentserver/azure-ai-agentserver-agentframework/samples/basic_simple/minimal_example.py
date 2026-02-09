# Copyright (c) Microsoft. All rights reserved.

from random import randint
from typing import Annotated

from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential   
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultTokenCredential
from dotenv import load_dotenv
load_dotenv()

from azure.ai.agentserver.agentframework import from_agent_framework
from azure.ai.agentserver.agentframework.persistence._foundry_thread_repository import FoundryConversationThreadRepository



def get_weather(
    location: Annotated[str, "The location to get the weather for."],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


def main() -> None:
    agent = AzureOpenAIChatClient(credential=DefaultAzureCredential()).create_agent(
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )
    repo = FoundryConversationThreadRepository(
        agent=agent,
        project_endpoint="https://lusuaihub5218927825.cognitiveservices.azure.com/",
        credential=AsyncDefaultTokenCredential())
    from_agent_framework(agent, thread_repository=None).run()


if __name__ == "__main__":
    main()
