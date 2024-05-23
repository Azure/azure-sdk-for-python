# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completions response from
    the service using a synchronous client, while supplying additional
    model-specific parameters as part of the request.
    See setting of an optional `unknown-parameters` request header via the
    `headers_policy` in the client constructor.
    See setting of `hyper_params` in the `complete` method.

USAGE:
    python sample_chat_completions_with_hyper_params.py

    Set these two environment variables before running the sample:
    1) CHAT_COMPLETIONS_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.inference.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) CHAT_COMPLETIONS_KEY - Your model key (a 32-character string). Keep it secret.
"""


def sample_chat_completions_with_hyper_params():
    import os

    try:
        endpoint = os.environ["CHAT_COMPLETIONS_ENDPOINT"]
        key = os.environ["CHAT_COMPLETIONS_KEY"]
    except KeyError:
        print("Missing environment variable 'CHAT_COMPLETIONS_ENDPOINT' or 'CHAT_COMPLETIONS_KEY'")
        print("Set them before running this sample.")
        exit()

    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage, UnknownParams
    from azure.core.credentials import AzureKeyCredential

    client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    # [START hyper_params]
    response = client.complete(
        messages=[
            SystemMessage(content="You are a helpful assistant."),
            UserMessage(content="How many feet are in a mile?"),
        ],
        unknown_params=UnknownParams.ALLOW,  # Optional. Supported values: "ALLOW", "IGNORE", "ERROR" (service default)
        hyper_params={  # Optional. Additional parameters to pass to the model.
            "key1": 1,
            "key2": True,
            "key3": "Some value",
            "key4": [1, 2, 3],
            "key5": {"key6": 2, "key7": False, "key8": "Some other value", "key9": [4, 5, 6, 7]},
        },
    )
    # [END chat_completions]

    print(response.choices[0].message.content)


if __name__ == "__main__":
    sample_chat_completions_with_hyper_params()
