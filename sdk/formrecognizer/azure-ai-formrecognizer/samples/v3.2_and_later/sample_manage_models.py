# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_manage_models.py

DESCRIPTION:
    This sample demonstrates how to manage the models on your account. To learn
    how to build a model, look at sample_build_model.py.

USAGE:
    python sample_manage_models.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) CONTAINER_SAS_URL - The shared access signature (SAS) Url of your Azure Blob Storage container
"""

import os


def sample_manage_models():
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import ResourceNotFoundError
    from azure.ai.formrecognizer import (
        DocumentModelAdministrationClient,
        ModelBuildMode,
    )

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
    container_sas_url = os.environ["CONTAINER_SAS_URL"]

    # [START get_resource_details]
    document_model_admin_client = DocumentModelAdministrationClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    account_details = document_model_admin_client.get_resource_details()
    print(
        f"Our resource has {account_details.custom_document_models.count} custom models, "
        f"and we can have at most {account_details.custom_document_models.limit} custom models"
    )
    neural_models = account_details.neural_document_model_quota
    print(
        f"The quota limit for custom neural document models is {neural_models.quota} and the resource has"
        f"used {neural_models.used}. The resource quota will reset on {neural_models.quota_resets_on}"
    )
    # [END get_resource_details]

    # Next, we get a paged list of all of our custom models
    # [START list_document_models]
    models = document_model_admin_client.list_document_models()

    print("We have the following 'ready' models with IDs and descriptions:")
    for model in models:
        print(f"{model.model_id} | {model.description}")
    # [END list_document_models]

    # let's build a model to use for this sample
    poller = document_model_admin_client.begin_build_document_model(
        ModelBuildMode.TEMPLATE,
        blob_container_url=container_sas_url,
        description="model for sample",
    )
    model = poller.result()

    # [START get_document_model]
    my_model = document_model_admin_client.get_document_model(model_id=model.model_id)
    print(f"\nModel ID: {my_model.model_id}")
    print(f"Description: {my_model.description}")
    print(f"Model created on: {my_model.created_on}")
    print(f"Model expires on: {my_model.expires_on}")
    # [END get_document_model]

    # Finally, we will delete this model by ID
    # [START delete_document_model]
    document_model_admin_client.delete_document_model(model_id=my_model.model_id)

    try:
        document_model_admin_client.get_document_model(model_id=my_model.model_id)
    except ResourceNotFoundError:
        print(f"Successfully deleted model with ID {my_model.model_id}")
    # [END delete_document_model]


if __name__ == "__main__":
    import sys
    from azure.core.exceptions import HttpResponseError

    try:
        sample_manage_models()
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
