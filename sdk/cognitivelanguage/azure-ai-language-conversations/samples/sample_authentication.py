# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication.py

DESCRIPTION:
    This sample demonstrates how to authenticate to the Conversational Language Understanding service.

    There are two supported methods of authentication:
    1) Use a Conversational Language Understanding API key with AzureKeyCredential from azure.core.credentials
    2) Use a token credential from azure-identity to authenticate with Azure Active Directory

    See more details about authentication here:
    https://docs.microsoft.com/azure/cognitive-services/authentication

    Note: the endpoint must be formatted to use the custom domain name for your resource:
    https://<NAME-OF-YOUR-RESOURCE>.cognitiveservices.azure.com/

USAGE:
    python sample_authentication.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONVERSATIONS_ENDPOINT - the endpoint to your Conversational Language Understanding resource.
    2) AZURE_CONVERSATIONS_KEY - your Conversational Language Understanding API key
    3) AZURE_CLIENT_ID - the client ID of your active directory application.
    4) AZURE_TENANT_ID - the tenant ID of your active directory application.
    5) AZURE_CLIENT_SECRET - the secret of your active directory application.
"""

import os


def sample_authentication_api_key():
    # [START create_dt_client_with_key]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.language.conversations import ConversationAnalysisClient


    endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    key = os.environ["AZURE_CONVERSATIONS_KEY"]

    clu_client = ConversationAnalysisClient(endpoint, AzureKeyCredential(key))
    # [END create_clu_client_with_key]


def sample_authentication_with_azure_active_directory():
    # [START create_dt_client_with_aad]
    """DefaultAzureCredential will use the values from these environment
    variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
    """
    from azure.identity import DefaultAzureCredential
    from azure.ai.language.conversations import ConversationAnalysisClient

    endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    credential = DefaultAzureCredential()

    clu_client = ConversationAnalysisClient(endpoint, credential)
    # [END create_dt_client_with_aad]


if __name__ == '__main__':
    sample_authentication_api_key()
    sample_authentication_with_azure_active_directory()
