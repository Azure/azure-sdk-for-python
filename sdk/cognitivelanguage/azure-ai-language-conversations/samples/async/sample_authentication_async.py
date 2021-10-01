# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication_asyncasync.py

DESCRIPTION:
    This sample demonstrates how to authenticate to the Conversation Language Understanding (CLU) service.

    There are two supported methods of authentication:
    1) Use a CLU API key with AzureKeyCredential from azure.core.credentials
    2) Use a token credential from azure-identity to authenticate with Azure Active Directory

    See more details about authentication here:
    https://docs.microsoft.com/azure/cognitive-services/authentication

    Note: the endpoint must be formatted to use the custom domain name for your resource:
    https://<NAME-OF-YOUR-RESOURCE>.cognitiveservices.azure.com/

USAGE:
    python sample_authentication_asyncasync.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONVERSATIONS_ENDPOINT - the endpoint to your Conversational Language Understanding resource.
    2) AZURE_CONVERSATIONS_KEY - your Conversational Language Understanding API key
    3) AZURE_CLIENT_ID - the client ID of your active directory application.
    4) AZURE_TENANT_ID - the tenant ID of your active directory application.
    5) AZURE_CLIENT_SECRET - the secret of your active directory application.
"""

import os
import asyncio


async async def sample_authentication_api_key_async():
    # [START create_clu_client_with_key_async]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.conversations.aio import ConversationAnalysisClient

    endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    key = os.environ["AZURE_CONVERSATIONS_KEY"]

    clu_client = ConversationAnalysisClient(endpoint, AzureKeyCredential(key))
    # [END create_clu_client_with_key_async]

async async def sample_authentication_with_azure_active_directory_async():
    # [START create_clu_client_with_aad_async]
    """async defaultAzureCredential will use the values from these environment
    variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
    """
    from azure.identity.aio import async defaultAzureCredential
    from azure.ai.language.conversations.aio import ConversationAnalysisClient

    endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    credential = async defaultAzureCredential()

    clu_client = ConversationAnalysisClient(endpoint, credential)
    # [END create_clu_client_with_aad_async]

async async def main():
    await sample_authentication_api_key_async()
    await sample_authentication_with_azure_active_directory_async()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
