# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_text_translation_authentication.py

DESCRIPTION:
    This sample demonstrates how to authenticate to the Text Translation service.

    There are two supported methods of authentication:
    1) Use a Text Translation API key with AzureKeyCredential from azure.core.credentials.
    2) Use a token credential from azure-identity to authenticate with Azure Active Directory.

    See more details about authentication here:
    https://docs.microsoft.com/azure/cognitive-services/authentication

    Both methods of authentication require a Text Translation endpoint to be included in the client constructor:
    The endpoint must be formatted to use the custom domain name for your resource:
    https://<NAME-OF-YOUR-RESOURCE>.cognitiveservices.azure.com/

USAGE:
    python sample_text_translation_authentication.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_TEXT_TRANSLATION_ENDPOINT - the endpoint to your Text Translation resource.

    For API key authentication, set an environment variable named AZURE_TEXT_TRANSLATION_KEY with your key.
    2) AZURE_TEXT_TRANSLATION_KEY - your Text Translation API key

    For Azure Active Directory authentication, first create an Azure Active Directory application registration:
    https://docs.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
    Next, set environment variables named AZURE_CLIENT_ID, AZURE_TENANT_ID, and AZURE_CLIENT_SECRET with your values.

    3) AZURE_CLIENT_ID - the client ID of your active directory application.
    4) AZURE_TENANT_ID - the tenant ID of your active directory application.
    5) AZURE_CLIENT_SECRET - the secret of your active directory application.
"""

import os


def sample_authentication_api_key():
    # [START create_text_translation_client_with_key]
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.translation.text import TextTranslationClient

    endpoint = os.environ["AZURE_TEXT_TRANSLATION_ENDPOINT"]
    key = os.environ["AZURE_TEXT_TRANSLATION_KEY"]

    text_translation_client = TextTranslationClient(endpoint, AzureKeyCredential(key))
    # [END create_text_translation_client_with_key]

    # make calls with authenticated client
    result = text_translation_client.translate(["hello"], "es");


def sample_authentication_with_azure_active_directory():
    # [START create_text_translation_client_with_aad]
    """DefaultAzureCredential will use the values from these environment
    variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
    """
    from azure.identity import DefaultAzureCredential
    from azure.ai.translation.text import TextTranslationClient

    endpoint = os.environ["AZURE_TEXT_TRANSLATION_ENDPOINT"]
    credential = DefaultAzureCredential()

    text_translation_client = TextTranslationClient(endpoint, credential)
    # [END create_text_translation_client_with_aad]

    # make calls with authenticated client
    result = text_translation_client.translate(["hello"], "es");
