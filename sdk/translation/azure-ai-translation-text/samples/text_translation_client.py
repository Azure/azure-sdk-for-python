# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: text_translation_client.py

DESCRIPTION:
    This file contains sample snippets for the Text Translation service.

USAGE:
    python text_translation_client.py

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
    # [START create_text_translation_client_with_endpoint]    
    from azure.ai.translation.text import TextTranslationClient

    endpoint = os.environ["AZURE_TEXT_TRANSLATION_ENDPOINT"]
    return TextTranslationClient(endpoint)
    # [END create_text_translation_client_with_endpoint]

def create_text_translation_client_with_credential():
    # [START create_text_translation_client_with_credential]
    from azure.ai.translation.text import (TextTranslationClient, TranslatorCredential)

    endpoint = os.environ["AZURE_TEXT_TRANSLATION_ENDPOINT"]
    apikey = os.environ["AZURE_TEXT_TRANSLATION_APIKEY"]
    region = os.environ["AZURE_TEXT_TRANSLATION_REGION"]   
    credential = TranslatorCredential(apikey, region)
    return TextTranslationClient(endpoint, credential)
    # [END create_text_translation_client_with_credential]

