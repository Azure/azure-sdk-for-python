# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_text_translation_transliterate.py

DESCRIPTION:
    This file contains sample snippets for the Text Translation service.

USAGE:
    python sample_text_translation_transliterate.py

    Set the text translation endpoint environment variables with your own value before running the samples:
        
        1) AZURE_TEXT_TRANSLATION_ENDPOINT - the endpoint to your Text Translation resource.
        Note: the endpoint must be formatted to use the custom domain name for your resource:
        https:\\<NAME-OF-YOUR-RESOURCE>.cognitiveservices.azure.com\
                    
    The create_text_translation_client_with_credential call requires additional variables:
        2) AZURE_TEXT_TRANSLATION_APIKEY - the API key to your Text Translation resource.
        3) AZURE_TEXT_TRANSLATION_REGION - the Azure Region of your Text Translation resource.
"""

from azure.core.exceptions import HttpResponseError

# -------------------------------------------------------------------------
# Text translation client
# -------------------------------------------------------------------------
import sample_text_translation_client

text_translator = sample_text_translation_client.create_text_translation_client_with_credential()


# -------------------------------------------------------------------------
# Text translation transliteration
# -------------------------------------------------------------------------
def get_text_transliteration():
    # [START get_text_transliteration]
    try:
        language = "zh-Hans"
        from_script = "Hans"
        to_script = "Latn"
        input_text_elements = ["这是个测试。"]

        response = text_translator.transliterate(
            body=input_text_elements,
            language=language,
            from_script=from_script,
            to_script=to_script,
        )
        transliteration = response[0] if response else None

        if transliteration:
            print(
                f"Input text was transliterated to '{transliteration.script}' script. Transliterated text: '{transliteration.text}'."
            )

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
        raise
    # [END get_text_transliteration]
