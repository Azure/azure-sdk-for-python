# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_operations.py

DESCRIPTION:
    This sample demonstrates how to list/get all document model operations (succeeded, in-progress, failed)
    associated with the Form Recognizer resource. Kinds of operations returned are "documentModelBuild",
    "documentModelCompose", and "documentModelCopyTo". Note that operation information only persists for
    24 hours. If the operation was successful, the document model can be accessed using get_document_model or list_document_models APIs.

USAGE:
    python sample_get_operations.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os


def sample_get_operations():
    # [START list_operations]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer import DocumentModelAdministrationClient

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    document_model_admin_client = DocumentModelAdministrationClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    operations = list(document_model_admin_client.list_operations())

    print("The following document model operations exist under my resource:")
    for operation in operations:
        print(f"\nOperation ID: {operation.operation_id}")
        print(f"Operation kind: {operation.kind}")
        print(f"Operation status: {operation.status}")
        print(f"Operation percent completed: {operation.percent_completed}")
        print(f"Operation created on: {operation.created_on}")
        print(f"Operation last updated on: {operation.last_updated_on}")
        print(
            f"Resource location of successful operation: {operation.resource_location}"
        )
    # [END list_operations]

    # [START get_operation]
    # Get an operation by ID
    if operations:
        print(f"\nGetting operation info by ID: {operations[0].operation_id}")
        operation_info = document_model_admin_client.get_operation(
            operations[0].operation_id
        )
        if operation_info.status == "succeeded":
            print(f"My {operation_info.kind} operation is completed.")
            result = operation_info.result
            if result is not None:
                if operation_info.kind == "documentClassifierBuild":
                    print(f"Classifier ID: {result.classifier_id}")
                else:
                    print(f"Model ID: {result.model_id}")
        elif operation_info.status == "failed":
            print(f"My {operation_info.kind} operation failed.")
            error = operation_info.error
            if error is not None:
                print(f"{error.code}: {error.message}")
        else:
            print(f"My operation status is {operation_info.status}")
    else:
        print("No operations found.")
    # [END get_operation]


if __name__ == "__main__":
    import sys
    from azure.core.exceptions import HttpResponseError

    try:
        sample_get_operations()
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
