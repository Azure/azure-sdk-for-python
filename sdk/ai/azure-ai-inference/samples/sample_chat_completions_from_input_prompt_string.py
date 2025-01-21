# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completions response from
    the service using a synchronous client, with input message template
    in string format.

    This sample assumes the AI model is hosted on a Serverless API or
    Managed Compute endpoint. For GitHub Models or Azure OpenAI endpoints,
    the client constructor needs to be modified. See package documentation:
    https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/README.md#key-concepts

USAGE:
    python sample_chat_completions_from_input_prompt_string.py

    Set these two environment variables before running the sample:
    1) AZURE_AI_CHAT_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.models.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) AZURE_AI_CHAT_KEY - Your model key (a 32-character string). Keep it secret.
"""
# pyright: reportAttributeAccessIssue=false


def sample_chat_completions_from_input_prompt_string():
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

    client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    response = client.complete(messages=messages)

    print(response.choices[0].message.content)


if __name__ == "__main__":
    sample_chat_completions_from_input_prompt_string()
