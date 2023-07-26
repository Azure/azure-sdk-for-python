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
        AZURE_TEXT_TRANSLATION_ENDPOINT - the endpoint to your Text Translation resource.
    Note: the endpoint must be formatted to use the custom domain name for your resource:
        https:\\<NAME-OF-YOUR-RESOURCE>.cognitiveservices.azure.com\
"""

import os

# -------------------------------------------------------------------------
# Text translation client
# -------------------------------------------------------------------------
def create_text_translation_client():
    # [START create_text_client_with_endpoint]    
    from azure.ai.translation.text import TextTranslationClient

    endpoint = os.environ["AZURE_TEXT_TRANSLATION_ENDPOINT"]
    return TextTranslationClient(endpoint)
    # [END create_text_client_with_endpoint]