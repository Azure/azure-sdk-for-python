# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_build_model.py

DESCRIPTION:
    This sample demonstrates how to build a model. For this sample, you can use the training
    documents found in https://aka.ms/azsdk/formrecognizer/sampletrainingfiles

    More details on setting up a container and required file structure can be found here:
    https://aka.ms/azsdk/formrecognizer/buildtrainingset

USAGE:
    python sample_build_model.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) CONTAINER_SAS_URL - The shared access signature (SAS) Url of your Azure Blob Storage container with your training files.
"""

import os


def sample_build_model():
    # [START build_model]
    from azure.ai.formrecognizer import (
        DocumentModelAdministrationClient,
        ModelBuildMode,
    )
    from azure.core.credentials import AzureKeyCredential

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
    container_sas_url = os.environ["CONTAINER_SAS_URL"]

    document_model_admin_client = DocumentModelAdministrationClient(
        endpoint, AzureKeyCredential(key)
    )
    poller = document_model_admin_client.begin_build_document_model(
        ModelBuildMode.TEMPLATE,
        blob_container_url=container_sas_url,
        description="my model description",
    )
    model = poller.result()

    print(f"Model ID: {model.model_id}")
    print(f"Description: {model.description}")
    print(f"Model created on: {model.created_on}")
    print(f"Model expires on: {model.expires_on}")
    print("Doc types the model can recognize:")
    for name, doc_type in model.doc_types.items():
        print(
            f"Doc Type: '{name}' built with '{doc_type.build_mode}' mode which has the following fields:"
        )
        for field_name, field in doc_type.field_schema.items():
            print(
                f"Field: '{field_name}' has type '{field['type']}' and confidence score "
                f"{doc_type.field_confidence[field_name]}"
            )
    # [END build_model]


if __name__ == "__main__":
    import sys
    from azure.core.exceptions import HttpResponseError

    try:
        sample_build_model()
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
