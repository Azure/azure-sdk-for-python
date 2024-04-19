# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completions response from
    the service using a synchronous client. Two completion calls are made,
    the second one containing the chat history from the first one.

USAGE:
    python sample_chat_completions_with_history.py

    Set these two environment variables before running the sample:
    1) CHAT_COMPLETIONS_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.inference.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) CHAT_COMPLETIONS_KEY - Your model key (a 32-character string). Keep it secret.
"""

def sample_chat_completions_with_history():
    import os

    try:
        endpoint = os.environ["CHAT_COMPLETIONS_ENDPOINT"]
        key = os.environ["CHAT_COMPLETIONS_KEY"]
    except KeyError:
        print("Missing environment variable 'CHAT_COMPLETIONS_ENDPOINT' or 'CHAT_COMPLETIONS_KEY'")
        print("Set them before running this sample.")
        exit()

    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
    from azure.core.credentials import AzureKeyCredential

    client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    messages=[
        SystemMessage(content="You are an AI assistant that helps people find information. Your replies are short, no more than two sentences."),
        UserMessage(content="What year was construction of the international space station mostly done?"),
    ]

    result = client.create(messages=messages)
    print(result.choices[0].message.content)

    messages.append(AssistantMessage(content=result.choices[0].message.content))
    messages.append(UserMessage(content="And what was the estimated cost to build it?"))

    result = client.create(messages=messages)
    print(result.choices[0].message.content)

if __name__ == "__main__":
    sample_chat_completions_with_history()
