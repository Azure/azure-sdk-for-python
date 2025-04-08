# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_manage_models_async.py

DESCRIPTION:
    This sample demonstrates how to manage the models on your account. To learn
    how to build a model, look at sample_build_model.py.

USAGE:
    python sample_manage_models_async.py

    Set the environment variables with your own values before running the sample:
    1) DOCUMENTINTELLIGENCE_ENDPOINT - the endpoint to your Document Intelligence resource.
    2) DOCUMENTINTELLIGENCE_API_KEY - your Document Intelligence API key.
    3) DOCUMENTINTELLIGENCE_STORAGE_CONTAINER_SAS_URL - The shared access signature (SAS) Url of your Azure Blob Storage container
"""

import asyncio
import os


async def sample_manage_models():
    # Let's build a model to use for this sample
    import uuid
    from azure.ai.documentintelligence.aio import DocumentIntelligenceAdministrationClient
    from azure.ai.documentintelligence.models import (
        DocumentBuildMode,
        BuildDocumentModelRequest,
        AzureBlobContentSource,
        DocumentModelDetails,
    )
    from azure.core.credentials import AzureKeyCredential

    endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
    key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]
    container_sas_url = os.environ["DOCUMENTINTELLIGENCE_STORAGE_CONTAINER_SAS_URL"]

    document_intelligence_admin_client = DocumentIntelligenceAdministrationClient(endpoint, AzureKeyCredential(key))
    async with document_intelligence_admin_client:
        poller = await document_intelligence_admin_client.begin_build_document_model(
            BuildDocumentModelRequest(
                model_id=str(uuid.uuid4()),
                build_mode=DocumentBuildMode.TEMPLATE,
                azure_blob_source=AzureBlobContentSource(container_url=container_sas_url),
                description="my model description",
            )
        )
        model: DocumentModelDetails = await poller.result()

        print(f"Model ID: {model.model_id}")
        print(f"Description: {model.description}")
        print(f"Model created on: {model.created_date_time}")
        print(f"Model expires on: {model.expiration_date_time}")
        if model.doc_types:
            print("Doc types the model can recognize:")
            for name, doc_type in model.doc_types.items():
                print(f"Doc Type: '{name}' built with '{doc_type.build_mode}' mode which has the following fields:")
                if doc_type.field_schema:
                    for field_name, field in doc_type.field_schema.items():
                        if doc_type.field_confidence:
                            print(
                                f"Field: '{field_name}' has type '{field['type']}' and confidence score "
                                f"{doc_type.field_confidence[field_name]}"
                            )
        if model.warnings:
            print("Warnings encountered while building the model:")
            for warning in model.warnings:
                print(
                    f"warning code: {warning.code}, message: {warning.message}, target of the error: {warning.target}"
                )

        account_details = await document_intelligence_admin_client.get_resource_details()
        print(
            f"Our resource has {account_details.custom_document_models.count} custom models, "
            f"and we can have at most {account_details.custom_document_models.limit} custom models"
        )

        # Next, we get a paged list of all of our custom models
        models = document_intelligence_admin_client.list_models()

        print("We have the following 'ready' models with IDs and descriptions:")
        async for model in models:
            print(f"{model.model_id} | {model.description}")

        my_model = await document_intelligence_admin_client.get_model(model_id=model.model_id)
        print(f"\nModel ID: {my_model.model_id}")
        print(f"Description: {my_model.description}")
        print(f"Model created on: {my_model.created_date_time}")
        print(f"Model expires on: {my_model.expiration_date_time}")

        # Finally, we will delete this model by ID
        await document_intelligence_admin_client.delete_model(model_id=my_model.model_id)

        from azure.core.exceptions import ResourceNotFoundError

        try:
            await document_intelligence_admin_client.get_model(model_id=my_model.model_id)
        except ResourceNotFoundError:
            print(f"Successfully deleted model with ID {my_model.model_id}")


async def main():
    await sample_manage_models()


if __name__ == "__main__":
    from azure.core.exceptions import HttpResponseError
    from dotenv import find_dotenv, load_dotenv

    try:
        load_dotenv(find_dotenv())
        asyncio.run(main())
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
