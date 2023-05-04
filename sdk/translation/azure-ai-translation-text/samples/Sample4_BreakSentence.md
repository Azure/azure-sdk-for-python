# Break Sentence

## Create a `TextTranslationClient`

To create a new `TextTranslationClient`, you will need the service endpoint and credentials of your Translator resource. In this sample, you will use an `TranslatorCredential`, which you can create with an API key and region.

```Python
credential = TranslatorCredential("<apiKey>", "<region>")
text_translator = TextTranslationClient(endpoint="<endpoint>", credential=credential)
```

The values of the `endpoint`, `apiKey` and `region` variables can be retrieved from environment variables, configuration settings, or any other secure approach that works for your application.

### Break Sentence with language and script parameters

When the input language is known, you can provide those to the service call.

```Python
try:
    source_language = "zh-Hans"
    source_script = "Latn"
    input_text_elements = [ InputTextItem(text = "zhè shì gè cè shì。") ]

    response = text_translator.find_sentence_boundaries(content = input_text_elements, language = source_language, script = source_script)
    sentence_boundaries = response[0] if response else None

    if sentence_boundaries:
        detected_language = sentence_boundaries.detected_language
        if detected_language:
            print(f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}.")
        print(f"The detected sentence boundaries:")
        for boundary in sentence_boundaries.sent_len:
            print(boundary)

except HttpResponseError as exception:
    print(f"Error Code: {exception.error.code}")
    print(f"Message: {exception.error.message}")
```

### Break Sentence with auto-detection

You can omit source language of the input text. In this case, API will try to auto-detect the language.

```Python
try:
    input_text_elements = [ InputTextItem(text = "This is a test. This is the second sentence.") ]

    response = text_translator.find_sentence_boundaries(content = input_text_elements)
    sentence_boundaries = response[0] if response else None

    if sentence_boundaries:
        detected_language = sentence_boundaries.detected_language
        if detected_language:
            print(f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}.")
        print(f"The detected sentence boundaries:")
        for boundary in sentence_boundaries.sent_len:
            print(boundary)

except HttpResponseError as exception:
    print(f"Error Code: {exception.error.code}")
    print(f"Message: {exception.error.message}")
```

See the [README] of the Text Translator client library for more information, including useful links and instructions.

[README]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/README.md
