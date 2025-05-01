# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to use Prompty (https://prompty.ai) as model config and
    prompt template, and get the chat completions response from the service using a
    synchronous client.

    This sample assumes the AI model is hosted on a Serverless API or
    Managed Compute endpoint. For GitHub Models or Azure OpenAI endpoints,
    the client constructor needs to be modified. See package documentation:
    https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/README.md#key-concepts

USAGE:
    python sample_chat_completions_with_prompty_file.py

    Set these two environment variables before running the sample:
    1) AZURE_AI_CHAT_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.models.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) AZURE_AI_CHAT_KEY - Your model key. Keep it secret.
"""
# pyright: reportAttributeAccessIssue=false

try:
    from prompty import load, prepare
except ImportError as exc:
    MISSING_PROMPTY_PACKAGE_MESSAGE = "Please install the 'prompty' package by running 'pip install prompty'."
    raise ImportError(MISSING_PROMPTY_PACKAGE_MESSAGE) from exc

def sample_chat_completions_with_prompty_file():
    import os
    from azure.ai.inference import ChatCompletionsClient
    from azure.core.credentials import AzureKeyCredential

    try:
        endpoint = os.environ["AZURE_AI_CHAT_ENDPOINT"]
        key = os.environ["AZURE_AI_CHAT_KEY"]
    except KeyError:
        print("Missing environment variable 'AZURE_AI_CHAT_ENDPOINT' or 'AZURE_AI_CHAT_KEY'")
        print("Set them before running this sample.")
        exit()

    # Load Prompty file
    prompty = load("./sample1.prompty")

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

    client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    # Retrieve the prompt template and model configuration from the Prompty file
    data = {
        "input": input,
        "rules": rules,
        "chat_history": chat_history,
    }
    messages = prepare(prompty, data)
    model_name = prompty.model.configuration["azure_deployment"] if "azure_deployment" in prompty.model.configuration else None

    response = client.complete(
        messages=messages,
        model=model_name,
        **prompty.model.parameters,
    )

    print(response.choices[0].message.content)


if __name__ == "__main__":
    sample_chat_completions_with_prompty_file()
