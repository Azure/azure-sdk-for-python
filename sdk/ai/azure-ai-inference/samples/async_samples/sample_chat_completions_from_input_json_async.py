# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completions response from
    the service using an asynchronous client, and directly providing the 
    JSON request body (containing input chat messages).

    This sample assumes the AI model is hosted on a Serverless API or
    Managed Compute endpoint. For GitHub Models or Azure OpenAI endpoints,
    the client constructor needs to be modified. See package documentation:
    https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/README.md#key-concepts

USAGE:
    python sample_chat_completions_from_input_json_async.py

    Set these two environment variables before running the sample:
    1) AZURE_AI_CHAT_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.models.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) AZURE_AI_CHAT_KEY - Your model key (a 32-character string). Keep it secret.
"""
# mypy: disable-error-code="union-attr"
# pyright: reportAttributeAccessIssue=false

import asyncio


async def sample_chat_completions_from_input_json_async():
    import os
    from azure.ai.inference.aio import ChatCompletionsClient
    from azure.core.credentials import AzureKeyCredential

    try:
        endpoint = os.environ["AZURE_AI_CHAT_ENDPOINT"]
        key = os.environ["AZURE_AI_CHAT_KEY"]
    except KeyError:
        print("Missing environment variable 'AZURE_AI_CHAT_ENDPOINT' or 'AZURE_AI_CHAT_KEY'")
        print("Set them before running this sample.")
        exit()

    async with ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key)) as client:

        request_body = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an AI assistant that helps people find information. Your replies are short, no more than two sentences.",
                },
                {
                    "role": "user",
                    "content": "What year was construction of the International Space Station mostly done?",
                },
                {
                    "role": "assistant",
                    "content": "The main construction of the International Space Station (ISS) was completed between 1998 and 2011. During this period, more than 30 flights by US space shuttles and 40 by Russian rockets were conducted to transport components and modules to the station.",
                },
                {
                    "role": "user",
                    "content": "And what was the estimated cost to build it?"
                },
            ]
        }

        response = await client.complete(request_body)

        print(response.choices[0].message.content)


async def main():
    await sample_chat_completions_from_input_json_async()


if __name__ == "__main__":
    asyncio.run(main())
