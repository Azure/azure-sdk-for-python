# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completions response from
    the service using a synchronous client, and directly providing the
    JSON request body (containing input chat messages). The sample
    shows how to include an image URL in the input chat messages.
    This sample will only work on AI models that support image input.
    Only these AI models accept the array form of `content` in the
    `UserMessage`, as shown here.

USAGE:
    python sample_chat_completions_from_input_json_with_image_url.py

    Set these two or three environment variables before running the sample:
    1) AZURE_AI_CHAT_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.inference.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) AZURE_AI_CHAT_KEY - Your model key (a 32-character string). Keep it secret.
    3) AZURE_AI_CHAT_DEPLOYMENT_NAME - Optional. The value for the HTTP
        request header `azureml-model-deployment`.
"""
# mypy: disable-error-code="union-attr"
# pyright: reportAttributeAccessIssue=false


def sample_chat_completions_from_input_json_with_image_url():
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

    try:
        model_deployment = os.environ["AZURE_AI_CHAT_DEPLOYMENT_NAME"]
    except KeyError:
        print("Could not read optional environment variable `AZURE_AI_CHAT_DEPLOYMENT_NAME`.")
        print("HTTP request header `azureml-model-deployment` will not be set.")
        model_deployment = None

    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
        headers={"azureml-model-deployment": model_deployment}
    )

    response = client.complete(
        {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an AI assistant that describes images in details",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What's in this image?"
                        },
                        {
                            "type": "image_url", 
                            "image_url": {
                                "url" : "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/ai/azure-ai-inference/samples/sample1.png",
                                "detail": "high",
                            },
                        },
                    ],
                },
            ]
        }
    )

    print(response.choices[0].message.content)


if __name__ == "__main__":
    sample_chat_completions_from_input_json_with_image_url()
