# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_text_translation_languages.py

DESCRIPTION:
    This file contains sample snippets for the Text Translation service.

USAGE:
    python sample_text_translation_languages.py

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

text_translator = sample_text_translation_client.create_text_translation_client_with_endpoint()


# -------------------------------------------------------------------------
# Get text translation languages
# -------------------------------------------------------------------------
def get_text_translation_languages():
    # [START get_text_translation_languages]
    try:
        response = text_translator.get_supported_languages()

        print(
            f"Number of supported languages for translate operation: {len(response.translation) if response.translation is not None else 0}"
        )
        print(
            f"Number of supported languages for transliterate operation: {len(response.transliteration) if response.transliteration is not None else 0}"
        )
        print(
            f"Number of supported languages for dictionary operations: {len(response.dictionary) if response.dictionary is not None else 0}"
        )

        if response.translation is not None:
            print("Translation Languages:")
            for key, value in response.translation.items():
                print(f"{key} -- name: {value.name} ({value.native_name})")

        if response.transliteration is not None:
            print("Transliteration Languages:")
            for key, value in response.transliteration.items():
                print(f"{key} -- name: {value.name}, supported script count: {len(value.scripts)}")

        if response.dictionary is not None:
            print("Dictionary Languages:")
            for key, value in response.dictionary.items():
                print(f"{key} -- name: {value.name}, supported target languages count: {len(value.translations)}")

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
        raise
    # [END get_text_translation_languages]


def get_text_translation_languages_scope():
    # [START get_text_translation_languages_scope]
    try:
        scope = "translation"
        response = text_translator.get_supported_languages(scope=scope)

        print(
            f"Number of supported languages for translate operation: {len(response.translation) if response.translation is not None else 0}"
        )
        print(
            f"Number of supported languages for transliterate operation: {len(response.transliteration) if response.transliteration is not None else 0}"
        )
        print(
            f"Number of supported languages for dictionary operations: {len(response.dictionary) if response.dictionary is not None else 0}"
        )

        if response.translation is not None:
            print("Translation Languages:")
            for key, value in response.translation.items():
                print(f"{key} -- name: {value.name} ({value.native_name})")

        if response.transliteration is not None:
            print("Transliteration Languages:")
            for key, value in response.transliteration.items():
                print(f"{key} -- name: {value.name}, supported script count: {len(value.scripts)}")

        if response.dictionary is not None:
            print("Dictionary Languages:")
            for key, value in response.dictionary.items():
                print(f"{key} -- name: {value.name}, supported target languages count: {len(value.translations)}")

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
        raise
    # [END get_text_translation_languages_scope]


def get_text_translation_languages_culture():
    # [START get_text_translation_languages_culture]
    try:
        accept_language = "es"
        response = text_translator.get_supported_languages(accept_language=accept_language)

        print(
            f"Number of supported languages for translate operation: {len(response.translation) if response.translation is not None else 0}"
        )
        print(
            f"Number of supported languages for transliterate operation: {len(response.transliteration) if response.transliteration is not None else 0}"
        )
        print(
            f"Number of supported languages for dictionary operations: {len(response.dictionary) if response.dictionary is not None else 0}"
        )

        if response.translation is not None:
            print("Translation Languages:")
            for key, value in response.translation.items():
                print(f"{key} -- name: {value.name} ({value.native_name})")

        if response.transliteration is not None:
            print("Transliteration Languages:")
            for key, value in response.transliteration.items():
                print(f"{key} -- name: {value.name}, supported script count: {len(value.scripts)}")

        if response.dictionary is not None:
            print("Dictionary Languages:")
            for key, value in response.dictionary.items():
                print(f"{key} -- name: {value.name}, supported target languages count: {len(value.translations)}")

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
        raise
    # [END get_text_translation_languages_culture]
