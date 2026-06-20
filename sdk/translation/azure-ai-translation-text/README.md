# Azure Text Translation client library for Python

Azure text translation is a cloud-based REST API provided by the Azure Translator service. It utilizes neural machine translation technology to deliver precise, contextually relevant, and semantically accurate real-time text translations across all supported languages.

Use the Text Translation client library for Python to:

- Retrieve the list of languages supported for translation and transliteration operations, as well as LLM models available for translations.

- Perform deterministic text translation from a specified source language to a target language, with configurable parameters to ensure precision and maintain contextual integrity.

- Execute transliteration by converting text from the original script to an alternative script representation.

- Use LLM models to produce translation output variants that are tone-specific and gender-aware.

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
text_translator = TextTranslationClient(credential=credential, region=region)
```

<!-- END SNIPPET -->

## Key concepts

### `TextTranslationClient`

A `TextTranslationClient` is the primary interface for developers using the Text Translation client library.  It provides both synchronous and asynchronous operations to access a specific use of text translator, such as get supported languages detection or text translation.

### Input

A **TranslateInputItem** is a single unit of input to be processed by the translation models in the Translator service. Each `TranslateInputItem` defines both the input string to translate and the output specifications for the translation.
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
        f"Number of supported models for translation: {len(response.models) if response.models is not None else 0}"
    )

    if response.translation is not None:
        print("Translation Languages:")
        for key, value in response.translation.items():
            print(f"{key} -- name: {value.name} ({value.native_name})")

    if response.transliteration is not None:
        print("Transliteration Languages:")
        for key, value in response.transliteration.items():
            print(f"{key} -- name: {value.name}, supported script count: {len(value.scripts)}")

    if response.models is not None:
        print(f"Models: {', '.join(response.models)}")

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
            print(
                f"Text was translated to: '{translated_text.language}' and the result is: '{translated_text.text}'."
            )

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


## Troubleshooting

When you interact with the Translator Service using the TextTranslator client library, errors returned by the Translator service correspond to the same HTTP status codes returned for REST API requests.

For example, if you submit a translation request without a target translate language, a `400` error is returned, indicating "Bad Request".

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
[python-dt-ref-docs]: https://learn.microsoft.com/azure/ai-services/translator/text-translation/preview/rest-api-guide
[python-dt-samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/samples

[pip]: https://pypi.org/project/pip/
[azure_cli]: https://learn.microsoft.com/cli/azure
[azure_portal]: https://portal.azure.com

[translator_resource_create]: https://learn.microsoft.com/azure/cognitive-services/Translator/create-translator-resource

[translator_client_class]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/azure/ai/translation/text/_client.py

[translator_auth]: https://learn.microsoft.com/azure/ai-services/translator/text-translation/reference/authentication
[translator_limits]: https://learn.microsoft.com/azure/cognitive-services/translator/request-limits

[languages_doc]: https://learn.microsoft.com/azure/ai-services/translator/text-translation/preview/get-languages
[translate_doc]: https://learn.microsoft.com/azure/ai-services/translator/text-translation/preview/translate-api
[transliterate_doc]: https://learn.microsoft.com/azure/ai-services/translator/text-translation/preview/transliterate-api

[client_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/samples/sample_text_translation_client.py
[languages_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/samples/sample_text_translation_languages.py
[translate_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/samples/sample_text_translation_translate.py
[transliterate_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/samples/sample_text_translation_transliterate.py

[samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-text/samples

[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
