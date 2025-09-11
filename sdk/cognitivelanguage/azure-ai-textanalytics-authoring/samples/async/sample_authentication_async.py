# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication_async.py
DESCRIPTION:
    This sample demonstrates how to authenticate to the Text Analytics
    **Authoring** service.
    We authenticate using an AzureKeyCredential from azure.core.credentials or a token credential from the
    azure-identity client library.
    See more details about authentication here:
    https://learn.microsoft.com/azure/cognitive-services/authentication
    Note: the endpoint must be formatted to use the custom domain name for your resource:
    https://<NAME-OF-YOUR-RESOURCE>.cognitiveservices.azure.com/
USAGE:
    python sample_authentication_async.py
    Set the environment variables with your own values before running the sample:
    For API Key authentication:
        1) AZURE_TEXT_ENDPOINT - the endpoint to your Text Analytics resource
        2) AZURE_TEXT_KEY      - your Text Analytics API key
    For Azure Active Directory (DefaultAzureCredential) authentication:
        1) AZURE_TEXT_ENDPOINT - the endpoint to your Text Analytics resource
        2) AZURE_CLIENT_ID              - your Azure Active Directory application client ID
        3) AZURE_TENANT_ID              - your Azure Active Directory tenant ID
        4) AZURE_CLIENT_SECRET          - your Azure Active Directory client secret
"""

import os
import asyncio


async def sample_authentication_api_key_async():
    # [START create_text_client_with_key_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics.authoring.aio import TextAuthoringClient

    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    key = os.environ["AZURE_TEXT_KEY"]

    text_client = TextAuthoringClient(endpoint, AzureKeyCredential(key))
    # [END create_text_client_with_key_async]


async def sample_authentication_with_azure_active_directory():
    """DefaultAzureCredential will use the values from these environment
    variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
    """
    print("\n.. authentication_with_azure_active_directory")
    from azure.ai.textanalytics.authoring.aio import TextAuthoringClient
    from azure.identity.aio import DefaultAzureCredential

    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    text_client = TextAuthoringClient(endpoint, credential=credential)


async def main():
    await sample_authentication_api_key_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
