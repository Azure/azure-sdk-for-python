# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_copy_model_to_async.py

DESCRIPTION:
    This sample demonstrates how to copy a custom model from a source Form Recognizer resource
    to a target Form Recognizer resource.

    The model used in this sample can be created in the sample_build_model_async.py using the
    training files in https://aka.ms/azsdk/formrecognizer/sampletrainingfiles

USAGE:
    python sample_copy_model_to_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_SOURCE_ENDPOINT - the endpoint to your source Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_SOURCE_KEY - your source Form Recognizer API key
    3) AZURE_FORM_RECOGNIZER_TARGET_ENDPOINT - the endpoint to your target Form Recognizer resource.
    4) AZURE_FORM_RECOGNIZER_TARGET_KEY - your target Form Recognizer API key
    5) AZURE_SOURCE_MODEL_ID - the model ID from the source resource to be copied over to the target resource.
        - OR -
       CONTAINER_SAS_URL - The shared access signature (SAS) Url of your Azure Blob Storage container with your training files.
       A model will be built and used to run the sample.
"""

import os
import asyncio


async def sample_copy_model_to_async(custom_model_id):
    # [START begin_copy_document_model_to_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer.aio import DocumentModelAdministrationClient

    source_endpoint = os.environ["AZURE_FORM_RECOGNIZER_SOURCE_ENDPOINT"]
    source_key = os.environ["AZURE_FORM_RECOGNIZER_SOURCE_KEY"]
    target_endpoint = os.environ["AZURE_FORM_RECOGNIZER_TARGET_ENDPOINT"]
    target_key = os.environ["AZURE_FORM_RECOGNIZER_TARGET_KEY"]
    source_model_id = os.getenv("AZURE_SOURCE_MODEL_ID", custom_model_id)

    target_client = DocumentModelAdministrationClient(
        endpoint=target_endpoint, credential=AzureKeyCredential(target_key)
    )
    async with target_client:
        target = await target_client.get_copy_authorization(
            description="model copied from other resource"
        )

    source_client = DocumentModelAdministrationClient(
        endpoint=source_endpoint, credential=AzureKeyCredential(source_key)
    )
    async with source_client:
        poller = await source_client.begin_copy_document_model_to(
            model_id=source_model_id,
            target=target,  # output from target client's call to get_copy_authorization()
        )
        copied_over_model = await poller.result()

    print(f"Model ID: {copied_over_model.model_id}")
    print(f"Description: {copied_over_model.description}")
    print(f"Model created on: {copied_over_model.created_on}")
    print(f"Model expires on: {copied_over_model.expires_on}")
    print("Doc types the model can recognize:")
    for name, doc_type in copied_over_model.doc_types.items():
        print(f"Doc Type: '{name}' which has the following fields:")
        for field_name, field in doc_type.field_schema.items():
            print(
                f"Field: '{field_name}' has type '{field['type']}' and confidence score "
                f"{doc_type.field_confidence[field_name]}"
            )
    # [END begin_copy_document_model_to_async]


async def main():
    model_id = None
    if os.getenv("CONTAINER_SAS_URL"):
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer.aio import DocumentModelAdministrationClient
        from azure.ai.formrecognizer import ModelBuildMode

        endpoint = os.getenv("AZURE_FORM_RECOGNIZER_SOURCE_ENDPOINT")
        key = os.getenv("AZURE_FORM_RECOGNIZER_SOURCE_KEY")

        if not endpoint or not key:
            raise ValueError("Please provide endpoint and API key to run the samples.")

        document_model_admin_client = DocumentModelAdministrationClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        async with document_model_admin_client:
            blob_container_sas_url = os.getenv("CONTAINER_SAS_URL")
            if blob_container_sas_url is not None:
                model = await (
                    await document_model_admin_client.begin_build_document_model(
                        ModelBuildMode.TEMPLATE,
                        blob_container_url=blob_container_sas_url,
                    )
                ).result()
                model_id = model.model_id

    await sample_copy_model_to_async(model_id)


if __name__ == "__main__":
    import sys
    from azure.core.exceptions import HttpResponseError

    try:
        asyncio.run(main())
    except HttpResponseError as error:
        print(
            "For more information about troubleshooting errors, see the following guide: "
            "https://aka.ms/azsdk/python/formrecognizer/troubleshooting"
        )
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
