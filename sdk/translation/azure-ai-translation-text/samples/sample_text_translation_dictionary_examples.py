# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_text_translation_dictionary_examples.py

DESCRIPTION:
    This file contains sample snippets for the Text Translation service.

USAGE:
    python sample_text_translation_dictionary_examples.py

    Set the text translation endpoint environment variables with your own value before running the samples:
        
        1) AZURE_TEXT_TRANSLATION_ENDPOINT - the endpoint to your Text Translation resource.
        Note: the endpoint must be formatted to use the custom domain name for your resource:
        https:\\<NAME-OF-YOUR-RESOURCE>.cognitiveservices.azure.com\
                    
    The create_text_translation_client_with_credential call requires additional variables:
        2) AZURE_TEXT_TRANSLATION_APIKEY - the API key to your Text Translation resource.
        3) AZURE_TEXT_TRANSLATION_REGION - the Azure Region of your Text Translation resource.
"""
from azure.core.exceptions import HttpResponseError
from azure.ai.translation.text.models import DictionaryExampleTextItem

# -------------------------------------------------------------------------
# Text translation client
# -------------------------------------------------------------------------
import sample_text_translation_client

text_translator = sample_text_translation_client.create_text_translation_client_with_credential()


# -------------------------------------------------------------------------
# Dictionary Lookup
# -------------------------------------------------------------------------
def get_text_translation_dictionary_examples():
    # [START get_text_translation_dictionary_examples]
    try:
        from_language = "en"
        to_language = "es"
        input_text_elements = [DictionaryExampleTextItem(text="fly", translation="volar")]

        response = text_translator.lookup_dictionary_examples(
            body=input_text_elements, from_language=from_language, to_language=to_language
        )
        dictionary_entry = response[0] if response else None

        if dictionary_entry:
            print(f"For the given input {len(dictionary_entry.examples)} entries were found in the dictionary.")
            print(
                f"First example: '{dictionary_entry.examples[0].target_prefix}{dictionary_entry.examples[0].target_term}{dictionary_entry.examples[0].target_suffix}'."
            )

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
    raise
    # [END get_text_translation_dictionary_examples]
