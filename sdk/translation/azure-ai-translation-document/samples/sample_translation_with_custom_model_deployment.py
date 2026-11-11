# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_translation_with_custom_model_deployment.py

DESCRIPTION:
    This sample demonstrates how to route a document translation request through a custom
    translation model by specifying the model's deployment name. The deployment name can be
    supplied for both batch and single document translation. After the operation completes,
    each document's status reports the deployment name that was used.

    To set up your containers for translation and generate SAS tokens to your containers (or files)
    with the appropriate permissions, see the README.

USAGE:
    python sample_translation_with_custom_model_deployment.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key.
    3) AZURE_SOURCE_CONTAINER_URL - the container SAS URL to your source container which has the documents
        to be translated.
    4) AZURE_TARGET_CONTAINER_URL - the container SAS URL to your target container where the translated documents
        will be written.
    5) AZURE_CUSTOM_MODEL_DEPLOYMENT_NAME - the deployment name of your custom translation model.
"""


def sample_translation_with_custom_model_deployment():
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.translation.document import DocumentTranslationClient

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]
    source_container_url = os.environ["AZURE_SOURCE_CONTAINER_URL"]
    target_container_url = os.environ["AZURE_TARGET_CONTAINER_URL"]
    deployment_name = os.environ["AZURE_CUSTOM_MODEL_DEPLOYMENT_NAME"]

    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))

    # Set the deployment name of your custom translation model on the request.
    poller = client.begin_translation(
        source_container_url,
        target_container_url,
        "es",
        deployment_name=deployment_name,
    )
    result = poller.result()

    print(f"Operation status: {poller.details.status}")
    print(f"Total number of translations on documents: {poller.details.documents_total_count}")

    for document in result:
        print(f"Document ID: {document.id}")
        print(f"Document status: {document.status}")
        if document.status == "Succeeded":
            print(f"Translated document location: {document.translated_document_url}")
            print(f"Deployment name used: {document.deployment_name}")
            print(f"Characters charged: {document.characters_charged}\n")
        elif document.error:
            print(f"Error Code: {document.error.code}, Message: {document.error.message}\n")


if __name__ == "__main__":
    sample_translation_with_custom_model_deployment()
