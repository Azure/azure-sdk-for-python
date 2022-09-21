# Azure Maps Timezone Package client library for Python

This package contains a Python SDK for Azure Maps Services for Timezone.
Read more about Azure Maps Services [here](https://docs.microsoft.com/azure/azure-maps/)

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-timezone) | [API reference documentation](https://docs.microsoft.com/rest/api/maps/timezone) | [Product documentation](https://docs.microsoft.com/azure/azure-maps/)

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to <https://github.com/Azure/azure-sdk-for-python/issues/20691>_

## Getting started

### Prerequisites

- Python 3.7 or later is required to use this package.
- An [Azure subscription][azure_subscription] and an [Azure Maps account](https://docs.microsoft.com/azure/azure-maps/how-to-manage-account-keys).
- A deployed Maps Services resource. You can create the resource via [Azure Portal][azure_portal] or [Azure CLI][azure_cli].

If you use Azure CLI, replace `<resource-group-name>` and `<account-name>` of your choice, and select a proper [pricing tier](https://docs.microsoft.com/azure/azure-maps/choose-pricing-tier) based on your needs via the `<sku-name>` parameter. Please refer to [this page](https://docs.microsoft.com/cli/azure/maps/account?view=azure-cli-latest#az_maps_account_create) for more details.

```bash
az maps account create --resource-group <resource-group-name> --account-name <account-name> --sku <sku-name>
```

### Install the package

Install the Azure Maps Service Timezone SDK.

```bash
pip install azure-maps-timezone
```

### Create and Authenticate the MapsTimezoneClient

To create a client object to access the Azure Maps Timezone API, you will need a **credential** object. Azure Maps Timezone client also support two ways to authenticate:

1. Authenticate with subscription key credential
2. Authenticate with Azure Active Directory credential

#### Authenticate with a Subscription Key Credential

You can authenticate with your Azure Maps Subscription Key.
Once the Azure Maps Subscription Key is created, set the value of the key as environment variable: `AZURE_SUBSCRIPTION_KEY`.
Then pass an `AZURE_SUBSCRIPTION_KEY` as the `credential` parameter into an instance of [AzureKeyCredential][azure-key-credential].

```python
from azure.core.credentials import AzureKeyCredential
from azure.maps.timezone import MapsTimezoneClient

credential = AzureKeyCredential(os.environ.get("AZURE_SUBSCRIPTION_KEY"))
timezone_client = MapsTimezoneClient(credential=credential)
```

#### 2. Authenticate with an Azure Active Directory credential

You can authenticate with [Azure Active Directory (AAD) token credential][maps_authentication_aad] using the [Azure Identity library][azure_identity].
Authentication by using AAD requires some initial setup:

- Install [azure-identity][azure-key-credential]
- Register a [new AAD application][register_aad_app]
- Grant access to Azure Maps by assigning the suitable role to your service principal. Please refer to the [Manage authentication page][manage_aad_auth_page].

After setup, you can choose which type of [credential][azure-key-credential] from `azure.identity` to use.
As an example, [DefaultAzureCredential][default_azure_credential]
can be used to authenticate the client:

Next, set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`

You will also need to specify the Azure Maps resource you intend to use by specifying the `client_id` in the client argument. The Azure Maps resource client id can be found in the Authentication sections in the Azure Maps resource. Please refer to the [documentation][how_to_manage_authentication] on how to find it.

```python
from azure.maps.timezone import MapsTimezoneClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
timezone_client = MapsTimezoneClient(
    client_id="<Azure Maps Client ID>",
    credential=credential
)
```

## Key concepts

The Azure Maps Timezone client library for Python allows you to interact with each of the components through the use of a dedicated client object.

### Sync Clients

`MapsTimezoneClient` is the primary client for developers using the Azure Maps Timezone client library for Python.
Once you initialized a `MapsTimezoneClient` class, you can explore the methods on this client object to understand the different features of the Azure Maps Timezone service that you can access.

### Async Clients

This library includes a complete async API supported on Python 3.5+. To use it, you must first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/).
See [azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#transport) for more information.

Async clients and credentials should be closed when they're no longer needed. These
objects are async context managers and define async `close` methods.

## Examples

The following sections provide several code snippets covering some of the most common Azure Maps Timezone tasks, including:

- [Get timezone by IANA ID](#get-timezone-by-iana-id)
- [Get Timezone by Coordinates](#get-timezone-by-coordinates)
- [Get Windows Timezone ID](#get-windows-timezone-id)
- [Get IANA Timezone ID](#get-iana-timezone-id)
- [Get IANA Version](#get-iana-version)
- [Convert Windows Timezone to IANA](#convert-windows-timezone-to-iana)

### Get timezone by IANA ID

Get timezone information for specific IANA ID:

```python
timezone = timezone_client.get_timezone_by_id("America/New_York")

print("Timzone name: {}, tag: {}, standard offset: {}".format(
    timezone.time_zones[0].names.generic,
    timezone.time_zones[0].reference_time.tag,
    timezone.time_zones[0].reference_time.standard_offset,
))
```

### Get Timezone by Coordinates

This API can get timzone by coordinate:

```python
timezone = client.get_timezone_by_coordinates(
    coordinates=LatLon(52.5069,13.2843)
)

print("Timzone name: {}, tag: {}, standard offset: {}".format(
    timezone.time_zones[0].names.generic,
    timezone.time_zones[0].reference_time.tag,
    timezone.time_zones[0].reference_time.standard_offset,
))
```

### Get Windows Timezone ID

This API will return all timezones with Windows ID. You can enumerate from the returned list:

```python
timezone_ids = timezone_client.get_windows_timezone_ids()

for timezone in timezone_ids:
    print('Timezone "{}": IANA ID is {}'.format(timezone.windows_id, timezone.iana_ids[0]))
```

### Get IANA Timezone ID

This API will return all IANA timezone IDs. You can enumerate from the returned list:

```python
timezone_ids = timezone_client.get_iana_timezone_ids()

for timezone in timezone_ids:
    print("IANA ID: {}".format(timezone.id))
    if timezone.is_alias:
        print(" -> is also alias of {}".format(timezone.alias_of))
```

### Get IANA Version

This API will return IANA version:

```python
version = timezone_client.get_iana_version()

print("Current IANA versions is: {}".format(version.version))
```

convert_windows_timezone_to_iana

### Convert Windows Timezone to IANA

This API will convert Windows timezone to IANA. You need to assign windows ID as argument:

```python
windows_timezone = "pacific standard time"
iana_results = timezone_client.convert_windows_timezone_to_iana(windows_timezone)

print("IANA list for timezone {}:".format(windows_timezone))
for iana in iana_results:
    print(iana.id)
```

## Troubleshooting

### General

Maps Timezone clients raise exceptions defined in [Azure Core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md).

This list can be used for reference to catch thrown exceptions. To get the specific error code of the exception, use the `error_code` attribute, i.e, `exception.error_code`.

### Logging

This library uses the standard [logging](https://docs.python.org/3/library/logging.html) library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO level.

Detailed DEBUG level logging, including request/response bodies and unredacted headers, can be enabled on a client with the `logging_enable` argument:

```python
import sys
import logging
from azure.maps.timezone import MapsTimezoneClient

# Create a logger for the 'azure.maps.timezone' SDK
logger = logging.getLogger('azure.maps.timezone')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

client_id = "<Azure Maps Client ID>"
credential = DefaultAzureCredential()

# This client will log detailed information about its HTTP sessions, at DEBUG level
timezone_client = MapsTimezoneClient(
    credential=credential, client_id=client_id, logging_enable=True)
```

### Additional

Still running into issues? If you encounter any bugs or have suggestions, please file an issue in the [Issues](https://github.com/Azure/azure-sdk-for-python/issues) section of the project.

## Next steps

### More sample code

Get started with our [Maps Timezone samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-timezone/samples) ([Async Version samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-timezone/samples/async_samples)).

Several Azure Maps Timezone Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Maps Timezone

```bash
set AZURE_SUBSCRIPTION_KEY="<RealSubscriptionKey>"

pip install azure-maps-timezone --pre

python samples/sample_authentication.py
python sample/sample_get_timezone_range.py
python samples/sample_get_timezone_directions.py
python samples/sample_request_timezone_matrix.py
python samples/async_samples/sample_authentication_async.py
python samples/async_samples/sample_get_timezone_range_async.py
python samples/async_samples/sample_request_timezone_matrix_async.py
python samples/async_samples/sample_get_timezone_directions_async.py
```

> Notes: `--pre` flag can be optionally added, it is to include pre-release and development versions for `pip install`. By default, `pip` only finds stable versions.

Further detail please refer to [Samples Introduction](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/maps/azure-maps-timezone/samples/README.md)

### Additional documentation

For more extensive documentation on Azure Maps Timezone, see the [Azure Maps Timezone documentation](https://docs.microsoft.com/rest/api/maps/timezone) on docs.microsoft.com.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit <https://cla.microsoft.com>.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

<!-- LINKS -->
[azure_subscription]: https://azure.microsoft.com/free/
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity
[azure_portal]: https://portal.azure.com
[azure_cli]: https://docs.microsoft.com/cli/azure
[azure-key-credential]: https://aka.ms/azsdk/python/core/azurekeycredential
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[register_aad_app]: https://docs.microsoft.com/powershell/module/Az.Resources/New-AzADApplication?view=azps-8.0.0
[maps_authentication_aad]: https://docs.microsoft.com/azure/azure-maps/how-to-manage-authentication
[manage_aad_auth_page]: https://docs.microsoft.com/azure/azure-maps/how-to-manage-authentication
[how_to_manage_authentication]: https://docs.microsoft.com/azure/azure-maps/how-to-manage-authentication#view-authentication-details
