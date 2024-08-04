# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication_async.py

DESCRIPTION:
    This sample demonstrates how to authenticate to the Document Translation service.

    There are two supported methods of authentication:
    1) Use a Document Translation API key with AzureKeyCredential from azure.core.credentials
    2) Use a token credential from azure-identity to authenticate with Azure Active Directory

    See more details about authentication here:
    https://docs.microsoft.com/azure/cognitive-services/authentication

    Note: the endpoint must be formatted to use the custom domain name for your resource:
    https://<NAME-OF-YOUR-RESOURCE>.cognitiveservices.azure.com/

USAGE:
    python sample_authentication_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_DOCUMENT_TRANSLATION_ENDPOINT - the endpoint to your Document Translation resource.
    2) AZURE_DOCUMENT_TRANSLATION_KEY - your Document Translation API key
    3) AZURE_CLIENT_ID - the client ID of your active directory application.
    4) AZURE_TENANT_ID - the tenant ID of your active directory application.
    5) AZURE_CLIENT_SECRET - the secret of your active directory application.
"""

import os
import asyncio


async def sample_authentication_api_key_async():
    # [START create_dt_client_with_key_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.translation.document.aio import DocumentTranslationClient

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]

    document_translation_client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))
    # [END create_dt_client_with_key_async]

    # make calls with authenticated client
    async with document_translation_client:
        result = await document_translation_client.get_supported_document_formats()


async def sample_authentication_with_azure_active_directory_async():
    # [START create_dt_client_with_aad_async]
    """DefaultAzureCredential will use the values from these environment
    variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
    """
    from azure.identity.aio import DefaultAzureCredential
    from azure.ai.translation.document.aio import DocumentTranslationClient

    endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]
    credential = DefaultAzureCredential()

    document_translation_client = DocumentTranslationClient(endpoint, credential)
    # [END create_dt_client_with_aad_async]

    # make calls with authenticated client
    async with document_translation_client:
        result = await document_translation_client.get_supported_document_formats()


async def main():
    await sample_authentication_api_key_async()
    await sample_authentication_with_azure_active_directory_async()


if __name__ == "__main__":
    asyncio.run(main())
