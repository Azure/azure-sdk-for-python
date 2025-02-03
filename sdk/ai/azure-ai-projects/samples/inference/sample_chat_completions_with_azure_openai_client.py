# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated 
    AsyncAzureOpenAI client from the azure.ai.inference package.

USAGE:
    python sample_chat_completions_with_azure_openai_client.py

    Before running the sample:

    pip install azure-ai-projects openai

    Set these environment variables with your own values:
    * PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
    * MODEL_DEPLOYMENT_NAME - The model deployment name, as found in your AI Foundry project.

    Update the Azure OpenAI api-version as needed (see `api_version=` below). Values can be found here:
    https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs
"""
import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from user_functions import user_functions
from dotenv import load_dotenv

load_dotenv()

project_connection_string = os.environ["PROJECT_CONNECTION_STRING"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                },
                "required": ["location", "format"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_n_day_weather_forecast",
            "description": "Get an N-day weather forecast",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                    "num_days": {
                        "type": "integer",
                        "description": "The number of days to forecast",
                    }
                },
                "required": ["location", "format", "num_days"]
            },
        }
    },
]

with AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=project_connection_string,
) as project_client:

    with project_client.inference.get_azure_openai_client(api_version="2024-06-01") as client:

        response = client.chat.completions.create(
            model=model_deployment_name,
            messages=[
                {
                    "role": "user",
                    "content": "How is weather in Seattle ? and weather forecast for next 3 days",
                },
            ],
            tools=tools,
        )

        print(response.choices[0].message.content)
