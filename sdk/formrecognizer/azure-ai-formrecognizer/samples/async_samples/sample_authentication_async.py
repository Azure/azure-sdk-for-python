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
    6) AZURE_FORM_RECOGNIZER_AAD_ENDPOINT - the endpoint to your Form Recognizer resource for using AAD.
"""

import os
import asyncio


class AuthenticationSampleAsync(object):

    url = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/receipt/contoso-receipt.png"

    async def authentication_with_api_key_credential_form_recognizer_client_async(self):
        # [START create_fr_client_with_key_async]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer.aio import FormRecognizerClient
        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

        form_recognizer_client = FormRecognizerClient(endpoint, AzureKeyCredential(key))
        # [END create_fr_client_with_key_async]
        async with form_recognizer_client:
            poller = await form_recognizer_client.begin_recognize_receipts_from_url(self.url)
            result = await poller.result()

    async def authentication_with_azure_active_directory_form_recognizer_client_async(self):
        # [START create_fr_client_with_aad_async]
        """DefaultAzureCredential will use the values from these environment
        variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
        """
        from azure.ai.formrecognizer.aio import FormRecognizerClient
        from azure.identity.aio import DefaultAzureCredential

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_AAD_ENDPOINT"]
        credential = DefaultAzureCredential()

        form_recognizer_client = FormRecognizerClient(endpoint, credential)
        # [END create_fr_client_with_aad_async]
        async with form_recognizer_client:
            poller = await form_recognizer_client.begin_recognize_receipts_from_url(self.url)
            result = await poller.result()

    async def authentication_with_api_key_credential_form_training_client_async(self):
        # [START create_ft_client_with_key_async]
        from azure.core.credentials import AzureKeyCredential
        from azure.ai.formrecognizer.aio import FormTrainingClient
        endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
        key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

        form_training_client = FormTrainingClient(endpoint, AzureKeyCredential(key))
        # [END create_ft_client_with_key_async]
        async with form_training_client:
            properties = await form_training_client.get_account_properties()

    async def authentication_with_azure_active_directory_form_training_client_async(self):
        # [START create_ft_client_with_aad_async]
        """DefaultAzureCredential will use the values from these environment
        variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
        """
        from azure.ai.formrecognizer.aio import FormTrainingClient
        from azure.identity.aio import DefaultAzureCredential

        endpoint = os.environ["AZURE_FORM_RECOGNIZER_AAD_ENDPOINT"]
        credential = DefaultAzureCredential()

        form_training_client = FormTrainingClient(endpoint, credential)
        # [END create_ft_client_with_aad_async]
        async with form_training_client:
            properties = await form_training_client.get_account_properties()


async def main():
    sample = AuthenticationSampleAsync()
    await sample.authentication_with_api_key_credential_form_recognizer_client_async()
    await sample.authentication_with_azure_active_directory_form_recognizer_client_async()
    await sample.authentication_with_api_key_credential_form_training_client_async()
    await sample.authentication_with_azure_active_directory_form_training_client_async()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
