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
    how to build a model, look at sample_build_model_async.py.

USAGE:
    python sample_manage_models_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) CONTAINER_SAS_URL - The shared access signature (SAS) Url of your Azure Blob Storage container
"""

import os
import asyncio


async def sample_manage_models_async():
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import ResourceNotFoundError
    from azure.ai.formrecognizer.aio import DocumentModelAdministrationClient
    from azure.ai.formrecognizer import ModelBuildMode

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
    container_sas_url = os.environ["CONTAINER_SAS_URL"]

    # [START get_resource_details_async]
    document_model_admin_client = DocumentModelAdministrationClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    async with document_model_admin_client:
        account_details = await document_model_admin_client.get_resource_details()
        print("Our resource has {} custom models, and we can have at most {} custom models\n".format(
            account_details.custom_document_models.count, account_details.custom_document_models.limit
        ))
        neural_models = account_details.custom_neural_document_model_builds
        print(f"The quota limit for custom neural document models is {neural_models.quota} and the resource has"
              f"used {neural_models.used}. The resource quota will reset on {neural_models.quota_resets_on}")
        # [END get_resource_details_async]

        # Next, we get a paged list of all of our custom models
        # [START list_document_models_async]
        models = document_model_admin_client.list_document_models()

        print("We have the following 'ready' models with IDs and descriptions:")
        async for model in models:
            print("{} | {}".format(model.model_id, model.description))
        # [END list_document_models_async]

        # let's build a model to use for this sample
        poller = await document_model_admin_client.begin_build_document_model(ModelBuildMode.TEMPLATE, blob_container_url=container_sas_url, description="model for sample")
        model = await poller.result()

        # [START get_document_model_async]
        my_model = await document_model_admin_client.get_document_model(model_id=model.model_id)
        print("\nModel ID: {}".format(my_model.model_id))
        print("Description: {}".format(my_model.description))
        print("Model created on: {}".format(my_model.created_on))
        print("Model expires on: {}".format(my_model.expires_on))
        # [END get_document_model_async]

        # Finally, we will delete this model by ID
        # [START delete_document_model_async]
        await document_model_admin_client.delete_document_model(model_id=my_model.model_id)

        try:
            await document_model_admin_client.get_document_model(model_id=my_model.model_id)
        except ResourceNotFoundError:
            print("Successfully deleted model with ID {}".format(my_model.model_id))
        # [END delete_document_model_async]


async def main():
    await sample_manage_models_async()

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
