# Translate

## Create a `TextTranslationClient`

To create a new `TextTranslationClient`, you will need the service endpoint and credentials of your Translator resource. In this sample, you will use an `TranslatorCredential`, which you can create with an API key and region.

```Python
credential = TranslatorCredential("<apiKey>", "<region>")
text_translator = TextTranslationClient(endpoint="<endpoint>", credential=credential)
```

The values of the `endpoint`, `apiKey` and `region` variables can be retrieved from environment variables, configuration settings, or any other secure approach that works for your application.

### Translate text

Translate text from known source language to target language.

```Python
try:
    source_language = "en"
    target_languages = ["cs"]
    input_text_elements = [ InputTextItem(text = "This is a test") ]

    response = text_translator.translate(content = input_text_elements, to = target_languages, from_parameter = source_language)
    translation = response[0] if response else None

    if translation:
        for translated_text in translation.translations:
            print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")

except HttpResponseError as exception:
    print(f"Error Code: {exception.error.code}")
    print(f"Message: {exception.error.message}")
```

### Translate with auto-detection

You can omit source language of the input text. In this case, API will try to auto-detect the language.

> Note that you must provide the source language rather than autodetection when using the dynamic dictionary feature.

> Note you can use `suggestedFrom` parameter that specifies a fallback language if the language of the input text can't be identified. Language autodetection is applied when the from parameter is omitted. If detection fails, the suggestedFrom language will be assumed.

```Python
try:
    target_languages = ["cs"]
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
```

### Translate with Transliteration

You can combine both Translation and Transliteration in one Translate call. Your source Text can be in non-standard Script of a language as well as you can ask for non-standard Script of a target language.

```Python
try:
    from_script = "Latn"
    from_language = "ar"
    to_script = "Latn"
    target_languages = ["zh-Hans"]
    input_text_elements = [ InputTextItem(text = "hudha akhtabar.") ]

    response = text_translator.translate(content = input_text_elements, to = target_languages, from_script=from_script, from_parameter=from_language, to_script=to_script)
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
    print(f"Error Code: {exception.error.code}")
    print(f"Message: {exception.error.message}")
```

### Translate multiple input texts

You can translate multiple text elements with a various length. Each input element can be in different language (source language parameter needs to be omitted and language auto-detection is used). Refer to [Request limits for Translator](https://learn.microsoft.com/azure/cognitive-services/translator/request-limits) for current limits.

```Python
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
```

### Translate multiple target languages

You can provide multiple target languages which results to each input element be translated to all target languages.

```Python
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
```

### Translate different text types

You can select whether the translated text is plain text or HTML text. Any HTML needs to be a well-formed, complete element. Possible values are: plain (default) or html.

```Python
try:
    text_type = TextType.HTML
    target_languages = ["cs"]
    input_text_elements = [ InputTextItem(text = "<html><body>This <b>is</b> a test.</body></html>") ]

    response = text_translator.translate(content = input_text_elements, to = target_languages, text_type=text_type)
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
```

### Don’t translate specific entity name in a text

It's sometimes useful to exclude specific content from translation. You can use the attribute class=notranslate to specify content that should remain in its original language. In the following example, the content inside the first div element won't be translated, while the content in the second div element will be translated.

```Python
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
```

### Translate specific entity name in a text applying a dictionary

If you already know the translation you want to apply to a word or a phrase, you can supply it as markup within the request. The dynamic dictionary is safe only for compound nouns like proper names and product names.

> Note You must include the From parameter in your API translation request instead of using the autodetect feature.

```Python
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
```

### Profanity handling

[Profanity handling](https://learn.microsoft.com/azure/cognitive-services/translator/reference/v3-0-translate#handle-profanity). Normally the Translator service will retain profanity that is present in the source in the translation. The degree of profanity and the context that makes words profane differ between cultures, and as a result the degree of profanity in the target language may be amplified or reduced.

If you want to avoid getting profanity in the translation, regardless of the presence of profanity in the source text, you can use the profanity filtering option. The option allows you to choose whether you want to see profanity deleted, whether you want to mark profanities with appropriate tags (giving you the option to add your own post-processing), or you want no action taken. The accepted values of `ProfanityAction` are `DELETED`, `MARKED` and `NOACTION` (default).

```Python
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
```

### Include alignments into translations

You can ask translation service to include alignment projection from source text to translated text.

```Python
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
```

### Include sentence length

You can ask translator service to include sentence boundaries for the input text and the translated text.

```Python
try:
    include_sentence_length = True
    target_languages = ["cs"]
    input_text_elements = [ InputTextItem(text = "The answer lies in machine translation. This is a test.") ]

    response = text_translator.translate(content = input_text_elements, to = target_languages, include_sentence_length=include_sentence_length)
    translation = response[0] if response else None

    if translation:
        detected_language = translation.detected_language
        if detected_language:
            print(f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}.")
        for translated_text in translation.translations:
            print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")
            if (translated_text.sent_len):
                print(f"Source Sentence length: {translated_text.sent_len.src_sent_len}")
                print(f"Translated Sentence length: {translated_text.sent_len.trans_sent_len}")

except HttpResponseError as exception:
    print(f"Error Code: {exception.error.code}")
    print(f"Message: {exception.error.message}")
```

### Custom Translator

You can get translations from a customized system built with [Custom Translator](https://learn.microsoft.com/azure/cognitive-services/translator/customization). Add the Category ID from your Custom Translator [project details](https://learn.microsoft.com/azure/cognitive-services/translator/custom-translator/how-to-create-project#view-project-details) to this parameter to use your deployed customized system.

It is possible to set `allow_fallback` parameter. It specifies that the service is allowed to fall back to a general system when a custom system doesn't exist. Possible values are: `True` (default) or `False`.

`allow_fallback=False` specifies that the translation should only use systems trained for the category specified by the request. If a translation for language X to language Y requires chaining through a pivot language E, then all the systems in the chain (X → E and E → Y) will need to be custom and have the same category. If no system is found with the specific category, the request will return a 400 status code. `allow_fallback=True` specifies that the service is allowed to fall back to a general system when a custom system doesn't exist.

```Python
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
```

See the [README] of the Text Translator client library for more information, including useful links and instructions.

[README]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/README.md
