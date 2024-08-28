# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to do chat completions with streaming,
    using a synchronous client, with an Entra ID authentication.
    It also shows how to set the optional HTTP request header `azureml-model-deployment`,
    which is supported when you deploy a model using "Managed Compute Endpoints". 
    It can be used to target test deployment during staging,
    instead of the default production deployment.

USAGE:
    python sample_chat_completions_streaming_with_entra_id_auth.py

    Set one or two of these environment variables before running the sample:
    1) AZURE_AI_CHAT_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.models.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) AZURE_AI_CHAT_DEPLOYMENT_NAME - Optional. The value for the HTTP
        request header `azureml-model-deployment`.
"""


def sample_chat_completions_streaming_with_entra_id_auth():
    import os

    try:
        endpoint = os.environ["AZURE_AI_CHAT_ENDPOINT"]
    except KeyError:
        print("Missing environment variable 'AZURE_AI_CHAT_ENDPOINT'")
        print("Set it. before running this sample.")
        exit()

    try:
        model_deployment = os.environ["AZURE_AI_CHAT_DEPLOYMENT_NAME"]
    except KeyError:
        print("Could not read optional environment variable `AZURE_AI_CHAT_DEPLOYMENT_NAME`.")
        print("HTTP request header `azureml-model-deployment` will not be set.")
        model_deployment = None

    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage
    from azure.identity import DefaultAzureCredential

    # For details on DefaultAzureCredential, see
    # https://learn.microsoft.com/python/api/overview/azure/identity-readme#defaultazurecredential

    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
        headers={"azureml-model-deployment": model_deployment},
    )

    response = client.complete(
        stream=True,
        messages=[
            SystemMessage(content="You are a helpful assistant."),
            UserMessage(content="Give me 5 good reasons why I should exercise every day."),
        ],
    )

    for update in response:
        print(update.choices[0].delta.content or "", end="", flush=True)

    client.close()


if __name__ == "__main__":
    sample_chat_completions_streaming_with_entra_id_auth()
