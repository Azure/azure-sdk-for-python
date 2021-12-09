---
page_type: sample
languages:
  - python
products:
  - azure
  - maps-service
urlFragment: maps-service-samples
---

# Maps Service API client library for Python Samples

The following are code samples that show common scenario operations with the Azure Maps Service API client library.

* [search.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/maps/azure-maps-samples/search.py) - Azure Maps Search Samples:
  * Get Search Address
  * Get Search Address Reverse
  * Get Search Address Reverse Cross Street
  * Get Search Address Structured
  * Get Search Fuzzy
  * Get Search POI
  * Get Search POI Category
  * Get Search POI Category Tree
  * Get Search Polygon
  * Post Search Address Batch
  * Post Search Address Reverse Batch
  * Post Search Fuzzy Batch
  * Post Search Inside Geometry

## Prerequisites
* Python 2.7 or 3.5.3+
* You must have an [Azure subscription](https://azure.microsoft.com/free/) and an
[Azure Maps account](https://docs.microsoft.com/azure/azure-maps/how-to-manage-account-keys) to run these samples.

## Setup

1. Install the latest beta version of Azure Maps Service that the samples use:

```bash
pip install azure-maps-service
```

2. Clone or download this sample repository.
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run. `SUBSCRIPTION_KEY` has to refer to your subscription key.
3. Follow the usage described in the file, e.g. `python alias.py`

## Next steps

Check out the [API reference documentation](https://aka.ms/azsdk-python-cosmos-ref) to learn more about what you can do with the Azure Maps Service API client library.