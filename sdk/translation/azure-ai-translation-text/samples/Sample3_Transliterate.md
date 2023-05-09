# Transliterate

## Create a `TextTranslationClient`

To create a new `TextTranslationClient`, you will need the service endpoint and credentials of your Translator resource. In this sample, you will use an `TranslatorCredential`, which you can create with an API key and region.

```Python
credential = TranslatorCredential("<apiKey>", "<region>")
text_translator = TextTranslationClient(endpoint="<endpoint>", credential=credential)
```

The values of the `endpoint`, `apiKey` and `region` variables can be retrieved from environment variables, configuration settings, or any other secure approach that works for your application.

### Transliterate Text

Converts characters or letters of a source language to the corresponding characters or letters of a target language.

```Python
try:
    language = "zh-Hans"
    from_script = "Hans"
    to_script = "Latn"
    input_text_elements = [ InputTextItem(text = "这是个测试。") ]

    response = text_translator.transliterate(content = input_text_elements, language = language, from_script = from_script, to_script = to_script)
    transliteration = response[0] if response else None

    if transliteration:
        print(f"Input text was transliterated to '{transliteration.script}' script. Transliterated text: '{transliteration.text}'.")

except HttpResponseError as exception:
    print(f"Error Code: {exception.error.code}")
    print(f"Message: {exception.error.message}")
```

See the [README] of the Text Translator client library for more information, including useful links and instructions.

[README]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/README.md
