# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_text_translation_translate.py

DESCRIPTION:
    This file contains sample snippets for the Text Translation service.

USAGE:
    python sample_text_translation_translate.py

    Set the text translation endpoint environment variables with your own value before running the samples:
        
        1) AZURE_TEXT_TRANSLATION_ENDPOINT - the endpoint to your Text Translation resource.
        Note: the endpoint must be formatted to use the custom domain name for your resource:
        https:\\<NAME-OF-YOUR-RESOURCE>.cognitiveservices.azure.com\
                    
    The create_text_translation_client_with_credential call requires additional variables:
        2) AZURE_TEXT_TRANSLATION_APIKEY - the API key to your Text Translation resource.
        3) AZURE_TEXT_TRANSLATION_REGION - the Azure Region of your Text Translation resource.
"""

from azure.core.exceptions import HttpResponseError
from azure.ai.translation.text.models import TextType, ProfanityAction, ProfanityMarker

# -------------------------------------------------------------------------
# Text translation client
# -------------------------------------------------------------------------
import sample_text_translation_client

text_translator = sample_text_translation_client.create_text_translation_client_with_credential()


# -------------------------------------------------------------------------
# Get text translation
# -------------------------------------------------------------------------
def get_text_translation():
    # [START get_text_translation]
    try:
        from_language = "en"
        to_language = ["cs"]
        input_text_elements = ["This is a test"]

        response = text_translator.translate(
            body=input_text_elements, to_language=to_language, from_language=from_language
        )
        translation = response[0] if response else None

        if translation:
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
        raise
    # [END get_text_translation]


def get_text_translation_auto():
    # [START get_text_translation_auto]
    try:
        to_language = ["cs"]
        input_text_elements = ["This is a test"]

        response = text_translator.translate(body=input_text_elements, to_language=to_language)
        translation = response[0] if response else None

        if translation:
            detected_language = translation.detected_language
            if detected_language:
                print(
                    f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}."
                )
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
        raise
    # [END get_text_translation_auto]


def get_text_translation_with_transliteration():
    # [START get_text_translation_with_transliteration]
    try:
        from_script = "Latn"
        from_language = "ar"
        to_script = "Latn"
        to_language = ["zh-Hans"]
        input_text_elements = ["hudha akhtabar."]

        response = text_translator.translate(
            body=input_text_elements,
            to_language=to_language,
            from_script=from_script,
            from_language=from_language,
            to_script=to_script,
        )
        translation = response[0] if response else None

        if translation:
            if translation.source_text:
                print(f"Source Text: {translation.source_text.text}")
            first_translation = translation.translations[0]
            if first_translation:
                print(f"Translation: '{first_translation.text}'.")
                transliteration = first_translation.transliteration
                if transliteration:
                    print(f"Transliterated text ({transliteration.script}): {transliteration.text}")

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
        raise
    # [END get_text_translation_with_transliteration]


def get_text_translation_multiple_inputs():
    # [START get_text_translation_multiple_inputs]
    try:
        to_language = ["cs"]
        input_text_elements = [
            "This is a test.",
            "Esto es una prueba.",
            "Dies ist ein Test.",
        ]

        translations = text_translator.translate(body=input_text_elements, to_language=to_language)

        for translation in translations:
            print(
                f"Detected languages of the input text: {translation.detected_language.language if translation.detected_language else None} with score: {translation.detected_language.score if translation.detected_language else None}."
            )
            print(
                f"Text was translated to: '{translation.translations[0].to if translation.translations else None}' and the result is: '{translation.translations[0].text if translation.translations else None}'."
            )

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
    # [END get_text_translation_multiple_inputs]


def get_text_translation_multiple_languages():
    # [START get_text_translation_multiple_languages]
    try:
        to_language = ["cs", "es", "de"]
        input_text_elements = ["This is a test"]

        response = text_translator.translate(body=input_text_elements, to_language=to_language)
        translation = response[0] if response else None

        if translation:
            detected_language = translation.detected_language
            if detected_language:
                print(
                    f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}."
                )
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
    # [END get_text_translation_multiple_languages]


def get_text_translation_type():
    # [START get_text_translation_type]
    try:
        text_type = TextType.HTML
        to_language = ["cs"]
        input_text_elements = ["<html><body>This <b>is</b> a test.</body></html>"]

        response = text_translator.translate(body=input_text_elements, to_language=to_language, text_type=text_type)
        translation = response[0] if response else None

        if translation:
            detected_language = translation.detected_language
            if detected_language:
                print(
                    f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}."
                )
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
    # [END get_text_translation_type]


def get_text_translation_exclude():
    # [START get_text_translation_exclude]
    try:
        text_type = TextType.HTML
        from_language = "en"
        to_language = ["cs"]
        input_text_elements = [
            '<div class="notranslate">This will not be translated.</div><div>This will be translated. </div>'
        ]

        response = text_translator.translate(
            body=input_text_elements,
            to_language=to_language,
            from_language=from_language,
            text_type=text_type,
        )
        translation = response[0] if response else None

        if translation:
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
    # [END get_text_translation_exclude]


def get_text_translation_entity():
    # [START get_text_translation_entity]
    try:
        from_language = "en"
        to_language = ["cs"]
        input_text_elements = [
            'The word <mstrans:dictionary translation="wordomatic">wordomatic</mstrans:dictionary> is a dictionary entry.'
        ]

        response = text_translator.translate(
            body=input_text_elements, to_language=to_language, from_language=from_language
        )
        translation = response[0] if response else None

        if translation:
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
    # [END get_text_translation_entity]


def get_text_translation_profanity():
    # [START get_text_translation_profanity]
    try:
        profanity_action = ProfanityAction.MARKED
        profanity_maker = ProfanityMarker.ASTERISK
        to_language = ["cs"]
        input_text_elements = ["This is ***."]

        response = text_translator.translate(
            body=input_text_elements,
            to_language=to_language,
            profanity_action=profanity_action,
            profanity_marker=profanity_maker,
        )
        translation = response[0] if response else None

        if translation:
            detected_language = translation.detected_language
            if detected_language:
                print(
                    f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}."
                )
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
    # [END get_text_translation_profanity]


def get_text_translation_alignment():
    # [START get_text_translation_alignment]
    try:
        include_alignment = True
        to_language = ["cs"]
        input_text_elements = ["The answer lies in machine translation."]

        response = text_translator.translate(
            body=input_text_elements, to_language=to_language, include_alignment=include_alignment
        )
        translation = response[0] if response else None

        if translation:
            detected_language = translation.detected_language
            if detected_language:
                print(
                    f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}."
                )
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")
                if translated_text.alignment:
                    print(f"Alignments: {translated_text.alignment.proj}")

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
    # [END get_text_translation_alignment]


def get_text_translation_sentence_length():
    # [START get_text_translation_sentence_length]
    try:
        include_sentence_length = True
        to_language = ["cs"]
        input_text_elements = ["The answer lies in machine translation. This is a test."]

        response = text_translator.translate(
            body=input_text_elements, to_language=to_language, include_sentence_length=include_sentence_length
        )
        translation = response[0] if response else None

        if translation:
            detected_language = translation.detected_language
            if detected_language:
                print(
                    f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}."
                )
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")
                if translated_text.sent_len:
                    print(f"Source Sentence length: {translated_text.sent_len.src_sent_len}")
                    print(f"Translated Sentence length: {translated_text.sent_len.trans_sent_len}")

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
    # [END get_text_translation_sentence_length]


def get_text_translation_custom():
    # [START get_text_translation_custom]
    try:
        category = "<<Category ID>>"
        to_language = ["cs"]
        input_text_elements = ["This is a test"]

        response = text_translator.translate(body=input_text_elements, to_language=to_language, category=category)
        translation = response[0] if response else None

        if translation:
            detected_language = translation.detected_language
            if detected_language:
                print(
                    f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}."
                )
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
    # [END get_text_translation_custom]
