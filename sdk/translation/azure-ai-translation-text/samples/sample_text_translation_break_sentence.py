# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_text_translation_break_sentence.py

DESCRIPTION:
    This file contains sample snippets for the Text Translation service.

USAGE:
    python sample_text_translation_break_sentence.py

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


def get_text_sentence_boundaries():
    # [START get_text_sentence_boundaries]
    try:
        from_language = "zh-Hans"
        source_script = "Latn"
        input_text_elements = ["zhè shì gè cè shì。"]

        response = text_translator.find_sentence_boundaries(
            body=input_text_elements, language=from_language, script=source_script
        )
        sentence_boundaries = response[0] if response else None

        if sentence_boundaries:
            detected_language = sentence_boundaries.detected_language
            if detected_language:
                print(
                    f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}."
                )
            print(f"The detected sentence boundaries:")
            for boundary in sentence_boundaries.sent_len:
                print(boundary)

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
        raise
    # [END get_text_sentence_boundaries]


def get_text_sentence_boundaries_auto():
    # [START get_text_sentence_boundaries_auto]
    try:
        input_text_elements = ["This is a test. This is the second sentence."]

        response = text_translator.find_sentence_boundaries(body=input_text_elements)
        sentence_boundaries = response[0] if response else None

        if sentence_boundaries:
            detected_language = sentence_boundaries.detected_language
            if detected_language:
                print(
                    f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}."
                )
            print(f"The detected sentence boundaries:")
            for boundary in sentence_boundaries.sent_len:
                print(boundary)

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
    # [END get_text_sentence_boundaries_auto]
