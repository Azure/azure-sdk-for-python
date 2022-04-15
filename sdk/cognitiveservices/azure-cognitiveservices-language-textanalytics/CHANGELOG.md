# Release History


## 0.2.1 (2022-02-15)

- There is a newer version of this package. Please install the [azure-ai-textanalytics](https://pypi.org/project/azure-ai-textanalytics/) package for the latest features and support.

## 0.2.0 (2019-03-12)

**Features**

  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance
  - New method "entities"
  - Model KeyPhraseBatchResultItem has a new parameter statistics
  - Model KeyPhraseBatchResult has a new parameter statistics
  - Model LanguageBatchResult has a new parameter statistics
  - Model LanguageBatchResultItem has a new parameter statistics
  - Model SentimentBatchResult has a new parameter statistics

**Breaking changes**

  - TextAnalyticsAPI main client has been renamed TextAnalyticsClient
  - TextAnalyticsClient parameter is no longer a region but a complete
    endpoint

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes.

  - Model signatures now use only keyword-argument syntax. All
    positional arguments must be re-written as keyword-arguments. To
    keep auto-completion in most cases, models are now generated for
    Python 2 and Python 3. Python 3 uses the "*" syntax for
    keyword-only arguments.
  - Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to
    improve the behavior when unrecognized enum values are encountered.
    While this is not a breaking change, the distinctions are important,
    and are documented here:
    <https://docs.python.org/3/library/enum.html#others> At a glance:
      - "is" should not be used at all.
      - "format" will return the string value, where "%s" string
        formatting will return `NameOfEnum.stringvalue`. Format syntax
        should be prefered.

**Bugfixes**

  - Compatibility of the sdist with wheel 0.31.0

## 0.1.0 (2018-01-12)

  - Initial Release
