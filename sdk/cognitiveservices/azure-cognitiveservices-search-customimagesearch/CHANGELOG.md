# Release History

## 0.2.1 (2024-06-26)

### Other Changes

- This package is no longer being maintained. Please refer to the samples in the [Bing Search for Python repo](https://github.com/microsoft/bing-search-sdk-for-python/tree/main) instead.

For additional support, please open a new issue in the [Issues](https://github.com/microsoft/bing-search-sdk-for-python/issues) section of the Microsoft Bing Search SDK for Python repo.

## 0.2.0 (2020-01-12)

**Breaking changes**

  - CustomImageSearchAPI main client has been renamed
    CustomImageSearchClient

**General Breaking Changes**

This version uses a next-generation code generator that might introduce
breaking changes if from some import. In summary, some modules were
incorrectly visible/importable and have been renamed. This fixed several
issues caused by usage of classes that were not supposed to be used in
the first place. CustomImageSearchClient cannot be imported from
azure.cognitiveservices.search.customimagesearch.custom_image_search_api
anymore (import from azure.cognitiveservices.search.customimagesearch
works like before) CustomImageSearchClientConfiguration import has been
moved from
azure.cognitiveservices.search.customimagesearch.custom_image_search_api
to azure.cognitiveservices.search.customimagesearch A model MyClass from
a "models" sub-module cannot be imported anymore using
azure.cognitiveservices.search.customimagesearch.models.my_class
(import from azure.cognitiveservices.search.customimagesearch.models
works like before) An operation class MyClassOperations from an
operations sub-module cannot be imported anymore using
azure.cognitiveservices.search.customimagesearch.operations.my_class_operations
(import from azure.cognitiveservices.search.customimagesearch.operations
works like before) Last but not least, HTTP connection pooling is now
enabled by default. You should always use a client as a context manager,
or call close(), or use no more than one client per process.

## 0.1.0 (2018-12-11)

  - Initial Release
