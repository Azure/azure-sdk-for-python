# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completions response from the service. Two completion
    calls are made, the second one containing the chat history from the first one. We convert responses 
    to a dictionary from an Azure OpenAI (AOAI) endpoint using a synchronous client. A dictionary format
    is often required for code reusability, API compatibility, readability and serialization. Two types
    of authentications are shown: key authentication and Entra ID authentication.

USAGE:
    python sample_chat_completions_azure_openai_with_history_and_dictionary.py

    Set these two environment variables before running the sample:
    1. AZURE_AI_CHAT_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.inference.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2. AZURE_AI_CHAT_KEY - Your model key (a 32-character string). Keep it secret.
    3. Set one or two environment variables, depending on your authentication method:
        * AZURE_OPENAI_CHAT_ENDPOINT - Your AOAI endpoint URL, with partial path, in the form 
            https://<your-unique-resouce-name>.openai.azure.com/openai/deployments/<your-deployment-name>
            where `your-unique-resource-name` is your globally unique AOAI resource name,
            and `your-deployment-name` is your AI Model deployment name.
            For example: https://your-unique-host.openai.azure.com/openai/deployments/gpt-4-turbo
        * AZURE_OPENAI_CHAT_KEY - Your model key (a 32-character string). Keep it secret. This
            is only required for key authentication.
    4. Run the sample:
       python sample_chat_completions_azure_openai_with_history_and_dictionary.py
"""


def sample_chat_completions_azure_openai_with_history_and_dictionary():
    import json
    import os
    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
    from azure.core.credentials import AzureKeyCredential

    try:
        endpoint = os.environ["AZURE_AI_CHAT_ENDPOINT"]
    except KeyError:
        print(
            "Missing environment variable 'AZURE_AI_CHAT_ENDPOINT' or 'AZURE_AI_CHAT_KEY'"
        )
        print("Set them before running this sample.")
        exit()

    key_auth = True  # Set to True for key authentication, or False for Entra ID authentication.

    if key_auth:
        try:
            key = os.environ["AZURE_AI_CHAT_KEY"]
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

        # Initialize a list of messages with a system message and a user message
        messages = [
            SystemMessage(
                content="You are an AI assistant that helps people find information. Your replies are short, no more than two sentences."
            ),
            UserMessage(
                content="What year was construction of the international space station mostly done?"
            ),
        ]

        # Convert messages to dictionaries before passing to openai_client
        response = openai_client.complete(messages=[msg.as_dict() for msg in messages])

        # Append the assistant's response to the messages list
        messages.append(
            AssistantMessage(content=response.choices[0].message["content"])
        )
        messages.append(
            UserMessage(content="And what was the estimated cost to build it?")
        )

        # Convert messages to dictionaries before passing to openai_client
        response = openai_client.complete(messages=[msg.as_dict() for msg in messages])
        messages.append(
            AssistantMessage(content=response.choices[0].message["content"])
        )

        # Convert messages to dictionaries before printing JSON
        print(json.dumps([msg.as_dict() for msg in messages], indent=2))

    else:  # Entra ID authentication
        from azure.identity import DefaultAzureCredential

        client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=DefaultAzureCredential(
                exclude_interactive_browser_credential=False
            ),
            credential_scopes=["https://cognitiveservices.azure.com/.default"],
            api_version="2024-06-01",  # AOAI api-version. Update as needed.
        )
        # Initialize a list of messages with a system message and a user message
        messages = [
            SystemMessage(
                content="You are an AI assistant that helps people find information. Your replies are short, no more than two sentences."
            ),
            UserMessage(
                content="What year was construction of the international space station mostly done?"
            ),
        ]

        # Convert messages to dictionaries before passing to openai_client
        response = openai_client.complete(messages=[msg.as_dict() for msg in messages])

        # Append the assistant's response to the messages list
        messages.append(
            AssistantMessage(content=response.choices[0].message["content"])
        )
        messages.append(
            UserMessage(content="And what was the estimated cost to build it?")
        )

        # Convert messages to dictionaries before passing to openai_client
        response = openai_client.complete(messages=[msg.as_dict() for msg in messages])
        messages.append(
            AssistantMessage(content=response.choices[0].message["content"])
        )

        # Convert messages to dictionaries before printing JSON
        print(json.dumps([msg.as_dict() for msg in messages], indent=2))


if __name__ == "__main__":
    sample_chat_completions_azure_openai_with_history_and_dictionary()