# Get Languages

This sample demonstrates how to get languages that are supported by other operations.

## Create a `TextTranslationClient`

For this operation you can create a new `TextTranslationClient` without any authentication. You will only need your endpoint:

```Python
translator_client = TextTranslationClient(endpoint="<endpoint>")
```

The values of the `endpoint` variable can be retrieved from environment variables, configuration settings, or any other secure approach that works for your application.

## Get Supported Languages for ALL other operations

This will return language metadata from all supported scopes.

```Python
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
```

### Get Supported Languages for a given scope

You can limit the scope of the response of the languages API by providing the optional parameter `scope`. A comma-separated list of names defining the group of languages to return. Allowed group names are: `translation`, `transliteration` and `dictionary`. If no scope is given, then all groups are returned, which is equivalent to passing `translation,transliteration,dictionary`.

```Python
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
```

### Get Languages in a given culture

You can select the language to use for user interface strings. Some of the fields in the response are names of languages or names of regions. Use this parameter to define the language in which these names are returned. The language is specified by providing a well-formed BCP 47 language tag. For instance, use the value `fr` to request names in French or use the value `zh-Hant` to request names in Chinese Traditional.
Names are provided in the English language when a target language is not specified or when localization is not available.

```Python
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
```

See the [README] of the Text Translator client library for more information, including useful links and instructions.

[README]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/README.md
