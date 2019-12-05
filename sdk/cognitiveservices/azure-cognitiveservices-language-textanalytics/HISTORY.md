# Change Log azure-cognitiveservices-language-textanalytics

## 2020-01-06 3.0.0b1

Version (TODO) is the first preview of our efforts to create a user-friendly and Pythonic client library for Azure Text Analytics. For more information about this, and preview releases of other Azure SDK libraries, please visit
https://azure.github.io/azure-sdk/releases/latest/python.html.

**Breaking changes: New API design**

- New operations and naming:
  - `detect_language` is renamed to `detect_languages`
  - `entities` is renamed to `recognize_entities`
  - `key_phrases` is renamed to `extract_key_phrases`
  - `sentiment` is renamed to `analyze_sentiment`
  - New operation `recognize_pii_entities` finds personally identifiable information entities in text
  - New operation `recognize_linked_entities` provides links from a well-known knowledge base for each recognized entity
  - New module-level operations `single_detect_language`, `single_recognize_entities`, `single_extract_key_phrases`, `single_analyze_sentiment`, `single_recognize_pii_entities`, and `single_recognize_linked_entities` perform
  function on a single string instead of a batch of text documents and can be imported from the `azure.cognitiveservices.language.textanalytics` namespace.
  - New client and module-level async APIs added to subnamespace `azure.cognitiveservices.language.textanalytics.aio`.
  - `MultiLanguageInput` has been renamed to `TextDocumentInput`
  - `LanguageInput` has been renamed to `DetectLanguageInput`

- New input types:
  - `detect_languages` can take as input a `list[DetectLanguageInput]` or a `list[str]`. A list of dict-like objects in the same shape as `DetectLanguageInput` is still accepted as input.
  - `recognize_entities`, `recognize_pii_entities`, `recognize_linked_entities`, `extract_key_phrases`, `analyze_sentiment` can take as input a `list[TextDocumentInput]` or `list[str]`.
  A list of dict-like objects in the same shape as `TextDocumentInput` is still accepted as input.

- New parameters:
  - All operations now take a parameter `model_version` which allows the user to specify a string referencing the desired model version to be used for analysis. If no string specified, it will default to the latest, non-preview version.
  - `detect_languages` now takes a parameter `country_hint` which allows you to specify the country hint for the entire batch. Any per-item country hints will take precedence over a whole batch hint.
  - `recognize_entities`, `recognize_pii_entities`, `recognize_linked_entities`, `extract_key_phrases`, `analyze_sentiment` now take a parameter `language` which allows you to specify the language for the entire batch.
  Any per-item specified language will take precedence over a whole batch hint.
  - A `response_hook` parameter can be passed with a callback to use the raw response from the service. Additionally, values returned for `RequestStatistics` and `model_version` must be retrieved using a response hook.

- New return types
  - The return types for the batching methods (`detect_languages`, `recognize_entities`, `recognize_pii_entities`, `recognize_linked_entities`, `extract_key_phrases`, `analyze_sentiment`) now return a heterogeneous list of 
  result objects and document errors in the order passed in with the request. To iterate over the list and filter for result or error, a boolean on each object called `is_error` can be used to determine whether the returned response object at 
  that index is a result or an error:
  - `detect_languages` now returns a List[Union[`DocumentLanguage`, `DocumentError`]]
  - `recognize_entities` now returns a List[Union[`DocumentEntities`, `DocumentError`]]
  - `recognize_pii_entities` now returns a List[Union[`DocumentEntities`, `DocumentError`]]
  - `recognize_linked_entities` now returns a List[Union[`DocumentLinkedEntities`, `DocumentError`]]
  - `extract_key_phrases` now returns a List[Union[`DocumentKeyPhrases`, `DocumentError`]]
  - `analyze_sentiment` now returns a List[Union[`DocumentSentiment`, `DocumentError`]]
  - The module-level, single text operations will return a single result object or raise the error found on the document:
  - `single_detect_languages` returns a `DocumentLanguage`
  - `single_recognize_entities` returns a `DocumentEntities`
  - `single_recognize_pii_entities` returns a `DocumentEntities`
  - `single_recognize_linked_entities` returns a `DocumentLinkedEntities`
  - `single_extract_key_phrases` returns a `DocumentKeyPhrases`
  - `single_analyze_sentiment` returns a `DocumentSentiment`

- New underlying REST pipeline implementation, based on the new `azure-core` library.
- Client and pipeline configuration is now available via keyword arguments at both the client level, and per-operation. See reference documentation for a full list of optional configuration arguments.
- Authentication using `azure-identity` credentials
  - see the
  [Azure Identity documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md)
  for more information
- New error hierarchy:
    - All service errors will now use the base type: `azure.core.exceptions.HttpResponseError`
    - There is one exception type derived from this base type for authentication errors:
        - `ClientAuthenticationError`: Authentication failed.

### 2019-03-12 0.2.0

**Features**

- Client class can be used as a context manager to keep the underlying HTTP session open for performance
- New method "entities"
- Model KeyPhraseBatchResultItem has a new parameter statistics
- Model KeyPhraseBatchResult has a new parameter statistics
- Model LanguageBatchResult has a new parameter statistics
- Model LanguageBatchResultItem has a new parameter statistics
- Model SentimentBatchResult has a new parameter statistics

**Breaking changes**

- TextAnalyticsAPI main client has been renamed TextAnalyticsClient
- TextAnalyticsClient parameter is no longer a region but a complete endpoint

**General Breaking changes**

This version uses a next-generation code generator that *might* introduce breaking changes.

- Model signatures now use only keyword-argument syntax. All positional arguments must be re-written as keyword-arguments.
  To keep auto-completion in most cases, models are now generated for Python 2 and Python 3. Python 3 uses the "*" syntax for keyword-only arguments.
- Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to improve the behavior when unrecognized enum values are encountered.
  While this is not a breaking change, the distinctions are important, and are documented here:
  https://docs.python.org/3/library/enum.html#others
  At a glance:

  - "is" should not be used at all.
  - "format" will return the string value, where "%s" string formatting will return `NameOfEnum.stringvalue`. Format syntax should be prefered.

**Bugfixes**

- Compatibility of the sdist with wheel 0.31.0


### 2018-01-12 0.1.0

* Initial Release
