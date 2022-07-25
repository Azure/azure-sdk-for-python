# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication_async.py

DESCRIPTION:
    This sample demonstrates how to authenticate to the Form Recognizer service.

    There are two supported methods of authentication:
    1) Use a Form Recognizer API key with AzureKeyCredential from azure.core.credentials
    2) Use a token credential from azure-identity to authenticate with Azure Active Directory

    See more details about authentication here:
    https://docs.microsoft.com/azure/cognitive-services/authentication

USAGE:
    python sample_authentication_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_FORM_RECOGNIZER_ENDPOINT - the endpoint to your Form Recognizer resource.
    2) AZURE_FORM_RECOGNIZER_KEY - your Form Recognizer API key
    3) AZURE_CLIENT_ID - the client ID of your active directory application.
    4) AZURE_TENANT_ID - the tenant ID of your active directory application.
    5) AZURE_CLIENT_SECRET - the secret of your active directory application.
"""

import os
import asyncio

url = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/forms/Form_1.jpg"


async def authentication_with_api_key_credential_document_analysis_client_async():
    # [START create_da_client_with_key_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer.aio import DocumentAnalysisClient
    from azure.core.exceptions import HttpResponseError

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    document_analysis_client = DocumentAnalysisClient(endpoint, AzureKeyCredential(key))
    # [END create_da_client_with_key_async]

    
    async with document_analysis_client:
        # The test is unstable in China cloud, we try to set the number of retries in the code to increase stability
        retry_times = 0
        while retry_times != 5 :
            try:
                # Begin analyze document from url, this sample test is unstable in China cloud.(We are testing sovereign cloud test)
                # Increasing the number of retries in the code until there is a better solution
                poller = await document_analysis_client.begin_analyze_document_from_url(
                    "prebuilt-layout", url
                )
            except HttpResponseError as e:
                retry_times += 1
                # Print the known unstable errors
                print(e.message)
                continue
            else:
                break
        print("--------Retry times: {}--------".format(retry_times))
        result = await poller.result()


async def authentication_with_azure_active_directory_document_analysis_client_async():
    # [START create_da_client_with_aad_async]
    """DefaultAzureCredential will use the values from these environment
    variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
    """
    from azure.ai.formrecognizer.aio import DocumentAnalysisClient
    from azure.identity.aio import DefaultAzureCredential
    from azure.core.exceptions import HttpResponseError

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    credential = DefaultAzureCredential()

    form_recognizer_endpoint_suffix = os.environ.get("FORMRECOGNIZER_ENDPOINT_SUFFIX",".cognitiveservices.azure.com")
    credential_scopes = ["https://{}/.default".format(form_recognizer_endpoint_suffix[1:])]
    document_analysis_client = DocumentAnalysisClient(endpoint, credential, credential_scopes=credential_scopes)
    # [END create_da_client_with_aad_async]
    async with document_analysis_client:
        # The test is unstable in China cloud, we try to set the number of retries in the code to increase stability
        retry_times = 0
        while retry_times != 5 :
            try:
                # Begin analyze document from url, this sample test is unstable in China cloud.(We are testing sovereign cloud test)
                # Increasing the number of retries in the code until there is a better solution
                poller = await document_analysis_client.begin_analyze_document_from_url(
                    "prebuilt-layout", url
                )
            except HttpResponseError as e:
                retry_times += 1
                # Print the known unstable errors
                print(e.message)
                continue
            else:
                break
        print("--------Retry times: {}--------".format(retry_times))
        result = await poller.result()


async def authentication_with_api_key_credential_document_model_admin_client_async():
    # [START create_dt_client_with_key_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer.aio import DocumentModelAdministrationClient

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

    document_model_admin_client = DocumentModelAdministrationClient(endpoint, AzureKeyCredential(key))
    # [END create_dt_client_with_key_async]
    async with document_model_admin_client:
        info = await document_model_admin_client.get_resource_info()


async def authentication_with_azure_active_directory_document_model_admin_client_async():
    # [START create_dt_client_with_aad_async]
    """DefaultAzureCredential will use the values from these environment
    variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
    """
    from azure.ai.formrecognizer.aio import DocumentModelAdministrationClient
    from azure.identity.aio import DefaultAzureCredential

    endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
    credential = DefaultAzureCredential()

    form_recognizer_endpoint_suffix = os.environ.get("FORMRECOGNIZER_ENDPOINT_SUFFIX",".cognitiveservices.azure.com")
    credential_scopes = ["https://{}/.default".format(form_recognizer_endpoint_suffix[1:])]
    document_model_admin_client = DocumentModelAdministrationClient(endpoint, credential, credential_scopes=credential_scopes)
    # [END create_dt_client_with_aad_async]
    async with document_model_admin_client:
        info = await document_model_admin_client.get_resource_info()


async def main():
    await authentication_with_api_key_credential_document_analysis_client_async()
    await authentication_with_azure_active_directory_document_analysis_client_async()
    await authentication_with_api_key_credential_document_model_admin_client_async()
    await authentication_with_azure_active_directory_document_model_admin_client_async()


if __name__ == "__main__":
    asyncio.run(main())
