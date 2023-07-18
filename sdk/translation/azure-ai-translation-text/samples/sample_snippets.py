# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_snippets.py

DESCRIPTION:
    This file contains sample snippets for the Text Translation service.

USAGE:
    python sample_snippets.py

    Set the text translation endpoint environment variables with your own value before running the samples:
        AZURE_TEXT_TRANSLATION_ENDPOINT - the endpoint to your Text Translation resource.
    Note: the endpoint must be formatted to use the custom domain name for your resource:
        https:\\<NAME-OF-YOUR-RESOURCE>.cognitiveservices.azure.com\
"""

import os
from azure.core.exceptions import HttpResponseError
from azure.ai.translation.text.models import (InputTextItem, TextType, ProfanityAction, ProfanityMarker)

# -------------------------------------------------------------------------
# Text translation client
# -------------------------------------------------------------------------
def create_text_translation_client():
    # [START create_text_client_with_endpoint]    
    from azure.ai.translation.text import TextTranslationClient

    endpoint = os.environ["AZURE_TEXT_TRANSLATION_ENDPOINT"]
    return TextTranslationClient(endpoint)
    # [END create_text_client_with_endpoint]

text_translator = create_text_translation_client()

# -------------------------------------------------------------------------
# Text translation languages
# -------------------------------------------------------------------------
def get_text_translation_languages():
    # [START get_text_translation_languages]
    try:
        response = response = text_translator.get_languages()

        print(f"Number of supported languages for translate operation: {len(response.translation) if response.translation is not None else 0}")
        print(f"Number of supported languages for transliterate operation: {len(response.transliteration) if response.transliteration is not None else 0}")
        print(f"Number of supported languages for dictionary operations: {len(response.dictionary) if response.dictionary is not None else 0}")

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
        print(f"Error Code: {exception.error.code}")
        print(f"Message: {exception.error.message}")
    # [END get_text_translation_languages]

def get_text_translation_languages_scope():
    # [START get_text_translation_languages_scope]
    try:
        scope = "translation"
        response = response = text_translator.get_languages(scope=scope)

        print(f"Number of supported languages for translate operation: {len(response.translation) if response.translation is not None else 0}")
        print(f"Number of supported languages for transliterate operation: {len(response.transliteration) if response.transliteration is not None else 0}")
        print(f"Number of supported languages for dictionary operations: {len(response.dictionary) if response.dictionary is not None else 0}")

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
        print(f"Error Code: {exception.error.code}")
        print(f"Message: {exception.error.message}")
    # [END get_text_translation_languages_scope]
    
def get_text_translation_languages_culture():
    # [START get_text_translation_languages_culture]
    try:
        accept_language = "es"
        response = response = text_translator.get_languages(accept_language=accept_language)

        print(f"Number of supported languages for translate operation: {len(response.translation) if response.translation is not None else 0}")
        print(f"Number of supported languages for transliterate operation: {len(response.transliteration) if response.transliteration is not None else 0}")
        print(f"Number of supported languages for dictionary operations: {len(response.dictionary) if response.dictionary is not None else 0}")

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
        print(f"Error Code: {exception.error.code}")
        print(f"Message: {exception.error.message}")
    # [END get_text_translation_languages_culture]

# -------------------------------------------------------------------------
# Text translation
# -------------------------------------------------------------------------
def get_text_translation():
    # [START get_text_translation]
    try:
        target_languages = ["cs"]
        input_text_elements = [ 
            InputTextItem(text = "This is a test."),
            InputTextItem(text = "Esto es una prueba."),
            InputTextItem(text = "Dies ist ein Test.")]

        translations = text_translator.translate(content = input_text_elements, to = target_languages)

        for translation in translations:
            print(f"Detected languages of the input text: {translation.detected_language.language if translation.detected_language else None} with score: {translation.detected_language.score if translation.detected_language else None}.")
            print(f"Text was translated to: '{translation.translations[0].to if translation.translations else None}' and the result is: '{translation.translations[0].text if translation.translations else None}'.")

    except HttpResponseError as exception:
        print(f"Error Code: {exception.error.code}")
        print(f"Message: {exception.error.message}")
    # [END get_text_translation]

def get_text_translation_multiple():
    # [START get_text_translation_multiple]
    try:
        target_languages = ["cs", "es", "de"]
        input_text_elements = [ InputTextItem(text = "This is a test") ]

        response = text_translator.translate(content = input_text_elements, to = target_languages)
        translation = response[0] if response else None

        if translation:
            detected_language = translation.detected_language
            if detected_language:
                print(f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}.")
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")

    except HttpResponseError as exception:
        print(f"Error Code: {exception.error.code}")
        print(f"Message: {exception.error.message}")
    # [END get_text_translation_multiple]

def get_text_translation_type():
    # [START get_text_translation_type]
    try:
        text_type = TextType.HTML
        target_languages = ["cs"]
        input_text_elements = [ InputTextItem(text = "<html><body>This <b>is</b> a test.</body></html>") ]

        response = text_translator.translate(content = input_text_elements, to = target_languages, text_type = text_type)
        translation = response[0] if response else None

        if translation:
            detected_language = translation.detected_language
            if detected_language:
                print(f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}.")
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")

    except HttpResponseError as exception:
        print(f"Error Code: {exception.error.code}")
        print(f"Message: {exception.error.message}")
    # [END get_text_translation_type]

def get_text_translation_exclude():
    # [START get_text_translation_exclude]
    try:
        text_type = TextType.HTML
        source_language = "en"
        target_languages = ["cs"]
        input_text_elements = [ InputTextItem(text = "<div class=\"notranslate\">This will not be translated.</div><div>This will be translated. </div>") ]

        response = text_translator.translate(content = input_text_elements, to = target_languages, from_parameter = source_language, text_type=text_type)
        translation = response[0] if response else None

        if translation:
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")

    except HttpResponseError as exception:
        print(f"Error Code: {exception.error.code}")
        print(f"Message: {exception.error.message}")
    # [END get_text_translation_exclude]

def get_text_translation_specify():
    # [START get_text_translation_specify]
    try:
        source_language = "en"
        target_languages = ["cs"]
        input_text_elements = [ InputTextItem(text = "The word <mstrans:dictionary translation=\"wordomatic\">wordomatic</mstrans:dictionary> is a dictionary entry.") ]

        response = text_translator.translate(content = input_text_elements, to = target_languages, from_parameter = source_language)
        translation = response[0] if response else None

        if translation:
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")

    except HttpResponseError as exception:
        print(f"Error Code: {exception.error.code}")
        print(f"Message: {exception.error.message}")
    # [END get_text_translation_specify]

def get_text_translation_profanity():
    # [START get_text_translation_profanity]
    try:
        profanity_action = ProfanityAction.MARKED
        profanity_maker = ProfanityMarker.ASTERISK
        target_languages = ["cs"]
        input_text_elements = [ InputTextItem(text = "This is ***.") ]

        response = text_translator.translate(content = input_text_elements, to = target_languages, profanity_action=profanity_action, profanity_marker=profanity_maker)
        translation = response[0] if response else None

        if translation:
            detected_language = translation.detected_language
            if detected_language:
                print(f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}.")
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")

    except HttpResponseError as exception:
        print(f"Error Code: {exception.error.code}")
        print(f"Message: {exception.error.message}")
    # [END get_text_translation_profanity]

def get_text_translation_alignment():
    # [START get_text_translation_alignment]
    try:
        include_alignment = True
        target_languages = ["cs"]
        input_text_elements = [ InputTextItem(text = "The answer lies in machine translation.") ]

        response = text_translator.translate(content = input_text_elements, to = target_languages, include_alignment = include_alignment)
        translation = response[0] if response else None

        if translation:
            detected_language = translation.detected_language
            if detected_language:
                print(f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}.")
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")
                if (translated_text.alignment):
                    print(f"Alignments: {translated_text.alignment.proj}")

    except HttpResponseError as exception:
        print(f"Error Code: {exception.error.code}")
        print(f"Message: {exception.error.message}")
    # [END get_text_translation_alignment]

def get_text_translation_sentence_length():
    # [START get_text_translation_sentence_length]
    try:
        include_alignment = True
        target_languages = ["cs"]
        input_text_elements = [ InputTextItem(text = "The answer lies in machine translation.") ]

        response = text_translator.translate(content = input_text_elements, to = target_languages, include_alignment = include_alignment)
        translation = response[0] if response else None

        if translation:
            detected_language = translation.detected_language
            if detected_language:
                print(f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}.")
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")
                if (translated_text.alignment):
                    print(f"Alignments: {translated_text.alignment.proj}")

    except HttpResponseError as exception:
        print(f"Error Code: {exception.error.code}")
        print(f"Message: {exception.error.message}")
    # [END get_text_translation_sentence_length]

def get_text_translation_sentence_length():
    # [START get_text_translation_sentence_length]
    try:
        category = "<<Category ID>>"
        target_languages = ["cs"]
        input_text_elements = [ InputTextItem(text = "This is a test") ]

        response = text_translator.translate(content = input_text_elements, to = target_languages, category = category)
        translation = response[0] if response else None

        if translation:
            detected_language = translation.detected_language
            if detected_language:
                print(f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}.")
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")

    except HttpResponseError as exception:
        print(f"Error Code: {exception.error.code}")
        print(f"Message: {exception.error.message}")
    # [END get_text_translation_sentence_length]

def get_dictionary_lookup():
    # [START get_dictionary_lookup]
    try:
        source_language = "en"
        target_language = "es"
        input_text_elements = [ InputTextItem(text = "fly") ]

        response = text_translator.lookup_dictionary_entries(content = input_text_elements, from_parameter = source_language, to = target_language)
        dictionary_entry = response[0] if response else None

        if dictionary_entry:
            print(f"For the given input {len(dictionary_entry.translations)} entries were found in the dictionary.")
            print(f"First entry: '{dictionary_entry.translations[0].display_target}', confidence: {dictionary_entry.translations[0].confidence}.")

    except HttpResponseError as exception:
        print(f"Error Code: {exception.error.code}")
        print(f"Message: {exception.error.message}")
    # [END get_dictionary_lookup]

def get_dictionary_entries():
    # [START get_dictionary_entries]
    try:
        source_language = "en"
        target_language = "es"
        input_text_elements = [ InputTextItem(text = "fly") ]

        response = text_translator.lookup_dictionary_entries(content = input_text_elements, from_parameter = source_language, to = target_language)
        dictionary_entry = response[0] if response else None

        if dictionary_entry:
            print(f"For the given input {len(dictionary_entry.translations)} entries were found in the dictionary.")
            print(f"First entry: '{dictionary_entry.translations[0].display_target}', confidence: {dictionary_entry.translations[0].confidence}.")

    except HttpResponseError as exception:
        print(f"Error Code: {exception.error.code}")
        print(f"Message: {exception.error.message}")
    # [END get_dictionary_entries]