# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completions streaming response from
    the service using an asynchronous client, with an Azure OpenAI (AOAI) endpoint.
    Two types of authentications are shown: key authentication and Entra ID
    authentication.

USAGE:
    1. Update `key_auth` below to `True` for key authentication, or `False` for
       Entra ID authentication.
    2. Update `api_version` (the AOAI REST API version) as needed.
       See the "Data plane - inference" row in the table here for latest AOAI api-version:
       https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs
    3. Set one or two environment variables, depending on your authentication method:
        * AZURE_OPENAI_CHAT_ENDPOINT - Your AOAI endpoint URL, with partial path, in the form
            https://<your-unique-resouce-name>.openai.azure.com/openai/deployments/<your-deployment-name>
            where `your-unique-resource-name` is your globally unique AOAI resource name,
            and `your-deployment-name` is your AI Model deployment name.
            For example: https://your-unique-host.openai.azure.com/openai/deployments/gpt-4o
        * AZURE_OPENAI_CHAT_KEY - Your model key (a 32-character string). Keep it secret. This
            is only required for key authentication.
    4. Run the sample:
       python sample_chat_completions_streaming_azure_openai_async.py
"""
import asyncio


async def sample_chat_completions_streaming_azure_openai_async():
    import os
    from azure.ai.inference.aio import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage

    try:
        endpoint = os.environ["AZURE_OPENAI_CHAT_ENDPOINT"]
    except KeyError:
        print("Missing environment variable 'AZURE_OPENAI_CHAT_ENDPOINT'")
        print("Set it before running this sample.")
        exit()

    key_auth = True  # Set to True for key authentication, or False for Entra ID authentication.

    if key_auth:
        from azure.core.credentials import AzureKeyCredential

        try:
            key = os.environ["AZURE_OPENAI_CHAT_KEY"]
        except KeyError:
            print("Missing environment variable 'AZURE_OPENAI_CHAT_KEY'")
            print("Set it before running this sample.")
            exit()

        client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(""),  # Pass in an empty value.
            headers={"api-key": key},
            api_version="2024-06-01",  # AOAI api-version. Update as needed.
        )

    else:  # Entra ID authentication
        from azure.identity import DefaultAzureCredential

        client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
            credential_scopes=["https://cognitiveservices.azure.com/.default"],
            api_version="2024-06-01",  # AOAI api-version. Update as needed.
        )

    response = await client.complete(
        stream=True,
        messages=[
            SystemMessage(content="You are a helpful assistant."),
            UserMessage(content="Give me 5 good reasons why I should exercise every day."),
        ],
    )

    # Iterate on the response to get chat completion updates, as they arrive from the service
    async for update in response:
        if len(update.choices) > 0:
            print(update.choices[0].delta.content or "", end="", flush=True)

    await client.close()


async def main():
    await sample_chat_completions_streaming_azure_openai_async()


if __name__ == "__main__":
    asyncio.run(main())
