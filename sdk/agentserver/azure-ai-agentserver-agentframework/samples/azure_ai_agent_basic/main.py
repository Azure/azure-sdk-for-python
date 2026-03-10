# Copyright (c) Microsoft. All rights reserved.

import asyncio

import asyncio
from random import randint
from typing import Annotated

from agent_framework.azure import AzureAIClient
from azure.identity import DefaultAzureCredential
from pydantic import Field

from dotenv import load_dotenv
load_dotenv()

from azure.ai.agentserver.agentframework import from_agent_framework

"""
Azure AI Agent Basic Example

This sample demonstrates basic usage of AzureAIAgentsProvider to create agents with automatic
lifecycle management. Shows both streaming and non-streaming responses with function tools.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


def main() -> None:
    agent = AzureAIClient(credential=DefaultAzureCredential()).create_agent(
            name="BasicWeatherAgent",
            instructions="You are a helpful weather agent.",
            tools=get_weather)

    from_agent_framework(agent).run()

    
if __name__ == "__main__":
    main()