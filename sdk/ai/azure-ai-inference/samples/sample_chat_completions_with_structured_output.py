# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completions response from
    the service using a synchronous client and structured output. The sample
    defines a JSON schema for a cooking recipe, and it sets it as the desired
    `response_format` for a chat completions call asking how to bake a choclate
    cake.

    This sample assumes the AI model is hosted on a Serverless API or
    Managed Compute endpoint. For GitHub Models or Azure OpenAI endpoints,
    the client constructor needs to be modified. See package documentation:
    https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/README.md#key-concepts

USAGE:
    python sample_chat_completions_with_structured_output.py

    Set these two environment variables before running the sample:
    1) AZURE_AI_CHAT_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.models.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) AZURE_AI_CHAT_KEY - Your model key (a 32-character string). Keep it secret.
"""


def sample_chat_completions_with_structured_output():
    import os
    import json

    from typing import Dict, Any
    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import (
        SystemMessage,
        UserMessage,
        ChatCompletionsResponseFormatJsonSchema,
        ChatCompletionsResponseFormatJsonSchemaDefinition,
    )
    from azure.core.credentials import AzureKeyCredential

    try:
        endpoint = os.environ["AZURE_AI_CHAT_ENDPOINT"]
        key = os.environ["AZURE_AI_CHAT_KEY"]
    except KeyError:
        print("Missing environment variable 'AZURE_AI_CHAT_ENDPOINT' or 'AZURE_AI_CHAT_KEY'")
        print("Set them before running this sample.")
        exit()

    recipe_schema: Dict[str, Any] = {
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
        response_format=ChatCompletionsResponseFormatJsonSchema(
            json_schema=ChatCompletionsResponseFormatJsonSchemaDefinition(
                name="JSON-schema-for-a-recpie",
                schema=recipe_schema,
                description="Descripes a recipe in details, listing the ingredients, the steps and the time needed to prepare it",
                strict=False,
            )
        ),
        messages=[
            SystemMessage(content="You are a helpful assistant. Your responses are in JSON format"),
            UserMessage(content="Please give me directions and ingredients to bake a chocolate cake."),
        ],
    )

    # Parse the JSON string response
    json_data = json.loads(response.choices[0].message.content)

    # Print the JSON data in a nicely formatted way
    print(json.dumps(json_data, indent=4))


if __name__ == "__main__":
    sample_chat_completions_with_structured_output()
