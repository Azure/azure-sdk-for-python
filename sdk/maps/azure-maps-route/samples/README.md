---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-maps-search
---

# Samples for Azure Maps Search client library for Python

These code samples show common scenario operations with the Azure Maps Search client library.

Authenticate the client with a Azure Maps Search [API Key Credential](https://docs.microsoft.com/azure/azure-maps/how-to-manage-account-keys):

[samples authentication](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/sample_authentication.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/async_samples/sample_authentication_async.py))

Then for common Azure Maps Search operations:

* Perform fuzzy search: [sample_fuzzy_search.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/sample_fuzzy_search.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/async_samples/sample_fuzzy_search_async.py))

* Perform get POI categories search: [sample_get_point_of_interest_categories.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/sample_get_point_of_interest_categories.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/async_samples/sample_get_point_of_interest_categories_async.py))

* Perform reverse search address: [sample_reverse_search_address.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/sample_reverse_search_address.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/async_samples/sample_reverse_search_address_async.py))

* Perform reverse search cross street address: [sample_reverse_search_cross_street_address.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/sample_reverse_search_cross_street_address.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/async_samples/sample_reverse_search_cross_street_address_async.py))

* Get search nearby POI: [sample_search_nearby_point_of_interest.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/sample_search_nearby_point_of_interest.py)) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/async_samples/sample_search_nearby_point_of_interest_async.py))

* Get search POI: [sample_search_point_of_interest.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/sample_search_point_of_interest.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/async_samples/sample_search_point_of_interest_async.py))

* Get search POI category: [sample_search_point_of_interest_category.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/sample_search_point_of_interest_category.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/async_samples/sample_search_point_of_interest_category_async.py))

* Perform search with structured address: [sample_search_structured_address.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/sample_search_structured_address.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/async_samples/sample_search_structured_address_async.py))

## Prerequisites

* Python 3.6 or later is required to use this package
* You must have an [Azure subscription](https://azure.microsoft.com/free/)
* A deployed Maps Services resource. You can create the resource via [Azure Portal][azure_portal] or [Azure CLI][azure_cli].

## Setup

1. Install the Azure Maps Search client library for Python with [pip](https://pypi.org/project/pip/):

   ```bash
   pip install azure-maps-search --pre
   ```

2. Clone or download [this repository](https://github.com/Azure/azure-sdk-for-python)
3. Open this sample folder in [Visual Studio Code](https://code.visualstudio.com) or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python sample_fuzzy_search.py`

## Next steps

Check out the [API reference documentation](https://docs.microsoft.com/rest/api/maps/search)
to learn more about what you can do with the Azure Maps Search client library.

<!-- LINKS -->
[azure_portal]: https://portal.azure.com
[azure_cli]: https://docs.microsoft.com/cli/azure
