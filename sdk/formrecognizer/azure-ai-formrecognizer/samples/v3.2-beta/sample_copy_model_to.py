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

    The model used in this sample can be created in the sample_build_model.py using the
    training files in https://aka.ms/azsdk/formrecognizer/sampletrainingfiles

USAGE:
    python sample_copy_model_to.py

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

def sample_copy_model_to(custom_model_id):
    # [START begin_copy_model_to]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer import DocumentModelAdministrationClient

    source_endpoint = os.environ["AZURE_FORM_RECOGNIZER_SOURCE_ENDPOINT"]
    source_key = os.environ["AZURE_FORM_RECOGNIZER_SOURCE_KEY"]
    target_endpoint = os.environ["AZURE_FORM_RECOGNIZER_TARGET_ENDPOINT"]
    target_key = os.environ["AZURE_FORM_RECOGNIZER_TARGET_KEY"]
    source_model_id = os.getenv("AZURE_SOURCE_MODEL_ID", custom_model_id)

    target_client = DocumentModelAdministrationClient(endpoint=target_endpoint, credential=AzureKeyCredential(target_key))

    target = target_client.get_copy_authorization(
        description="model copied from other resource"
    )

    source_client = DocumentModelAdministrationClient(endpoint=source_endpoint, credential=AzureKeyCredential(source_key))
    poller = source_client.begin_copy_model_to(
        model_id=source_model_id,
        target=target  # output from target client's call to get_copy_authorization()
    )
    copied_over_model = poller.result()

    print("Model ID: {}".format(model.model_id))
    print("Description: {}".format(model.description))
    print("Model created on: {}\n".format(model.created_on))
    print("Doc types the model can recognize:")
    for name, doc_type in model.doc_types.items():
        print("\nDoc Type: '{}' which has the following fields:".format(name))
        for field_name, field in doc_type.field_schema.items():
            print("Field: '{}' has type '{}' and confidence score {}".format(
                field_name, field["type"], doc_type.field_confidence[field_name]
            ))
    # [END begin_copy_model_to]


if __name__ == '__main__':
    model_id = None
    if os.getenv("CONTAINER_SAS_URL"):

        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer import DocumentModelAdministrationClient, DocumentBuildMode

        endpoint = os.getenv("AZURE_FORM_RECOGNIZER_SOURCE_ENDPOINT")
        key = os.getenv("AZURE_FORM_RECOGNIZER_SOURCE_KEY")

        if not endpoint or not key:
            raise ValueError("Please provide endpoint and API key to run the samples.")

        document_model_admin_client = DocumentModelAdministrationClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        model = document_model_admin_client.begin_build_model(os.getenv("CONTAINER_SAS_URL"), DocumentBuildMode.TEMPLATE).result()
        model_id = model.model_id

    sample_copy_model_to(model_id)
