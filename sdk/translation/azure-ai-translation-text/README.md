# Azure Text Translation client library for Python

Text Translation is a cloud-based REST API feature of the Translator service that uses neural machine translation technology to enable quick and accurate source-to-target text translation in real time across all supported languages.

Use the Text Translation client library for Python to:

* Return a list of languages supported by Translate, Transliterate, and Dictionary operations.

* Render single source-language text to multiple target-language texts with a single request.

* Convert text of a source language in letters of a different script.

* Return equivalent words for the source term in the target language.

* Return grammatical structure and context examples for the source term and target term pair.

[Source code][python-dt-src]
| [Package (PyPI)][python-dt-pypi]
| [API reference documentation][python-dt-ref-docs]
| [Product documentation][python-dt-product-docs]
| [Samples][python-dt-samples]

## Getting started

### Prerequisites

* Python 3.7 or later is required to use this package.
* An existing Translator service or Cognitive Services resource.

### Install the package

Install the Azure Text Translation client library for Python with [pip][pip]:

```bash
pip install azure-ai-translation-text
```

#### Create a Translator service resource

You can create Translator resource following [Create a Translator resource][translator_resource_create].

### Authenticate the client

Interaction with the service using the client library begins with creating an instance of the [TextTranslationClient][translator_client_class] class. You will need an **API key** or ``TokenCredential`` to instantiate a client object. For more information regarding authenticating with cognitive services, see [Authenticate requests to Translator Service][translator_auth].

#### Get an API key

You can get the `endpoint`, `API key` and `Region` from the Cognitive Services resource or Translator service resource information in the [Azure Portal][azure_portal].

Alternatively, use the [Azure CLI][azure_cli] snippet below to get the API key from the Translator service resource.

```PowerShell
az cognitiveservices account keys list --resource-group <your-resource-group-name> --name <your-resource-name>
```

#### Create a `TextTranslationClient` using an API key and Region credential

Once you have the value for the API key and Region, create an `AzureKeyCredential`. This will allow you to
update the API key without creating a new client.

With the value of the `endpoint`, `credential` and a `region`, you can create the [TextTranslationClient][client_sample]:

<!-- SNIPPET: sample_text_translation_client.create_text_translation_client_with_credential -->

```python
credential = AzureKeyCredential(apikey)
text_translator = TextTranslationClient(credential=credential, endpoint=endpoint, region=region)
```

<!-- END SNIPPET -->

## Key concepts

### `TextTranslationClient`

A `TextTranslationClient` is the primary interface for developers using the Text Translation client library.  It provides both synchronous and asynchronous operations to access a specific use of text translator, such as get supported languages detection or text translation.

### Input

A **text element** (`string`), is a single unit of input to be processed by the translation models in the Translator service. Operations on `TextTranslationClient` may take a single text element or a collection of text elements.
For text element length limits, maximum requests size, and supported text encoding see [here][translator_limits].

## Examples

The following section provides several code snippets using the `client` [created above](#create-a-texttranslationclient-using-an-api-key-and-region-credential), and covers the main features present in this client library. Although most of the snippets below make use of synchronous service calls, keep in mind that the Text Translation for Python library package supports both synchronous and asynchronous APIs.

### Get Supported Languages

Gets the set of languages currently supported by other operations of the Translator.

<!-- SNIPPET: sample_text_translation_languages.get_text_translation_languages -->

```python
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
```

<!-- END SNIPPET -->

For samples on using the `languages` endpoint refer to more samples [here][languages_sample].

Please refer to the service documentation for a conceptual discussion of [languages][languages_doc].

### Translate

Renders single source-language text to multiple target-language texts with a single request.

<!-- SNIPPET: sample_text_translation_translate.get_text_translation_multiple_languages -->

```python
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
```

<!-- END SNIPPET -->


For samples on using the `translate` endpoint refer to more samples [here][translate_sample].

Please refer to the service documentation for a conceptual discussion of [translate][translate_doc].

### Transliterate

Converts characters or letters of a source language to the corresponding characters or letters of a target language.

<!-- SNIPPET: sample_text_translation_transliterate.get_text_transliteration -->

```python
try:
    language = "zh-Hans"
    from_script = "Hans"
    to_script = "Latn"
    input_text_elements = ["这是个测试。"]

    response = text_translator.transliterate(
        body=input_text_elements,
        language=language,
        from_script=from_script,
        to_script=to_script,
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
For samples on using the `transliterate` endpoint refer to more samples [here][transliterate_sample].

Please refer to the service documentation for a conceptual discussion of [transliterate][transliterate_doc].

### Break Sentence

Identifies the positioning of sentence boundaries in a piece of text.

<!-- SNIPPET: sample_text_translation_translate.get_text_translation_sentence_length -->

```python
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
```

<!-- END SNIPPET -->

For samples on using the `break sentence` endpoint refer to more samples [here][breaksentence_sample].

Please refer to the service documentation for a conceptual discussion of [break sentence][breaksentence_doc].

### Dictionary Lookup

Returns equivalent words for the source term in the target language.

<!-- SNIPPET: sample_text_translation_dictionary_lookup.get_text_translation_dictionary_lookup -->

```python
try:
    from_language = "en"
    to_language = "es"
    input_text_elements = ["fly"]

    response = text_translator.lookup_dictionary_entries(
        body=input_text_elements, from_language=from_language, to_language=to_language
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

For samples on using the `dictionary lookup` endpoint refer to more samples [here][dictionarylookup_sample].

Please refer to the service documentation for a conceptual discussion of [dictionary lookup][dictionarylookup_doc].

### Dictionary Examples

Returns grammatical structure and context examples for the source term and target term pair.

<!-- SNIPPET: sample_text_translation_dictionary_examples.get_text_translation_dictionary_examples -->

```python
try:
    from_language = "en"
    to_language = "es"
    input_text_elements = [DictionaryExampleTextItem(text="fly", translation="volar")]

    response = text_translator.lookup_dictionary_examples(
        body=input_text_elements, from_language=from_language, to_language=to_language
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

For samples on using the `dictionary examples` endpoint refer to more samples [here][dictionaryexamples_sample].

Please refer to the service documentation for a conceptual discussion of [dictionary examples][dictionaryexamples_doc].

## Troubleshooting

When you interact with the Translator Service using the TextTranslator client library, errors returned by the Translator service correspond to the same HTTP status codes returned for REST API requests.

For example, if you submit a translation request without a target translate language, a `400` error is returned, indicating "Bad Request".

You can find the different error codes returned by the service in the [Service Documentation][service_errors].

## Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the
[Issues](https://github.com/Azure/azure-sdk-for-python/issues)
section of the project.

## Next steps

More samples can be found under the [samples][samples] directory.

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[python-dt-src]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/azure/ai/translation/text
[python-dt-pypi]: https://aka.ms/azsdk/python/texttranslation/pypi
[python-dt-product-docs]: https://learn.microsoft.com/azure/cognitive-services/translator/
[python-dt-ref-docs]: https://learn.microsoft.com/azure/cognitive-services/translator/reference/v3-0-reference
[python-dt-samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/samples

[pip]: https://pypi.org/project/pip/
[azure_cli]: https://docs.microsoft.com/cli/azure
[azure_portal]: https://portal.azure.com

[translator_resource_create]: https://learn.microsoft.com/azure/cognitive-services/Translator/create-translator-resource

[translator_client_class]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/azure/ai/translation/text/_client.py

[translator_auth]: https://learn.microsoft.com/azure/cognitive-services/translator/reference/v3-0-reference#authentication
[translator_limits]: https://learn.microsoft.com/azure/cognitive-services/translator/request-limits
[service_errors]: https://learn.microsoft.com/azure/cognitive-services/translator/reference/v3-0-reference#errors

[languages_doc]: https://learn.microsoft.com/azure/cognitive-services/translator/reference/v3-0-languages
[translate_doc]: https://learn.microsoft.com/azure/cognitive-services/translator/reference/v3-0-translate
[transliterate_doc]: https://learn.microsoft.com/azure/cognitive-services/translator/reference/v3-0-transliterate
[breaksentence_doc]: https://learn.microsoft.com/azure/cognitive-services/translator/reference/v3-0-break-sentence
[dictionarylookup_doc]: https://learn.microsoft.com/azure/cognitive-services/translator/reference/v3-0-dictionary-lookup
[dictionaryexamples_doc]: https://learn.microsoft.com/azure/cognitive-services/translator/reference/v3-0-dictionary-examples

[client_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/samples/sample_text_translation_client.py
[languages_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/samples/sample_text_translation_languages.py
[translate_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/samples/sample_text_translation_translate.py
[transliterate_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/samples/sample_text_translation_transliterate.py
[breaksentence_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/samples/sample_text_translation_break_sentence.py
[dictionarylookup_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/samples/sample_text_translation_dictionary_lookup.py
[dictionaryexamples_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/samples/sample_text_translation_dictionary_examples.py

[samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/samples

[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
