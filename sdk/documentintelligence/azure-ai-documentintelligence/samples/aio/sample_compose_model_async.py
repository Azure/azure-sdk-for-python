# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_compose_model_async.py

DESCRIPTION:
    Model compose allows multiple models to be composed and called with a single model ID.
    This is useful when you have built different models and want to aggregate a group of
    them into a single model that you (or a user) could use to analyze a document. When doing
    so, you can let the service decide which model more accurately represents the document to
    analyze, instead of manually trying each built model against the document and selecting
    the most accurate one.

    In our case, we will be writing an application that collects the expenses a company is making.
    There are 4 main areas where we get purchase orders from (office supplies, office equipment,
    furniture, and cleaning supplies). Because each area has its own document with its own structure,
    we need to build a model per document. Note that you can substitute your own models or container
    SAS URLs for this sample.

USAGE:
    python sample_compose_model_async.py

    Set the environment variables with your own values before running the sample:
    1) DOCUMENTINTELLIGENCE_ENDPOINT - the endpoint to your Document Intelligence resource.
    2) DOCUMENTINTELLIGENCE_API_KEY - your Document Intelligence API key.
    3) DOCUMENTINTELLIGENCE_STORAGE_CONTAINER_SAS_URL - a container SAS URL to your Azure Storage blob container.
"""

import asyncio
import os


async def sample_compose_model():
    # [START composed_model]
    import uuid
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.documentintelligence.aio import DocumentIntelligenceAdministrationClient
    from azure.ai.documentintelligence.models import (
        AzureBlobContentSource,
        BuildDocumentModelRequest,
        ComposeDocumentModelRequest,
        ComponentDocumentModelDetails,
        DocumentBuildMode,
        DocumentModelDetails,
    )

    endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
    key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]
    container_sas_url = os.environ["DOCUMENTINTELLIGENCE_STORAGE_CONTAINER_SAS_URL"]

    document_intelligence_admin_client = DocumentIntelligenceAdministrationClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    async with document_intelligence_admin_client:
        supplies_poller = await document_intelligence_admin_client.begin_build_document_model(
            BuildDocumentModelRequest(
                model_id=str(uuid.uuid4()),
                build_mode=DocumentBuildMode.TEMPLATE,
                azure_blob_source=AzureBlobContentSource(container_url=container_sas_url),
                description="Purchase order-Office Supplies",
            )
        )
        equipment_poller = await document_intelligence_admin_client.begin_build_document_model(
            BuildDocumentModelRequest(
                model_id=str(uuid.uuid4()),
                build_mode=DocumentBuildMode.TEMPLATE,
                azure_blob_source=AzureBlobContentSource(container_url=container_sas_url),
                description="Purchase order-Office Equipment",
            )
        )
        furniture_poller = await document_intelligence_admin_client.begin_build_document_model(
            BuildDocumentModelRequest(
                model_id=str(uuid.uuid4()),
                build_mode=DocumentBuildMode.TEMPLATE,
                azure_blob_source=AzureBlobContentSource(container_url=container_sas_url),
                description="Purchase order-Office Furniture",
            )
        )
        cleaning_supplies_poller = await document_intelligence_admin_client.begin_build_document_model(
            BuildDocumentModelRequest(
                model_id=str(uuid.uuid4()),
                build_mode=DocumentBuildMode.TEMPLATE,
                azure_blob_source=AzureBlobContentSource(container_url=container_sas_url),
                description="Purchase order-Office Cleaning Supplies",
            )
        )
        supplies_model: DocumentModelDetails = await supplies_poller.result()
        equipment_model: DocumentModelDetails = await equipment_poller.result()
        furniture_model: DocumentModelDetails = await furniture_poller.result()
        cleaning_supplies_model: DocumentModelDetails = await cleaning_supplies_poller.result()

        poller = await document_intelligence_admin_client.begin_compose_model(
            ComposeDocumentModelRequest(
                model_id=str(uuid.uuid4()),
                component_models=[
                    ComponentDocumentModelDetails(model_id=supplies_model.model_id),
                    ComponentDocumentModelDetails(model_id=equipment_model.model_id),
                    ComponentDocumentModelDetails(model_id=furniture_model.model_id),
                    ComponentDocumentModelDetails(model_id=cleaning_supplies_model.model_id),
                ],
                description="Office Supplies Composed Model",
            ),
        )
        model: DocumentModelDetails = await poller.result()

    print("Office Supplies Composed Model Info:")
    print(f"Model ID: {model.model_id}")
    print(f"Description: {model.description}")
    print(f"Model created on: {model.created_date_time}")
    print(f"Model expires on: {model.expiration_date_time}")
    if model.doc_types:
        print("Doc types the model can recognize:")
        for name, doc_type in model.doc_types.items():
            print(f"Doc Type: '{name}' which has the following fields:")
            if doc_type.field_confidence:
                for field_name, field in doc_type.field_schema.items():
                    print(
                        f"Field: '{field_name}' has type '{field['type']}' and confidence score "
                        f"{doc_type.field_confidence[field_name]}"
                    )
    if model.warnings:
        print("Warnings encountered while building the model:")
        for warning in model.warnings:
            print(f"warning code: {warning.code}, message: {warning.message}, target of the error: {warning.target}")
    # [END composed_model]


async def main():
    await sample_compose_model()


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
