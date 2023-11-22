# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_text_translation_client.py

DESCRIPTION:
    This file contains sample snippets for the Text Translation service.

USAGE:
    python sample_text_translation_client.py

    Set the text translation endpoint environment variables with your own value before running the samples:
        
        1) AZURE_TEXT_TRANSLATION_ENDPOINT - the endpoint to your Text Translation resource.
        Note: the endpoint must be formatted to use the custom domain name for your resource:
        https:\\<NAME-OF-YOUR-RESOURCE>.cognitiveservices.azure.com\
                    
    The create_text_translation_client_with_credential call requires these additional environment variables:
        1) AZURE_TEXT_TRANSLATION_APIKEY - the API key to your Text Translation resource.
        2) AZURE_TEXT_TRANSLATION_REGION - the Azure Region of your Text Translation resource.

    The create_text_translation_client_with_aad_credential call requires these additional environment variables:
        1) AZURE_CLIENT_ID - the client ID of your Text Translation AAD application.
        2) AZURE_TENANT_ID - the tenant ID of your Text Translation AAD application.
        3) AZURE_CLIENT_SECRET - the secret of your Text Translation AAD application.
"""

import os

# -------------------------------------------------------------------------
# Text translation client
# -------------------------------------------------------------------------
def create_text_translation_client_with_endpoint():
    # [START create_text_translation_client_with_endpoint]
    from azure.ai.translation.text import TextTranslationClient

    endpoint = os.environ["AZURE_TEXT_TRANSLATION_ENDPOINT"]
    
    text_translator = TextTranslationClient(endpoint=endpoint, credential=None)
    # [END create_text_translation_client_with_endpoint]
    return text_translator


def create_text_translation_client_with_credential():
    # [START create_text_translation_client_with_credential]
    from azure.ai.translation.text import TextTranslationClient, TranslatorCredential

    endpoint = os.environ["AZURE_TEXT_TRANSLATION_ENDPOINT"]
    apikey = os.environ["AZURE_TEXT_TRANSLATION_APIKEY"]
    region = os.environ["AZURE_TEXT_TRANSLATION_REGION"]

    credential = TranslatorCredential(apikey, region)
    text_translator = TextTranslationClient(endpoint=endpoint, credential=credential)
    # [END create_text_translation_client_with_credential]
    return text_translator

def create_text_translation_client_with_aad_credential():
    # [START create_text_translation_client_with_aad_credential]
    """DefaultAzureCredential will use the values from these environment
    variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
    """
    from azure.identity import DefaultAzureCredential
    from azure.ai.translation.text import TextTranslationClient

    endpoint = os.environ["AZURE_TEXT_TRANSLATION_ENDPOINT"]
    credential = DefaultAzureCredential()

    text_translator = TextTranslationClient(endpoint=endpoint, credential=credential)
    # [END create_text_translation_client_with_aad_credential]
    return text_translator
