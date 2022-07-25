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
    from azure.ai.formrecognizer import DocumentModelAdministrationClient, DocumentBuildMode

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]
    container_sas_url = os.environ["CONTAINER_SAS_URL"]

    # [START get_resource_details]
    document_model_admin_client = DocumentModelAdministrationClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    account_info = document_model_admin_client.get_resource_details()
    print("Our resource has {} custom models, and we can have at most {} custom models\n".format(
        account_info.document_model_count, account_info.document_model_limit
    ))
    # [END get_resource_details]

    # Next, we get a paged list of all of our custom models
    # [START list_models]
    models = document_model_admin_client.list_models()

    print("We have the following 'ready' models with IDs and descriptions:")
    for model in models:
        print("{} | {}".format(model.model_id, model.description))
    # [END list_models]

    # let's build a model to use for this sample
    poller = document_model_admin_client.begin_build_model(container_sas_url, DocumentBuildMode.TEMPLATE, description="model for sample")
    model = poller.result()

    # [START get_model]
    my_model = document_model_admin_client.get_model(model_id=model.model_id)
    print("\nModel ID: {}".format(my_model.model_id))
    print("Description: {}".format(my_model.description))
    print("Model created on: {}".format(my_model.created_on))
    # [END get_model]

    # Finally, we will delete this model by ID
    # [START delete_model]
    document_model_admin_client.delete_model(model_id=my_model.model_id)

    try:
        document_model_admin_client.get_model(model_id=my_model.model_id)
    except ResourceNotFoundError:
        print("Successfully deleted model with ID {}".format(my_model.model_id))
    # [END delete_model]


if __name__ == '__main__':
    sample_manage_models()
