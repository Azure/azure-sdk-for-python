# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get text embeddings for a list of sentences
    using a synchronous client, with an Azure OpenAI (AOAI) endpoint.
    Two types of authentications are shown: key authentication and Entra ID
    authentication.

USAGE:
    1. Update `key_auth` below to `True` for key authentication, or `False` for
       Entra ID authentication.
    2. Update `api_version` (the AOAI REST API version) as needed.
       See the "Data plane - inference" row in the table here for latest AOAI api-version:
       https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs
    3. Set one or two environment variables, depending on your authentication method:
        * AZURE_OPENAI_EMBEDDINGS_ENDPOINT - Your AOAI endpoint URL, with partial path, in the form 
            https://<your-unique-resouce-name>.openai.azure.com/openai/deployments/<your-deployment-name>
            where `your-unique-resource-name` is your globally unique AOAI resource name,
            and `your-deployment-name` is your AI Model deployment name.
            For example: https://your-unique-host.openai.azure.com/openai/deployments/gpt-4o
        * AZURE_OPENAI_EMBEDDINGS_KEY - Your model key (a 32-character string). Keep it secret. This
            is only required for key authentication.
    4. Run the sample:
       python sample_embeddings_azure_openai.py
"""


def sample_embeddings_azure_openai():
    import os
    from azure.ai.inference import EmbeddingsClient

    try:
        endpoint = os.environ["AZURE_OPENAI_EMBEDDINGS_ENDPOINT"]
    except KeyError:
        print("Missing environment variable 'AZURE_OPENAI_EMBEDDINGS_ENDPOINT'")
        print("Set it before running this sample.")
        exit()

    key_auth = True  # Set to True for key authentication, or False for Entra ID authentication.

    if key_auth:
        from azure.core.credentials import AzureKeyCredential

        try:
            key = os.environ["AZURE_OPENAI_EMBEDDINGS_KEY"]
        except KeyError:
            print("Missing environment variable 'AZURE_OPENAI_EMBEDDINGS_KEY'")
            print("Set it before running this sample.")
            exit()

        client = EmbeddingsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(""),  # Pass in an empty value.
            headers={"api-key": key},
            api_version="2024-06-01",  # AOAI api-version. Update as needed.
        )

    else:  # Entra ID authentication
        from azure.identity import DefaultAzureCredential

        client = EmbeddingsClient(
            endpoint=endpoint,
            credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
            credential_scopes=["https://cognitiveservices.azure.com/.default"],
            api_version="2024-06-01",  # AOAI api-version. Update as needed.
        )

    response = client.embed(input=["first phrase", "second phrase", "third phrase"])

    for item in response.data:
        length = len(item.embedding)
        print(
            f"data[{item.index}]: length={length}, [{item.embedding[0]}, {item.embedding[1]}, "
            f"..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
        )


if __name__ == "__main__":
    sample_embeddings_azure_openai()
