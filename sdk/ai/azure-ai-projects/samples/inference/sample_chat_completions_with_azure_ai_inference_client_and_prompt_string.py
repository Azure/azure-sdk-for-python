# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to
    * Get an authenticated ChatCompletionsClient from the azure.ai.inference package
    * Define a Mustache template, and render the template with provided parameters to create a list of chat messages.
    * Perform one chat completion operation.
    Package azure.ai.inference required. For more information see https://pypi.org/project/azure-ai-inference/.
    Package prompty required. For more information see https://pypi.org/project/prompty/.

USAGE:
    sample_chat_completions_with_azure_ai_inference_client_and_prompt_string.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-inference azure-identity prompty

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The AI model deployment name, as found in your AI Foundry project.
"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient, PromptTemplate

endpoint = os.environ["PROJECT_ENDPOINT"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

with DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential:

    with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:

        with project_client.inference.get_chat_completions_client() as client:

            prompt_template_str = """
                system:
                You are an AI assistant in a hotel. You help guests with their requests and provide information about the hotel and its services.

                # context
                {{#rules}}
                {{rule}}
                {{/rules}}

                {{#chat_history}}
                {{role}}:
                {{content}}
                {{/chat_history}}

                user:
                {{input}}
            """
            prompt_template = PromptTemplate.from_string(api="chat", prompt_template=prompt_template_str)

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
            print(messages)

            response = client.complete(model=model_deployment_name, messages=messages)

            print(response.choices[0].message.content)
