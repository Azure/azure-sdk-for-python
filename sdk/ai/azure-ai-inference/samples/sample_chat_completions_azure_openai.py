# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completions response from
    the service using a synchronous client, using an Azure OpenAI endpoint.

USAGE:
    python sample_chat_completions_azure_openai.py

    Set these two environment variables before running the sample:
    1) AOAI_CHAT_COMPLETIONS_ENDPOINT - Your endpoint URL, in the form 
        https://<your-unique-label>.openai.azure.com/openai/deployments/<your-deployment-name>
        where `your-deployment-name` is your unique AI Model deployment name.
        For example: https://my-unique-label.openai.azure.com/openai/deployments/gpt-4-turbo
    2) AOAI_CHAT_COMPLETIONS_KEY - Your model key (a 32-character string). Keep it secret.
"""


def sample_chat_completions_azure_openai():
    import os

    import sys
    import logging
    logger = logging.getLogger("azure")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))
    #logger.addHandler(logging.FileHandler(filename = "c:\\temp\\sample.log"))

    try:
        endpoint = os.environ["AOAI_CHAT_COMPLETIONS_ENDPOINT"]
        key = os.environ["AOAI_CHAT_COMPLETIONS_KEY"]
    except KeyError:
        print("Missing environment variable 'AOAI_CHAT_COMPLETIONS_ENDPOINT' or 'AOAI_CHAT_COMPLETIONS_KEY'")
        print("Set them before running this sample.")
        exit()

    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage

    # Using key auth
    # from azure.core.credentials import AzureKeyCredential
    # client = ChatCompletionsClient(
    #     endpoint=endpoint, 
    #     credential=AzureKeyCredential(""), # Pass in a dummy or empty value, as `credential` is a mandatory parameter
    #     headers={"api-key": key}, # AOAI uses this header for key auth. MaaS/MaaP uses "Authorization" header.
    #     api_version="2024-02-15-preview", logging_enable = True) # MaaS/MaaP uses "2024-05-01-preview"

    # Using Entra ID auth
    from azure.identity import DefaultAzureCredential
    client = ChatCompletionsClient(
        endpoint=endpoint, 
        credential=DefaultAzureCredential(),
        credential_scopes=["https://cognitiveservices.azure.com/.default"], # MaaS/MaaP uses https://ml.azure.com/.default
        api_version="2024-02-15-preview", # MaaS/MaaP uses "2024-05-01-preview"
        logging_enable = True)

    response = client.complete(
        messages=[
            SystemMessage(content="You are a helpful assistant."),
            UserMessage(content="How many feet are in a mile?"),
        ]
    )

    print(response.choices[0].message.content)


if __name__ == "__main__":
    sample_chat_completions_azure_openai()
