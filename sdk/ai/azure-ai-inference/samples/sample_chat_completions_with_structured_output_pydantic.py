# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completions response from
    the service using a synchronous client and structured output. This sample
    indirectly defines a JSON schema for a cooking recipe, by first defining a set of
    classes and then using the Pydantic package to create a JSON schema from those classes.
    Then it sets the JSON schema as the desired `response_format` for a chat completions
    call asking how to bake a chocolate cake.

    Structured output is only supported by some Chat Completions models. This
    sample was run on a GPT-4o model hosted on Azure OpenAI, with api-version
    "2024-08-01-preview".

    If you are targeting a different endpoint (e.g. GitHub Models endpoint,
    Serverless API endpoint, Managed Compute endpoint) the client constructor may
    needs to be modified. See package documentation:
    https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/README.md#key-concepts

USAGE:
    pip install pydantic
    python sample_chat_completions_with_structured_output_pydantic.py

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


def sample_chat_completions_with_structured_output_pydantic():
    import os
    import json

    from pydantic import BaseModel, ConfigDict, Field
    from typing import List
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

    # These classes define the structure of a cooking recipe.
    # For more information, see https://docs.pydantic.dev/latest/concepts/json_schema/
    class CookingIngredient(BaseModel):
        model_config = ConfigDict(extra="forbid")
        name: str
        quantity: str

    class CookingStep(BaseModel):
        model_config = ConfigDict(extra="forbid")
        step: int
        directions: str

    class CookingRecipe(BaseModel):
        model_config = ConfigDict(extra="forbid")
        title: str
        servings: int
        prep_time: int = Field(
            description="Preperation time in minutes",
        )
        cooking_time: int = Field(
            description="Cooking time in minutes",
        )
        ingredients: List[CookingIngredient]
        steps: List[CookingStep]
        notes: str

    # Use Pydantic package to convert the above classes to a JSON schema, which you would like the AI model to adhere to.
    json_schema = CookingRecipe.model_json_schema()
    print(f"json_schema = {json.dumps(json_schema, indent=4)}")

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
    print(f"json_response_message = {json.dumps(json_response_message, indent=4)}")


if __name__ == "__main__":
    sample_chat_completions_with_structured_output_pydantic()
