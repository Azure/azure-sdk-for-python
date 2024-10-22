# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completions response from
    the service using a synchronous client, and directly providing the 
    input in Prompty format from a Prompty file. Prompty website: https://prompty.ai

    This sample assumes the AI model is hosted on a Serverless API or
    Managed Compute endpoint. For GitHub Models or Azure OpenAI endpoints,
    the client constructor needs to be modified. See package documentation:
    https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/README.md#key-concepts

USAGE:
    python sample_chat_completions_from_input_prompty.py

    Set these two environment variables before running the sample:
    1) AZURE_AI_CHAT_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.models.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) AZURE_AI_CHAT_KEY - Your model key (a 32-character string). Keep it secret.
"""
# mypy: disable-error-code="union-attr"
# pyright: reportAttributeAccessIssue=false


def sample_chat_completions_from_input_prompty():
    import os
    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.prompts import PromptTemplate
    from azure.core.credentials import AzureKeyCredential

    try:
        endpoint = os.environ["AZURE_AI_CHAT_ENDPOINT"]
        key = os.environ["AZURE_AI_CHAT_KEY"]
    except KeyError:
        print("Missing environment variable 'AZURE_AI_CHAT_ENDPOINT' or 'AZURE_AI_CHAT_KEY'")
        print("Set them before running this sample.")
        exit()


    path = "./sample1.prompty"
    prompt_template = PromptTemplate.from_prompty(file_path=path)

    input_variables = {
        "input": "What's the checkin and checkout time?",
        "rules": [
            { "rule": "The checkin time is 3pm" },
            { "rule": "The checkout time is 11am" },
            { "rule": "Breakfast is served from 7am to 10am" },
        ],
    }

    messages = prompt_template.render(input_variables=input_variables)

    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    response = client.complete(
        messages=messages,
        model=prompt_template.model_name,
        **prompt_template.config,
    )

    print(response.choices[0].message.content)


if __name__ == "__main__":
    sample_chat_completions_from_input_prompty()
