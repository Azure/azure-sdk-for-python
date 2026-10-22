---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-maps-timezone
---

# Samples for Azure Maps Timezone client library for Python

These code samples show common scenario operations with the Azure Maps Timezone client library.

Authenticate the client with Azure Maps Timezone [API Key Credential](https://learn.microsoft.com/azure/azure-maps/how-to-manage-account-keys):

Then for common Azure Maps Timezone operations:

* Get timezone by id: [get_timezone_by_id.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-timezone/samples/get_timezone_by_id.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-timezone/samples/async_samples/get_timezone_by_id_async.py))

* Get timezone by coordinates: [get_timezone_by_coordinates.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-timezone/samples/get_timezone_by_coordinates.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-timezone/samples/async_samples/get_timezone_by_coordinates_async.py))

* Get iana timezone ids: [get_iana_timezone_ids.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-timezone/samples/get_iana_timezone_ids.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-timezone/samples/async_samples/get_iana_timezone_ids_async.py))

* Get windows timezone ids: [get_windows_timezone_ids.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-timezone/samples/get_windows_timezone_ids.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-timezone/samples/async_samples/get_windows_timezone_ids_async.py))

* Get iana version: [get_iana_version.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-timezone/samples/get_iana_version.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-timezone/samples/async_samples/get_iana_version_async.py))

* Convert windows timezone to iana: [convert_windows_timezone_to_iana.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-timezone/samples/convert_windows_timezone_to_iana.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-timezone/samples/async_samples/convert_windows_timezone_to_iana_async.py))


## Prerequisites

* Python 3.8 or later is required to use this package
* You must have an [Azure subscription](https://azure.microsoft.com/free/)
* A deployed Maps Services resource. You can create the resource via [Azure Portal][azure_portal] or [Azure CLI][azure_cli].

## Setup

1. Install the Azure Maps Timezone client library for Python with [pip](https://pypi.org/project/pip/):

   ```bash
   pip install azure-maps-timezone --pre
   ```

2. Clone or download [this repository](https://github.com/Azure/azure-sdk-for-python)
3. Open this sample folder in [Visual Studio Code](https://code.visualstudio.com) or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python sample_geocode.py`

## Next steps

Check out the [API reference documentation](https://learn.microsoft.com/rest/api/maps/timezone)
to learn more about what you can do with the Azure Maps Timezone client library.

<!-- LINKS -->
[azure_portal]: https://portal.azure.com
[azure_cli]: https://learn.microsoft.com/cli/azure
