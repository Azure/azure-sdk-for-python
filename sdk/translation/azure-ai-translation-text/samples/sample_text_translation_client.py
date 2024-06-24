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

        2) AZURE_TEXT_TRANSLATION_APIKEY - the API key to your Text Translation resource.
        3) AZURE_TEXT_TRANSLATION_REGION - the Azure Region of your Text Translation resource.
        4) AZURE_TEXT_TRANSLATION_RESOURCE_ID - the Azure Resource Id path
"""

import os

from static_access_token_credential import StaticAccessTokenCredential


# -------------------------------------------------------------------------
# Text translation client
# -------------------------------------------------------------------------
def create_text_translation_client_with_endpoint():
    from azure.ai.translation.text import TextTranslationClient

    endpoint = "http://localhost"
    # [START create_text_translation_client_with_endpoint]
    text_translator = TextTranslationClient(endpoint=endpoint)
    # [END create_text_translation_client_with_endpoint]
    return text_translator


def create_text_translation_client_with_credential():
    from azure.ai.translation.text import TextTranslationClient
    from azure.core.credentials import AzureKeyCredential

    apikey = os.environ["AZURE_TEXT_TRANSLATION_APIKEY"]
    region = os.environ["AZURE_TEXT_TRANSLATION_REGION"]
    # [START create_text_translation_client_with_credential]
    credential = AzureKeyCredential(apikey)
    text_translator = TextTranslationClient(credential=credential, region=region)
    # [END create_text_translation_client_with_credential]
    return text_translator

def create_text_translation_client_custom_with_credential():
    from azure.ai.translation.text import TextTranslationClient
    from azure.core.credentials import AzureKeyCredential

    endpoint = os.environ["AZURE_TEXT_TRANSLATION_ENDPOINT"]
    apikey = os.environ["AZURE_TEXT_TRANSLATION_APIKEY"]
    # [START create_text_translation_client_custom_with_credential]
    credential = AzureKeyCredential(apikey)
    text_translator = TextTranslationClient(credential=credential, endpoint=endpoint)
    # [END create_text_translation_client_custom_with_credential]
    return text_translator

def create_text_translation_client_with_cognitive_services_token():
    from azure.ai.translation.text import TextTranslationClient
    from azure.core.credentials import TokenCredential

    apikey = os.environ["AZURE_TEXT_TRANSLATION_APIKEY"]
    region = os.environ["AZURE_TEXT_TRANSLATION_REGION"]

    credential: TokenCredential = StaticAccessTokenCredential(apikey, region)

    # [START create_text_translation_client_with_cognitive_services_token]
    client = TextTranslationClient(credential=credential, audience="https://api.microsofttranslator.com/")
    # [END create_text_translation_client_with_cognitive_services_token]

def create_text_translation_client_with_entra_id_token():
    from azure.ai.translation.text import TextTranslationClient
    from azure.identity import DefaultAzureCredential

    region = os.environ["AZURE_TEXT_TRANSLATION_REGION"]
    resource_id = os.environ["AZURE_TEXT_TRANSLATION_RESOURCE_ID"]

    # [START create_text_translation_client_with_entra_id_token]
    credential = DefaultAzureCredential()
    client = TextTranslationClient(credential=credential, region=region, resource_id=resource_id)
    # [END create_text_translation_client_with_entra_id_token]

def create_text_translation_client_custom_with_entra_id_token():
    from azure.ai.translation.text import TextTranslationClient
    from azure.identity import DefaultAzureCredential

    endpoint = os.environ["AZURE_TEXT_TRANSLATION_ENDPOINT"]

    # [START create_text_translation_client_custom_with_entra_id_token]
    credential = DefaultAzureCredential()
    client = TextTranslationClient(credential=credential, endpoint=endpoint)
    # [END create_text_translation_client_custom_with_entra_id_token]
