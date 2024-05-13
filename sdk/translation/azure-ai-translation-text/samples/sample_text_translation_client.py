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
                    
    The create_text_translation_client_with_credential call requires additional variables:
        2) AZURE_TEXT_TRANSLATION_APIKEY - the API key to your Text Translation resource.
        3) AZURE_TEXT_TRANSLATION_REGION - the Azure Region of your Text Translation resource.
"""

import os


# -------------------------------------------------------------------------
# Text translation client
# -------------------------------------------------------------------------
def create_text_translation_client_with_endpoint():
    from azure.ai.translation.text import TextTranslationClient

    endpoint = os.environ["AZURE_TEXT_TRANSLATION_ENDPOINT"]
    # [START create_text_translation_client_with_endpoint]
    text_translator = TextTranslationClient(endpoint=endpoint)
    # [END create_text_translation_client_with_endpoint]
    return text_translator


def create_text_translation_client_with_credential():
    from azure.ai.translation.text import TextTranslationClient
    from azure.core.credentials import AzureKeyCredential

    endpoint = os.environ["AZURE_TEXT_TRANSLATION_ENDPOINT"]
    apikey = os.environ["AZURE_TEXT_TRANSLATION_APIKEY"]
    region = os.environ["AZURE_TEXT_TRANSLATION_REGION"]
    # [START create_text_translation_client_with_credential]
    credential = AzureKeyCredential(apikey)
    text_translator = TextTranslationClient(credential=credential, endpoint=endpoint, region=region)
    # [END create_text_translation_client_with_credential]
    return text_translator
