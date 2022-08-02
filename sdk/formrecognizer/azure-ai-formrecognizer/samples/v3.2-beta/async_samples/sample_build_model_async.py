# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_build_model_async.py

DESCRIPTION:
    This sample demonstrates how to build a model. For this sample, you can use the training
    documents found in https://aka.ms/azsdk/formrecognizer/sampletrainingfiles

    More details on setting up a container and required file structure can be found here:
    https://aka.ms/azsdk/formrecognizer/buildtrainingset

USAGE:
    python sample_build_model_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) CONTAINER_SAS_URL - The shared access signature (SAS) Url of your Azure Blob Storage container with your training files.
"""

import os
import asyncio


async def sample_build_model_async():
    # [START build_model_async]
    from azure.ai.formrecognizer.aio import DocumentModelAdministrationClient
    from azure.ai.formrecognizer import DocumentBuildMode
    from azure.core.credentials import AzureKeyCredential

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
    container_sas_url = os.environ["CONTAINER_SAS_URL"]

    document_model_admin_client = DocumentModelAdministrationClient(endpoint, AzureKeyCredential(key))
    async with document_model_admin_client:
        poller = await document_model_admin_client.begin_build_model(
            DocumentBuildMode.TEMPLATE, container_sas_url, description="my model description"
        )
        model = await poller.result()

    print("Model ID: {}".format(model.model_id))
    print("Description: {}".format(model.description))
    print("Model created on: {}\n".format(model.created_on))
    print("Doc types the model can recognize:")
    for name, doc_type in model.doc_types.items():
        print("\nDoc Type: '{}' built with '{}' mode which has the following fields:".format(name, doc_type.build_mode))
        for field_name, field in doc_type.field_schema.items():
            print("Field: '{}' has type '{}' and confidence score {}".format(
                field_name, field["type"], doc_type.field_confidence[field_name]
            ))
    # [END build_model_async]


async def main():
    await sample_build_model_async()

if __name__ == '__main__':
    asyncio.run(main())
