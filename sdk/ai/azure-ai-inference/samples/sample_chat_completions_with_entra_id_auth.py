# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completions response from the service using a synchronous client,
    with Entra ID authentication.

PREREQUISITES:
    1) An AI model deployed to an "AI Services" resource, in your AI Foundry Project, using Entra ID authentication.
    2) You have the "Cognitive Services User" role assigned to you in the "AI Service" resource. Do that in your
       Azure portal (https://portal.azure.com/), under the "Access control (IAM)" tab of your "AI Service" resource.

USAGE:
    Set these two environment variables before running the sample:

    1) AZURE_AI_CHAT_ENDPOINT - Your endpoint URL for model inference, in the form 
       "https://<your-ai-services-resouce-name>.services.ai.azure.com/models".
       This URL is shown in the model card page in your AI Foundry project: Click on "Models + endpoints" tab,
       then click on the relevant model name to open the model card page. Copy the URL up to and including the
       "/models" route.
       
    2) AZURE_AI_CHAT_MODEL_DEPLOYMENT_NAME - Your model deployment name, as appears under the "Name"
       in the "Deployment info" section of the model card page. Note that this may be different than the
       "Model name" shown in the card.

    Open a console window and make sure you have latest version of "az" CLI installed.
    See https://learn.microsoft.com/cli/azure/install-azure-cli

    Run "az login" and pick the subscription/tenant that was used by your AI Foundry project.

    Now run the sample:
        python sample_chat_completions_with_entra_id_auth.py
"""


def sample_chat_completions_with_entra_id_auth():
    import os

    try:
        endpoint = os.environ["AZURE_AI_CHAT_ENDPOINT"]
        model_deployment_name = os.environ["AZURE_AI_CHAT_MODEL_DEPLOYMENT_NAME"]
    except KeyError:
        print("Missing environment variable 'AZURE_AI_CHAT_ENDPOINT' or 'AZURE_AI_CHAT_MODEL_DEPLOYMENT_NAME'")
        print("Set them before running this sample.")
        exit()

    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage
    from azure.identity import DefaultAzureCredential

    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
        credential_scopes=["https://cognitiveservices.azure.com/.default"],
    )

    response = client.complete(
        messages=[
            SystemMessage("You are a helpful assistant."),
            UserMessage("How many feet are in a mile?"),
        ],
        model=model_deployment_name,
    )

    print(response.choices[0].message.content)


if __name__ == "__main__":
    sample_chat_completions_with_entra_id_auth()
