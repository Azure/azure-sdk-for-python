# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completions response from
    the service using a synchronous client and structured output. This sample
    directly defines a JSON schema for a cooking recipe, and it sets it as the desired
    `response_format` for a chat completions call asking how to bake a chocolate
    cake.

    Structured output is only supported by some Chat Completions models. This
    sample was run on a GPT-4o model hosted on Azure OpenAI, with api-version
    "2024-08-01-preview".

    If you are targeting a different endpoint (e.g. GitHub Models endpoint,
    Serverless API endpoint, Managed Compute endpoint) the client constructor may
    needs to be modified. See package documentation:
    https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/README.md#key-concepts

USAGE:
    python sample_chat_completions_with_structured_output.py

    Set these two environment variables before running the sample:
    1) AZURE_OPENAI_CHAT_ENDPOINT - Your AOAI endpoint URL, with partial path, in the form
        https://<your-unique-resouce-name>.openai.azure.com/openai/deployments/<your-deployment-name>
        where `your-unique-resource-name` is your globally unique AOAI resource name,
        and `your-deployment-name` is your AI Model deployment name.
        For example: https://your-unique-host.openai.azure.com/openai/deployments/gpt-4o
    2) AZURE_OPENAI_CHAT_KEY - Your model key (a 32-character string). Keep it secret. This
        is only required for key authentication.

    Update `api_version` (the AOAI REST API version) as needed, based on the model documents.
    See also the "Data plane - inference" row in the table here for latest AOAI api-version:
    https://aka.ms/azsdk/azure-ai-inference/azure-openai-api-versions
"""


def sample_chat_completions_with_structured_output():
    import os
    import json

    from typing import Dict, Any
    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import (
        SystemMessage,
        UserMessage,
        JsonSchemaFormat,
    )
    from azure.core.credentials import AzureKeyCredential

    try:
        endpoint = os.environ["AZURE_OPENAI_CHAT_ENDPOINT"]
        key = os.environ["AZURE_OPENAI_CHAT_KEY"]
    except KeyError:
        print("Missing environment variable 'AZURE_OPENAI_CHAT_ENDPOINT' or 'AZURE_OPENAI_CHAT_KEY'")
        print("Set them before running this sample.")
        exit()

    # Defines a JSON schema for a cooking recipe. You would like the AI model to respond in this format.
    json_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "The name of the recipe"},
            "servings": {"type": "integer", "description": "How many servings are in this recipe"},
            "ingredients": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the ingredient",
                        },
                        "quantity": {
                            "type": "string",
                            "description": "The quantity of the ingredient",
                        },
                    },
                    "required": ["name", "quantity"],
                    "additionalProperties": False,
                },
            },
            "steps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "step": {
                            "type": "integer",
                            "description": "Enumerates the step",
                        },
                        "directions": {
                            "type": "string",
                            "description": "Description of the recipe step",
                        },
                    },
                    "required": ["step", "directions"],
                    "additionalProperties": False,
                },
            },
            "prep_time": {
                "type": "integer",
                "description": "Preperation time in minutes",
            },
            "cooking_time": {
                "type": "integer",
                "description": "Cooking time in minutes",
            },
            "notes": {
                "type": "string",
                "description": "Any additional notes related to this recipe",
            },
        },
        "required": ["title", "servings", "ingredients", "steps", "prep_time", "cooking_time", "notes"],
        "additionalProperties": False,
    }

    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
        api_version="2024-08-01-preview",  # Azure OpenAI api-version. See https://aka.ms/azsdk/azure-ai-inference/azure-openai-api-versions
    )

    response = client.complete(
        response_format=JsonSchemaFormat(
            name="Recipe_JSON_Schema",
            schema=json_schema,
            description="Descripes a recipe in details, listing the ingredients, the steps and the time needed to prepare it",
            strict=True,
        ),
        messages=[
            SystemMessage("You are a helpful assistant."),
            UserMessage("Please give me directions and ingredients to bake a chocolate cake."),
        ],
    )

    # Parse the JSON string response and print it in a nicely formatted way
    json_response_message = json.loads(response.choices[0].message.content)
    print(json.dumps(json_response_message, indent=4))


if __name__ == "__main__":
    sample_chat_completions_with_structured_output()
