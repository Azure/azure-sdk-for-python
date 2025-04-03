# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated 
    async ChatCompletionsClient from the azure.ai.inference package, and then work with Prompty.
    For more information on the azure.ai.inference package see https://pypi.org/project/azure-ai-inference/.

USAGE:
    python sample_chat_completions_with_azure_ai_inference_client_and_prompty.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    * PROJECT_CONNECTION_STRING - The Azure AI Project connection string, as found in your AI Foundry project.
    * MODEL_DEPLOYMENT_NAME - The model deployment name, as found in your AI Foundry project.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.prompts import PromptTemplate
from azure.ai.inference.models import UserMessage
from azure.identity import DefaultAzureCredential

project_connection_string = os.environ["PROJECT_CONNECTION_STRING"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

with AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=project_connection_string,
) as project_client:

    with project_client.inference.get_chat_completions_client() as client:

        path = "./sample1.prompty"
        prompt_template = PromptTemplate.from_prompty(file_path=path)

        input = "When I arrived, can I still have breakfast?"
        rules = [
            {"rule": "The check-in time is 3pm"},
            {"rule": "The check-out time is 11am"},
            {"rule": "Breakfast is served from 7am to 10am"},
        ]
        chat_history = [
            {"role": "user", "content": "I'll arrive at 2pm. What's the check-in and check-out time?"},
            {"role": "system", "content": "The check-in time is 3 PM, and the check-out time is 11 AM."},
        ]
        messages = prompt_template.create_messages(input=input, rules=rules, chat_history=chat_history)

        response = client.complete(model=model_deployment_name, messages=messages)

        print(response.choices[0].message.content)
