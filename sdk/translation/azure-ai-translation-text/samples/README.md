---
page_type: sample
languages:
- python
products:
- azure
- cognitive-services
- azure-text-translator
name: azure.ai.translation.text samples for Python
description: Samples for the azure.ai.translation.text client library.
---

# Azure Text Translator client library for Python

Translator Service is a cloud-based neural machine translation service that is part of the Azure Cognitive Services family of REST APIs and can be used with any operating system. This client library offers the following features:

* Create Translation Client
* Get Supported Languages
* Translate
* Transliterate
* Break Sentence
* Dictionary Lookup
* Dictionary Examples

See the [README][README] of the Text Translator client library for more information, including useful links and instructions.

## Common scenarios samples

# Create Client

You can create Translator resource following [Create a Translator resource][translator_resource_create].  For general information about authentication with a cognitive services resource please refer to the documentation [here][cognitive_auth].

To get a list of languages you can create a new `TextTranslationClient` without any authentication. You will only need your `endpoint``.  The values of the `endpoint` variable can be retrieved from environment variables, configuration settings, or any other secure approach that works for your application.

Four different types of authentication are available for different types of endpoints: global, regional, token and Entra (Azure Active Directory).  For details about each including curl examples refer to the documentation available [here][authentication_details].  These samples demonstrate API Key and Entra (AAD) authentication.

<!-- SNIPPET: sample_text_translation_client.create_text_translation_client_with_endpoint -->

```python
from azure.ai.translation.text import TextTranslationClient

endpoint = os.environ["AZURE_TEXT_TRANSLATION_ENDPOINT"]

text_translator = TextTranslationClient(endpoint=endpoint, credential=None)
```

<!-- END SNIPPET -->

## API Key Authentication
A constructor is provided that uses a TextTranslationCredential.  In addition to `endpoint`, this function requires configuring an `apikey` and `region` to create the credential.  The values of the `endpoint`, `apiKey` and `region` variables can be retrieved from environment variables, configuration settings, or any other secure approach that works for your application.  Samples are presented using environment variables.  For additional information about resource creation and how to obtain the endpoint and secrets refer this [document][resource_details].

<!-- SNIPPET: sample_text_translation_client.create_text_translation_client_with_credential -->

```python
from azure.ai.translation.text import TextTranslationClient, TranslatorCredential

endpoint = os.environ["AZURE_TEXT_TRANSLATION_ENDPOINT"]
apikey = os.environ["AZURE_TEXT_TRANSLATION_APIKEY"]
region = os.environ["AZURE_TEXT_TRANSLATION_REGION"]

credential = TranslatorCredential(apikey, region)
text_translator = TextTranslationClient(endpoint=endpoint, credential=credential)
```

<!-- END SNIPPET -->

## Entra (Azure Active Directory) Authentication

`AzureKeyCredential` authentication is used in most of the examples, but you can also authenticate with Entra (Azure Active Directory) using the [Azure Identity library][azure_identity].  Create a [custom subdomain][custom_subdomain] for your resource in order to use this type of authentication.  Use this value for the `endpoint` variable for `AZURE_TEXT_TRANSLATION_ENDPOINT`.  Only custom subdomains are supported.

To use the [DefaultAzureCredential][DefaultAzureCredential] provider shown below, install the Azure.Identity package:

```powershell
pip install azure-identity
```

You will also need to [register a new AAD application][register_aad_app] and [grant access][aad_grant_access] to your Translator resource by assigning the `"Cognitive Services User"` role to your service principal.  Additional information about Entra authentication is available [here][custom_details].

Set the values of the `client ID`, `tenant ID`, and `client secret` of the AAD application as environment variables: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`.

<!-- SNIPPET: sample_text_translation_client.create_text_translation_client_with_aad_credential -->

```python
from azure.identity import DefaultAzureCredential
from azure.ai.translation.text import TextTranslationClient

endpoint = os.environ["AZURE_TEXT_TRANSLATION_ENDPOINT"]
credential = DefaultAzureCredential()

text_translator = TextTranslationClient(endpoint=endpoint, credential=credential)
```

<!-- END SNIPPET -->

# Get Languages

This sample demonstrates how to get languages that are supported by other operations.

## Get Supported Languages for all other operations

This will return language metadata from all supported scopes.

<!-- SNIPPET: sample_text_translation_languages.get_text_translation_languages -->

```python
try:
    response = text_translator.get_languages()

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
```

<!-- END SNIPPET -->

### Get Supported Languages for a given scope

You can limit the scope of the response of the languages API by providing the optional parameter `scope`. A comma-separated list of names defining the group of languages to return. Allowed group names are: `translation`, `transliteration` and `dictionary`. If no scope is given, then all groups are returned, which is equivalent to passing `translation,transliteration,dictionary`.

<!-- SNIPPET: sample_text_translation_languages.get_text_translation_languages_scope -->

```python
try:
    scope = "translation"
    response = text_translator.get_languages(scope=scope)

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
```

<!-- END SNIPPET -->

### Get Languages in a given culture

You can select the language to use for user interface strings. Some of the fields in the response are names of languages or names of regions. Use this parameter to define the language in which these names are returned. The language is specified by providing a well-formed BCP 47 language tag. For instance, use the value `fr` to request names in French or use the value `zh-Hant` to request names in Chinese Traditional.
Names are provided in the English language when a target language is not specified or when localization is not available.

<!-- SNIPPET: sample_text_translation_languages.get_text_translation_languages_culture -->

```python
try:
    accept_language = "es"
    response = text_translator.get_languages(accept_language=accept_language)

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
```

<!-- END SNIPPET -->

# Translate

### Translate text

Translate text from known source language to target language.

<!-- SNIPPET: sample_text_translation_translate.get_text_translation -->

```python
try:
    source_language = "en"
    target_languages = ["cs"]
    input_text_elements = [InputTextItem(text="This is a test")]

    response = text_translator.translate(
        request_body=input_text_elements, to=target_languages, from_parameter=source_language
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
```

<!-- END SNIPPET -->

### Translate with auto-detection

You can omit source language of the input text. In this case, API will try to auto-detect the language.

> Note that you must provide the source language rather than autodetection when using the dynamic dictionary feature.

> Note you can use `suggestedFrom` parameter that specifies a fallback language if the language of the input text can't be identified. Language autodetection is applied when the from parameter is omitted. If detection fails, the suggestedFrom language will be assumed.

<!-- SNIPPET: sample_text_translation_translate.get_text_translation_auto -->

```python
try:
    target_languages = ["cs"]
    input_text_elements = [InputTextItem(text="This is a test")]

    response = text_translator.translate(request_body=input_text_elements, to=target_languages)
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
```

<!-- END SNIPPET -->

### Translate with Transliteration

You can combine both Translation and Transliteration in one Translate call. Your source Text can be in non-standard Script of a language as well as you can ask for non-standard Script of a target language.

<!-- SNIPPET: sample_text_translation_translate.get_text_translation_with_transliteration -->

```python
try:
    from_script = "Latn"
    from_language = "ar"
    to_script = "Latn"
    target_languages = ["zh-Hans"]
    input_text_elements = [InputTextItem(text="hudha akhtabar.")]

    response = text_translator.translate(
        request_body=input_text_elements,
        to=target_languages,
        from_script=from_script,
        from_parameter=from_language,
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
```

<!-- END SNIPPET -->

### Translate multiple input texts

You can translate multiple text elements with a various length. Each input element can be in different language (source language parameter needs to be omitted and language auto-detection is used). Refer to [Request limits for Translator](https://learn.microsoft.com/azure/cognitive-services/translator/request-limits) for current limits.

<!-- SNIPPET: sample_text_translation_translate.get_text_translation_multiple_inputs -->

```python
try:
    target_languages = ["cs"]
    input_text_elements = [
        InputTextItem(text="This is a test."),
        InputTextItem(text="Esto es una prueba."),
        InputTextItem(text="Dies ist ein Test."),
    ]

    translations = text_translator.translate(request_body=input_text_elements, to=target_languages)

    for translation in translations:
        print(
            f"Detected languages of the input text: {translation.detected_language.language if translation.detected_language else None} with score: {translation.detected_language.score if translation.detected_language else None}."
        )
        print(
            f"Text was translated to: '{translation.translations[0].to if translation.translations else None}' and the result is: '{translation.translations[0].text if translation.translations else None}'."
        )

except HttpResponseError as exception:
    print(f"Error Code: {exception.error.code}")
    print(f"Message: {exception.error.message}")
```

<!-- END SNIPPET -->

### Translate multiple target languages

You can provide multiple target languages which results to each input element be translated to all target languages.

<!-- SNIPPET: sample_text_translation_translate.get_text_translation_multiple_languages -->

```python
try:
    target_languages = ["cs", "es", "de"]
    input_text_elements = [InputTextItem(text="This is a test")]

    response = text_translator.translate(request_body=input_text_elements, to=target_languages)
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
    print(f"Error Code: {exception.error.code}")
    print(f"Message: {exception.error.message}")
```

<!-- END SNIPPET -->

### Translate different text types

You can select whether the translated text is plain text or HTML text. Any HTML needs to be a well-formed, complete element. Possible values are: plain (default) or html.

<!-- SNIPPET: sample_text_translation_translate.get_text_translation_type -->

```python
try:
    text_type = TextType.HTML
    target_languages = ["cs"]
    input_text_elements = [InputTextItem(text="<html><body>This <b>is</b> a test.</body></html>")]

    response = text_translator.translate(request_body=input_text_elements, to=target_languages, text_type=text_type)
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
    print(f"Error Code: {exception.error.code}")
    print(f"Message: {exception.error.message}")
```

<!-- END SNIPPET -->

### Don’t translate specific entity name in a text

It's sometimes useful to exclude specific content from translation. You can use the attribute class=notranslate to specify content that should remain in its original language. In the following example, the content inside the first div element won't be translated, while the content in the second div element will be translated.

<!-- SNIPPET: sample_text_translation_translate.get_text_translation_exclude -->

```python
try:
    text_type = TextType.HTML
    source_language = "en"
    target_languages = ["cs"]
    input_text_elements = [
        InputTextItem(
            text='<div class="notranslate">This will not be translated.</div><div>This will be translated. </div>'
        )
    ]

    response = text_translator.translate(
        request_body=input_text_elements, to=target_languages, from_parameter=source_language, text_type=text_type
    )
    translation = response[0] if response else None

    if translation:
        for translated_text in translation.translations:
            print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")

except HttpResponseError as exception:
    print(f"Error Code: {exception.error.code}")
    print(f"Message: {exception.error.message}")
```

<!-- END SNIPPET -->

### Translate specific entity name in a text applying a dictionary

If you already know the translation you want to apply to a word or a phrase, you can supply it as markup within the request. The dynamic dictionary is safe only for compound nouns like proper names and product names.

> Note You must include the From parameter in your API translation request instead of using the autodetect feature.

<!-- SNIPPET: sample_text_translation_translate.get_text_translation_entity -->

```python
try:
    source_language = "en"
    target_languages = ["cs"]
    input_text_elements = [
        InputTextItem(
            text='The word <mstrans:dictionary translation="wordomatic">wordomatic</mstrans:dictionary> is a dictionary entry.'
        )
    ]

    response = text_translator.translate(
        request_body=input_text_elements, to=target_languages, from_parameter=source_language
    )
    translation = response[0] if response else None

    if translation:
        for translated_text in translation.translations:
            print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")

except HttpResponseError as exception:
    print(f"Error Code: {exception.error.code}")
    print(f"Message: {exception.error.message}")
```

<!-- END SNIPPET -->

### Profanity handling

[Profanity handling](https://learn.microsoft.com/azure/cognitive-services/translator/reference/v3-0-translate#handle-profanity). Normally the Translator service will retain profanity that is present in the source in the translation. The degree of profanity and the context that makes words profane differ between cultures, and as a result the degree of profanity in the target language may be amplified or reduced.

If you want to avoid getting profanity in the translation, regardless of the presence of profanity in the source text, you can use the profanity filtering option. The option allows you to choose whether you want to see profanity deleted, whether you want to mark profanities with appropriate tags (giving you the option to add your own post-processing), or you want no action taken. The accepted values of `ProfanityAction` are `DELETED`, `MARKED` and `NOACTION` (default).

<!-- SNIPPET: sample_text_translation_translate.get_text_translation_profanity -->

```python
try:
    profanity_action = ProfanityAction.MARKED
    profanity_maker = ProfanityMarker.ASTERISK
    target_languages = ["cs"]
    input_text_elements = [InputTextItem(text="This is ***.")]

    response = text_translator.translate(
        request_body=input_text_elements,
        to=target_languages,
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
    print(f"Error Code: {exception.error.code}")
    print(f"Message: {exception.error.message}")
```

<!-- END SNIPPET -->

### Include alignments into translations

You can ask translation service to include alignment projection from source text to translated text.

<!-- SNIPPET: sample_text_translation_translate.get_text_translation_alignment -->

```python
try:
    include_alignment = True
    target_languages = ["cs"]
    input_text_elements = [InputTextItem(text="The answer lies in machine translation.")]

    response = text_translator.translate(
        request_body=input_text_elements, to=target_languages, include_alignment=include_alignment
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
    print(f"Error Code: {exception.error.code}")
    print(f"Message: {exception.error.message}")
```

<!-- END SNIPPET -->

### Include sentence length

You can ask translator service to include sentence boundaries for the input text and the translated text.

<!-- SNIPPET: sample_text_translation_translate.get_text_translation_sentence_length -->

```python
try:
    include_sentence_length = True
    target_languages = ["cs"]
    input_text_elements = [InputTextItem(text="The answer lies in machine translation. This is a test.")]

    response = text_translator.translate(
        request_body=input_text_elements, to=target_languages, include_sentence_length=include_sentence_length
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
    print(f"Error Code: {exception.error.code}")
    print(f"Message: {exception.error.message}")
```

<!-- END SNIPPET -->

### Custom Translator

You can get translations from a customized system built with [Custom Translator](https://learn.microsoft.com/azure/cognitive-services/translator/customization). Add the Category ID from your Custom Translator [project details](https://learn.microsoft.com/azure/cognitive-services/translator/custom-translator/how-to-create-project#view-project-details) to this parameter to use your deployed customized system.

It is possible to set `allow_fallback` parameter. It specifies that the service is allowed to fall back to a general system when a custom system doesn't exist. Possible values are: `True` (default) or `False`.

`allow_fallback=False` specifies that the translation should only use systems trained for the category specified by the request. If a translation for language X to language Y requires chaining through a pivot language E, then all the systems in the chain (X → E and E → Y) will need to be custom and have the same category. If no system is found with the specific category, the request will return a 400 status code. `allow_fallback=True` specifies that the service is allowed to fall back to a general system when a custom system doesn't exist.

<!-- SNIPPET: sample_text_translation_translate.get_text_translation_custom -->

```python
try:
    category = "<<Category ID>>"
    target_languages = ["cs"]
    input_text_elements = [InputTextItem(text="This is a test")]

    response = text_translator.translate(request_body=input_text_elements, to=target_languages, category=category)
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
    print(f"Error Code: {exception.error.code}")
    print(f"Message: {exception.error.message}")
```

<!-- END SNIPPET -->

# Transliterate

### Transliterate Text

Converts characters or letters of a source language to the corresponding characters or letters of a target language.

<!-- SNIPPET: sample_text_translation_transliterate.get_text_transliteration -->

```python
try:
    language = "zh-Hans"
    from_script = "Hans"
    to_script = "Latn"
    input_text_elements = [InputTextItem(text="这是个测试。")]

    response = text_translator.transliterate(
        request_body=input_text_elements, language=language, from_script=from_script, to_script=to_script
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
```

<!-- END SNIPPET -->

# Break Sentence

### Break Sentence with language and script parameters

When the input language is known, you can provide those to the service call.

<!-- SNIPPET: sample_text_translation_break_sentence.get_text_sentence_boundaries -->

```python
try:
    source_language = "zh-Hans"
    source_script = "Latn"
    input_text_elements = [InputTextItem(text="zhè shì gè cè shì。")]

    response = text_translator.find_sentence_boundaries(
        request_body=input_text_elements, language=source_language, script=source_script
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
```

<!-- END SNIPPET -->

### Break Sentence with auto-detection

You can omit source language of the input text. In this case, API will try to auto-detect the language.

<!-- SNIPPET: sample_text_translation_break_sentence.get_text_sentence_boundaries_auto -->

```python
try:
    input_text_elements = [InputTextItem(text="This is a test. This is the second sentence.")]

    response = text_translator.find_sentence_boundaries(request_body=input_text_elements)
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
    print(f"Error Code: {exception.error.code}")
    print(f"Message: {exception.error.message}")
```

<!-- END SNIPPET -->

# Dictionary

### Dictionary Lookup

Returns equivalent words for the source term in the target language.

<!-- SNIPPET: sample_text_translation_dictionary_lookup.get_text_translation_dictionary_lookup -->

```python
try:
    source_language = "en"
    target_language = "es"
    input_text_elements = [InputTextItem(text="fly")]

    response = text_translator.lookup_dictionary_entries(
        request_body=input_text_elements, from_parameter=source_language, to=target_language
    )
    dictionary_entry = response[0] if response else None

    if dictionary_entry:
        print(f"For the given input {len(dictionary_entry.translations)} entries were found in the dictionary.")
        print(
            f"First entry: '{dictionary_entry.translations[0].display_target}', confidence: {dictionary_entry.translations[0].confidence}."
        )

except HttpResponseError as exception:
    if exception.error is not None:
        print(f"Error Code: {exception.error.code}")
        print(f"Message: {exception.error.message}")
    raise
```

<!-- END SNIPPET -->

### Dictionary Examples

Returns grammatical structure and context examples for the source term and target term pair.

<!-- SNIPPET: sample_text_translation_dictionary_examples.get_text_translation_dictionary_examples -->

```python
try:
    source_language = "en"
    target_language = "es"
    input_text_elements = [DictionaryExampleTextItem(text="fly", translation="volar")]

    response = text_translator.lookup_dictionary_examples(
        request_body=input_text_elements, from_parameter=source_language, to=target_language
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
```

<!-- END SNIPPET -->

* [Create Client][client_sample]
* [Translate][translate_sample]
* [Transliterate][transliterate_sample]
* [Break Sentence][breaksentence_sample]
* [Dictionary Lookup][dictionarylookup_sample]
* [Dictionary Examples][dictionaryexamples_sample]

[README]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/README.md
[client_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/samples/sample_text_translation_client.py
[languages_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/samples/sample_text_translation_languages.py
[translate_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/samples/sample_text_translation_translate.py
[transliterate_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/samples/sample_text_translation_transliterate.py
[breaksentence_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/samples/sample_text_translation_break_sentence.py
[dictionarylookup_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/samples/sample_text_translation_dictionary_lookup.py
[dictionaryexamples_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/samples/sample_text_translation_dictionary_examples.py
[azure_identity]: https://github.com/Azure/azure-sdk-for-net/blob/master/sdk/identity/Azure.Identity/README.md
[DefaultAzureCredential]: https://github.com/Azure/azure-sdk-for-net/blob/main/sdk/identity/Azure.Identity/README.md#defaultazurecredential
[register_aad_app]: https://docs.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[aad_grant_access]: https://docs.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[custom_subdomain]: https://docs.microsoft.com/azure/cognitive-services/authentication#create-a-resource-with-a-custom-subdomain
[cognitive_auth]: https://docs.microsoft.com/azure/cognitive-services/authentication
[resource_details]: https://learn.microsoft.com/azure/ai-services/translator/create-translator-resource#authentication-keys-and-endpoint-url
[custom_details]: https://learn.microsoft.com/azure/ai-services/translator/reference/v3-0-reference#authentication-with-microsoft-entra-id
[authentication_details]: https://learn.microsoft.com/azure/ai-services/translator/reference/v3-0-reference