# Dictionary Examples

## Create a `TextTranslationClient`

To create a new `TextTranslationClient`, you will need the service endpoint and credentials of your Translator resource. In this sample, you will use an `TranslatorCredential`, which you can create with an API key and region.

```Python
credential = TranslatorCredential("<apiKey>", "<region>")
text_translator = TextTranslationClient(endpoint="<endpoint>", credential=credential)
```

The values of the `endpoint`, `apiKey` and `region` variables can be retrieved from environment variables, configuration settings, or any other secure approach that works for your application.

```Python
try:
    source_language = "en"
    target_language = "es"
    input_text_elements = [ DictionaryExampleTextItem(text = "fly", translation = "volar") ]

    response = text_translator.lookup_dictionary_examples(content = input_text_elements, from_parameter = source_language, to = target_language)
    dictionary_entry = response[0] if response else None

    if dictionary_entry:
        print(f"For the given input {len(dictionary_entry.examples)} entries were found in the dictionary.")
        print(f"First example: '{dictionary_entry.examples[0].target_prefix}{dictionary_entry.examples[0].target_term}{dictionary_entry.examples[0].target_suffix}'.")

except HttpResponseError as exception:
    print(f"Error Code: {exception.error.code}")
    print(f"Message: {exception.error.message}")
```

See the [README] of the Text Translator client library for more information, including useful links and instructions.

[README]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/README.md
