# pylint: disable=line-too-long,useless-suppression
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
from azure.ai.translation.text.models import TranslateInputItem, TranslationTarget, TextType, ProfanityAction, ProfanityMarker

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
                print(f"Text was translated to: '{translated_text.language}' and the result is: '{translated_text.text}'.")

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
                print(f"Text was translated to: '{translated_text.language}' and the result is: '{translated_text.text}'.")

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
        raise
    # [END get_text_translation_auto]


def get_text_translation_with_llm():
    # [START get_text_translation_with_llm]
    try:
        llm_model_name = "gpt-4o-mini"
        tone = "formal"
        gender = "female"
        to_language = "zh-Hans"
        input_text = "This is a test"
        input_text_element = TranslateInputItem(
            text=input_text,
            targets=[TranslationTarget(language=to_language, deployment_name=llm_model_name, tone=tone, gender=gender)],
        )

        response = text_translator.translate(body=[input_text_element])
        translation = response[0] if response else None

        if translation:
            detected_language = translation.detected_language
            if detected_language:
                print(
                    f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}."
                )
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.language}' and the result is: '{translated_text.text}' using LLM.")
    
    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
        raise
    # [END get_text_translation_with_llm]


def get_text_translation_with_transliteration():
    # [START get_text_translation_with_transliteration]
    try:
        from_script = "Latn"
        from_language = "ar"
        to_script = "Latn"
        to_language = "zh-Hans"
        input_text = "hudha akhtabar."
        input_text_element = TranslateInputItem(
            text=input_text,
            targets=[TranslationTarget(language=to_language, script=to_script)],
            language=from_language,
            script=from_script,
        )

        response = text_translator.translate(body=[input_text_element])
        translation = response[0] if response else None

        if translation:
            first_translation = translation.translations[0]
            if first_translation:
                print(f"Translation in transliteration script: '{first_translation.text}'.")

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
                f"Text was translated to: '{translation.translations[0].language if translation.translations else None}' and the result is: '{translation.translations[0].text if translation.translations else None}'."
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
                print(f"Text was translated to: '{translated_text.language}' and the result is: '{translated_text.text}'.")

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
    # [END get_text_translation_multiple_languages]


def get_text_translation_type():
    # [START get_text_translation_type]
    try:
        text_type = TextType.HTML
        to_language = "cs"
        input_text = "<html><body>This <b>is</b> a test.</body></html>"
        input_text_element = TranslateInputItem(
            text=input_text,
            targets=[TranslationTarget(language=to_language)],
            text_type=text_type,
        )

        response = text_translator.translate(body=[input_text_element])
        translation = response[0] if response else None

        if translation:
            detected_language = translation.detected_language
            if detected_language:
                print(
                    f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}."
                )
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.language}' and the result is: '{translated_text.text}'.")

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
        to_language = "cs"
        input_text = '<div class="notranslate">This will not be translated.</div><div>This will be translated. </div>'
        input_text_element = TranslateInputItem(
            text=input_text,
            targets=[TranslationTarget(language=to_language)],
            language=from_language,
            text_type=text_type,
        )

        response = text_translator.translate(body=[input_text_element])
        translation = response[0] if response else None

        if translation:
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.language}' and the result is: '{translated_text.text}'.")

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
    # [END get_text_translation_exclude]


def get_text_translation_entity():
    # [START get_text_translation_entity]
    try:
        from_language = "en"
        to_language = "cs"
        input_text = 'The word <mstrans:dictionary translation="wordomatic">wordomatic</mstrans:dictionary> is a dictionary entry.'
        input_text_element = TranslateInputItem(
            text=input_text,
            targets=[TranslationTarget(language=to_language)],
            language=from_language,
        )

        response = text_translator.translate(body=[input_text_element])
        translation = response[0] if response else None

        if translation:
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.language}' and the result is: '{translated_text.text}'.")

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
        to_language = "cs"
        input_text = "This is ***."
        input_text_element = TranslateInputItem(
            text=input_text,
            targets=[TranslationTarget(language=to_language, profanity_action=profanity_action, profanity_marker=profanity_maker)],
        )

        response = text_translator.translate(body=[input_text_element])
        translation = response[0] if response else None

        if translation:
            detected_language = translation.detected_language
            if detected_language:
                print(
                    f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}."
                )
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.language}' and the result is: '{translated_text.text}'.")

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
    # [END get_text_translation_profanity]


def get_text_translation_custom():
    # [START get_text_translation_custom]
    try:
        category = "<<Category ID>>"
        to_language = "cs"
        input_text = "This is a test"
        input_text_element = TranslateInputItem(
            text=input_text,
            targets=[TranslationTarget(language=to_language, deployment_name=category)],
        )

        response = text_translator.translate(body=[input_text_element])
        translation = response[0] if response else None

        if translation:
            detected_language = translation.detected_language
            if detected_language:
                print(
                    f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}."
                )
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.language}' and the result is: '{translated_text.text}'.")

    except HttpResponseError as exception:
        if exception.error is not None:
            print(f"Error Code: {exception.error.code}")
            print(f"Message: {exception.error.message}")
    # [END get_text_translation_custom]
