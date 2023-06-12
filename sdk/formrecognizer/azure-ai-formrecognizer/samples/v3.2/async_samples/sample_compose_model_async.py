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
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) PURCHASE_ORDER_OFFICE_SUPPLIES_SAS_URL - a container SAS URL to your Azure Storage blob container.
    4) PURCHASE_ORDER_OFFICE_EQUIPMENT_SAS_URL - a container SAS URL to your Azure Storage blob container.
    5) PURCHASE_ORDER_OFFICE_FURNITURE_SAS_URL - a container SAS URL to your Azure Storage blob container.
    6) PURCHASE_ORDER_OFFICE_CLEANING_SUPPLIES_SAS_URL - a container SAS URL to your Azure Storage blob container.
"""

import os
import asyncio


async def sample_compose_model_async():
    # [START composed_model_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer.aio import DocumentModelAdministrationClient
    from azure.ai.formrecognizer import ModelBuildMode

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
    po_supplies = os.environ["PURCHASE_ORDER_OFFICE_SUPPLIES_SAS_URL"]
    po_equipment = os.environ["PURCHASE_ORDER_OFFICE_EQUIPMENT_SAS_URL"]
    po_furniture = os.environ["PURCHASE_ORDER_OFFICE_FURNITURE_SAS_URL"]
    po_cleaning_supplies = os.environ["PURCHASE_ORDER_OFFICE_CLEANING_SUPPLIES_SAS_URL"]

    document_model_admin_client = DocumentModelAdministrationClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    async with document_model_admin_client:
        supplies_poller = await document_model_admin_client.begin_build_document_model(
            ModelBuildMode.TEMPLATE,
            blob_container_url=po_supplies,
            description="Purchase order-Office supplies",
        )
        equipment_poller = await document_model_admin_client.begin_build_document_model(
            ModelBuildMode.TEMPLATE,
            blob_container_url=po_equipment,
            description="Purchase order-Office Equipment",
        )
        furniture_poller = await document_model_admin_client.begin_build_document_model(
            ModelBuildMode.TEMPLATE,
            blob_container_url=po_furniture,
            description="Purchase order-Furniture",
        )
        cleaning_supplies_poller = (
            await document_model_admin_client.begin_build_document_model(
                ModelBuildMode.TEMPLATE,
                blob_container_url=po_cleaning_supplies,
                description="Purchase order-Cleaning Supplies",
            )
        )
        supplies_model = await supplies_poller.result()
        equipment_model = await equipment_poller.result()
        furniture_model = await furniture_poller.result()
        cleaning_supplies_model = await cleaning_supplies_poller.result()

        purchase_order_models = [
            supplies_model.model_id,
            equipment_model.model_id,
            furniture_model.model_id,
            cleaning_supplies_model.model_id,
        ]

        poller = await document_model_admin_client.begin_compose_document_model(
            purchase_order_models, description="Office Supplies Composed Model"
        )
        model = await poller.result()

    print("Office Supplies Composed Model Info:")
    print(f"Model ID: {model.model_id}")
    print(f"Description: {model.description}")
    print(f"Model created on: {model.created_on}")
    print(f"Model expires on: {model.expires_on}")
    print("Doc types the model can recognize:")
    for name, doc_type in model.doc_types.items():
        print(f"Doc Type: '{name}' which has the following fields:")
        for field_name, field in doc_type.field_schema.items():
            print(
                f"Field: '{field_name}' has type '{field['type']}' and confidence score "
                f"{doc_type.field_confidence[field_name]}"
            )
    # [END composed_model_async]


async def main():
    await sample_compose_model_async()


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
