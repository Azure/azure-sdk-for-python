# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication.py

DESCRIPTION:
    This sample demonstrates how to authenticate to the Form Recognizer service.

    There are two supported methods of authentication:
    1) Use a Form Recognizer API key with AzureKeyCredential from azure.core.credentials
    2) Use a token credential from azure-identity to authenticate with Azure Active Directory

    See more details about authentication here:
    https://docs.microsoft.com/azure/cognitive-services/authentication

USAGE:
    python sample_authentication.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) AZURE_CLIENT_ID - the client ID of your active directory application.
    4) AZURE_TENANT_ID - the tenant ID of your active directory application.
    5) AZURE_CLIENT_SECRET - the secret of your active directory application.
"""

import os

url = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/forms/Form_1.jpg"


def authentication_with_api_key_credential_document_analysis_client():
    # [START create_da_client_with_key]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer import DocumentAnalysisClient

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    document_analysis_client = DocumentAnalysisClient(endpoint, AzureKeyCredential(key))
    # [END create_da_client_with_key]
    poller = document_analysis_client.begin_analyze_document_from_url(
        "prebuilt-layout", url
    )
    result = poller.result()


def authentication_with_azure_active_directory_document_analysis_client():
    # [START create_da_client_with_aad]
    """DefaultAzureCredential will use the values from these environment
    variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
    """
    from azure.ai.formrecognizer import DocumentAnalysisClient
    from azure.identity import DefaultAzureCredential

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    credential = DefaultAzureCredential()

    document_analysis_client = DocumentAnalysisClient(endpoint, credential)
    # [END create_da_client_with_aad]
    poller = document_analysis_client.begin_analyze_document_from_url(
        "prebuilt-layout", url
    )
    result = poller.result()


def authentication_with_api_key_credential_document_model_admin_client():
    # [START create_dt_client_with_key]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer import DocumentModelAdministrationClient

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    document_model_admin_client = DocumentModelAdministrationClient(
        endpoint, AzureKeyCredential(key)
    )
    # [END create_dt_client_with_key]
    info = document_model_admin_client.get_resource_details()


def authentication_with_azure_active_directory_document_model_admin_client():
    # [START create_dt_client_with_aad]
    """DefaultAzureCredential will use the values from these environment
    variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
    """
    from azure.ai.formrecognizer import DocumentModelAdministrationClient
    from azure.identity import DefaultAzureCredential

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    credential = DefaultAzureCredential()

    document_model_admin_client = DocumentModelAdministrationClient(
        endpoint, credential
    )
    # [END create_dt_client_with_aad]
    info = document_model_admin_client.get_resource_details()


if __name__ == "__main__":
    import sys
    from azure.core.exceptions import HttpResponseError

    try:
        authentication_with_api_key_credential_document_analysis_client()
        authentication_with_azure_active_directory_document_analysis_client()
        authentication_with_api_key_credential_document_model_admin_client()
        authentication_with_azure_active_directory_document_model_admin_client()
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
