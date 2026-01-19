# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

from azure.ai.agentserver.langgraph import from_langgraph
from azure.ai.agentserver.langgraph.tools import use_foundry_tools

load_dotenv()

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)

memory = MemorySaver()
deployment_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o")
model = AzureChatOpenAI(model=deployment_name, azure_ad_token_provider=token_provider)

foundry_tools = use_foundry_tools([
    {
        # use the python tool to calculate what is 4 * 3.82. and then find its square root and then find the square root of that result
        "type": "code_interpreter"
    },
    {
        # Give me the Azure CLI commands to create an Azure Container App with a managed identity. search Microsoft Learn
        "type": "mcp",
        "project_connection_id": "MicrosoftLearn"
    },
    # {
    #     "type": "mcp",
    #     "project_connection_id": "FoundryMCPServerpreview"
    # }
])


agent_executor = create_agent(model, checkpointer=memory, middleware=[foundry_tools])

if __name__ == "__main__":
    # host the langgraph agent
    from_langgraph(agent_executor).run()
