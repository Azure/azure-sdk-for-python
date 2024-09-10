# Release History

## 0.3.1 (2024-06-26)

### Other Changes

- This package is no longer being maintained. Please refer to the samples in the [Bing Search for Python repo](https://github.com/microsoft/bing-search-sdk-for-python/tree/main) instead.

For additional support, please open a new issue in the [Issues](https://github.com/microsoft/bing-search-sdk-for-python/issues) section of the Microsoft Bing Search SDK for Python repo.

## 0.3.0 (2020-01-12)

**General Breaking Changes**

This version uses a next-generation code generator that might introduce
breaking changes if from some import. In summary, some modules were
incorrectly visible/importable and have been renamed. This fixed several
issues caused by usage of classes that were not supposed to be used in
the first place. CustomSearchClient cannot be imported from
azure.cognitiveservices.search.customsearch.custom_search_api anymore
(import from azure.cognitiveservices.search.customsearch works like
before) CustomSearchClientConfiguration import has been moved from
azure.cognitiveservices.search.customsearch.custom_search_api to
azure.cognitiveservices.search.customsearch A model MyClass from a
"models" sub-module cannot be imported anymore using
azure.cognitiveservices.search.customsearch.models.my_class (import
from azure.cognitiveservices.search.customsearch.models works like
before) An operation class MyClassOperations from an operations
sub-module cannot be imported anymore using
azure.cognitiveservices.search.customsearch.operations.my_class_operations
(import from azure.cognitiveservices.search.customsearch.operations
works like before) Last but not least, HTTP connection pooling is now
enabled by default. You should always use a client as a context manager,
or call close(), or use no more than one client per process.

## 0.2.0 (2018-12-11)

**Features**

  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

**Breaking changes**

  - CustomSearchAPI main client has been renamed CustomSearchClient
  - "search" method has changes in positional arguments

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
