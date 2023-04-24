# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_operations_async.py

DESCRIPTION:
    This sample demonstrates how to list/get all document model operations (succeeded, in-progress, failed)
    associated with the Form Recognizer resource. Kinds of operations returned are "documentModelBuild",
    "documentModelCompose", and "documentModelCopyTo". Note that operation information only persists for
    24 hours. If the operation was successful, the document model can be accessed using get_document_model or list_document_models APIs.

USAGE:
    python sample_get_operations_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
"""

import os
import asyncio


async def sample_get_operations_async():
    # [START list_operations_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer.aio import DocumentModelAdministrationClient

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    document_model_admin_client = DocumentModelAdministrationClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    async with document_model_admin_client:
        operations = document_model_admin_client.list_operations()

        print("The following document model operations exist under my resource:")
        async for operation in operations:
            print("\nOperation ID: {}".format(operation.operation_id))
            print("Operation kind: {}".format(operation.kind))
            print("Operation status: {}".format(operation.status))
            print("Operation percent completed: {}".format(operation.percent_completed))
            print("Operation created on: {}".format(operation.created_on))
            print("Operation last updated on: {}".format(operation.last_updated_on))
            print("Resource location of successful operation: {}".format(operation.resource_location))
    # [END list_operations_async]

        # [START get_operation_async]
        # Get an operation by ID
        try:
            first_operation = await operations.__anext__()

            print("\nGetting operation info by ID: {}".format(first_operation.operation_id))
            operation_info = await document_model_admin_client.get_operation(first_operation.operation_id)
            if operation_info.status == "succeeded":
                print("My {} operation is completed.".format(operation_info.kind))
                result = operation_info.result
                if result is not None:
                    if operation_info.kind == "documentClassifierBuild":
                        print(f"Classifier ID: {result.classifier_id}")
                    else:
                        print("Model ID: {}".format(result.model_id))
            elif operation_info.status == "failed":
                print("My {} operation failed.".format(operation_info.kind))
                error = operation_info.error
                if error is not None:
                    print("{}: {}".format(error.code, error.message))
            else:
                print("My operation status is {}".format(operation_info.status))
        except StopAsyncIteration:
            print("No operations found.")
        # [END get_operation_async]

async def main():
    await sample_get_operations_async()


if __name__ == '__main__':
    import sys
    from azure.core.exceptions import HttpResponseError
    try:
        asyncio.run(main())
    except HttpResponseError as error:
        print("For more information about troubleshooting errors, see the following guide: "
              "https://aka.ms/azsdk/python/formrecognizer/troubleshooting")
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
