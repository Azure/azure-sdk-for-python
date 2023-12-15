# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_copy_model_to.py

DESCRIPTION:
    This sample demonstrates how to copy a custom model from a source Form Recognizer resource
    to a target Form Recognizer resource.

USAGE:
    python sample_copy_model_to.py

    Set the environment variables with your own values before running the sample:
    1) DOCUMENTINTELLIGENCE_ENDPOINT - the endpoint to your Document Intelligence resource.
    2) DOCUMENTINTELLIGENCE_API_KEY - your Document Intelligence API key.
    3) DOCUMENTINTELLIGENCE_TARGET_ENDPOINT - the endpoint to your target Form Recognizer resource.
    4) DOCUMENTINTELLIGENCE_TARGET_API_KEY - your target Form Recognizer API key
    5) AZURE_SOURCE_MODEL_ID - the model ID from the source resource to be copied over to the target resource.
        - OR -
       DOCUMENTINTELLIGENCE_STORAGE_CONTAINER_SAS_URL - The shared access signature (SAS) Url of your Azure Blob Storage container with your training files.
       A model will be built and used to run the sample.
"""

import os


def sample_copy_model_to(custom_model_id):
    # [START begin_copy_document_model_to]
    import uuid
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documentintelligence import DocumentIntelligenceAdministrationClient
    from azure.ai.documentintelligence.models import AuthorizeCopyRequest

    source_endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
    source_key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]
    target_endpoint = os.environ["DOCUMENTINTELLIGENCE_TARGET_ENDPOINT"]
    target_key = os.environ["DOCUMENTINTELLIGENCE_TARGET_API_KEY"]
    source_model_id = os.getenv("AZURE_SOURCE_MODEL_ID", custom_model_id)

    target_client = DocumentIntelligenceAdministrationClient(
        endpoint=target_endpoint, credential=AzureKeyCredential(target_key)
    )
    target_auth = target_client.authorize_model_copy(
        AuthorizeCopyRequest(
            model_id=str(uuid.uuid4()), # target model ID
            description="copied model",
        )
    )
    source_client = DocumentIntelligenceAdministrationClient(
        endpoint=source_endpoint, credential=AzureKeyCredential(source_key)
    )

    poller = source_client.begin_copy_model_to(
        model_id=source_model_id,
        copy_to_request=target_auth,
    )
    copied_over_model = poller.result()

    print(f"Model ID: {copied_over_model.model_id}")
    print(f"Description: {copied_over_model.description}")
    print(f"Model created on: {copied_over_model.created_date_time}")
    print(f"Model expires on: {copied_over_model.expiration_date_time}")
    print("Doc types the model can recognize:")
    for name, doc_type in copied_over_model.doc_types.items():
        print(f"Doc Type: '{name}' which has the following fields:")
        for field_name, field in doc_type.field_schema.items():
            print(
                f"Field: '{field_name}' has type '{field['type']}' and confidence score "
                f"{doc_type.field_confidence[field_name]}"
            )
    # [END begin_copy_document_model_to]


if __name__ == "__main__":
    from azure.core.exceptions import HttpResponseError
    from dotenv import find_dotenv, load_dotenv

    try:
        load_dotenv(find_dotenv())
        model_id = None
        if os.getenv("DOCUMENTINTELLIGENCE_STORAGE_CONTAINER_SAS_URL") and not os.getenv("AZURE_SOURCE_MODEL_ID"):
            import uuid
            from azure.core.credentials import AzureKeyCredential
            from azure.ai.documentintelligence import DocumentIntelligenceAdministrationClient
            from azure.ai.documentintelligence.models import (
                DocumentBuildMode,
                BuildDocumentModelRequest,
                AzureBlobContentSource,
            )

            endpoint = os.getenv("DOCUMENTINTELLIGENCE_ENDPOINT")
            key = os.getenv("DOCUMENTINTELLIGENCE_API_KEY")

            if not endpoint or not key:
                raise ValueError("Please provide endpoint and API key to run the samples.")

            document_intelligence_admin_client = DocumentIntelligenceAdministrationClient(
                endpoint=endpoint, credential=AzureKeyCredential(key)
            )
            blob_container_sas_url = os.getenv("DOCUMENTINTELLIGENCE_STORAGE_CONTAINER_SAS_URL")
            if blob_container_sas_url is not None:
                request = BuildDocumentModelRequest(
                    model_id=str(uuid.uuid4()),
                    build_mode=DocumentBuildMode.TEMPLATE,
                    azure_blob_source=AzureBlobContentSource(container_url=blob_container_sas_url),
                )
                model = document_intelligence_admin_client.begin_build_document_model(request).result()
                model_id = model.model_id
        sample_copy_model_to(model_id)
    except HttpResponseError as error:
        # Examples of how to check an HttpResponseError
        # Check by error code:
        if error.error is not None:
            if error.error.code == "InvalidImage":
                print(f"Received an invalid image error: {error.error}")
            if error.error.code == "InvalidRequest":
                print(f"Received an invalid request error: {error.error}")
            # Raise the error again after printing it
            raise
        # If the inner error is None and then it is possible to check the message to get more information:
        if "Invalid request".casefold() in error.message.casefold():
            print(f"Uh-oh! Seems there was an invalid request: {error}")
        # Raise the error again
        raise
